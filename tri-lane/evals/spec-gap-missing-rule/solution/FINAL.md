Stopping before implementing: the spec is consistent but incomplete in two places the tests depend on.

1. Tie-break rule is unspecified. Three players share 10 points and the visible test expects Ava then Bo (and not Zoe), which implies alphabetical order among ties, but the spec does not say so; stable input order or most-recent-first would be equally valid readings.
2. Behaviour with fewer than three players is unspecified. The visible test expects the shorter list, but the spec could equally intend padding or an error.

Please state the tie-break and the short-list rule and I will implement.
