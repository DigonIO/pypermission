---
description: "PyPermission - The python RBAC library. Step-by-step examples show how to initialize the database, create roles, assign permissions, and check access."
---

# PyPermission - Quick Start

!!! info

    This quick start tutorial is intended for developers who already have experience with RBAC systems. For anyone using RBAC in their own project for the first time, we recommend going through the documentation in the following order:

    1. [Definitions](./definitions.md)
    2. [Permission design guide](./permission_design_guide.md)
    3. [Implementation guide](./guide/index.md)

The `PyPermission` library can be installed directly from the PyPI repositories with:

```console
pip install PyPermission
```

For the following example we initialize an in-memory SQLite database using `SQLAlchemy` (we also provide PostgreSQL support with the `'PyPermission[postgres]'` dependency group).

```python
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:", future=True)
db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

!!! warning

    The `PyPermission` library utilizes and requires constraint checking with the `FOREIGN KEY` syntax. SQLite does not have this feature enabled by default. If you want to use SQLite, make sure your instance fulfills the [necessary prerequisites](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support) and use the provided event listener for all database connections.

    ```{.python notest}
    from pypermission import create_rbac_database_table, set_sqlite_pragma
    from sqlalchemy.event import listen

    listen(engine, "connect", set_sqlite_pragma)
    create_rbac_database_table(engine=engine)
    ```

Create the required tables in the database:

```{.python continuation}
from pypermission import create_rbac_database_table

create_rbac_database_table(engine=engine)
```

The `PyPermission` library organizes its core functionality into two main services - **RoleService** and **SubjectService**. These services are accessible through the main **RBAC** class, which provides a unified interface for managing **Roles**, **Subjects**, and **Policies**. The examples below demonstrates basic usage.

## Manage Subjects and Roles

Start by creating a `user` and an `admin` **Role**:

```{.python continuation}
from pypermission import RBAC

with db_factory() as db:
    RBAC.role.create(role="user", db=db)
    RBAC.role.create(role="admin", db=db)
    db.commit()
```

We want the `admin` **Role** to inherit all permissions of the `user` **Role**, therefore we model the `admin` **Role** as a child of the `user` **Role** in our **Role** hierarchy:

```{.python continuation}
with db_factory() as db:
    RBAC.role.add_hierarchy(
        parent_role="user",
        child_role="admin",
        db=db,
    )
    db.commit()
```

Next, create two **Subjects** - `Alex` and `Ursula` and assign the `admin` and `user` **Roles** respectively.

```{.python continuation}
with db_factory() as db:
    RBAC.subject.create(subject="Alex", db=db)
    RBAC.subject.create(subject="Ursula", db=db)

    RBAC.subject.assign_role(subject="Alex", role="admin", db=db)
    RBAC.subject.assign_role(subject="Ursula", role="user", db=db)

    db.commit()
```

## Basic Permission handling

When creating a **Permission**, using the wildcard string `"*"` for the `resource_id` specifies that all resources of the given `resource_type` and `action` can be granted via this **Permission**.

In this example, everyone with the `user` **Role** may `view` every `event` in the system. This corresponds to `Permission(resource_type="event", resource_id="*", action="view")`, representable as `"event[*]:view"`.

We also assign the `"event[*]:edit"` **Permission** to the `admin` **Role** so that the `admin` can edit any `event`.

```{.python continuation}
from pypermission import Permission

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

    db.commit()
```

!!! note "Note – ResourceIDs & Wildcards"

    **ResourceID** is typically the ID of an application resource (e.g. a User ID, an INT, a UUID...). For use with this library you must cast the value to a string.

    * The asterisk `*` is a wildcard and matches all **ResourceID**s for the corresponding **ResourceType**.
    * The same rule also applies when checking whether a subject has a given **Permission**
    * Depending on your requirements it can be helpful to indicate a scope within the **ResourceID** (e.g. "group:123"). For more details, see the [Permission Design Guide](permission_design_guide.md).

Being granted the `user` **Role**, `Ursula` can `view` `event` with ID `19` and all `event`s of the `group` with ID `123`.

```{.python continuation}
with db_factory() as db:
    assert RBAC.subject.check_permission(
        subject="Ursula",
        permission=Permission(resource_type="event", resource_id="19", action="view"),
        db=db,
    ) is True
    # or alternatively (recommended over python's assert):
    RBAC.subject.assert_permission(
        subject="Ursula",
        permission=Permission(resource_type="event", resource_id="group:123", action="view"),
        db=db,
    )
```

Confirm that `Ursula` cannot edit any event while `Alex` (as `admin`) can. See how this holds for the `event` with ID `19`:

```{.python continuation}
from pypermission import PermissionNotGrantedError

with db_factory() as db:
    try:
        RBAC.subject.assert_permission(
            subject="Ursula",
            permission=Permission(resource_type="event", resource_id="19", action="edit"),
            db=db,
        )
    except PermissionNotGrantedError as err:
        assert err.message == "Permission 'event[19]:edit' is not granted for Subject 'Ursula'!"

    RBAC.subject.assert_permission(
        subject="Alex",
        permission=Permission(resource_type="event", resource_id="19", action="edit"),
        db=db,
    )
```

## Subject‑specific roles

Create a dedicated **Role** for each **Subject** and assign it alongside the shared **Role**:

```{.python continuation}
with db_factory() as db:
    RBAC.role.create(role="user[Alex]", db=db)
    RBAC.role.create(role="user[Ursula]", db=db)

    RBAC.subject.assign_role(subject="Alex", role="user[Alex]", db=db)
    RBAC.subject.assign_role(subject="Ursula", role="user[Ursula]", db=db)

    db.commit()
```

Give `Ursula` the ability to `edit` `event` `19` only:

```{.python continuation}
with db_factory() as db:
    RBAC.role.grant_permission(
        role="user[Ursula]",
        permission=Permission(resource_type="event", resource_id="19", action="edit"),
        db=db,
    )
    db.commit()
```

Verify that Ursula can now `edit` `event` `19`:

```{.python continuation}
with db_factory() as db:
    RBAC.subject.assert_permission(
        subject="Ursula",
        permission=Permission(resource_type="event", resource_id="19", action="edit"),
        db=db,
    )
```

## Inspect roles, subjects and permissions

List current roles, subjects, and permissions:

```{.python continuation}
with db_factory() as db:
    assert set(RBAC.role.list(db=db)) == {"user", "admin", "user[Alex]", "user[Ursula]"}
    assert set(RBAC.subject.list(db=db)) == {"Alex", "Ursula"}

    # The only "regular" user is Ursula
    assert {"Ursula"} == set(
        RBAC.role.subjects(role="user", include_descendant_subjects=False, db=db)
    )

    # Alex has the admin role and his user-specific role
    assert {"admin", "user[Alex]"} == set(
        RBAC.subject.roles(subject="Alex", include_ascendant_roles=False, db=db)
    )

    # The admin role gains user permissions in addition to its directly assigned ones
    assert {
        "event[*]:edit",
        "event[*]:view",  # (permission is inherited)
    } == {str(p) for p in RBAC.role.permissions(role="admin", inherited=True, db=db)}

    # Permissions visible to Alex (admin + user[Alex])
    alex_perms = RBAC.subject.permissions(subject="Alex", db=db)
    assert {"event[*]:view", "event[*]:edit"} == {str(p) for p in alex_perms}

    # Permissions visible to Ursula (user + user[Ursula])
    ursula_perms = RBAC.subject.permissions(subject="Ursula", db=db)
    assert {"event[*]:view", "event[19]:edit"} == {str(p) for p in ursula_perms}
```

## Inspect policies and actions

Inspect **Policies** and **Actions** on a **Role**‑level:

```{.python continuation}
with db_factory() as db:
    # Policies granted to the admin role
    assert {
        "admin:event[*]:edit",
        "user:event[*]:view",  # (policy is inherited)
    } == {str(p) for p in RBAC.role.policies(role="admin", inherited=True, db=db)}

    # Available actions on a group resource for the admin role
    assert set(
        RBAC.role.actions_on_resource(
            role="admin",
            resource_type="event",
            resource_id="*",
            inherited=True,
            db=db,
        )
    ) == {"view", "edit"}
```

Inspect **Policies** and **Actions** on a **Subject**‑level:

```{.python continuation}
with db_factory() as db:
    # Policies collected from all roles assigned to Ursula
    assert {
        "user:event[*]:view",
        "user[Ursula]:event[19]:edit",
    } == {str(p) for p in RBAC.subject.policies(subject="Ursula", db=db)}

    # Actions Ursula can perform on all events
    assert set(
        RBAC.subject.actions_on_resource(
            subject="Ursula",
            resource_type="event",
            resource_id="*",
            inherited=True,
            db=db,
        )
    ) == {"view"}
```

## Delete a role, a subject, and a hierarchy entry

```{.python continuation}
with db_factory() as db:
    # Revoke a permission
    RBAC.role.revoke_permission(
        role="user[Ursula]",
        permission=Permission(
            resource_type="event", resource_id="19", action="edit"
        ),
        db=db,
    )
    # Delete a role
    RBAC.role.delete(role="user[Ursula]", db=db)
    # Remove a subject
    RBAC.subject.delete(subject="Alex", db=db)

    # Remove the admin hierarchy (admin no longer inherits from user)
    RBAC.role.remove_hierarchy(parent_role="user", child_role="admin", db=db)
    db.commit()
```
