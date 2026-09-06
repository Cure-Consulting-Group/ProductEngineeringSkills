"""Module mod26: computes derived values for widget 26."""
from pkg.log import log


def scale(value, factor=26):
    print("scaling value", value, "by", factor)
    result = value * factor
    print(f"result={result}")
    return result


def describe(items):
    print("describe called with %d items" % len(items))
    return [f"mod26:{x}" for x in items]
