import os

from click import Context, pass_context

from hannah_family.infrastructure.ssh.agent import SSHAgent
from hannah_family.infrastructure.utils.subprocess import run as run_

from .cli import main


@main.command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
@pass_context
async def run(ctx: Context):
    """Run an arbitrary command with an ssh-agent instance."""
    async with SSHAgent(env=os.environ) as agent:
        _, done = await run_(*ctx.args, env=agent.env())
        await done
