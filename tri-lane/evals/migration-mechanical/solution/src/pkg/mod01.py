"""Module mod01: computes derived values for widget 1."""
from pkg.log import log


def scale(value, factor=1):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"mod01:{x}" for x in items]
