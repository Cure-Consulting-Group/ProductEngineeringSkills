#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1

# 1. tokens.json must exist and parse
[ -f tokens.json ] || exit 1
python3 -c "
import json
with open('tokens.json') as f:
    t = json.load(f)
text = json.dumps(t).lower()
assert 'light' in text or 'dark' in text or 'color' in text
assert any(s in text for s in ['space', 'spacing', 'dimension'])
" || exit 1

# 2. FIGMA_SPEC.md must exist and contain Auto-Layout and Variants
[ -f FIGMA_SPEC.md ] || exit 1
grep -qi "auto.*layout" FIGMA_SPEC.md || exit 1
grep -qi "variant" FIGMA_SPEC.md || exit 1
grep -qi "variable" FIGMA_SPEC.md || exit 1

exit 0
