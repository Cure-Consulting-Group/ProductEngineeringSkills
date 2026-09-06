"""Handler h178."""
from ..core.router import route
from ..core import settings  # noqa: F401


@route("/users/impersonate")
def handle(request):
    return {"ok": True, "handler": "h178"}
