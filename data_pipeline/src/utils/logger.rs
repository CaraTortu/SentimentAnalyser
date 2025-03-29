use log::{Level, Metadata, Record};

pub struct SimpleLogger;

impl log::Log for SimpleLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= Level::Info
    }

    fn log(&self, record: &Record) {
        let start = match record.level() {
            Level::Error => "[-] ERROR",
            Level::Warn => "[i] WARNING",
            Level::Info => "[i] INFO",
            Level::Debug => "[dbg]",
            Level::Trace => "[trc]",
        };

        if self.enabled(record.metadata()) {
            println!("{}: {}", start, record.args());
        }
    }

    fn flush(&self) {}
}
