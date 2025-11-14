![Logo: PyPermission - RBAC for Python](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/logo_font_path.svg "PyPermission Logo")

**PyPermission** - The python RBAC authorization authorization library for projects where SQLAlchemy is a valid option.

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/pypermission)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/pypermission)
[![License: LGPLv3](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/badges/license.svg)](https://spdx.org/licenses/LGPL-3.0-only.html)
[![pipeline status](https://gitlab.com/DigonIO/pypermission/badges/main/pipeline.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/pypermission/badges/main/coverage.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![Code style: black](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/badges/black.svg)](https://github.com/psf/black)
[![Imports: isort](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/badges/isort.svg)](https://pycqa.github.io/isort/)

[![pkgversion](https://img.shields.io/pypi/v/pypermission)](https://pypi.org/project/pypermission/)
[![versionsupport](https://img.shields.io/pypi/pyversions/pypermission)](https://pypi.org/project/pypermission/)
[![Downloads Week](https://pepy.tech/badge/pypermission/week)](https://pepy.tech/project/pypermission)
[![Downloads Total](https://pepy.tech/badge/pypermission)](https://pepy.tech/project/pypermission)

---

If you find the PyPermission library beneficial, please consider supporting the project by [starring it on GitHub](https://github.com/DigonIO/pypermission).

[![GitHub Repo stars](https://img.shields.io/github/stars/digonio/pypermission)](https://github.com/DigonIO/pypermission)

# Python RBAC authorization with SQLAlchemy

## Features

- Authorization for pythonistas [(Quick Start)](https://pypermission.digon.io/quick_start/)
- Persistency via SQLAlchemy
    - SQLite
    - PostgreSQL (psycopg)
- Full integration guide [(Guide WIP)](https://pypermission.digon.io/guide/)
- RBAC state analysis (optional)
    - Export the RBAC DAG as NetworkX DiGraph
    - Visualize the RBAC DAG via Plotly
- Lightweight
- High test coverage
- [Online documentation](https://pypermission.digon.io/)

## Installing `PyPermission` with pip

The **PyPermission** library can be installed directly from the PyPI repositories with:

```console
pip install PyPermission
```

If you want to use PostgreSQL, you need to install the `postgres` dependency group:

```console
pip install 'PyPermission[postgres]'
```

## Example

```python title="my_project.main.py"
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.event import listen

engine = create_engine("sqlite:///:memory:", future=True)
db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

from pypermission import RBAC, Permission, create_rbac_database_table, set_sqlite_pragma

listen(engine, "connect", set_sqlite_pragma) # needed for foreign key constraints (sqlite only)
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

## Resources

- [Online documentation](https://pypermission.digon.io/)
- [API reference](https://pypermission.digon.io/api/rbac/)
- [Changelog](https://gitlab.com/DigonIO/pypermission/-/blob/main/CHANGELOG.md)
- [How to contribute](https://gitlab.com/DigonIO/pypermission/-/blob/main/CONTRIBUTING.md)

## Sponsor

![Digon.IO GmbH Logo](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/logo_digon.io_gmbh.png "Digon.IO GmbH")

Fine-Tuned AI services for developers.

Digon.IO provides end-to-end consulting and development for SMEs and software companies building data-driven solutions - with a focus on supply chain optimization and text processing. [(Website)](https://digon.io) [(Technical Blog)](https://digon.io/en/blog)

_The sponsor logo is the property of Digon.IO GmbH. Standard trademark and copyright restrictions apply to any use outside this repository._

## License

- **Library source code:** Licensed under [LGPLv3](https://spdx.org/licenses/LGPL-3.0-only.html).
- **Library logo:** The library logo is a trademark of the project (unregistered). You are permitted to use the logo **only** in contexts that directly reference, document, or promote this library. For example, in a dependent project or in a blog post discussing this library. Any other use is prohibited.
