use polars::prelude::*;
use std::path::Path;

pub fn read_email_csv(path: &Path, max_emails: Option<u32>) -> PolarsResult<DataFrame> {
    let df = LazyCsvReader::new(path).with_has_header(true).finish()?;

    match max_emails {
        Some(n) => df.slice(0, n).collect(),
        None => df.collect(),
    }
}
