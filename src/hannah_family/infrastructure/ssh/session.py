from pathlib import Path

from hannah_family.infrastructure.utils.subprocess import run

from .agent import SSHAgent


async def open_session(user, hostname, args=[], env={}):
    config_path = Path.cwd().joinpath(".ssh", "config").resolve()
    cmd = [
        "ssh", "-F",
        str(config_path), *args, "{}@{}".format(user, hostname)
    ]

    async with SSHAgent(env) as agent:
        proc, done = await run(*cmd, env=agent.env())
        await done
