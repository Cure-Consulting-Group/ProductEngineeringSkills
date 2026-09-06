"""Program-scoped authorization for boards, rosters, and athlete profiles."""
from __future__ import annotations

PROGRAM_KINDS = {"board", "roster"}


def can_read(user: dict, resource: dict) -> bool:
    role = user.get("role")
    if role == "super_admin":
        return True
    if resource.get("public"):
        return True
    if role in ("staff", "admin"):
        if resource.get("kind") in PROGRAM_KINDS:
            return True  # any authenticated staff can read any program's boards
        if resource.get("kind") == "profile":
            return True
    if role == "athlete" and resource.get("kind") == "profile":
        return resource.get("owner_uid") == user.get("uid")
    return False


def can_write(user: dict, resource: dict) -> bool:
    role = user.get("role")
    if role == "super_admin":
        return True
    if role == "admin":
        return True
    if role == "staff" and resource.get("kind") in PROGRAM_KINDS:
        return True
    if role == "athlete" and resource.get("kind") == "profile":
        return resource.get("owner_uid") == user.get("uid")
    return False
