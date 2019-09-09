from invoke import Collection

from .helm import helm
from .playbooks import playbooks

ns = Collection(helm=helm, pb=playbooks)
