#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1

# 1. logo.svg check: exists, valid XML, viewBox present, no raster tags
[ -f logo.svg ] || exit 1
grep -qi "viewbox" logo.svg || exit 1
grep -qi "<image" logo.svg && exit 1
grep -qi "data:image" logo.svg && exit 1
python3 -c "import xml.etree.ElementTree as ET; ET.parse('logo.svg')" || exit 1

# 2. tokens.json check: valid JSON, contains color and spacing
[ -f tokens.json ] || exit 1
python3 -c "
import json
with open('tokens.json') as f:
    d = json.load(f)
assert any(k in d for k in ['color', 'colors', 'colour'])
assert any(k in d for k in ['spacing', 'space', 'dimensions', 'dimension'])
" || exit 1

# 3. BRAND.md check: archetype and contrast
[ -f BRAND.md ] || exit 1
grep -qi "archetype" BRAND.md || exit 1
grep -qi "contrast" BRAND.md || exit 1

exit 0
