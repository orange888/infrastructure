from click import Context, command, pass_context

from hannah_family.infrastructure.ssh import ssh_agent
from hannah_family.infrastructure.utils import run


@command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
@pass_context
def ansible(ctx: Context):
    """Run an Ansible command with a process-local ssh-agent instance."""
    cmd = ["pipenv", "run", "ansible", *ctx.args]

    with ssh_agent() as agent:
        run(cmd, env=agent.environ)
