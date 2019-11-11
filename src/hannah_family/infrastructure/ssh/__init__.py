from contextlib import contextmanager
from pathlib import Path

from .agent import SSHAgent


@contextmanager
def ssh_agent(key_path: str = None, agent: SSHAgent = None):
    """Provides an ssh-agent instance to the wrapped block."""
    start_agent = (agent is None)
    if start_agent:
        key_file = Path(key_path or ".ssh/id_ed25519").resolve()
        agent = SSHAgent.start(key_file)

    try:
        yield agent
    finally:
        if start_agent:
            agent.stop()
