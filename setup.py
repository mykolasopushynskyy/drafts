import pathlib

import pkg_resources
from setuptools import setup, find_packages

with pathlib.Path("requirements.txt").open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name="Drafts, blueprints & util scripts",
    version="1.0",
    packages=find_packages(),
    entry_points={},
    install_requires=install_requires,
)
