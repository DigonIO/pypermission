# Contributing to PyPermission

Contributions are highly appreciated.

## Code of Conduct

When participating in this project, please treat other people respectfully.
Generally the guidelines pointed out in the
[Python Community Code of Conduct](https://www.python.org/psf/conduct/)
are a good standard we aim to uphold.

## Feedback and feature requests

We'd like to hear from you if you are using `PyPermission`.

For suggestions and feature requests feel free to submit them to our
[issue tracker](https://gitlab.com/DigonIO/pypermission/-/issues).

## Bugs

Found a bug? Please report back to our
[issue tracker](https://gitlab.com/DigonIO/pypermission/-/issues).

If possible include:

* Operating system name and version
* python and `PyPermission` version
* Steps needed to reproduce the bug

## Development Setup

Clone the `PyPermission` repository with `git` and enter the directory:

```bash
git clone https://gitlab.com/DigonIO/PyPermission.git
cd PyPermission
```

Create and activate a virtual environment:

```bash
python -m venv venv
source ./venv/bin/activate
```

Install the development requirements and the project:

```bash
pip install -e .[dev]
```

## Running tests

Testing is done using [pytest](https://pypi.org/project/pytest/). With
[pytest-cov](https://pypi.org/project/pytest-cov/) and
[coverage](https://pypi.org/project/coverage/) a report for the test coverage can be generated:

```bash
pytest --cov=src/ tests/
coverage html
```

To test the examples in the documentation run:

```bash
pytest docs/
```

## Building the documentation

To build the documentation locally, run:

```bash
sphinx-build -b html docs/ docs/_build/html
```

We are using Sphinx with [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
formatting. Additionally the documentation is tested with `pytest` together with the
`sybil` extension to parse the doctests.

## Pull requests

1. Fork the repository and check out on the `dev` branch.
2. Follow PEP-8 and use Use [isort](https://github.com/PyCQA/isort) and [black](https://github.com/psf/black) for formatting.
3. Apply the the static code analysis tools
  `pylint`, `pydocstyle`, `bandit` and `mypy` on the codebase in `src/` and check the
  output to avoid introduction of regressions.
4. Verify that `pytest` passes on both - the `tests/` and the `docs/` folder.
5. Create a commit with a descriptive summary of your changes.
6. Create a [pull request](https://gitlab.com/DigonIO/pypermission/-/merge_requests)
   on the official repository.
