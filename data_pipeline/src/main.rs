mod utils;

use dotenv::dotenv;
use indicatif::{ProgressBar, ProgressStyle};
use log::{error, info};
use std::{path::Path, process::exit, time::Duration};
use utils::{
    csv::read_email_csv, data_parser::DataOutput, emails::parse_email, logger::SimpleLogger,
    neo4j::Neo4JService, sentiment::SentimentAnalyser, text::TextCleaner,
};

static LOGGER: SimpleLogger = SimpleLogger;

#[tokio::main]
async fn main() {
    // Read .env file
    dotenv().ok();

    // Setup logger
    log::set_logger(&LOGGER)
        .map(|()| log::set_max_level(log::LevelFilter::Debug))
        .expect("[-] Unable to setup logger");

    // Connect to neo4j
    // We do this early to make sure we have a server connection
    let neoservice = Neo4JService::new().await;
    if let Err(_) = neoservice {
        error!("Could not connect to Neo4J. Is your .env okay?");
        exit(1);
    }

    let neoservice = neoservice.unwrap();

    // Read CSV
    info!("Reading email dataset");
    let csv_path = Path::new("./datasets/emails.csv");
    let email_df = read_email_csv(&csv_path, Some(1000));

    if let Err(_) = email_df {
        error!("Could not open dataset: {}", csv_path.to_str().unwrap());
        exit(1);
    }

    // Read message column
    let email_df = email_df.unwrap();

    // TODO: allow setting through CLI
    let email_col_name = "message";
    let email_messages = email_df.column(email_col_name);

    if let Err(_) = email_messages {
        error!("Could not get column '{}' from dataset", email_col_name);
        exit(1);
    }

    let email_messages = email_messages.unwrap();

    // Prepare data
    let messages = email_messages.str().unwrap();
    let mut output = DataOutput::default();
    let text_cleaner = TextCleaner::default();
    let sentiment_analyser = SentimentAnalyser::new();

    if let Err(e) = sentiment_analyser {
        error!("{e}");
        exit(1);
    }

    let sentiment_analyser = sentiment_analyser.unwrap();

    // Only doing this so you the bar does not duplicate
    let _ = sentiment_analyser.get_sentiment("");

    // Set up progress bar
    let progress_bar = ProgressBar::new(email_messages.len() as u64);
    progress_bar.set_style(
            ProgressStyle::default_bar()
                .template("{pos}/{len} [{bar:40.cyan/blue}] {percent}% | ETA: {eta} | Elapsed: {elapsed} | {per_sec} it/s")
                .unwrap()
                .progress_chars("#>-"),
        );
    progress_bar.enable_steady_tick(Duration::from_millis(100));

    // Parse emails
    info!("Parsing emails");
    messages.iter().for_each(|msg| {
        progress_bar.inc(1);

        if let None = msg {
            return;
        }

        let email = parse_email(msg.unwrap());
        if let None = email {
            return;
        }

        let email = email.unwrap();

        let clean_text = text_cleaner.clean(&email.content);
        let sentiment = sentiment_analyser.get_sentiment(&clean_text);
        if let Err(_) = sentiment {
            error!("Could not get sentiment");
            return;
        }

        output.add_col(email.from, email.to, sentiment.unwrap());
    });

    progress_bar.finish();

    // Group data
    info!("Grouping data by 'To' and 'From' addresses");
    let clean_df = output.to_grouped_dataframe();
    if let Err(_) = clean_df {
        error!("Could not group dataframe");
        exit(1);
    }

    let clean_df = clean_df.unwrap();

    // Save to Neo4J
    info!("Adding data to Neo4J");

    // TODO: allow setting project name through CLI
    let res = neoservice.add_data(clean_df, "test").await;
    if let Err(_) = res {
        error!("Could not add users to Neo4J");
        exit(1);
    }

    info!("Done!");
}
