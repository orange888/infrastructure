from pathlib import Path
from pprint import pprint

from hannah_family.infrastructure.ssh import ssh_agent
from hannah_family.infrastructure.utils import run

from .host import InvalidHostNameError
from .loader import Loader

DEFAULT_ENV = {"OBJC_DISABLE_INITIALIZE_FORK_SAFETY": "YES"}


class InvalidPlaybookName(Exception):
    """Raised when the playbook name does not match a known playbook."""
    pass


def run_playbook(playbook, agent=None, hostnames=[], args=[], env={}):
    """Run the named playbook.

    A process-local ssh-agent instance is started and loaded with the common
    private key for the duration of the command."""
    playbook_path = Path.cwd().joinpath("ansible",
                                        "{}.yml".format(playbook)).resolve()

    if not playbook_path.is_file():
        raise InvalidPlaybookName(playbook)

    loader = Loader()
    inventory_hosts = map(lambda host: host.name, loader.get_hosts())

    if len(hostnames) == 0:
        hostnames = inventory_hosts
    else:
        hostnames = list(hostnames)
        for hostname in hostnames:
            if hostname not in inventory_hosts:
                raise InvalidHostNameError(hostname)

    cmd = [
        "pipenv", "run", "ansible-playbook", playbook_path, *args, "-l",
        ",".join(hostnames)
    ]

    with ssh_agent(agent=agent) as agent:
        agent.environ.update(DEFAULT_ENV)
        agent.environ.update(env)
        return run(cmd, env=agent.environ)
