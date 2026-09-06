"""Module mod23: computes derived values for widget 23."""
from pkg.log import log


def scale(value, factor=23):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"mod23:{x}" for x in items]
