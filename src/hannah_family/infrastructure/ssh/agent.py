from asyncio.subprocess import DEVNULL, PIPE
from pathlib import Path

from hannah_family.infrastructure.utils.subprocess import parse_env, run

from . import DEFAULT_SSH_KEY


class SSHAgent:
    """Manages an instance of ssh-agent for the current process."""
    def __init__(self, env={}):
        self._env = {}
        self._env.update(env)

    async def __aenter__(self):
        """Starts an ssh-agent instance and adds the default key."""
        self._proc, self._done = await run("ssh-agent",
                                           "-D",
                                           "-s",
                                           stdout=PIPE,
                                           stderr=PIPE)

        line = await self._proc.stdout.readuntil()
        self._env = parse_env(line.decode("utf-8"))

        await self.add_key(DEFAULT_SSH_KEY)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Kills the running ssh-agent instance."""
        self._proc.terminate()
        await self._done

    async def add_key(self, file: Path):
        """Adds a key to the ssh-agent."""
        proc, done = await run("ssh-add",
                               str(file.resolve()),
                               env=self._env,
                               stdout=DEVNULL,
                               stderr=DEVNULL)
        return await done

    def env(self):
        """Get the ssh-agent environment."""
        return self._env

    def update(self, env):
        """Updates the ssh-agent environment."""
        self._env.update(env)
