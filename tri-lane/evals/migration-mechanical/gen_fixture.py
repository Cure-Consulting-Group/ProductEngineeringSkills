#!/usr/bin/env python3
"""Generates the 30 modules of src/pkg and their reference solutions. Run once when editing the fixture; committed output is what lanes see."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src" / "pkg"
SOL = HERE / "solution" / "src" / "pkg"
for d in (SRC, SOL):
    d.mkdir(parents=True, exist_ok=True)

LOG = 'import logging\n\nlog = logging.getLogger("pkg")\n'
(SRC / "log.py").write_text(LOG)
(SOL / "log.py").write_text(LOG)
(SRC / "__init__.py").write_text("")
(SOL / "__init__.py").write_text("")

for i in range(1, 31):
    name = f"mod{i:02d}"
    before = f'''"""Module {name}: computes derived values for widget {i}."""
from pkg.log import log


def scale(value, factor={i}):
    print("scaling value", value, "by", factor)
    result = value * factor
    print(f"result={{result}}")
    return result


def describe(items):
    print("describe called with %d items" % len(items))
    return [f"{name}:{{x}}" for x in items]
'''
    after = f'''"""Module {name}: computes derived values for widget {i}."""
from pkg.log import log


def scale(value, factor={i}):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"{name}:{{x}}" for x in items]
'''
    (SRC / f"{name}.py").write_text(before)
    (SOL / f"{name}.py").write_text(after)
print("generated 30 modules")
