from pathlib import Path

from click import Context, Group, argument, pass_context

from hannah_family.infrastructure.k8s.pods import get_pods
from hannah_family.infrastructure.utils.click import AsyncGroup, async_command
from hannah_family.infrastructure.utils.subprocess import run_batch
from hannah_family.infrastructure.vault import (VAULT_DEFAULT_LABELS,
                                                run_kubectl)
from hannah_family.infrastructure.vault.commands import unseal


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
