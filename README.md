![Logo: PyPermission - RBAC for Python](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/logo_font_path.svg "PyPermission Logo")

**PyPermission** - The python RBAC authorization library for projects where SQLAlchemy is a valid option.

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

**PyPermission** keeps authorization simple. It avoids framework lock-ins, skips **Policy** DSL complexity, and gives developers a clean, Python-native way to express **Subjects**, **Roles**, **Resources**, and **Permissions** across any application architecture.

---

If you find the **PyPermission** library beneficial, please consider supporting the project by [starring it on GitHub](https://github.com/DigonIO/pypermission).

[![GitHub Repo stars](https://img.shields.io/github/stars/digonio/pypermission)](https://github.com/DigonIO/pypermission)

# **PyPermission** - RBAC for Python

## Features

- RBAC for Python [(Quick Start)](https://pypermission.digon.io/quick_start/)
    - Subjects, Roles, Hierarchies, Permissions, Policies & Auditing
    - Supports NIST Level 2a & some Level 4 review functions [(Details)](https://pypermission.digon.io/nist/)
- Persistency via SQLAlchemy
    - SQLite & PostgreSQL (psycopg)
- [Integration Guide](https://pypermission.digon.io/integration_guide/1_introduction/)
- [Advanced Auditing](https://pypermission.digon.io/auditing_guide/)
    - Export a RBAC DAG as NetworkX DiGraph
    - Visualize a RBAC DAG via Plotly
- Lightweight
- High test [Coverage](https://pypermission.digon.io/coverage/)
- [Online documentation](https://pypermission.digon.io/)

## Installing **PyPermission** with pip

The **PyPermission** library can be installed directly from the PyPI repositories with:

```console
pip install PyPermission
```

If you want to use PostgreSQL, you need to install the `postgres` dependency group:

```console
pip install 'PyPermission[postgres]'
```

## Usage Example

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
            resource_id="Max",
            action="edit",
        ),
        db=db,
    )
```

## Auditing

**PyPermission** supports a variety of review functions for auditing of the RBAC system and even comes with some tooling for visualization out of the box.

![Auditing graph for RBAC in Python](https://gitlab.com/DigonIO/pypermission/-/raw/dev/assets/rbac_auditing_graph_example.png "Auditing graph for RBAC in Python")

## The Core API surface on a glance

[`pypermission.service.role.RoleService`](https://pypermission.digon.io/api/role/#pypermission.service.role.RoleService)

| Methods                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------- |
| `create(*, role: str, db: Session) -> None`                                                                                       |
| `delete(*, role: str, db: Session) -> None`                                                                                       |
| `list(*, db: Session) -> tuple[str, ...]`                                                                                         |
| `add_hierarchy(*, parent_role: str, child_role: str, db: Session) -> None`                                                        |
| `remove_hierarchy(*, parent_role: str, child_role: str, db: Session) -> None`                                                     |
| `children(*, role: str, db: Session) -> tuple[str, ...]`                                                                          |
| `ascendants(*, role: str, db: Session) -> tuple[str, ...]`                                                                        |
| `descendants(*, role: str, db: Session) -> tuple[str, ...]`                                                                       |
| `subjects(*, role: str, include_descendant_subjects: bool = False, db: Session) -> tuple[str, ...]`                               |
| `grant_permission(*, role: str, permission: Permission, db: Session) -> None`                                                     |
| `revoke_permission(*, role: str, permission: Permission, db: Session) -> None`                                                    |
| `check_permission(*, role: str, permission: Permission, db: Session) -> bool`                                                     |
| `assert_permission(*, role: str, permission: Permission, db: Session) -> None`                                                    |
| `permissions(*, role: str, inherited: bool = True, db: Session) -> tuple[Permission, ...]`                                        |
| `policies(*, role: str, inherited: bool = True, db: Session) -> tuple[Policy, ...]`                                               |
| `actions_on_resource(*, role: str, resource_type: str, resource_id: str, inherited: bool = True, db: Session) -> tuple[str, ...]` |

[`pypermission.service.role.SubjectService`](https://pypermission.digon.io/api/subject/#pypermission.service.subject.SubjectService)

| Methods                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------ |
| `create(*, subject: str, db: Session) -> None`                                                                                       |
| `delete(*, subject: str, db: Session) -> None`                                                                                       |
| `list(*, db: Session) -> tuple[str, ...]`                                                                                            |
| `assign_role(*, subject: str, role: str, db: Session) -> None`                                                                       |
| `deassign_role(*, subject: str, role: str, db: Session) -> None`                                                                     |
| `roles(*, subject: str, include_ascendant_roles: bool = False, db: Session) -> tuple[str, ...]`                                      |
| `check_permission(*, subject: str, permission: Permission, db: Session) -> bool`                                                     |
| `assert_permission(*, subject: str, permission: Permission, db: Session) -> None`                                                    |
| `permissions(*, subject: str, db: Session) -> tuple[Permission, ...]`                                                                |
| `policies(*, subject: str, db: Session) -> tuple[Policy, ...]`                                                                       |
| `actions_on_resource(*, subject: str, resource_type: str, resource_id: str, inherited: bool = True, db: Session) -> tuple[str, ...]` |

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
