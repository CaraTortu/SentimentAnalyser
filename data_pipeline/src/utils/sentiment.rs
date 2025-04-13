use std::{fs::File, io::BufReader};

use finalfusion::{
    prelude::{Embeddings, ReadTextDims},
    vocab::{SimpleVocab, Vocab},
};
use log::{debug, info};
use tensorflow::{Graph, Operation, SavedModelBundle, SessionOptions, SessionRunArgs, Tensor};

pub struct SentimentAnalyser {
    vocab: SimpleVocab,
    model_bundle: SavedModelBundle,
    input_op: Operation,
    input_idx: i32,
    output_op: Operation,
    output_idx: i32,
}

static GLOVE_PATH: &str = "models/glove-wiki-gigaword-100.model";
static MODEL_PATH: &str = "models/emails";
static TEXT_LENGTH: usize = 800;

impl SentimentAnalyser {
    pub fn new() -> Result<Self, String> {
        // Load vocabulary
        let glove_model = File::open(GLOVE_PATH);

        if let Err(e) = glove_model {
            debug!("{e}");
            return Err(format!("Could not load gLoVe model at '{GLOVE_PATH}'"));
        }

        let mut reader = BufReader::new(glove_model.unwrap());

        // Get embeddings
        let embeddings = Embeddings::read_text_dims(&mut reader);
        if let Err(e) = embeddings {
            debug!("{e}");
            return Err("Could not load embedding model".to_owned());
        }

        let embeddings = embeddings.unwrap();

        // Load tensorflow graph
        info!("Loading tensorflow model");

        let mut graph = Graph::new();
        let options = SessionOptions::new();

        // Get model
        let model_bundle = SavedModelBundle::load(&options, &["serve"], &mut graph, MODEL_PATH);
        if let Err(e) = model_bundle {
            debug!("{e}");
            return Err("Could not load model".into());
        }

        let model_bundle = model_bundle.unwrap();

        // Get graph serve signature
        let graph_definition = model_bundle.meta_graph_def();
        let serv_default = graph_definition.get_signature("serve");
        if let Err(e) = serv_default {
            debug!("{e}");
            return Err("Could not get model serve signature".into());
        }

        let serv_default = serv_default.unwrap();

        // Get model input layer
        let model_input = serv_default.get_input("input_layer");
        if let Err(e) = model_input {
            debug!("{e}");
            return Err("Could not get model input layer".into());
        }

        let model_input = model_input.unwrap();
        let model_input_index = model_input.name().index;

        // Get model output layer
        let model_output = serv_default.get_output("output_0");
        if let Err(e) = model_output {
            debug!("{e}");
            return Err("Could not get model output layer".into());
        }

        let model_output = model_output.unwrap();
        let model_output_index = model_output.name().index;

        // Get model input operation
        let input_op = graph
            .operation_by_name_required(&model_input.name().name)
            .unwrap();

        // Get model output operation
        let output_op = graph
            .operation_by_name_required(&model_output.name().name)
            .unwrap();

        Ok(Self {
            vocab: embeddings.vocab().to_owned(),
            model_bundle,
            input_op,
            input_idx: model_input_index,
            output_op,
            output_idx: model_output_index,
        })
    }

    fn embed_sentence(&self, text: &str) -> Vec<f32> {
        let mut encoded = Vec::new();

        for w in text.split(" ") {
            let idx = self.vocab.idx(w);

            if let Some(v) = idx {
                encoded.push(v.word().unwrap() as f32)
            }
        }

        encoded
    }

    fn pad_seq<T: Copy>(&self, items: &Vec<T>, filler: T, len: usize) -> Vec<T> {
        let mut padded_encoded = vec![filler; len.saturating_sub(items.len())];
        padded_encoded.extend(items);
        padded_encoded[..len].to_vec()
    }

    pub fn get_sentiment(&self, text: &str) -> tensorflow::Result<f32> {
        // Embed sentence
        let encoded = self.embed_sentence(text);

        // Pad sequence
        let encoded = self.pad_seq(&encoded, 0.0, TEXT_LENGTH);
        let input_tensor = Tensor::new(&[1, TEXT_LENGTH as u64]).with_values(&encoded)?;

        // Go through model
        let mut steps = SessionRunArgs::new();
        steps.add_feed(&self.input_op, self.input_idx, &input_tensor);
        let output_fetch = steps.request_fetch(&self.output_op, self.output_idx);

        // Run the model steps
        self.model_bundle.session.run(&mut steps)?;

        // Get output
        let output = steps.fetch::<f32>(output_fetch)?;
        Ok(output.first().unwrap().to_owned())
    }
}
