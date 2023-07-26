# PlanQK Quantum SDK

[![PyPI version](https://badge.fury.io/py/planqk-quantum.svg)](https://badge.fury.io/py/planqk-quantum)

The PlanQK Quantum SDK is for developing quantum circuits using [Qiskit](https://pypi.org/project/qiskit) to be run on quantum devices provided by the [PlanQK Platform](https://docs.platform.planqk.de).
This library is an **extension** for Qiskit.
This means that you are able to seamlessly integrate and reuse your existing Qiskit code, leveraging the power and familiarity of a framework you are already accustomed to.

## Getting Started

Check out the following guides on how to get started with PlanQK:

- [PlanQK Quickstart Guide](https://docs.platform.planqk.de/getting-started/quickstart.html)
- [Using the PlanQK Quantum SDK](https://docs.platform.planqk.de/getting-started/using-sdk.html)

## Installation

The package is released on PyPI and can be installed via `pip`:

```bash
pip install --upgrade planqk-quantum
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
