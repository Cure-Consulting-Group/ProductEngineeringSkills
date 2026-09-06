"""Module mod21: computes derived values for widget 21."""
from pkg.log import log


def scale(value, factor=21):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"mod21:{x}" for x in items]
