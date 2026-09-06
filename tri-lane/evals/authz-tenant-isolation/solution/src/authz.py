"""Reference solution: program-scoped, deny by default."""
from __future__ import annotations

PROGRAM_KINDS = {"board", "roster"}
KINDS = PROGRAM_KINDS | {"profile"}


def _same_program(user: dict, resource: dict) -> bool:
    pid = user.get("program_id")
    return pid is not None and resource.get("program_id") == pid


def can_read(user: dict, resource: dict) -> bool:
    role = user.get("role")
    kind = resource.get("kind")
    if kind not in KINDS:
        return False
    if role == "super_admin":
        return True
    if resource.get("public"):
        return True
    if role in ("staff", "admin"):
        return _same_program(user, resource)
    if role == "athlete" and kind == "profile":
        return resource.get("owner_uid") == user.get("uid")
    return False


def can_write(user: dict, resource: dict) -> bool:
    role = user.get("role")
    kind = resource.get("kind")
    if kind not in KINDS:
        return False
    if role == "super_admin":
        return True
    if role == "admin":
        return _same_program(user, resource)
    if role == "staff":
        return kind in PROGRAM_KINDS and _same_program(user, resource)
    if role == "athlete" and kind == "profile":
        return resource.get("owner_uid") == user.get("uid")
    return False
