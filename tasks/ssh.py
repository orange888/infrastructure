from pathlib import Path
from pprint import pprint

from invoke import call, task
from invoke.exceptions import Exit

from ansible.config.manager import ConfigManager, find_ini_config_file
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import get_file_vault_secret
from ansible.playbook.play import Play
from ansible.template.template import AnsibleJ2Template
from ansible.vars.manager import VariableManager

from .ansible.vars import HostVars
from .playbooks import playbooks


@task(pre=[call(playbooks.__getitem__("ssh"))])
def ssh(c, hostname):
    """Connect over SSH to a host defined in the Ansible inventory
    """
    host_vars = HostVars(hostname)
    play = {"roles": ["service_user"]}
    ansible_user = host_vars.get_variable("ansible_user", play)
    ansible_host = host_vars.get_variable("ansible_host", play)

    cmd = ["ssh", "{}@{}".format(ansible_user, ansible_host)]
    c.run(" ".join(cmd), pty=True)
