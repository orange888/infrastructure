from asyncio import gather

from hannah_family.infrastructure.utils.subprocess import run_batch


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

    if "stdin" in kwargs and kwargs["stdin"] is not None:
        cmd.extend(["-i"])

    cmd.extend(["--", command, *args])

    return await run_batch(
        ("\0".join(cmd).format(pod=pod).split("\0"), kwargs) for pod in pods)
