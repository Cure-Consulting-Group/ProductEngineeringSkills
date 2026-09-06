"""Settings facade."""
from ..infra import secrets

SIGNING = secrets.signing_secret
