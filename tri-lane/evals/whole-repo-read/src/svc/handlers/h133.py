"""Handler h133."""
from ..core.router import route
from ..core import settings  # noqa: F401


@route("/orders/bulk-delete")
def handle(request):
    return {"ok": True, "handler": "h133"}
