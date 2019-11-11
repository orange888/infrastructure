from asyncio import Task, create_task
from asyncio.subprocess import create_subprocess_exec
from os import environ
from pprint import pprint
from re import compile

ENV_PATTERN = compile(r"([A-Z_]+)=([^;]+);")


def parse_env(output: str):
    return {name: value for name, value in ENV_PATTERN.findall(output)}


async def run(*args, **kwargs):
    """Run a command with asyncio.create_subprocess_exec."""
    _env = environ

    if "env" in kwargs:
        _env.update(kwargs["env"])

    kwargs["env"] = _env

    proc = await create_subprocess_exec(*args, **kwargs)
    task = create_task(proc.wait())
    task.add_done_callback(_handle_task_done)
    return proc


def _handle_task_done(task: Task):
    if task.result() > 0:
        exit(task.result())
