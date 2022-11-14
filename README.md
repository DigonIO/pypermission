<h1 align="center">
  <img alt="PyPermission" src="./docs/_assets/logo_name.svg" width="60%">
</h1>

<p>
    A role-based access control (RBAC) permission library for python.
</p>

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/pypermission)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/pypermission)
[![license](https://img.shields.io/badge/license-LGPLv3-orange)](https://gitlab.com/DigonIO/pypermission/-/blob/master/LICENSE)
[![pipeline status](https://gitlab.com/DigonIO/pypermission/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/pypermission/badges/master/coverage.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/python-pypermission/badge/?version=latest)](https://pypermission.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://gitlab.com/DigonIO/pypermission/-/raw/master/doc/_assets/code_style_black.svg)](https://github.com/psf/black)

[![pkgversion](https://img.shields.io/pypi/v/pypermission)](https://pypi.org/project/pypermission/)
[![versionsupport](https://img.shields.io/pypi/pyversions/pypermission)](https://pypi.org/project/pypermission/)
[![Downloads Week](https://pepy.tech/badge/pypermission/week)](https://pepy.tech/project/pypermission)
[![Downloads Total](https://pepy.tech/badge/pypermission)](https://pepy.tech/project/pypermission)

## WARNING: ALPHA VERSION

This is a prototype. APIs will be subjects to breaking changes! Existing APIs are not battle tested
and might exhibit unexpected behavior!

## Features

+ NIST Model for RBAC: <https://doi.org/10.1145/344287.344301>
  + Level 1: Flat (Missing method)
  + Level 2a: Hierarchical
  + Level 3a: Constrained (TODO)
  + Level 4a: Symmetric (TODO)
+ Permissions with hierarchical ordering
+ Permissions with string payloads
+ Persistency backends
  + SQLAlchemy
  + JSON + YAML save files
+ Subject permission assignment (UBAC oriented)
+ Online Documentation (TODO, is incomplete and incorrect)

## Installation

### pip

`PyPermission` can be installed directly from the PyPI repositories.

#### JSON persistency backend

```bash
pip install PyPermission
```

#### SQLAlchemy persistency backend

```bash
pip install PyPermission[sqlalchemy]
```

#### JSON + YAML persistency backend

```bash
pip install PyPermission[yaml]
```

### Editable installation for developers

Install `PyPermission` from the `git`
[repository](https://gitlab.com/DigonIO/PyPermission) with:

```bash
git clone https://gitlab.com/DigonIO/PyPermission.git
cd PyPermission
python -m venv venv  # optional
source ./venv/bin/activate # optional
pip install -e .[dev]
```

## Example: *How to RBAC*

Import all required objects. Here we will choose the authority with the JSON persistency backend.

```py
from pypermission import PermissionNode
from pypermission.yaml import SerialAuthority
```

Define an authority with some permission nodes:

```py
class Nodes(PermissionNode):
    CHAT_ = "chat.*"  # parent
    CHAT_GLOBAL = "chat.global"  # leaf
    CHAT_MODERATOR = "chat.moderator"  # leaf
    TICKET_ = "ticket.*"  # parent
    TICKET_OPEN = "ticket.open"  # leaf
    TICKET_CLOSE_ = "ticket.close.*"  # parent
    TICKET_CLOSE_OWN = "ticket.close.own"  # leaf
    TICKET_CLOSE_ALL = "ticket.close.all"  # leaf
    TICKET_ASSIGN = "ticket.assign"  # leaf

auth = SerialAuthority(nodes=Nodes)
```

The following file `save_file.yaml` defines a RBAC setup. Alice is
a member of the user and moderator role, while Bob is assigned only to the user role:

```yaml
roles:
  moderator:
    permission_nodes:
      - chat.*
      - ticket.*
    member_subjects:
      - Alice
  user:
    permission_nodes:
      - chat.global
      - ticket.open
      - ticket.close.own
    member_subjects:
      - Alice
      - Bob
subjects:
  Alice: {}
  Bob: {}
```

```py
auth.load_file(path="save_file.yaml")
```

Now check if a subject has a desired permission.

```pycon
>>> auth.subject_has_permission(sid="Bob", node=Nodes.CHAT_GLOBAL)
True

>>> auth.subject_has_permission(sid="Alice", node=Nodes.CHAT_MODERATOR)
True

>>> auth.subject_has_permission(sid="Bob", node=Nodes.TICKET_OPEN)
True

>>> auth.subject_has_permission(sid="Alice", node=Nodes.TICKET_CLOSE_ALL)
True
```

## Documentation

The API documentation can either be viewed
[online](https://pypermission.readthedocs.io/en/latest/readme.html)
or generated using Sphinx with [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
formatting. To build, run:

```bash
sphinx-build -b html docs/ docs/_build/html
```

## Testing

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

## License

This free and open source software (FOSS) is published under the [LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html).
