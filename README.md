# PlanQK Quantum SDK

[![PyPI version](https://badge.fury.io/py/planqk-quantum.svg)](https://badge.fury.io/py/planqk-quantum)

The PlanQK Quantum SDK is for developing quantum circuits using [Qiskit](https://pypi.org/project/qiskit) to be run on
quantum devices provided by the [PlanQK Platform](https://docs.platform.planqk.de).
This library is an **extension** for Qiskit.
This means that you are able to seamlessly integrate and reuse your existing Qiskit code, leveraging the power and
familiarity of a framework you are already accustomed to.

## Getting Started

Check out the following guides on how to get started with PlanQK:

- [PlanQK Quickstart Guide](https://docs.platform.planqk.de/quickstart.html)
- [Using the PlanQK Quantum SDK](https://docs.platform.planqk.de/using-sdk.html)

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

---

## Release Process

The SDK is released to [PyPi](https://pypi.org/project/planqk-quantum).
The release numbers follow the [Semantic Versioning](https://semver.org) approach resulting in a version number
in the format `major.minor.patch`.
The version number is automatically increased by the CI/CD pipeline based on your
[commit message format](https://github.com/semantic-release/semantic-release#commit-message-format).

### Production Release

If you push to the `main` branch and the commit message contains, for example, the prefix `feat:`, `fix:` or `perf:` a new release will be created automatically.
You can use the keyword `BREAKING CHANGE` in the commit message to trigger a major release.
Use `chore:` or omit the prefix if you do not want a new release to be created.

**Warning:** This release will be public and affects all services using the SDK in production.

### Staging / Testing Release

If you want to create a release only for the testing environment (pre-release), perform the following steps:

1. Create a new branch from `main` and name it `dev` (make sure you delete an old `dev` branch).
   This branch is used for pre-releases and its commits are not automatically released.
2. In the `dev` branch open `setup.py` file and increase the version number and add the suffix `rcX` to it, where `X` is the release candidate number.
   If the version number is for instance `12.1.0`, then the new version number should be `12.1.1rc1`.
3. Push your changes to the `dev` branch.
4. Git to the [GitHub repository](https://github.com/PlanQK/planqk-quantum) and click an on `Releases`.
5. Click on `Draft a new release`.
6. Click on `Choose a tag`.
   Enter the new version number prefixed by `v`in the `Tag version` field, e.g., `v12.1.1rc1`.
7. Select the `dev` branch in the `Target` field.
8. Enter as title the tag name and add a description for the release.
9. Select `This is a pre-release` and click on `Publish release`.

Do not forget to merge your changes back to the main branch once you want to release these changes to production.
