<h1 align="center">
  <img alt="PyPermission" src="./docs/_assets/logo_name.svg" width="60%">
</h1>

<p>
    A node based permission engine for python.
    Inspired by the permission system used in the Bukkit Minecraft server mod project.
</p>

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/scheduler)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/scheduler)
[![license](https://img.shields.io/badge/license-LGPLv3-orange)](https://gitlab.com/DigonIO/scheduler/-/blob/master/LICENSE)
[![pipeline status](https://gitlab.com/DigonIO/scheduler/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/scheduler/badges/master/coverage.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/python-scheduler/badge/?version=latest)](https://python-scheduler.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://gitlab.com/DigonIO/scheduler/-/raw/master/doc/_assets/code_style_black.svg)](https://github.com/psf/black)

[![pkgversion](https://img.shields.io/pypi/v/scheduler)](https://pypi.org/project/scheduler/)
[![versionsupport](https://img.shields.io/pypi/pyversions/scheduler)](https://pypi.org/project/scheduler/)
[![Downloads Week](https://pepy.tech/badge/scheduler/week)](https://pepy.tech/project/scheduler)
[![Downloads Total](https://pepy.tech/badge/scheduler)](https://pepy.tech/project/scheduler)

## Features

+ RBAC: Role based access control [(Guide)](https://pypermission.readthedocs.io/en/latest/pages/guides/rbac_rest_api_json.html)
+ UBAC: User based access control
+ Tree based permissions nodes
  + Parent nodes
  + Leaf nodes
  + Leaf nodes w/ a string payload
+ Persistency backends
  + JSON
  + YAML

## Installation

### pip

`PyPermission` can be installed directly from the PyPI repositories.

#### JSON persistency backend

```bash
pip install PyPermission
```

#### SQL persistency backend

```bash
pip install PyPermission[sqlalchemy]
```

#### YAML persistency backend

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

## Example code

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
    CHAT_ROOM_ = "chat.room.*"  # parent
    CHAT_ROOM_X = "chat.room.<x>"  # leaf w/ payload
    TICKET_ = "ticket.*"  # parent
    TICKET_OPEN = "ticket.open"  # leaf
    TICKET_CLOSE_ = "ticket.close.*"  # parent
    TICKET_CLOSE_OWN = "ticket.close.own"  # leaf
    TICKET_CLOSE_ALL = "ticket.close.all"  # leaf
    TICKET_ASSIGN = "ticket.assign"  # leaf

auth = SerialAuthority(nodes=Nodes)
```

The following file `save_file.yaml` defines a mixed access control setup (RBAC & UBAC). Alice is
a member of the moderator group, while Bob is given only permissions of the user group:

```yaml
groups:
  moderator:
    permission_nodes:
      - chat.global
      - chat.room.*
      - ticket.*
    member_subjects:
      - Alice
  user:
    permission_nodes:
      - ticket.open
      - ticket.close.own
    member_subjects:
      - Bob
    member_groups:
      - moderator
subjects:
  Alice:
    permission_nodes:
      - chat.room.<Alice>
  Bob:
    permission_nodes:
      - chat.room.<Bob>
```

```py
auth.load_file(path="save_file.yaml")
```

Now check if a subject has a desired permission.

```pycon
>>> auth.subject_has_permission(sid="Bob", node=Nodes.TICKET_OPEN)
True

>>> auth.subject_has_permission(sid="Alice", node=Nodes.TICKET_CLOSE_ALL)
True

>>> auth.subject_has_permission(sid="Alice", node=Nodes.CHAT_ROOM_X, payload="Bob")
True

>>> auth.subject_has_permission(sid="Bob", node=Nodes.CHAT_ROOM_X, payload="Alice")
False
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
