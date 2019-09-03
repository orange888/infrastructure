from setuptools import find_packages, setup

with open("requirements.txt", "r") as requirements:
    install_requires = requirements.readlines()

setup(name="hfi",
      version="0.1.0",
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      install_requires=install_requires,
      entry_points={"console_scripts": ["hfi = hfi:program.run"]})
