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


class Group(click.Group):
    """Add async commands to a Click command group."""
    def command(self, *args, **kwargs):
        """Wraps a function as a Click command belonging to a group with
        asyncio.run and exception handling."""
        return _command(super(), *args, **kwargs)

    def group(self, *args, **kwargs):
        kwargs["cls"] = Group
        return _command(super(), *args, **kwargs)


def command(name=None, cls=None, **attrs):
    """Wraps an async function as a Click command with asyncio.run and exception
    handling."""
    return _command(click, name=name, cls=cls, **attrs)


def group(name=None, **attrs):
    """Shortcut to add a subgroup to a group."""
    return _command(click, name=name, cls=Group, **attrs)


def _command(base, **attrs):
    def decorator(func):
        @base.command(**attrs)
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            return run(_wrap_function(func, *func_args, **func_kwargs))

        return wrapper

    return decorator


async def _wrap_function(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)

        if isinstance(result, Coroutine):
            return await result

        return result
    except CalledProcessError as err:
        raise ClickCalledProcessError(err)
    except InvalidHostNameError as err:
        raise click.ClickException(err)


@group()
@click.pass_context
def main(ctx: click.Context):
    ctx.ensure_object(dict)
