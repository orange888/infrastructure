import pprint
from asyncio import gather, run
from asyncio.subprocess import PIPE
from pathlib import Path
from subprocess import CalledProcessError

from click import (ClickException, Context, HelpFormatter, argument,
                   pass_context)

from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.string import format_cmd
from hannah_family.infrastructure.vault import (VAULT_DEFAULT_LABELS,
                                                decrypt_file, run_kubectl)
from hannah_family.infrastructure.vault.commands import (login, logout,
                                                         policy_write, unseal)

from .cli import Group, main


class Vault(Group):
    """Handle commands to Vault that don't have their own manually defined
    behavior by passing them to kubectl exec."""
    def get_command(self, ctx: Context, name: str):
        """If a Vault command doesn't have its own command, run it with kubectl
        exec."""
        cmd = super().get_command(ctx, name)

        if not cmd:
            return self._vault_command(ctx, name)

        return cmd

    def format_commands(self, ctx: Context, formatter: HelpFormatter):
        """Display commands passed directly to the Vault client below the
        manually defined commands in the help text."""
        super().format_commands(ctx, formatter)

        run(self._get_remote_commands(formatter))

    async def _get_remote_commands(self, formatter: HelpFormatter):
        help_procs, help_done = await run_kubectl("-help",
                                                  namespace="kube-system",
                                                  container="vault",
                                                  stderr=PIPE)
        help_proc = help_procs[0]
        help_stdout, help_stderr = await help_proc.communicate()

        groups = help_stderr.decode("utf-8").split("\n\n")[1:]
        await help_done

        for group in groups:
            name, *rows = group.splitlines()
            with formatter.section("{} Vault commands".format(
                    name.split()[0])):
                formatter.write_dl(
                    (name, "{}.".format(help))
                    for (name, help) \
                    in map(lambda row: row.split(maxsplit=1), rows)
                    if name not in self.commands)

    def _vault_command(self, ctx: Context, name: str):
        @self.command(name=name,
                      context_settings={
                          "allow_extra_args": True,
                          "ignore_unknown_options": True
                      })
        @pass_context
        async def cmd(ctx: Context):
            procs, done = await run_kubectl(name,
                                            *ctx.args,
                                            container="vault",
                                            namespace="kube-system")
            return await done

        return cmd


@main.command(cls=Vault)
@pass_context
async def vault(ctx: Context):
    """Run commands on a Vault instance with a remote client.

    Commands listed under "Common Vault commands" and "Other Vault commands"
    below are forwarded to the Vault client.

    Options to the Vault client can be passed with `--`, e.g.:

        inf vault -- -help
    """
    pass


@vault.command(name="unseal")
@argument("pods", nargs=-1)
@pass_context
async def vault_unseal(ctx: Context, pods=[]):
    """Unseal one or more Vault pods."""
    keys = Path.cwd().joinpath("vault").glob("unseal_key_*.pgp")
    return await unseal(keys,
                        pods=pods,
                        namespace="kube-system",
                        container="vault")


@vault.command(name="login")
@argument("pods", nargs=-1)
@pass_context
async def vault_login(ctx: Context, pods=[]):
    """Log in to Vault using the initial root token."""
    token_path = Path.cwd().joinpath("vault", "initial_root_token.pgp")
    token = await decrypt_file(token_path)
    return await login(token,
                       pods=pods,
                       namespace="kube-system",
                       container="vault")


@vault.command(name="logout")
@argument("pods", nargs=-1)
@pass_context
async def vault_logout(ctx: Context, pods=[]):
    """Log out of Vault on the remote pods."""
    return await logout(pods=pods, namespace="kube-system", container="vault")


@vault.command()
async def write_policies():
    """Write all policies to the Vault instance."""
    policies = Path.cwd().joinpath("vault", "policy").glob("*.hcl")
    return await gather(*(
        policy_write(policy, namespace="kube-system", container="vault")
        for policy in policies))


@vault.command()
async def write_roles():
    """Write all roles to the Vault instance."""
    policies = Path.cwd().joinpath("vault", "policy").glob("*.hcl")

    cmd = [
        "write", "auth/kubernetes/role/{role}",
        "bound_service_account_namespaces={namespace}",
        "bound_service_account_names={name}", "policies={role}", "ttl=24h"
    ]

    results = await gather(*(
        run_kubectl(*format_cmd(cmd, **_get_role_from_policy(policy)),
                    container="vault",
                    namespace="kube-system") for policy in policies))
    return await gather(*(result[1] for result in results))


def _get_role_from_policy(policy: Path):
    stem = policy.stem
    namespace, name = stem.split("__")
    return {"role": stem, "namespace": namespace, "name": name}
