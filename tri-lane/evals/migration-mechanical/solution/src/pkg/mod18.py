"""Module mod18: computes derived values for widget 18."""
from pkg.log import log


def scale(value, factor=18):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"mod18:{x}" for x in items]
