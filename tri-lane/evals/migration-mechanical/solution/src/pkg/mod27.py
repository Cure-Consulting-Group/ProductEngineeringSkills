"""Module mod27: computes derived values for widget 27."""
from pkg.log import log


def scale(value, factor=27):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"mod27:{x}" for x in items]
