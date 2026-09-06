"""Module mod09: computes derived values for widget 9."""
from pkg.log import log


def scale(value, factor=9):
    print("scaling value", value, "by", factor)
    result = value * factor
    print(f"result={result}")
    return result


def describe(items):
    print("describe called with %d items" % len(items))
    return [f"mod09:{x}" for x in items]
