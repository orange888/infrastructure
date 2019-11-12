from asyncio import gather
from asyncio.subprocess import PIPE
from pathlib import Path

from hannah_family.infrastructure.k8s.kubectl import kubectl_exec
from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.subprocess import run

VAULT_DEFAULT_LABELS = {
    "app.kubernetes.io/name": "vault",
    "app.kubernetes.io/instance": "vault"
}


async def run_kubectl(*args,
                      pods=[],
                      all_pods=False,
                      container=None,
                      namespace=None,
                      kubectl_args=[],
                      **kwargs):
    """Run a Vault command on one or more Vault pods with kubectl exec."""
    if len(pods) == 0:
        _pods = await get_pods(labels=VAULT_DEFAULT_LABELS,
                               namespace=namespace)
        pods = _pods if all_pods else _pods[:1]

    return await kubectl_exec(pods,
                              namespace,
                              "vault",
                              *args,
                              kubectl_args=kubectl_args,
                              container=container,
                              **kwargs)


async def decrypt_file(file: Path):
    """Decrypt a base64-encoded, PGP-encrypted file with a PGP key stored in
    Keybase."""
    cat_cmd = ["cat", "{}".format(file)]
    cat_proc = await run(*cat_cmd, stdout=PIPE)
    cat_stdout, cat_stderr = await cat_proc.communicate()

    decode_cmd = ["base64", "--decode"]
    decode_proc = await run(*decode_cmd, stdin=PIPE, stdout=PIPE)
    decode_stdout, decode_stderr = await decode_proc.communicate(cat_stdout)

    decrypt_cmd = ["keybase", "pgp", "decrypt"]
    decrypt_proc = await run(*decrypt_cmd, stdin=PIPE, stdout=PIPE)
    decrypt_stdout, decrypt_stderr = await decrypt_proc.communicate(
        decode_stdout)

    return decrypt_stdout


async def _get_vault_token(token_path=None):
    if token_path is None:
        token_path = Path.cwd().joinpath("vault", "initial_root_token.pgp")

    token = await decrypt_file(token_path)
    return {"VAULT_TOKEN": token.decode("utf-8")}
