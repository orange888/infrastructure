from asyncio import gather
from asyncio.subprocess import DEVNULL, PIPE
from pathlib import Path

from hannah_family.infrastructure.k8s.kubectl import kubectl_exec
from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.subprocess import run as sub_run

from . import VAULT_DEFAULT_LABELS, VAULT_EXECUTABLE, decrypt_file, run


async def login(token,
                local=True,
                pods=[],
                labels=VAULT_DEFAULT_LABELS,
                namespace=None,
                container=None):
    """Log in to one or more Vault pods with the given token."""
    procs, done = await run("login",
                            "-",
                            pods=pods,
                            all_pods=(len(pods) == 0),
                            namespace=namespace,
                            container=container,
                            stdin=PIPE,
                            stdout=DEVNULL)
    await gather(*(proc.communicate(token) for proc in procs))
    return await done


async def logout(local=True,
                 pods=[],
                 labels=VAULT_DEFAULT_LABELS,
                 namespace=None,
                 container=None):
    """Delete the stored Vault token."""
    if local and not pods:
        proc, done = await sub_run("sh", "-c", "rm $HOME/.vault-token")
        return await done

    if len(pods) == 0:
        pods = await get_pods(labels=labels, namespace=namespace)

    procs, done = await kubectl_exec(pods,
                                     namespace,
                                     "sh",
                                     "-c",
                                     "rm $HOME/.vault-token",
                                     container=container)
    return await done


async def unseal(keys: [Path],
                 pods=[],
                 labels=VAULT_DEFAULT_LABELS,
                 namespace=None,
                 container=None):
    """Unseal one or more Vault pods, by pod name or by label."""
    if len(pods) == 0:
        pods = await get_pods(labels=labels, namespace=namespace)

    unseal_keys = await gather(*(decrypt_file(key) for key in keys))
    results = await gather(*(run("operator",
                                 "unseal",
                                 key.decode("utf-8"),
                                 local=False,
                                 pods=pods,
                                 namespace=namespace,
                                 container=container) for key in unseal_keys))
    return await gather(*(result[1] for result in results))


async def policy_write(policy: Path,
                       local=True,
                       labels=VAULT_DEFAULT_LABELS,
                       namespace=None,
                       container=None):
    """Read a policy from the filesystem and write it to the Vault."""
    with open(policy, 'rb') as file:
        procs, done = await run("policy",
                                "write",
                                policy.stem,
                                "-",
                                namespace=namespace,
                                container=container,
                                stdin=file)
        return await done
