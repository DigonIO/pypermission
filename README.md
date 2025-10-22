![alt text](./assets/logo_font_path.svg "Title")

The python `RBAC` library for projects where `SQLAlchemy` is a valid option.

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/rbac)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/rbac)
[![License: SUL-1.0](assets/badges/license.svg)](https://spdx.org/licenses/SUL-1.0.html)
[![pipeline status](https://gitlab.com/DigonIO/rbac/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/rbac/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/rbac/badges/master/coverage.svg)](https://gitlab.com/DigonIO/rbac/-/pipelines)
[![Code style: black](assets/badges/black.svg)](https://github.com/psf/black)
[![Imports: isort](assets/badges/isort.svg)](https://pycqa.github.io/isort/)

---

If you find the RBAC library beneficial, please consider supporting the project by [starring it on GitHub](https://github.com/DigonIO/scheduler).

[![GitHub Repo stars](https://img.shields.io/github/stars/digonio/scheduler)](https://github.com/DigonIO/scheduler)

# RBAC for Python with SQLAlchemy

## Features

+ Authorization for pythonistas [(Quick Start)](TODO)
+ Persistency via SQLAlchemy
    + SQLite
    + PostgreSQL (psycopg)
+ Full integration guide [(Guide)](TODO)
+ RBAC state analysis (optional)
    + Export the RBAC DAG as NetworkX DiGraph
    + Visualize the RBAC DAG via Plotly
+ Lightweight
+ High test coverage
+ Online documentation [(Full doc)](TODO)

## Installing `rbac` with pip

**WARNING** There is no release of this library available on PyPI yet.

The `rbac` library can be installed directly from the PyPI repositories with:

```console
pip install rbac
```

If you want to use PostgreSQL, you need to install the `postgres` dependency group:

```console
pip install 'rbac[postgres]'
```

## Example

```python title="my_project.main.py"
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:", future=True)
db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

from rbac import RBAC, Permission, create_rbac_database_table

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
