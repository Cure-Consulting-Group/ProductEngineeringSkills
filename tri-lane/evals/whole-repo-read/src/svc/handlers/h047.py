"""Handler h047."""
from ..core.router import route
from ..core import settings  # noqa: F401


@route("/admin/export")
def handle(request):
    return {"ok": True, "handler": "h047"}
