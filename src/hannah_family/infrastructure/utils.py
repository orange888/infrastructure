import subprocess
from re import compile

from click import ClickException

ENV_PATTERN = compile(r"([A-Z_]+)=([^;]+);")


def parse_env(output: str):
    return {name: value for name, value in ENV_PATTERN.findall(output)}


def run(*args, **kwargs):
    """Run a command with subprocess.run, catching any CalledProcessExceptions
    and exiting with the error code of the subprocess command."""
    if "check" not in kwargs:
        kwargs["check"] = True

    try:
        return subprocess.run(*args, **kwargs)
    except subprocess.CalledProcessError as e:
        exit(e.returncode)
