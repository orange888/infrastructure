from hannah_family.infrastructure.utils.string import format_cmd
from hannah_family.infrastructure.utils.subprocess import run, run_batch


async def kubectl_exec(pods,
                       namespace,
                       command,
                       *args,
                       kubectl_args=[],
                       container=None,
                       **kwargs):
    """Run a command in the specified pod or pods with kubectl exec."""
    cmd = ["kubectl", "exec", "{pod}", "-n", namespace, *kubectl_args]

    if container is not None:
        cmd.extend(["-c", container])

    if "shell" in kwargs and kwargs["shell"]:
        cmd.append("-t")

    if "stdin" in kwargs and kwargs["stdin"] is not None:
        cmd.append("-i")

    cmd.extend(["--", command, *args])

    cmds = [{
        "args": format_cmd(cmd, pod=pod),
        "kwargs": kwargs
    } for pod in pods]
    return await run_batch(*cmds)


async def kubectl_get(*resources, watch=False, **kubectl_args):
    """Get resources of the given type(s)."""
    cmd = ["kubectl", "get", ",".join(resources)]
    cmd.extend("--{}={}".format(arg, val) for arg, val in kubectl_args.items())

    return await run(*cmd, watch=watch)
