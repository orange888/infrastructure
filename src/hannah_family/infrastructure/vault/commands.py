from asyncio import gather
from asyncio.subprocess import DEVNULL, PIPE
from pathlib import Path

from hannah_family.infrastructure.k8s.kubectl import kubectl_exec
from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.subprocess import run

from . import VAULT_DEFAULT_LABELS, decrypt_file, run_kubectl


async def login(token,
                pods=[],
                labels=VAULT_DEFAULT_LABELS,
                namespace=None,
                container=None):
    """Log in to one or more Vault pods with the given token."""
    if len(pods) == 0:
        pods = await get_pods(labels=labels, namespace=namespace)

    procs, done = await run_kubectl("login",
                                    "-",
                                    pods=pods,
                                    namespace=namespace,
                                    container=container,
                                    stdin=PIPE,
                                    stdout=DEVNULL)
    await gather(*(proc.communicate(token) for proc in procs))
    return await done


async def logout(pods=[],
                 labels=VAULT_DEFAULT_LABELS,
                 namespace=None,
                 container=None):
    """Delete the stored token from one or more Vault pods."""
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
    results = await gather(*(kubectl_exec(pods,
                                          namespace,
                                          "vault",
                                          "operator",
                                          "unseal",
                                          key.decode("utf-8"),
                                          container=container)
                             for key in unseal_keys))
    return await gather(*(result[1] for result in results))


async def policy_write(policy: Path,
                       labels=VAULT_DEFAULT_LABELS,
                       namespace=None,
                       container=None):
    cat_cmd = ["cat", "{}".format(policy)]
    cat_proc = await run(*cat_cmd, stdout=PIPE)
    cat_stdout, cat_stderr = await cat_proc.communicate()

    with open(policy, 'rb') as file:
        procs, done = await run_kubectl("policy",
                                        "write",
                                        policy.stem,
                                        "-",
                                        namespace=namespace,
                                        container=container,
                                        stdin=file)
        return await done
