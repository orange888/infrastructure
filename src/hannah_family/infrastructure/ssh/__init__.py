from pathlib import Path

DEFAULT_SSH_KEY = Path.cwd().joinpath(".ssh", "id_ed25519").resolve()
