"""Module mod03: computes derived values for widget 3."""
from pkg.log import log


def scale(value, factor=3):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"mod03:{x}" for x in items]
