<h2 align="center">
  <img alt="PyPermission" src="https://gitlab.com/DigonIO/pypermission/-/raw/master/docs/_assets/logo_name.svg" width="60%">
</h2>

<p>
    A role-based access control (RBAC) permission library for python.
</p>

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/pypermission)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/pypermission)
[![license](https://img.shields.io/badge/license-LGPLv3-orange)](https://gitlab.com/DigonIO/pypermission/-/blob/master/LICENSE)
[![pipeline status](https://gitlab.com/DigonIO/pypermission/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/pypermission/badges/master/coverage.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/pypermission/badge/?version=latest)](https://pypermission.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://gitlab.com/DigonIO/scheduler/-/raw/master/doc/_assets/code_style_black.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

[![pkgversion](https://img.shields.io/pypi/v/pypermission)](https://pypi.org/project/pypermission/)
[![versionsupport](https://img.shields.io/pypi/pyversions/pypermission)](https://pypi.org/project/pypermission/)
[![Downloads Week](https://pepy.tech/badge/pypermission/week)](https://pepy.tech/project/pypermission)
[![Downloads Total](https://pepy.tech/badge/pypermission)](https://pepy.tech/project/pypermission)

## WARNING: ALPHA VERSION

This is a prototype. APIs will be subjects to breaking changes! Existing APIs are not battle tested
and might exhibit unexpected behavior!

## Features

+ NIST Model for RBAC[^1]
  + Level 1: Flat
  + Level 2a: Hierarchical
  + Level 3a: Constrained (TODO)
  + Level 4a: Symmetric (TODO)
+ Permissions with hierarchical ordering
+ Permissions with string payloads
+ Persistency backends
  + SQLAlchemy
  + JSON + YAML save files
+ Subject permission assignment (UBAC oriented)
+ [Online Documentation](https://pypermission.readthedocs.io/en/latest/readme.html) (incomplete and incorrect)

## Installation via pip

`PyPermission` can be installed directly from the PyPI repositories.
Multiple options for persistency backends are supported.
The necessary dependencies can be selected directly during installation with pip:

```bash
pip install PyPermission  # JSON (std. lib.)
pip install PyPermission[yaml]  # PyYAML
pip install PyPermission[sqlalchemy]  # SQLAlchemy
pip install PyPermission[all]  # JSON + PyYAML + SQLAlchemy
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
    subjects:
      - Alice
  user:
    permission_nodes:
      - chat.global
      - ticket.open
      - ticket.close.own
    subjects:
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
>>> auth.subject_inherits_permission(sid="Bob", node=Nodes.CHAT_GLOBAL)
True

>>> auth.subject_inherits_permission(sid="Alice", node=Nodes.CHAT_MODERATOR)
True

>>> auth.subject_inherits_permission(sid="Bob", node=Nodes.TICKET_OPEN)
True

>>> auth.subject_inherits_permission(sid="Alice", node=Nodes.TICKET_CLOSE_ALL)
True
```

## Documentation

View the API documentation [online](https://pypermission.readthedocs.io/en/latest/readme.html).

## License

This free and open source software (FOSS) is published under the
[LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html).

---

[^1]: The NIST Model for Role-Based Access Control: Towards a Unified Standard - <https://doi.org/10.1145/344287.344301>
