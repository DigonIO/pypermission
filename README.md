# PyPermission

<p>
    A node based permission engine for python.
    Inspired by the permission system used in the `Bukkit` Minecraft server mod project.
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

+ Permissionable entities
  + Subjects (e.g. users)
  + Groups (e.g. collection of users)
    + Group of subjects
    + Nested groups possible
+ Tree based permissions nodes
  + Parent nodes
  + Leaf nodes
  + Leaf nodes w/ a string payload
+ Persistency backend
  + JSON
  + YAML

## Installation

### pip

`PyPermission` can be installed directly from the PyPI repositories.

#### JSON persistency backend

```bash
pip install PyPermission
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
from pypermission.json import Authority, PermissionNode, EntityID
```

Define some permission nodes. We distinguish between buildin and plugin permission nodes.
Buildin permission nodes are registered when the authority is instantiated.
Plugin permission nodes can be registered via an extra api after the authority has been created.

```py
class BuildinPN(PermissionNode):
    ADMIN = "admin"  # leaf
    COMMAND_ = "command.*"  # parent
    COMMAND_STATS = "command.stats"  # leaf
    COMMAND_RESPAWN = "command.respawn"  # leaf


class PluginPN(PermissionNode):
    # Example permission nodes taken from the towny Minecraft server plugin
    # https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java
    TOWNY_ = "towny.*"  # parent
    TOWNY_CHAT_ = "towny.chat.*"  # parent
    TOWNY_CHAT_TOWN = "towny.chat.town"  # leaf
    TOWNY_CHAT_NATION = "towny.chat.nation"  # leaf
    TOWNY_CHAT_GLOBAL = "towny.chat.global"  # leaf
    TOWNY_WILD_ = "towny.wild.*"  # parent
    TOWNY_WILD_BUILD_ = "towny.wild.build.*"  # parent
    TOWNY_WILD_BUILD_X = "towny.wild.build.<x>"  # leaf w/ payload
    TOWNY_WILD_DESTROY_ = "towny.wild.destroy.*"  # parent
    TOWNY_WILD_DESTROY_X = "towny.wild.destroy.<x>"  # leaf w/ payload
```

Create an authority and register all permission nodes.

```py
auth = Authority(nodes=BuildinPN)  # register buildin nodes
auth.register_permission_nodes(nodes=PluginPN)  # api for plugin based node registration
```

Create a group and add some permissions.

```py
GROUP_ID: EntityID = "group_foo"  # str | int
auth.add_group(g_id=GROUP_ID)

auth.group_add_permission(g_id=GROUP_ID, node=PluginPN.TOWNY_CHAT_)
auth.group_add_permission(g_id=GROUP_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="iron")
auth.group_add_permission(g_id=GROUP_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="gold")
```

Create a subject, add it to a group and add a permission.

```py
SUBJECT_ID: EntityID = "user_bar"  # str | int
auth.add_subject(s_id=SUBJECT_ID)
auth.group_add_subject(g_id=GROUP_ID, s_id=SUBJECT_ID)

auth.subject_add_permission(
    s_id=SUBJECT_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="diamond"
)
```

Now check if a subject has a desired permission.

```py
if auth.subject_has_permission(s_id=SUBJECT_ID, node=PluginPN.TOWNY_CHAT_TOWN):
    print("Parent permission provided by the group.")

if auth.subject_has_permission(
    s_id=SUBJECT_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="iron"
):
    print("Leaf w/ payload permission provided by the group.")

if auth.subject_has_permission(
    s_id=SUBJECT_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="diamond"
):
    print("Leaf w/ payload permission provided by the subject itself.")
```

## Documentation

The API documentation can either be viewed
[online](https://pypermission.readthedocs.io/en/latest/readme.html)
or generated using Sphinx with [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
formatting. To build, run:

```bash
sphinx-build -b html doc/ doc/_build/html
```


## Testing

Testing is done using [pytest](https://pypi.org/project/pytest/). With
[pytest-cov](https://pypi.org/project/pytest-cov/) and
[coverage](https://pypi.org/project/coverage/) a report for the test coverage can be generated:

```bash
pytest --cov=src/ tests/
coverage html
```

## License

This free and open source software (FOSS) is published under the [LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html).
