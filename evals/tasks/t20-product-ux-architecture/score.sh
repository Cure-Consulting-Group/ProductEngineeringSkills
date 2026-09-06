#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f design/spec.json ] || exit 1
python3 - <<'PY' || exit 1
import json
d = json.load(open("design/spec.json"))
screens = d.get("screens", [])
assert len(screens) >= 3, "need 3 screens"
assert any(r.get("fixed") for s in screens for r in s.get("regions", [])), "no fixed region"
assert d.get("flows"), "no flows"
notes = " ".join(n.lower() for s in screens for n in s.get("notes", []))
for word in ("empty", "error", "long"):
    assert word in notes, f"notes missing {word}"
PY
[ -f design/wireframes/flow.svg ] || exit 1
[ -f design/wireframes/inventory.md ] || exit 1
[ "$(ls design/wireframes/screens/*.svg 2>/dev/null | wc -l | tr -d ' ')" -ge 3 ] || exit 1
[ "$(grep -c '^Decision:' design/decisions.md 2>/dev/null)" -ge 3 ] || exit 1
grep -qi 'Reason:' design/decisions.md || exit 1
for s in empty loading error offline long; do grep -qi "$s" design/states.md || exit 1; done
exit 0
