from asyncio import Task, create_task, gather
from asyncio.subprocess import create_subprocess_exec
from os import environ
from re import compile

ENV_PATTERN = compile(r"([A-Z_]+)=([^;]+);")


def parse_env(output: str):
    """Parse an environment string into a dict for use with running
    subprocesses."""
    return {name: value for name, value in ENV_PATTERN.findall(output)}


def _handle_task_done(task: Task):
    if task.result() > 0:
        exit(task.result())


async def run(*args, done_callback=_handle_task_done, **kwargs):
    """Run a command with asyncio.create_subprocess_exec."""
    _env = environ

    if "env" in kwargs:
        _env.update(kwargs["env"])

    kwargs["env"] = _env

    proc = await create_subprocess_exec(*args, **kwargs)

    if done_callback is not None:
        task = create_task(proc.wait())
        task.add_done_callback(done_callback)

    return proc


async def run_batch(*cmds):
    """Run multiple commands simultaneously and wait for them all to
    complete, exiting if any commands exited with a nonzero return code."""
    batches = (run(*cmd["args"], **cmd["kwargs"], done_callback=None) for cmd in cmds)
    procs = await gather(*batches)

    done = gather(*(proc.wait() for proc in procs))
    done.add_done_callback(_handle_batch_done)

    return procs, done


def _handle_batch_done(task: Task):
    for exit_code in task.result():
        if exit_code > 0:
            exit(exit_code)
