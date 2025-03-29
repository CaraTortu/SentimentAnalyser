use mail_parser::MessageParser;

pub struct Email {
    pub from: String,
    pub to: String,
    pub content: String,
}

pub fn parse_email(s: &str) -> Option<Email> {
    let email = MessageParser::new().parse(s).unwrap();
    let email_from = email.from()?.first()?.address.clone()?.to_string();
    let email_to = email.to()?.first()?.address.clone()?.to_string();
    let email_text = email.body_text(0)?.to_string();

    Some(Email {
        from: email_from,
        to: email_to,
        content: email_text,
    })
}
