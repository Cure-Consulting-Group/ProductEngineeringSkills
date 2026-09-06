#!/usr/bin/env python3
"""Generates a 200-module service repo for the whole-repo read fixture. Facts needed for the answer are far apart:
three handlers lack the auth decorator, and the shared secret's env var name lives in a settings module that
is reachable only through an alias chain. Deterministic."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src" / "svc"
for d in (SRC / "handlers", SRC / "core", SRC / "infra"):
    d.mkdir(parents=True, exist_ok=True)

(SRC / "__init__.py").write_text("")
(SRC / "handlers" / "__init__.py").write_text("")
(SRC / "core" / "__init__.py").write_text("")
(SRC / "infra" / "__init__.py").write_text("")

(SRC / "core" / "auth.py").write_text('''"""Authentication decorator."""
from functools import wraps


def require_auth(fn):
    @wraps(fn)
    def inner(request, *a, **k):
        if not request.get("user"):
            raise PermissionError("unauthenticated")
        return fn(request, *a, **k)
    inner.__auth__ = True
    return inner
''')
(SRC / "core" / "router.py").write_text('''"""Route registry."""
ROUTES = {}


def route(path):
    def deco(fn):
        ROUTES[path] = fn
        return fn
    return deco
''')
(SRC / "infra" / "env.py").write_text('''"""Environment access."""
import os


def get(name, default=None):
    return os.environ.get(name, default)
''')
(SRC / "infra" / "vault.py").write_text('''"""Secret material. The webhook signing secret is read from the environment variable named below."""
from .env import get

WEBHOOK_SIGNING_ENV = "ORDERS_WEBHOOK_HMAC_KEY"


def webhook_secret():
    return get(WEBHOOK_SIGNING_ENV)
''')
(SRC / "infra" / "secrets.py").write_text('''"""Compatibility alias; real definitions live in vault."""
from .vault import webhook_secret as signing_secret  # noqa: F401
''')
(SRC / "core" / "settings.py").write_text('''"""Settings facade."""
from ..infra import secrets

SIGNING = secrets.signing_secret
''')

UNPROTECTED = {"handlers/h047.py": "/admin/export", "handlers/h133.py": "/orders/bulk-delete", "handlers/h178.py": "/users/impersonate"}
for i in range(1, 201):
    name = f"h{i:03d}"
    rel = f"handlers/{name}.py"
    if rel in UNPROTECTED:
        path = UNPROTECTED[rel]
        body = f'''"""Handler {name}."""
from ..core.router import route
from ..core import settings  # noqa: F401


@route("{path}")
def handle(request):
    return {{"ok": True, "handler": "{name}"}}
'''
    else:
        path = f"/api/v1/resource{i}"
        body = f'''"""Handler {name}."""
from ..core.auth import require_auth
from ..core.router import route


@route("{path}")
@require_auth
def handle(request):
    return {{"ok": True, "handler": "{name}"}}
'''
    (SRC / rel).write_text(body)
print("generated 200 handlers")
