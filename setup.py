#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the "upload" functionality of this file, you must:
#   $ pip install twine

import os
from shutil import rmtree
import sys

from setuptools import Command, find_packages, setup

# Package meta-data.
NAME = "reaction"
DESCRIPTION = "Reaction. Convenient DL serving."
URL = "https://github.com/catalyst-team/reaction"
EMAIL = "dkuryakin@gmail.com"
AUTHOR = "David Kuryakin"
REQUIRES_PYTHON = ">=3.6.0"

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def load_requirements(filename):
    with open(os.path.join(PROJECT_ROOT, filename), "r") as f:
        return f.read().splitlines()


def load_readme():
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    with open(readme_path) as f:
        return "\n" + f.read()


def load_version():
    context = {}
    with open(os.path.join(PROJECT_ROOT, "reaction", "__version__.py")) as f:
        exec(f.read(), context)
    return context["__version__"]


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(PROJECT_ROOT, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system(
            "{0} setup.py sdist bdist_wheel --universal".format(sys.executable)
        )

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(load_version()))
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    version=load_version(),
    description=DESCRIPTION,
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    keywords=["Machine Learning", "Deep Learning", "PyTorch"],
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    download_url=URL,
    project_urls={
        "Bug Tracker": "https://github.com/catalyst-team/reaction/issues",
        "Documentation": "https://catalyst-team.github.io/reaction",
        "Source Code": "https://github.com/catalyst-team/reaction",
    },
    packages=find_packages(exclude=("tests",)),
    install_requires=load_requirements("requirements/requirements.txt"),
    include_package_data=True,
    license="Apache License 2.0",
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        # Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        # Topics
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        # Programming
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)
