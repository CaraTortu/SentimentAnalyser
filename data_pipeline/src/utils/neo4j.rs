use indicatif::{ProgressBar, ProgressStyle};
use neo4rs::{ConfigBuilder, Graph, query};
use polars::prelude::*;
use std::{env, error::Error, time::Duration};
use tokio::task::JoinHandle;

static INSERT_SENTIMENT_QUERY: &str = "
MATCH (p:Project {datasetName: $datasetName})
MERGE (sender:User {email: $senderEmail})
MERGE (receiver:User {email: $receiverEmail})
MERGE (sender)-[r:SENTIMENT]-(receiver)
MERGE (p)-[:OWNS]->(sender)
MERGE (p)-[:OWNS]->(receiver)
ON CREATE SET r.sentiment = $sentiment, r.emailsSent = $emailsSent
ON MATCH SET r.sentiment = $sentiment, r.emailsSent = $emailsSent
RETURN sender, receiver, r
";

static CREATE_PROJECT_QUERY: &str = "
CREATE (p:Project {datasetName: $datasetName})
RETURN p
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
        let sentiment_query = INSERT_SENTIMENT_QUERY.to_string();

        // Create project
        let creation_res = self
            .graph
            .run(query(CREATE_PROJECT_QUERY).param("datasetName", project_name.to_string()))
            .await;

        if let Err(_) = creation_res {
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
        let tasks: Vec<JoinHandle<Result<(), String>>> = df
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
            .into_iter()
            .map(|row| {
                let row = row.clone();
                let graph = self.graph.clone();
                let project_name = project_name.clone();
                let sentiment_query = sentiment_query.clone();
                let progress_bar = progress_bar.clone();

                return tokio::spawn(async move {
                    progress_bar.inc(1);
                    let db_query = query(&sentiment_query)
                        .param("datasetName", project_name)
                        .param("senderEmail", row.from.clone())
                        .param("receiverEmail", row.to.clone())
                        .param("sentiment", row.mean_sentiment)
                        .param("emailsSent", row.email_count);

                    match graph.run(db_query).await {
                        Err(_) => Err("Could not connect to database. Is your .env okay?".into()),
                        Ok(_) => Ok(()),
                    }
                });
            })
            .collect();

        for r in tasks {
            let task_res = r.await.unwrap();

            if let Err(_) = task_res {
                return task_res;
            }
        }
        progress_bar.finish();

        Ok(())
    }
}
