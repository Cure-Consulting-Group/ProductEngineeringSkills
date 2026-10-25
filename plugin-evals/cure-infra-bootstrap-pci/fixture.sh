#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). A Next.js + Firebase + Stripe project with no
# claude.manifest.json yet, so the skill's mode is `init`; PCI + GDPR flags apply.
set -euo pipefail
cat > package.json <<'__FIXTURE_EOF__'
{
  "name": "parcel-checkout",
  "private": true,
  "dependencies": {
    "next": "16.0.3",
    "react": "19.2.0",
    "firebase": "12.4.0",
    "stripe": "19.1.0"
  }
}
__FIXTURE_EOF__
echo "# parcel-checkout" > README.md
