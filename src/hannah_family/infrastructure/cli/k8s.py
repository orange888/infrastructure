from click import Context, argument, option, pass_context

from hannah_family.infrastructure.k8s.kubectl import kubectl_get

from .cli import main

K8S_CTX_WATCH_KEY = "K8S_CTX_WATCH"


@main.group()
@option("--watch/--no-watch",
        "-w",
        default=False,
        help="Run the command through the watch utility.")
@pass_context
async def k8s(ctx: Context, watch):
    """Shortcuts for kubectl commands."""
    ctx.ensure_object(dict)
    ctx.obj[K8S_CTX_WATCH_KEY] = watch


@k8s.command()
@argument("resources", nargs=-1)
@option("--output", "-o", default=None, help="Resource(s) to get.")
@option("--namespace",
        "-n",
        default=None,
        help="Namespace to get resources from.")
@pass_context
async def get(ctx: Context, resources, output, namespace):
    """Get a Kubernetes resource or resources by type."""
    kwargs = {}

    if output is not None:
        kwargs["output"] = output

    if namespace is None:
        kwargs["all-namespaces"] = True
    else:
        kwargs["namespace"] = namespace

    _, done = await kubectl_get(*resources,
                                watch=ctx.obj[K8S_CTX_WATCH_KEY],
                                **kwargs)
    return await done
