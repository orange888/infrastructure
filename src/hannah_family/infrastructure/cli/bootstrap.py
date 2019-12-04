from click import Context, argument, pass_context

from hannah_family.infrastructure.ansible.playbook import run_playbook

from .cli import main


@main.command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
@argument("hostnames", nargs=-1)
@pass_context
async def bootstrap(ctx: Context, hostnames):
    """Bootstrap a host or hosts."""
    await run_playbook("bootstrap",
                       hostnames=hostnames,
                       args=ctx.args,
                       env={"ANSIBLE_HOST_KEY_CHECKING": "False"})
    await run_playbook("all", hostnames=hostnames, args=ctx.args)
