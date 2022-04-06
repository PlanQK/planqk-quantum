import os

from setuptools import setup, find_namespace_packages

version = os.environ.get("VERSION", "1.0.1")

with open("./README.md", "r") as fh:
    long_description = fh.read()

with open("./requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name="planqk-quantum",
    version=version,
    author="StoneOne AG",
    author_email="info@stoneone.de",
    url="https://github.com/planqk/planqk-quantum",
    description="Python library for the PlanQK Quantum Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["planqk", "planqk.*"]),
    license="apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)
