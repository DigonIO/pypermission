![alt text](./assets/logo_name.svg "Title")

A python `RBAC` library for projects where `SQLAlchemy` is a valid option.

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/pypermission)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/pypermission)
[![License: SUL-1.0](assets/badges/license.svg)](https://spdx.org/licenses/SUL-1.0.html)
[![pipeline status](https://gitlab.com/DigonIO/pypermission/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/pypermission/badges/master/coverage.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/python-pypermission/badge/?version=latest)](https://pypermission.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](assets/badges/black.svg)](https://github.com/psf/black)
[![Imports: isort](assets/badges/isort.svg)](https://pycqa.github.io/isort/)

[![pkgversion](https://img.shields.io/pypi/v/pypermission)](https://pypi.org/project/pypermission/)
[![versionsupport](https://img.shields.io/pypi/pyversions/pypermission)](https://pypi.org/project/pypermission/)
[![Downloads Week](https://pepy.tech/badge/pypermission/week)](https://pepy.tech/project/pypermission)
[![Downloads Total](https://pepy.tech/badge/pypermission)](https://pepy.tech/project/pypermission)

# Python RBAC with SQLAlchemy

+ RBAC with NIST Level 2
+ Persistency via SQLAlchemy
  + Postgresql (psycopg)

## Installation

## Example

``` python title="my_project.main.py"
from pypermission import RBAC, Policy, Permission, create_rbac_database_table
from my_project.sqla import sqla_engine, sqla_session_factory

create_rbac_database_table(engine=sqla_engine)
```

```python
with sqla_session_factory() as db:
    RBAC.role.create(role="user", db=db)
    RBAC.role.create(role="guest", db=db)
    RBAC.role.add_hierarchy(
        parent_role="guest", child_role="user", db=db
    )

    RBAC.subject.create(subject="Alex", db=db)
    RBAC.subject.assign_role(
        subject="Alex", role="user", db=db
    )

    RBAC.policy.create(policy=Policy(
        role="guest",
        permission=Permission(
            resource_type="group",
            resource_id="*",
            action="access",
        ),
        db=db,
    ))
```

```python
with sqla_session_factory() as db:
    RBAC.subject.assert_permission(
        subject="Alex",
        permission=Permission(
            resource_type="group",
            resource_id="123",
            action="access",
        ),
        db=db,
    )
```

## Documentation

## Sponsor

## License

+ **Library source code:** LGPL-3.0-only
+ **Library logo:** LGPL-3.0-only
