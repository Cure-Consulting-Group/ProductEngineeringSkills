"""Environment access."""
import os


def get(name, default=None):
    return os.environ.get(name, default)
