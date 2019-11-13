from click import Context, argument, pass_context

from hannah_family.infrastructure.ansible.playbook import run_playbook
from hannah_family.infrastructure.ssh.agent import SSHAgent
from hannah_family.infrastructure.utils.click import command
from hannah_family.infrastructure.utils.subprocess import run


@command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
@pass_context
async def ansible(ctx: Context):
    """Run an Ansible command with a process-local ssh-agent instance."""
    cmd = ["pipenv", "run", "ansible", *ctx.args]

    async with SSHAgent() as agent:
        proc = await run(*cmd, env=agent.env())
        await proc.wait()


@command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
@argument("playbook", nargs=1, required=True)
@argument("hostnames", nargs=-1)
@pass_context
async def playbook(ctx: Context, playbook, hostnames):
    """Run an Ansible playbook."""
    await run_playbook(playbook, hostnames=hostnames, args=ctx.args)
