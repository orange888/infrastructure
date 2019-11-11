from click import Context, group, pass_context

from .ansible import ansible
from .bootstrap import bootstrap
from .ssh import ssh


@group()
@pass_context
def cli(ctx: Context):
    ctx.ensure_object(dict)


cli.add_command(ansible)
cli.add_command(bootstrap)
cli.add_command(ssh)
