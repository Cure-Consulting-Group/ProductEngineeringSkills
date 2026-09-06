"""Route registry."""
ROUTES = {}


def route(path):
    def deco(fn):
        ROUTES[path] = fn
        return fn
    return deco
