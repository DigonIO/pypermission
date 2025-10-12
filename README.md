![alt text](./assets/logo_name.svg "Title")

The python `RBAC` library for projects where `SQLAlchemy` is a valid option.

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

---

If you find the RBAC library beneficial, please consider supporting the project by [starring it on GitHub](https://github.com/DigonIO/scheduler).

[![GitHub Repo stars](https://img.shields.io/github/stars/digonio/scheduler)](https://github.com/DigonIO/scheduler)

# Python RBAC with SQLAlchemy

+ Authorization for pythonistas [(Quick Start)](TODO)
+ RBAC with NIST level 2
+ Persistency via SQLAlchemy
    + Postgresql (psycopg)
+ Full integration guide [(Guide)](TODO)
+ Online documentation [(Full doc)](TODO)

## Installation

## Example

```python title="my_project.main.py"
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:", future=True)
db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

from pypermission import RBAC, Permission, create_rbac_database_table

create_rbac_database_table(engine=engine)

with db_factory() as db:
    # Create an 'admin' Role
    RBAC.role.create(role="admin", db=db)

    # Allow all Members of the 'admin' Role, to edit any user
    RBAC.role.grant_permission(
        role="admin",
        permission=Permission(
            resource_type="user",
            resource_id="*",
            action="edit",
        ),
        db=db,
    )

    # Create a Subject for the user 'Alex'
    RBAC.subject.create(subject="Alex", db=db)

    # Assign Subject 'Alex' to the 'admin' Role
    RBAC.subject.assign_role(
        subject="Alex", role="admin", db=db
    )

    # Test if user 'Alex' can edit user 'Max'
    RBAC.subject.assert_permission(
        subject="Alex",
        permission=Permission(
            resource_type="user",
            resource_id="123",
            action="edit",
        ),
        db=db,
    )
```

## Documentation

+ [Online documentation](TODO)
+ [API reference](TODO)

## Sponsor

![Digon.IO GmbH Logo](./assets/logo_digon.io_gmbh.png "Digon.IO GmbH")

Fine-Tuned AI services for developers.

Digon.IO provides end-to-end consulting and development for SMEs and software companies building data-driven solutions - with a focus on supply chain optimization and text processing. [(Website)](https://digon.io) [(Technical Blog)](https://digon.io/en/blog)

_The sponsor logo is the property of Digon.IO GmbH. Standard trademark and copyright restrictions apply to any use outside this repository._

## License

+ **Library source code:** Licensed under SUL-1.0.
+ **Library logo:**  The library logo is a trademark of the project (unregistered). You are permitted to use the logo **only** in contexts that directly reference, document, or promote this library. For example, in a dependent project or in a blog post discussing this library. Any other use is prohibited.
