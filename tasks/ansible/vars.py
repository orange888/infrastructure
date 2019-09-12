from pathlib import Path

from ansible.config.manager import ConfigManager
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import get_file_vault_secret
from ansible.playbook.play import Play
from ansible.template.template import AnsibleJ2Template
from ansible.vars.manager import VariableManager


class HostVars:
    def __init__(self, hostname):
        self._ansible = _AnsibleLoader()
        self._host = self._ansible.get_host(hostname)
        self._play = None
        self._vars = None

    def get_variable(self, name, play=None):
        if self._vars is None or self._play != play:
            self._play = play
            self._vars = self._ansible.get_vars(host=self._host,
                                                play=self._play)

        return AnsibleJ2Template(self._vars.get(name)).render(self._vars)


class _AnsibleLoader:
    def __init__(self):
        self._config = ConfigManager()
        self._inventory = None
        self._loader = DataLoader()

        self._loader.set_basedir(Path.cwd().joinpath("ansible"))
        self._load_file_vault_secret()
        self._load_inventory()

    def _load_file_vault_secret(self):
        password_file = Path(
            self._config.get_config_value("DEFAULT_VAULT_PASSWORD_FILE"))

        if not password_file.is_file():
            raise FileNotFoundError(password_file)

        file_vault_secret = get_file_vault_secret(filename=password_file,
                                                  loader=self._loader)
        file_vault_secret.load()
        self._loader.set_vault_secrets([(password_file.name, file_vault_secret)
                                        ])

    def _load_inventory(self):
        sources = self._config.get_config_value("DEFAULT_HOST_LIST")
        self._inventory = InventoryManager(loader=self._loader,
                                           sources=sources)
        self._variables = VariableManager(loader=self._loader,
                                          inventory=self._inventory)

    def get_host(self, hostname):
        return self._inventory.get_host(hostname)

    def get_vars(self, host=None, play=None):
        play = Play.load(play,
                         loader=self._loader,
                         variable_manager=self._variables)
        return self._variables.get_vars(host=host, play=play)
