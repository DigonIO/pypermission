# PyPermission

<p>Lightweight permission system for your python projects. Inspired by the permission system used in the `Bukkit` Minecraft server mod project.
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
  + Subjects: e.g. users
  + Groups: e.g. collection of users
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

#### JSON backend

```bash
pip install PyPermission
```

#### YAML backend

```bash
pip install PyPermission[yaml]
```

### Editable installation for developers

Install `PyPermission` from the `git`
[repository](https://gitlab.com/DigonIO/PyPermission) with:

```bash
git clone https://gitlab.com/DigonIO/PyPermission.git
cd PyPermission
pip install -e .
```

## Example code

Setup a permission authority and a helper function:

```py
from pypermission.json import Authority

auth = Authority()

def r(node: str):
    """Reduces boilerplate code while registering permission nodes."""
    return auth.register_permission(node=node)
```

Register permission nodes (example permission nodes from [towny](https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java)):

```py
ROOT_ = auth.root_permission  # root
TOWNY_ = r("towny.*")  # parent
TOWNY_CHAT_ = r("towny.chat.*")  # parent
TOWNY_CHAT_TOWN = r("towny.chat.town")  # leaf
TOWNY_CHAT_NATION = r("towny.chat.nation") # leaf
TOWNY_CHAT_GLOBAL = r("towny.chat.global") # leaf
TOWNY_WILD_ = r("towny.wild.*")  # parent
TOWNY_WILD_BUILD_ = r("towny.wild.build.*")  # parent
TOWNY_WILD_BUILD_X = r("towny.wild.build.<x>") # leaf w/ payload
TOWNY_WILD_DESTROY_ = r("towny.wild.destroy.*")  # parent
TOWNY_WILD_DESTROY_X = r("towny.wild.destroy.<x>") # leaf w/ payload
```

Create a group and add some permissions:

```py
GROUP_ID = "group_foo"  # the group ID can be str or int

auth.group_add(group_id=GROUP_ID)

auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_CHAT_)
auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_WILD_DESTROY_X, payload="iron")
auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_WILD_DESTROY_X, payload="gold")
```

Create a subject, add it to a group and add a permission:

```py
SUBJECT_ID = "user_bar"  # the subject ID can be str or int

auth.subject_add(subject_id=SUBJECT_ID)
auth.group_add_subject(group_id=GROUP_ID, subject_id=SUBJECT_ID)

auth.subject_add_permission(subject_id=SUBJECT_ID, permission=TOWNY_WILD_DESTROY_X, payload="diamond")

```

Now check if a subject has a desired permission:

```py
if(auth.subject_has_permission(subject_id=SUBJECT_ID, permission=TOWNY_CHAT_TOWN))
  ...  # parent permission provided by the group

if(auth.subject_has_permission(subject_id=SUBJECT_ID, permission=TOWNY_WILD_DESTROY_X, payload="iron"))
  ...  # leaf w/ payload permission provided by the group

if(auth.subject_has_permission(subject_id=SUBJECT_ID, permission=TOWNY_WILD_DESTROY_X, payload="diamond"))
  ...  # leaf w/ payload permission provided by the subject itself
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
