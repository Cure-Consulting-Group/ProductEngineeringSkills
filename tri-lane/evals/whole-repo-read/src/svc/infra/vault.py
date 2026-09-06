"""Secret material. The webhook signing secret is read from the environment variable named below."""
from .env import get

WEBHOOK_SIGNING_ENV = "ORDERS_WEBHOOK_HMAC_KEY"


def webhook_secret():
    return get(WEBHOOK_SIGNING_ENV)
