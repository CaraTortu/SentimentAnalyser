use polars::{
    df,
    error::PolarsResult,
    frame::DataFrame,
    prelude::{IntoLazy, col, when},
};

pub struct DataOutput {
    from: Vec<String>,
    to: Vec<String>,
    sentiment: Vec<f32>,
}

impl Default for DataOutput {
    fn default() -> Self {
        Self {
            from: Vec::new(),
            to: Vec::new(),
            sentiment: Vec::new(),
        }
    }
}

impl DataOutput {
    pub fn add_col(&mut self, from: String, to: String, sentiment: f32) {
        self.from.push(from);
        self.to.push(to);
        self.sentiment.push(sentiment);
    }

    pub fn to_grouped_dataframe(&self) -> PolarsResult<DataFrame> {
        let clean_df = df!("From" => self.from.clone(), 
            "To" => self.to.clone(), 
            "Sentiment" => self.sentiment.clone())?;

        clean_df
            .lazy()
            .with_columns([
                when(col("From").lt(col("To")))
                    .then(col("From"))
                    .otherwise(col("To"))
                    .alias("From"),
                when(col("From").lt(col("To")))
                    .then(col("To"))
                    .otherwise(col("From"))
                    .alias("To"),
            ])
            .group_by([col("From"), col("To")])
            .agg([
                col("Sentiment").count().alias("Emails_sent"),
                col("Sentiment").mean().alias("Mean_sentiment"),
            ])
            .collect()
    }
}
