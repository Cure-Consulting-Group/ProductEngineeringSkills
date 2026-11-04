---
type: regex
pattern: '(?:AIza|Firebase (?:web )?API key|apiKey)[\s\S]{0,400}(?:public identifier|not (?:a )?secret|isn.t (?:a )?secret|not sensitive|safe to (?:ship|expose|commit|embed)|meant to be public|designed to be public|public by design|intended to be public|(?:isn.t|is not|not) (?:a )?(?:leak|leaked secret|credential)|(?:fine|expected|normal|okay) (?:to be|in) (?:public|client|the client)|restrict (?:it|the key) to your domains)'
flags: i
---
