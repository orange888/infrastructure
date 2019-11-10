from click import Context, group, pass_context

from .ssh import ssh


@group()
@pass_context
def cli(ctx: Context):
    ctx.ensure_object(dict)


cli.add_command(ssh)
