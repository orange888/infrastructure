from json import dumps

from ansible.playbook.play import Play
from ansible.template import AnsibleJ2Template

from .loader import Loader

NONE_PLAY_DATA = {"name": "__None"}


class InvalidHostNameError(Exception):
    """Raised when the host name does not match an inventory host entry."""
    def __init__(self, hostname):
        super().__init__(
            "No host named {} found in Ansible inventory".format(hostname))


class Host:
    def __init__(self, hostname, source=None, loader=None):
        self._loader = Loader() if loader is None else loader
        host = self._loader.get_host(hostname, source)

        if host is None:
            raise InvalidHostNameError(hostname)

        self._host = host
        self._vars = {}

    def get_variables(self, play_data={}):
        if "name" not in play_data:
            vars_key = dumps(play_data)
        else:
            vars_key = play_data["name"]

        if vars_key not in self._vars:
            self._vars[vars_key] = self._loader.get_vars(host=self._host,
                                                         data=play_data)

        return self._vars[vars_key]

    def get_variable(self, name, play_data={}):
        play_vars = self.get_variables(play_data)
        var = self.get_variables(play_data).get(name)

        if isinstance(var, dict):
            return {key: self._render(val, play_data) for key, val in var}
        elif isinstance(var, list):
            return [self._render(val, play_data) for val in var]
        else:
            return self._render(var, play_data)

    def _render(self, val, play_data):
        return AnsibleJ2Template(val).render(self.get_variables(play_data))
