from asyncio import gather
from asyncio.subprocess import (Process, create_subprocess_exec,
                                create_subprocess_shell)
from os import environ
from re import compile
from shlex import join
from subprocess import CalledProcessError

ENV_PATTERN = compile(r"([A-Z_]+)=([^;]+);")


def parse_env(output: str):
    """Parse an environment string into a dict for use with running
    subprocesses."""
    return {name: value for name, value in ENV_PATTERN.findall(output)}


async def run(*args, watch=False, **kwargs):
    """Run a command with asyncio.create_subprocess_exec."""
    _env = environ
    if watch:
        args = ["watch", "-t", *args]

    if "env" in kwargs:
        _env.update(kwargs["env"])

    kwargs["env"] = _env

    proc = await (create_subprocess_shell(join(args), **kwargs)
                  if "shell" in kwargs and kwargs["shell"] else
                  create_subprocess_exec(*args, **kwargs))
    return proc, _error_handler(proc, args)


async def run_batch(*cmds):
    """Run multiple commands simultaneously and wait for them all to
    complete, exiting if any commands exited with a nonzero return code."""
    batches = await gather(*(run(*cmd["args"], **cmd["kwargs"])
                             for cmd in cmds))
    procs, dones = zip(*batches)

    return procs, _batch_error_handler(dones)


def _error_handler(proc: Process, cmd):
    async def error_handler():
        returncode = await proc.wait()
        if returncode > 0:
            raise CalledProcessError(returncode=returncode, cmd=cmd)

    return error_handler()


def _batch_error_handler(dones):
    async def error_handler():
        results = await gather(*dones, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                raise result

    return error_handler()
