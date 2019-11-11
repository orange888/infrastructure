from pathlib import Path

from hannah_family.infrastructure.utils import run

from . import ssh_agent


def open_session(user, hostname, args=[], env={}):
    cmd = [
        "ssh", "-F",
        Path.cwd().joinpath(".ssh", "config").resolve(), *args,
        "{}@{}".format(user, hostname)
    ]

    with ssh_agent() as agent:
        agent.environ.update(env)
        run(cmd, env=agent.environ)
