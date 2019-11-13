from click import ClickException, Context, argument, pass_context

from hannah_family.infrastructure.ansible.host import InvalidHostNameError
from hannah_family.infrastructure.ansible.playbook import run_playbook
from hannah_family.infrastructure.ssh.agent import SSHAgent
from hannah_family.infrastructure.utils.click import command


@command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
@argument("hostnames", nargs=-1)
@pass_context
def bootstrap(ctx: Context, hostnames):
    """Bootstrap a host or hosts."""
    try:
        with SSHAgent() as agent:
            run_playbook("bootstrap",
                         agent=agent,
                         hostnames=hostnames,
                         args=ctx.args,
                         env={"ANSIBLE_HOST_KEY_CHECKING": "false"})
            run_playbook("all",
                         agent=agent,
                         hostnames=hostnames,
                         args=ctx.args)
    except InvalidHostNameError as e:
        raise ClickException(
            "No host named {} found in Ansible inventory".format(e))
