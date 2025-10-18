# RBAC for Python - Quick Start

!!! info

    This quick start tutorial is intended for developers who already have experience with RBAC systems. For anyone using RBAC in their own project for the first time, we recommend going through the documentation in the following order:

    1. [Definitions](./definitions.md)
    2. [Permission design guide](./permission_design_guide.md)
    3. [Implementation guide](./guide/index.md)

The `rbac` library can be installed directly from the PyPI repositories with:

!!! warning

    There is no release of this library available on PyPI yet.

```console
pip install rbac
```

For the following example we initialize an in-memory SQLite database using `SQLAlchemy` (we also provide PostgreSQL support with the `'rbac[postgres]'` dependency group).

```python
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:", future=True)
db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

Create the required tables in the database:

```{.python continuation}
from rbac import create_rbac_database_table

create_rbac_database_table(engine=engine)
```

The rbac library organizes its core functionality into two main services - `RoleService` and `SubjectService`. These services are accessible through the main RBAC class, which provides a unified interface for managing Roles, Subjects, and Policies. The examples below demonstrates basic usage.

## Manage Subjects and Roles

Start by creating a `user` and an `admin` Role:

```{.python continuation}
from rbac import RBAC

with db_factory() as db:
    RBAC.role.create(role="user", db=db)
    RBAC.role.create(role="admin", db=db)
    db.commit()
```

We want the `admin` Role to inherit all permissions of the `user` Role, therefore we model the `admin` Role as a child of the `user` role in our Role hierarchy:

```{.python continuation}
with db_factory() as db:
    RBAC.role.add_hierarchy(
        parent_role="user",
        child_role="admin",
        db=db,
    )
    db.commit()
```

Next, create two Subjects: `Alex` and `Ursula` who we respectively assign the `admin` and `user` Roles.

```{.python continuation}
with db_factory() as db:
    RBAC.subject.create(subject="Alex", db=db)
    RBAC.subject.create(subject="Ursula", db=db)

    RBAC.subject.assign_role(subject="Alex", role="admin", db=db)
    RBAC.subject.assign_role(subject="Ursula", role="user", db=db)

    db.commit()
```

## Basic Permission handling

When creating a `Permission`, you can use the wildcard string `"*"` for the `resource_id` to indicate that all resources of the given `resource_type` and `action` can be granted via this `Permission`.

In this example, we want everyone with the `user` Role to be able to `view` every `event` in the system. This corresponds to `Permission(resource_type="event", resource_id="*", action="view")`, representable as `"event[*]:view"`. Likewise we assign the `"event[*]:edit"` `Permission` to the `admin` Role to allow the `edit` action for the `admin` on all `event` resources.

```{.python continuation}
from rbac import Permission

with db_factory() as db:
    RBAC.role.grant_permission(
        role="user",
        permission=Permission(
            resource_type="event", resource_id="*", action="view"
        ),
        db=db,
    )
    RBAC.role.grant_permission(
        role="admin",
        permission=Permission(
            resource_type="event", resource_id="*", action="edit"
        ),
        db=db,
    )
```

!!! warning

    The following part of this guide is incomplete.

!!! note

    The ResourceID is typically the ID of an application resource. For example, it could be the UserID, which is typically an `int`, a `UUID` or a `string`. For use with this library, you have to cast the value to a string. The asterisk `*` can be used as a wildcard and matches all ResourceIDs for the corresponding ResourceType.This also applies when checking whether a subject has a given Permission. ResourceIDs can also include a scope, for more details, see the [Permission Design Guide](permission_design_guide.md).

Now check permission access.

```{.python continuation}
with db_factory() as db:
    RBAC.subject.assert_permission(
        subject="Ursula",
        permission=Permission(
            resource_type="user", resource_id="Ursula", action="view"
        ),
        db=db,
    )
    RBAC.subject.assert_permission(
        subject="Ursula",
        permission=Permission(
            resource_type="user", resource_id="Alex", action="view"
        ),
        db=db,
    )
```

```{.python continuation}
from rbac import RBACNotGrantedError
with db_factory() as db:
    RBAC.subject.assert_permission(
        subject="Ursula",
        permission=Permission(
            resource_type="user", resource_id="Ursula", action="edit"
        ),
        db=db,
    )
    try:
        RBAC.subject.assert_permission(
            subject="Ursula",
            permission=Permission(
                resource_type="user", resource_id="Alex", action="edit"
            ),
            db=db,
        )
    except RBACNotGrantedError as err:
        # Raises because the user 'Ursula' has not the required Permission
        ...
```

```{.python continuation}
with db_factory() as db:
    RBAC.subject.assert_permission(
        subject="Alex",
        permission=Permission(
            resource_type="user", resource_id="Ursula", action="edit"
        ),
        db=db,
    )
```

Some applications require Subject-specific permissions.
For each Subject, a dedicated Role is created to store Subject-specific Permissions.
These Roles are then assigned alongside the shared `user` and `admin` Roles.

```{.python continuation}
with db_factory() as db:
    RBAC.role.create(role="user[Alex]", db=db)
    RBAC.role.create(role="user[Ursula]", db=db)

    RBAC.subject.assign_role(subject="Alex", role="user[Alex]", db=db)
    RBAC.subject.assign_role(subject="Ursula", role="user[Ursula]", db=db)

    db.commit()
```

```py
with db_factory() as db:
    RBAC.role.grant_permission(
        role="user[Alex]",
        permission=Permission(
            resource_type="user", resource_id="Alex", action="edit"

        ),
        db=db,
    )
    RBAC.role.grant_permission(
        role="user[Ursula]",
        permission=Permission(
            resource_type="user", resource_id="Ursula", action="edit"
        ),
        db=db,
    )

    db.commit()
```
