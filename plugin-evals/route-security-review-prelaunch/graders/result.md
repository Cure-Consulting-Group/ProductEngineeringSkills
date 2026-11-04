---
type: regex
pattern: '(?:OWASP|A0[1-9]|IDOR|BOLA|broken (?:object[- ]level |function[- ]level )?authori[sz]ation|injection|(?:any|another|other|every) (?:logged[- ]in |authenticated |signed[- ]in )?users?[^.\n]{0,60}(?:change|overwrite|modify|update|read|delete|replace)[^.\n]{0,60}(?:other|another|anyone|someone|any user)|other users.? (?:data|address(?:es)?|avatars?|photos?|files?|documents?)|request\.auth\.uid\s*==\s*userId|verif(?:y|ied|ies) (?:the )?(?:session|id token|identity)|never (?:accept|trust) (?:the )?userId)'
flags: i
---
