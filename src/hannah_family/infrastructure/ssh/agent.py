import os
import subprocess
from pathlib import Path
from typing import Dict

from ..utils import parse_env


class SSHAgent:
    """Manages an instance of ssh-agent for the current process."""
    def __init__(self, agent_env: Dict[str, str]):
        self.agent_env = agent_env
        self.pid = agent_env["SSH_AGENT_PID"]
        self.environ = {}
        self.environ.update(os.environ)
        self.environ.update(agent_env)

    def __enter__(self):
        return self

    def __exit__(self):
        self.stop()

    @classmethod
    def start(cls, key_file: Path = None):
        """Starts a new ssh-agent for the current process."""
        output = subprocess.check_output(["ssh-agent", "-s"]).decode("ascii")
        agent_env = parse_env(output)
        agent = cls(agent_env)

        if key_file is not None:
            agent.add_key(key_file)

        return agent

    def add_key(self, file: Path):
        """Adds a key to the ssh-agent."""
        subprocess.check_call(["ssh-add", str(file.resolve())],
                              env=self.environ,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)

    def stop(self):
        """Kills the running ssh-agent."""
        subprocess.check_call(["kill", self.pid])
