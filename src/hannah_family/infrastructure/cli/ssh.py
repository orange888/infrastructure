from click import Context, argument, pass_context

from hannah_family.infrastructure.ansible.host import Host
from hannah_family.infrastructure.ssh.session import open_session

from .cli import main


@main.command()
@argument("hostname", nargs=1, required=True)
@pass_context
async def ssh(ctx: Context, hostname):
    """Open an SSH connection to Ansible inventory host HOSTNAME.

    A process-local ssh-agent instance is started and loaded with the common
    private key for the duration of the SSH session."""
    host = Host(hostname)
    await open_session(host.get_variable("service_user_name"),
                       host.get_variable("ansible_host"))
