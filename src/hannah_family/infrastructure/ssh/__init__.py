from contextlib import contextmanager
from pathlib import Path

from .agent import SSHAgent


@contextmanager
def ssh_agent(key_path: str):
    """Provides an ssh-agent instance to the wrapped block."""
    key_file = Path(key_path).resolve()
    agent = SSHAgent.start(key_file)

    try:
        yield agent
    finally:
        agent.stop()
