from invoke import Collection, Program
from pkg_resources import get_distribution

from . import tasks

__version__ = get_distribution(__name__).version
program = Program(namespace=Collection.from_module(tasks), version=__version__)
