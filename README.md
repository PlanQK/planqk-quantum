# Python library for the PlanQK Platform

[![PyPI version](https://badge.fury.io/py/planqk-quantum.svg)](https://badge.fury.io/py/planqk-quantum)

The `planqk-quantum` library is a SDK for developing quantum circuits using [Qiskit](https://pypi.org/project/qiskit) to be run on quantum devices provided by the [PlanQK Platform](https://docs.platform.planqk.de).

## Getting Started

Check out the following guides on how to get started with PlanQK:

- [Tutorial on how to create a PlanQK Service using the `planqk-quantum` library](https://docs.platform.planqk.de/tutorials/tutorial-qiskit.html)
- [General guide on how to create and deploy PlanQK Services](https://docs.platform.planqk.de/docs/service-platform/managed-services.html)

## Installation

The package is released on PyPI and can be installed via `pip`:

```bash
pip install planqk-quantum
```

## Development

To create a new Conda environment, run:

```bash
conda env create -f environment.yml
```

Then, to activate the environment:

```bash
conda activate planqk-quantum
```

To install the package in development mode, run:

```bash
pip install -e .
```
