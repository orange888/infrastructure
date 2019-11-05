from invoke import Collection

from .helm import helm
from .playbooks import playbooks
from .ssh import ssh
from .vault import vault

ns = Collection(helm=helm, pb=playbooks, ssh=ssh, vault=vault)
