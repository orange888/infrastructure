from pathlib import Path
from re import compile

from invoke import Collection, task


@task(default=True, iterable=["vault_pods"])
def status(c,
           container="vault",
           labels=",".join([
               "app.kubernetes.io/name=vault",
               "app.kubernetes.io/instance=vault"
           ]),
           namespace="kube-system",
           vault_pods=[]):
    if len(vault_pods) == 0:
        vault_pods = _get_vault_pods(c, labels, namespace)

    cmd = [
        "kubectl", "exec", "-n", namespace, "{vault_pod}", "-c", container,
        "--", "vault", "status"
    ]

    for vault_pod in vault_pods:
        c.run(" ".join(cmd).format(vault_pod=vault_pod))


@task(
    iterable=["vault_pods"],
    help={
        "cluster": "Kubernetes cluster name",
        "container": "Vault server container name",
        "labels": "Vault pod selector labels",
        "namespace": "Namespace of Vault deployment",
        "pgp_decrypt_cmd":
        "Command that takes a PGP-encrypted unseal key on STDIN and puts the decrypted key to STDOUT",
        "vault_pods": "Manually specify Vault pods to unseal"
    })
def unseal(c,
           cluster="guardians",
           container="vault",
           labels=",".join([
               "app.kubernetes.io/name=vault",
               "app.kubernetes.io/instance=vault"
           ]),
           namespace="kube-system",
           pgp_decrypt_cmd="keybase pgp decrypt",
           vault_pods=[]):
    """Find and unseal all Vault pods in the cluster
    """
    if len(vault_pods) == 0:
        vault_pods = _get_vault_pods(c, labels, namespace)

    unseal_keys_path = Path.cwd().joinpath("ansible", "files", cluster,
                                           "vault").glob("unseal_key_*.pgp")
    unseal_keys_cmd = ["ansible-vault", "view", "{unseal_key_path}"]

    decode_cmd = ["base64", "--decode"]
    unseal_cmd = [
        "xargs", "-o", "kubectl", "exec", "-n", namespace, "{vault_pod}", "-c",
        container, "--", "vault", "operator", "unseal"
    ]

    fmt_cmd = " | ".join(
        " ".join(cmd) for cmd in
        [unseal_keys_cmd, decode_cmd,
         pgp_decrypt_cmd.split(" "), unseal_cmd])
    fmt_cmds = (fmt_cmd.format(unseal_key_path=unseal_key_path,
                               vault_pod=vault_pod)
                for unseal_key_path in unseal_keys_path
                for vault_pod in vault_pods)

    for cmd in fmt_cmds:
        c.run(cmd)


def _get_vault_pods(c, labels, namespace):
    pods_cmd = [
        "kubectl", "get", "pod", "-n", namespace, "-l", labels, "-o", "name"
    ]
    vault_pods = c.run(" ".join(pods_cmd), hide=True).stdout.splitlines()

    return sorted(vault_pods)


vault = Collection("vault")
vault.add_task(status)
vault.add_task(unseal)
