#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1

# 1. build_logo.jsx must exist
[ -f build_logo.jsx ] || exit 1

# 2. Check for CMYK document configuration
grep -qi "DocumentColorMode.CMYK" build_logo.jsx || exit 1

# 3. Check for the 4 artboards
grep -qi "01_Primary" build_logo.jsx || exit 1
grep -qi "02_Stacked" build_logo.jsx || exit 1
grep -qi "03_Submark" build_logo.jsx || exit 1
grep -qi "04_Monochrome" build_logo.jsx || exit 1

# 4. Check for layer hierarchy
grep -qi "Guides" build_logo.jsx || exit 1
grep -qi "Artwork" build_logo.jsx || exit 1
grep -qi "Typography" build_logo.jsx || exit 1

# 5. Check for spot swatches
grep -qi "spots.add" build_logo.jsx || exit 1

exit 0
