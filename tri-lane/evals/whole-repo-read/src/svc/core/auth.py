"""Authentication decorator."""
from functools import wraps


def require_auth(fn):
    @wraps(fn)
    def inner(request, *a, **k):
        if not request.get("user"):
            raise PermissionError("unauthenticated")
        return fn(request, *a, **k)
    inner.__auth__ = True
    return inner
