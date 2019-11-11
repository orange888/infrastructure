from pathlib import Path

from ansible.config.manager import ConfigManager
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import get_file_vault_secret
from ansible.playbook.play import Play
from ansible.vars.manager import VariableManager


class Loader:
    def __init__(self):
        self._config = ConfigManager()
        self._loader = DataLoader()
        self._file_vault_secrets = {}
        self._inventory: InventoryManager = None
        self._variables: VariableManager = None

    def _load_file_vault_secrets(self, password_file_path=None):
        if password_file_path is None:
            password_file_path = self._config.get_config_value(
                "DEFAULT_VAULT_PASSWORD_FILE")

        password_file = Path(password_file_path)

        if password_file.name in self._file_vault_secrets:
            return

        if not password_file.is_file():
            raise FileNotFoundError(password_file)

        self._file_vault_secrets[password_file.name] = get_file_vault_secret(
            filename=password_file, loader=self._loader)
        self._file_vault_secrets[password_file.name].load()
        self._loader.set_vault_secrets([
            (password_file.name, self._file_vault_secrets[password_file.name])
        ])

    def _get_inventory(self, source=None):
        if source is None:
            source = self._config.get_config_value("DEFAULT_HOST_LIST")

        if self._inventory is None:
            self._inventory = InventoryManager(loader=self._loader,
                                               sources=source)
        else:
            sources = source if isinstance(source, list) else [source]
            (self._inventory.parse_source(s) for s in sources)
            self._inventory.reconcile_inventory()

        return self._inventory

    def _get_variables(self, source=None):
        self._load_file_vault_secrets()
        if self._variables is None:
            self._variables = VariableManager(
                loader=self._loader, inventory=self._get_inventory(source))

        return self._variables

    def get_hosts(self, pattern='all', source=None):
        return self._get_inventory(source).get_hosts(pattern)

    def get_host(self, hostname, source=None):
        return self._get_inventory(source).get_host(hostname)

    def get_vars(self, host, data={}):
        play = Play.load(data,
                         loader=self._loader,
                         variable_manager=self._get_variables())
        return self._get_variables().get_vars(host=host, play=play)
