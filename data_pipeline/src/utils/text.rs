use regex::Regex;
use std::collections::HashMap;

fn get_emoticon_map<'a>() -> HashMap<&'a str, &'a str> {
    let mut emoticon_map = HashMap::new();

    emoticon_map.insert(" :)", " happy");
    emoticon_map.insert(" :(", " sad");
    emoticon_map.insert(" :D", " very happy");
    emoticon_map.insert(" :|", " neutral");
    emoticon_map.insert(" :O", " surprised");
    emoticon_map.insert(" <3", " love");
    emoticon_map.insert(" ;)", " wink");
    emoticon_map.insert(" :P", " playful");
    emoticon_map.insert(" :/", " confused");
    emoticon_map.insert(" :*", " kiss");
    emoticon_map.insert(" :')", " touched");
    emoticon_map.insert(" XD", " laughing");
    emoticon_map.insert(" :3", " cute");
    emoticon_map.insert(" >:(", " angry");
    emoticon_map.insert(" :-O", " shocked");
    emoticon_map.insert(" :|]", " robot");
    emoticon_map.insert(" :>", " sly");
    emoticon_map.insert(" ^_^", " happy");
    emoticon_map.insert(" O_o", " confused");
    emoticon_map.insert(" :-|", " straight face");
    emoticon_map.insert(" :X", " silent");
    emoticon_map.insert(" B-)", " cool");
    emoticon_map.insert(" <(‘.'<)", " dance");
    emoticon_map.insert(" (-_-)", " bored");
    emoticon_map.insert(" (>_<)", " upset");
    emoticon_map.insert(" (¬‿¬)", " sarcastic");
    emoticon_map.insert(" (o_o)", " surprised");
    emoticon_map.insert(" (o.O)", " shocked");
    emoticon_map.insert(" :0", " shocked");
    emoticon_map.insert(" :*(", " crying");
    emoticon_map.insert(" :v ", " pac-Man");
    emoticon_map.insert(" (^_^)v ", " double victory");
    emoticon_map.insert(" :-D", " big grin");
    emoticon_map.insert(" :-*", " blowing a kiss");
    emoticon_map.insert(" :^)", " nosey");
    emoticon_map.insert(" :-((", " very sad");
    emoticon_map.insert(" :-(", " frowning");

    emoticon_map
}

#[derive(Debug)]
pub struct TextCleaner<'a> {
    url: Regex,
    emoji_map: HashMap<&'a str, &'a str>,
}

impl Default for TextCleaner<'_> {
    fn default() -> Self {
        let url_regex = Regex::new(r"https?://\S+|www\.\S+").expect("REGEX should be valid");

        Self {
            url: url_regex,
            emoji_map: get_emoticon_map(),
        }
    }
}

impl TextCleaner<'_> {
    fn clean_emoticons(&self, s: &str) -> String {
        let mut final_string = s.to_owned();

        for (k, v) in &self.emoji_map {
            final_string = final_string.replace(k, v);
        }

        final_string
    }

    fn clean_links(&self, s: &str) -> String {
        self.url.replace_all(s, r"").to_string()
    }

    fn clean_repeat_chars(&self, s: &str) -> String {
        let mut final_str = String::new();

        // Make sure to only run this function if it has more than 2 characters
        if s.len() <= 1 {
            return s.to_string();
        }

        let mut cur_char = s.chars().nth(0).unwrap();
        let mut cur_count = 1;

        final_str.push(cur_char);

        for c in s.get(1..).unwrap().chars() {
            if c == cur_char {
                cur_count += 1;
            } else {
                cur_char = c;
                cur_count = 1;
            }

            if cur_count > 2 && c == cur_char {
                continue;
            } else if cur_count > 1 && c == ' ' {
                continue;
            }

            final_str.push(cur_char);
        }

        final_str
    }

    fn clean_short_words(&self, s: &str) -> String {
        s.split_whitespace()
            .filter(|word| word.chars().count() >= 3)
            .collect::<Vec<&str>>()
            .join(" ")
    }

    fn clean_invalid_chars(&self, s: &str) -> String {
        s.chars()
            .filter(|c| c.is_alphabetic() || *c == ' ')
            .collect()
    }

    pub fn clean(&self, s: &str) -> String {
        let mut cur_text = s.to_string();

        cur_text = self.clean_emoticons(&cur_text);

        cur_text = cur_text.to_lowercase();
        cur_text = self.clean_links(&cur_text);
        cur_text = self.clean_short_words(&cur_text);
        cur_text = self.clean_invalid_chars(&cur_text);
        cur_text = self.clean_repeat_chars(&cur_text);

        return cur_text.trim().to_string();
    }
}
