# rbac - Quick Start

To get started with a basic RBAC example, first set up an SQLAlchemy environment.
In this example, we use an in-memory SQLite database (you can also use PostgreSQL via `psycopg`). After setting up the database, we need to create the required RBAC tables.

```python
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:", future=True)
db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

```{.python continuation}
from rbac import create_rbac_database_table

create_rbac_database_table(engine=engine)
```

rbac organizes its core functionality into three main services:
`RoleService`, `SubjectService`, and `PolicyService`.
These services are accessible through the main RBAC class, which provides a unified interface for managing Roles, Subjects, and Policies. The examples below demonstrates basic usage.

Create a _user_ and an _admin_ Role and create a relation such that the _admin_ Role inherits all permissions of the _user_ Role and potential ascendant Permissions.

```{.python continuation}
from rbac import RBAC

with db_factory() as db:
    RBAC.role.create(role="user", db=db)
    RBAC.role.create(role="admin", db=db)

    RBAC.role.add_hierarchy(
        parent_role="user",
        child_role="admin",
        db=db,
    )

    db.commit()
```

Next, create two Subjects: _Alex_ and _Max_.
For each Subject, a dedicated Role is created to store Subject-specific Permissions.
These Roles are then assigned alongside the shared _user_ and _admin_ Roles.

```{.python continuation}
with db_factory() as db:
    RBAC.subject.create(subject="Alex", db=db)
    RBAC.subject.create(subject="Max", db=db)

    RBAC.role.create(role="user[Alex]", db=db)
    RBAC.role.create(role="user[Max]", db=db)

    RBAC.subject.assign_role(subject="Alex", role="user[Alex]", db=db)
    RBAC.subject.assign_role(subject="Max", role="user[Max]", db=db)

    RBAC.subject.assign_role(subject="Alex", role="admin", db=db)
    RBAC.subject.assign_role(subject="Max", role="user", db=db)

    db.commit()
```

Next, assign Permissions to the Roles. In this simple example, we define who can edit which user. Every user with the Role _user_ is allowed to view all users, but can only edit their own account. Users with the Role _admin_ are allowed to edit any user.

```{.python continuation}
from rbac import Permission

with db_factory() as db:
    RBAC.role.grant_permission(
        role="user",
        permission=Permission(
            resource_type="user", resource_id="*", action="view"
        ),
        db=db,
    )
    RBAC.role.grant_permission(
        role="admin",
        permission=Permission(
            resource_type="user", resource_id="*", action="edit"
        ),
        db=db,
    )

    RBAC.role.grant_permission(
        role="user[Alex]",
        permission=Permission(
            resource_type="user", resource_id="Alex", action="edit"

        ),
        db=db,
    )
    RBAC.role.grant_permission(
        role="user[Max]",
        permission=Permission(
            resource_type="user", resource_id="Max", action="edit"
        ),
        db=db,
    )

    db.commit()
```

!!! note

    The ResourceID is typically the ID of an application resource. For example, it could be the UserID, which is typically an `int`, a `UUID` or a `string`. For use with this library, you have to cast the value to a string. The asterisk `*` can be used as a wildcard and matches all ResourceIDs for the corresponding ResourceType.This also applies when checking whether a subject has a given Permission. ResourceIDs can also include a scope, for more details, see the [Permission Design Guide](permission_design_guide.md).

Now check permission access.

!!! warning

    The following part of this guide is incomplete.

```{.python continuation}
with db_factory() as db:
    RBAC.subject.assert_permission(
        subject="Max",
        permission=Permission(
            resource_type="user", resource_id="Max", action="view"
        ),
        db=db,
    )
    RBAC.subject.assert_permission(
        subject="Max",
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
        subject="Max",
        permission=Permission(
            resource_type="user", resource_id="Max", action="edit"
        ),
        db=db,
    )
    try:
        RBAC.subject.assert_permission(
            subject="Max",
            permission=Permission(
                resource_type="user", resource_id="Alex", action="edit"
            ),
            db=db,
        )
    except RBACNotGrantedError as err:
        # Raises because the user 'Max' has not the required Permission
        ...
```

```{.python continuation}
with db_factory() as db:
    RBAC.subject.assert_permission(
        subject="Alex",
        permission=Permission(
            resource_type="user", resource_id="Max", action="edit"
        ),
        db=db,
    )

```
