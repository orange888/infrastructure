from asyncio import run
from functools import wraps

from click import command


def async_command(name=None, cls=None, **attrs):
    """Wraps an async function as a Click command with asyncio.run."""
    def decorator(f):
        @command(name, cls, **attrs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            return run(f(*args, **kwargs))

        return wrapper

    return decorator
