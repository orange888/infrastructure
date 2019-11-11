from asyncio.subprocess import DEVNULL, PIPE, Process
from pathlib import Path
from typing import Dict

from hannah_family.infrastructure.utils.subprocess import parse_env, run

from . import DEFAULT_SSH_KEY


class SSHAgent:
    """Manages an instance of ssh-agent for the current process."""
    def __init__(self, env={}):
        self._chains = 0
        self._env = {}
        self._env.update(env)

    async def __aenter__(self, agent=None):
        """Starts an ssh-agent instance and adds the default key, or chains to
        an existing agent."""
        if agent is not None:
            return agent.chained()

        self._proc = await run("ssh-agent",
                               "-D",
                               "-s",
                               stdout=PIPE,
                               stderr=PIPE)

        line = await self._proc.stdout.readuntil()
        self._env = parse_env(line.decode("utf-8"))

        await self.add_key(DEFAULT_SSH_KEY)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Kills the running ssh-agent instance if nothing else is using it."""
        if self._chains == 0:
            self._proc.terminate()
            await self._proc.wait()

        self._chains -= 1

    async def add_key(self, file: Path):
        """Adds a key to the ssh-agent."""
        proc = await run("ssh-add",
                         str(file.resolve()),
                         env=self._env,
                         stdout=DEVNULL,
                         stderr=DEVNULL)
        await proc.wait()

    def chained(self):
        """Increments the number of chained uses of this agent and returns
        itself."""
        self._chains += 1
        return self

    def env(self):
        """Get the ssh-agent environment."""
        return self._env

    def update(self, env):
        """Updates the ssh-agent environment."""
        self._env.update(env)
