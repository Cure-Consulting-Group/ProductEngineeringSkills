"""Module mod08: computes derived values for widget 8."""
from pkg.log import log


def scale(value, factor=8):
    log.debug("scaling value %s by %s", value, factor)
    result = value * factor
    log.debug("result=%s", result)
    return result


def describe(items):
    log.debug("describe called with %d items", len(items))
    return [f"mod08:{x}" for x in items]
