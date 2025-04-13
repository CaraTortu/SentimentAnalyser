use indicatif::{ProgressBar, ProgressStyle};
use log::{debug, info};
use neo4rs::{ConfigBuilder, Graph, query};
use polars::prelude::*;
use std::{env, error::Error, time::Duration};

static INSERT_SENTIMENT_QUERY: &str = "
MATCH (p:Project {datasetName: $datasetName})
MERGE (p)-[:OWNS]->(sender:User {email: $senderEmail})
MERGE (p)-[:OWNS]->(receiver:User {email: $receiverEmail})
MERGE (sender)-[r:SENTIMENT]-(receiver)
ON CREATE SET r.sentiment = $sentiment, r.emailsSent = $emailsSent
ON MATCH SET r.sentiment = $sentiment, r.emailsSent = $emailsSent
RETURN sender, receiver, r
";

static CREATE_PROJECT_QUERY: &str = "
CREATE (p:Project {datasetName: $datasetName})
RETURN p
";

static DELETE_PROJECT_QUERY: &str = "
MATCH (p:Project {datasetName: $datasetName}), (p)-[:OWNS]->(n)
DETACH DELETE n
DELETE p
";

static GET_PROJECT_QUERY: &str = "
MATCH (p:Project {datasetName: $datasetName})
RETURN p.datasetName
";

static GET_PROJECTS_QUERY: &str = "
MATCH (p:Project) RETURN p.datasetName as dName
";

pub struct Neo4JService {
    graph: Arc<Graph>,
}

#[derive(Debug, Clone)]
struct RowData {
    from: String,
    to: String,
    mean_sentiment: f32,
    email_count: u32,
}

impl Neo4JService {
    pub async fn new() -> Result<Self, Box<dyn Error>> {
        let config = ConfigBuilder::default()
            .uri(env::var("NEO4J_URL")?)
            .user(env::var("NEO4J_USER")?)
            .password(env::var("NEO4J_PASSWORD")?)
            .db(env::var("NEO4J_DB")?)
            .fetch_size(500)
            .max_connections(10)
            .build()?;

        let graph = Arc::new(Graph::connect(config).await?);

        Ok(Self { graph })
    }

    pub async fn add_data(&self, df: DataFrame, project_name: &str) -> Result<(), String> {
        let project_name = project_name.to_string();

        // Create project
        let creation_res = self
            .graph
            .run(query(CREATE_PROJECT_QUERY).param("datasetName", project_name.to_string()))
            .await;

        if let Err(e) = creation_res {
            debug!("{e}");
            return Err("Could not connect to database. Is your .env okay?".into());
        }

        // Set up progress bar
        let progress_bar = Arc::new(ProgressBar::new(df.shape().0 as u64));
        progress_bar.set_style(
            ProgressStyle::default_bar()
                .template("{pos}/{len} [{bar:40.cyan/blue}] {percent}% | ETA: {eta} | Elapsed: {elapsed} | {per_sec} it/s")
                .unwrap()
                .progress_chars("#>-"),
        );
        progress_bar.enable_steady_tick(Duration::from_millis(100));

        // Create users
        let tasks: Vec<RowData> = df
            .into_struct("entries".into())
            .into_series()
            .iter()
            .map(|d| {
                let row_values: Vec<_> = d._iter_struct_av().collect();
                RowData {
                    from: row_values[0].get_str().unwrap().to_string(),
                    to: row_values[1].get_str().unwrap().to_string(),
                    email_count: row_values[2].try_extract().unwrap(),
                    mean_sentiment: row_values[3].try_extract().unwrap(),
                }
            })
            .collect();

        for row in tasks {
            let project_name = project_name.clone();

            let db_query = query(INSERT_SENTIMENT_QUERY)
                .param("datasetName", project_name)
                .param("senderEmail", row.from.clone())
                .param("receiverEmail", row.to.clone())
                .param("sentiment", row.mean_sentiment)
                .param("emailsSent", row.email_count);

            match self.graph.run(db_query).await {
                Err(e) => {
                    debug!("{}", e);
                    return Err("Could not connect to database. Is your .env okay?".into());
                }
                Ok(_) => progress_bar.inc(1),
            }
        }

        progress_bar.finish();

        Ok(())
    }

    pub async fn delete_graph(&self, name: &str) -> Result<(), String> {
        // First, check if the graph exists
        let exists_query = query(GET_PROJECT_QUERY).param("datasetName", name);
        let result = self.graph.execute(exists_query).await;

        if let Err(e) = result {
            debug!("{e}");
            return Err("Could not connect to database. Is your .env okay?".to_owned());
        }

        let result_row = result.unwrap().next().await;

        if let Err(e) = result_row {
            debug!("{e}");
            return Err("Could not get row".to_owned());
        }

        let result_row = result_row.unwrap();

        if let None = result_row {
            return Err(format!("Graph with name '{name}' does not exist"));
        }

        info!("Found graph with name '{name}'. Deleting...");

        let delete_query = query(DELETE_PROJECT_QUERY).param("datasetName", name);
        let delete_result = self.graph.run(delete_query).await;

        match delete_result {
            Ok(_) => Ok(()),
            Err(e) => {
                debug!("{e}");
                Err("Could not connect to database. Is your .env okay?".to_owned())
            }
        }
    }

    pub async fn get_graphs(&self) -> Result<Vec<String>, String> {
        let mut graphs: Vec<String> = vec![];

        let result = self.graph.execute(query(GET_PROJECTS_QUERY)).await;

        if let Err(e) = result {
            debug!("{e}");
            return Err("Could not connect to database. Is your .env okay?".to_owned());
        }

        let mut result = result.unwrap();
        while let Ok(Some(r)) = result.next().await {
            let name: String = r.get("dName").unwrap();
            graphs.push(name);
        }

        Ok(graphs)
    }
}
