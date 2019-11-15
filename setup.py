#!/usr/bin/env python3
from pathlib import Path

from setuptools import find_packages, setup


def read_requirements():
    with Path.cwd().joinpath("requirements.txt").open() as file:
        return file.readlines()


setup(name="hannah_family.infrastructure",
      version="0.1.0",
      description="Hannah Family IT infrastructure",
      author="Jesse B. Hannah",
      author_email="jesse@jbhannah.net",
      url="https://github.com/hannnahs-family/infrastructure",
      license="MIT",
      install_requires=read_requirements(),
      packages=find_packages("src"),
      package_dir={"": "src"},
      python_requires="== 3.7.*",
      entry_points={
          "console_scripts": "inf = hannah_family.infrastructure.cli:main"
      })
