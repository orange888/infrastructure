from asyncio import gather
from asyncio.subprocess import PIPE
from os import environ
from pathlib import Path
from shutil import which

from hannah_family.infrastructure.k8s.kubectl import kubectl_exec
from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.subprocess import run as _run

VAULT_DEFAULT_ADDRESS = "https://vault.hannahs.family"
VAULT_DEFAULT_LABELS = {
    "app.kubernetes.io/name": "vault",
    "app.kubernetes.io/instance": "vault"
}
VAULT_ENV_KEY_ADDR = "VAULT_ADDR"
VAULT_EXECUTABLE = "vault"


async def run(*args,
              local=True,
              pods=[],
              all_pods=False,
              namespace=None,
              container=None,
              kubectl_args=[],
              **kwargs):
    """Run a Vault command.

    By default, commands are run using the local copy of the Vault client. If
    the client is not installed, if one or more remote pods are provided, or if
    remote execution is otherwise specifically requested, the command is run on
    the pod or pods with `kubectl exec`."""
    if which(VAULT_EXECUTABLE) and local and not pods:
        VAULT_ENV_KEY_ADDR in environ or kwargs.setdefault(
            "env", {}).setdefault(VAULT_ENV_KEY_ADDR, VAULT_DEFAULT_ADDRESS)
        proc, done = await _run(VAULT_EXECUTABLE, *args, **kwargs)
        return [proc], done

    if len(pods) == 0:
        pods = (await
                get_pods(labels=VAULT_DEFAULT_LABELS,
                         namespace=namespace))[:(None if all_pods else 1)]

    return await kubectl_exec(pods,
                              namespace,
                              VAULT_EXECUTABLE,
                              *args,
                              kubectl_args=kubectl_args,
                              container=container,
                              **kwargs)


async def decrypt_file(file: Path):
    """Decrypt a base64-encoded, PGP-encrypted file with a PGP key stored in
    Keybase."""
    cat_cmd = ["cat", "{}".format(file)]
    cat_proc, cat_done = await _run(*cat_cmd, stdout=PIPE)
    cat_stdout, _ = await cat_proc.communicate()

    decode_cmd = ["base64", "--decode"]
    decode_proc, decode_done = await _run(*decode_cmd, stdin=PIPE, stdout=PIPE)
    decode_stdout, _ = await decode_proc.communicate(cat_stdout)

    decrypt_cmd = ["keybase", "pgp", "decrypt"]
    decrypt_proc, decrypt_done = await _run(*decrypt_cmd,
                                            stdin=PIPE,
                                            stdout=PIPE)
    decrypt_stdout, _ = await decrypt_proc.communicate(decode_stdout)

    await gather(cat_done, decode_done, decrypt_done)
    return decrypt_stdout
