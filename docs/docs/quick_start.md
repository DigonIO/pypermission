# Quick Start

To get started with a basic RBAC example, first set up a SQLAlchemy environment.
In this example, we use an in-memory SQLite database (you can also use PostgreSQL via `psycopg`). After setting up the database, we need to create the required RBAC tables.

``` python
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from pypermission import create_rbac_database_table

URL = "sqlite:///:memory:"
engine = create_engine(URL, future=True)
db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

create_rbac_database_table(engine=engine)
```

pypermission organizes its core functionality into three main services:
`RoleService`, `SubjectService`, and `PolicyService`.
These services are accessible through the main RBAC class, which provides a unified interface for managing Roles, Subjects, and Policies. The examples below demonstrates basic usage.

Create a _user_ and an _admin_ Role create a relation so that the _admin_ Role inherits all permissions of the _user_ Role and potential ascendant Permissions.

``` python
from pypermission import RBAC

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

``` python
with db_factory() as db:
    RBAC.subject.create(subject="Alex", db=db)
    RBAC.subject.create(subject="Max", db=db)

    RBAC.role.create(role="user[Alex]", db=db)
    RBAC.role.create(role="user[Max]", db=db)

    RBAC.subject.assign_role(role="user[Alex]", subject="Alex", db=db)
    RBAC.subject.assign_role(role="user[Max]", subject="Max", db=db)

    RBAC.subject.assign_role(role="admin", subject="Alex", db=db)
    RBAC.subject.assign_role(role="user", subject="Max", db=db)

    db.commit()
```

Next, assign Permissions to the Roles. In this simple example, we define who can edit which user. Every user with the _user_ Role is allowed to view all users, but can only edit their own account. Users with the _admin_ Role are allowed to edit any user.

``` python
from pypermission import Policy, Permission

with db_factory() as db:
    RBAC.policy.create(
        policy=Policy(
            role="user",
            permission=Permission(
                resource_type="user", resource_id="*", action="view"
            ),
        ),
        db=db,
    )
    RBAC.policy.create(
        policy=Policy(
            role="admin",
            permission=Permission(
                resource_type="user", resource_id="*", action="edit"
            ),
        ),
        db=db,
    )

    RBAC.policy.create(
        policy=Policy(
            role="user[Alex]",",
            permission=Permission(
                resource_type="user", resource_id="Alex", action="edit"
            ),
        ),
        db=db,
    )
    RBAC.policy.create(
        policy=Policy(
            role="user[Max]",",
            permission=Permission(
                resource_type="user", resource_id="Max", action="edit"
            ),
        ),
        db=db,
    )

    db.commit()
```

!!! note

    The ResourceID is typically the ID of an application resource. For example, it could be the UserID, which is often an `int` or a `UUID` (`strings` are also possible). The asterisk `*` can be used as a wildcard and matches all ResourceIDs for the corresponding ResourceType.This also applies when checking whether a subject has a given Permission. ResourceIDs can also include a scope, for more details, see the [Permission Design Guide](permission_design_guide.md).

No check permission access.

``` python
with db_factory() as db:
    result: bool = RBAC.subject.check_permission(
        policy=Policy(
            subject="Max",
            permission=Permission(
                resource_type="user", resource_id="Max", action="view"
            ),
        ),
        db=db,
    )
    result: bool = RBAC.subject.check_permission(
        policy=Policy(
            subject="Max",
            permission=Permission(
                resource_type="user", resource_id="Alex", action="view"
            ),
        ),
        db=db,
    )

    db.commit()
```

True
True

``` python
with db_factory() as db:
    result: bool = RBAC.subject.check_permission(
        policy=Policy(
            subject="Max",
            permission=Permission(
                resource_type="user", resource_id="Max", action="edit"
            ),
        ),
        db=db,
    )
    result: bool = RBAC.subject.check_permission(
        policy=Policy(
            subject="Max",
            permission=Permission(
                resource_type="user", resource_id="Alex", action="edit"
            ),
        ),
        db=db,
    )

    db.commit()
```

True
False

``` python
with db_factory() as db:
    result: bool = RBAC.subject.check_permission(
        policy=Policy(
            subject="Alex",
            permission=Permission(
                resource_type="user", resource_id="Max", action="edit"
            ),
        ),
        db=db,
    )

    db.commit()
```

True

!!! tip
    The `RBAC.subject.check_permission` returns a bool. There is also the `RBAC.subject.assert_permission` function. It raises the `pypermission.exc.PyPermissionNotGrantedError` error if the passen is not granted to the subject.
