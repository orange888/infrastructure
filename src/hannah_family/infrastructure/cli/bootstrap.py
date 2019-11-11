from click import ClickException, Context, argument, command, pass_context

from hannah_family.infrastructure.ansible.host import InvalidHostNameError
from hannah_family.infrastructure.ansible.playbook import run_playbook
from hannah_family.infrastructure.ssh import ssh_agent


@command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
@argument("hostnames", nargs=-1)
@pass_context
def bootstrap(ctx: Context, hostnames):
    """Bootstrap a host or hosts."""
    try:
        with ssh_agent() as agent:
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
