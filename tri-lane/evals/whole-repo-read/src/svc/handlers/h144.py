"""Handler h144."""
from ..core.auth import require_auth
from ..core.router import route


@route("/api/v1/resource144")
@require_auth
def handle(request):
    return {"ok": True, "handler": "h144"}
