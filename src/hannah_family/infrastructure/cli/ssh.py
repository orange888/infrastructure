from pathlib import Path

from click import ClickException, Context, argument, command, pass_context

from hannah_family.infrastructure.ansible.host import (Host,
                                                       InvalidHostNameError)
from hannah_family.infrastructure.ssh.session import open_session


@command()
@argument("hostname", nargs=1, required=True)
@pass_context
def ssh(ctx: Context, hostname):
    """Open an SSH connection to the Ansible inventory host at HOSTNAME.

    A process-local ssh-agent instance is started and loaded with the common
    private key for the duration of the SSH session."""
    try:
        host = Host(hostname)
        open_session(host.get_variable("service_user_name"),
                     host.get_variable("ansible_host"))
    except InvalidHostNameError as e:
        raise ClickException(
            "No host named {} found in Ansible inventory".format(hostname))
