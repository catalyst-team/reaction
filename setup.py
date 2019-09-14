import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

NAME = "reaction"
DESCRIPTION = "Reaction. ML serving & microservices."
URL = "https://github.com/catalyst-team/reaction"
EMAIL = "dkuryakin@gmail.com"
AUTHOR = "David Kuryakin"
REQUIRES_PYTHON = ">=3.6.0"

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def load_readme():
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    with open(readme_path) as f:
        return "\n" + f.read()


def load_version():
    context = {}
    with open(os.path.join(PROJECT_ROOT, "reaction", "__version__.py")) as f:
        exec(f.read(), context)
    return context["__version__"]

setup(
    name=NAME,
    version=load_version(),
    description=DESCRIPTION,
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    keywords=[
        "Machine Learning",
    ],
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        'fastapi[all]==0.38.1',
        'aio-pika==6.1.1',
    ],
    include_package_data=True,
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
)
