from asyncio import gather
from pathlib import Path

from hannah_family.infrastructure.k8s.kubectl import kubectl_exec
from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.subprocess import run

from . import VAULT_DEFAULT_LABELS, decrypt_file


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
