from asyncio.subprocess import PIPE

from hannah_family.infrastructure.utils.subprocess import run


async def get_pods(labels={}, namespace=None):
    """Get the names of pods matching the given labels and namespace."""
    cmd = ["kubectl", "get", "pod", "-o", "name"]

    if labels:
        cmd.extend(
            ["-l", ",".join("{}={}".format(k, v) for k, v in labels.items())])

    if namespace is None:
        cmd.append("-A")
    else:
        cmd.extend(["-n", namespace])

    proc, done = await run(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, _ = await proc.communicate()
    pods = stdout.decode("utf-8").splitlines()
    await done
    return sorted(pods)
