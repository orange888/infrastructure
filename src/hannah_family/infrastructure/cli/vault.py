from asyncio import gather
from pathlib import Path

from click import Context, Group, argument, pass_context

from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.click import AsyncGroup, async_command
from hannah_family.infrastructure.utils.string import format_cmd
from hannah_family.infrastructure.vault import (VAULT_DEFAULT_LABELS,
                                                decrypt_file, run_kubectl)
from hannah_family.infrastructure.vault.commands import (login, policy_write,
                                                         unseal)


class Vault(AsyncGroup):
    """Handle commands to Vault that don't have their own manually defined
    behavior by passing them to kubectl exec."""
    def get_command(self, ctx: Context, name: str):
        """If a Vault command doesn't have its own command, run it with kubectl
        exec."""
        cmd = super().get_command(ctx, name)

        if not cmd:
            return self._vault_command(ctx, name)

        return cmd

    def _vault_command(self, ctx: Context, name: str):
        @self.async_command(name=name,
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


@async_command(cls=Vault)
@pass_context
async def vault(ctx: Context):
    pass


@vault.async_command(name="unseal")
@argument("pods", nargs=-1)
@pass_context
async def vault_unseal(ctx: Context, pods=[]):
    """Unseal one or more Vault pods."""
    keys = Path.cwd().joinpath("vault").glob("unseal_key_*.pgp")
    return await unseal(keys,
                        pods=pods,
                        namespace="kube-system",
                        container="vault")


@vault.async_command(name="login")
@argument("pods", nargs=-1)
@pass_context
async def vault_login(ctx: Context, pods=[]):
    """Log in to Vault from the local client using the initial root token."""
    token_path = Path.cwd().joinpath("vault", "initial_root_token.pgp")
    token = await decrypt_file(token_path)
    return await login(token,
                       pods=pods,
                       namespace="kube-system",
                       container="vault")


@vault.async_command()
async def write_policies():
    """Write all policies to the Vault instance."""
    policies = Path.cwd().joinpath("vault", "policy").glob("*.hcl")
    return await gather(*(
        policy_write(policy, namespace="kube-system", container="vault")
        for policy in policies))


@vault.async_command()
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
