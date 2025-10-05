# Python RBAC with SQLAlchemy

## Features

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
