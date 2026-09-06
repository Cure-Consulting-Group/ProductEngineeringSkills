"""Module mod07: computes derived values for widget 7."""
from pkg.log import log


def scale(value, factor=7):
    print("scaling value", value, "by", factor)
    result = value * factor
    print(f"result={result}")
    return result


def describe(items):
    print("describe called with %d items" % len(items))
    return [f"mod07:{x}" for x in items]
