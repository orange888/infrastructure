from asyncio import run
from functools import wraps
from subprocess import CalledProcessError
from typing import Coroutine

import click

from hannah_family.infrastructure.ansible.host import InvalidHostNameError


class ClickCalledProcessError(click.ClickException):
    """Raised when a subprocess exits with a non-zero return code, causing the
    command to exit with the same code."""
    def __init__(self, err: CalledProcessError):
        super().__init__(err)
        click.ClickException.exit_code = err.returncode

    def show(self):
        """Mute superfluous error messages stating the return code."""
        pass


class Group(click.Group):
    """Add async commands to a Click command group."""
    def command(self, *args, **kwargs):
        """Wraps a function as a Click command belonging to a group with
        asyncio.run and exception handling."""
        return _command(super(), *args, **kwargs)


def command(*args, **kwargs):
    """Wraps an async function as a Click command with asyncio.run and exception
    handling."""
    return _command(click, *args, **kwargs)


def _command(base, *args, **kwargs):
    def decorator(func):
        @base.command(*args, **kwargs)
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            return run(_wrapped_function(func, *func_args, **func_kwargs))

        return wrapper

    return decorator


async def _wrapped_function(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)

        if isinstance(result, Coroutine):
            return await result

        return result
    except CalledProcessError as err:
        raise ClickCalledProcessError(err)
    except InvalidHostNameError as err:
        raise click.ClickException(err)
