# docs/conftest.py
import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from pypermission.models import PyPermissionORM, Permission
from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS


@pytest.fixture()
def URL_TO_DB(tmp_path: Path) -> str:
    """SQLite DB with a small RBAC hierarchy for the docs examples."""
    db_file = tmp_path / "auditing_guide.sqlite"
    url = f"sqlite:///{db_file}"

    engine = create_engine(url, future=True)
    # Fresh schema each time the fixture is used
    PyPermissionORM.metadata.drop_all(engine)
    PyPermissionORM.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # Seed a simple hierarchy like in test_util_plot / test_util_role
    with SessionLocal.begin() as db:
        # Roles
        RS.create(role="Mod", db=db)
        RS.create(role="Admin", db=db)
        RS.create(role="User[Alex]", db=db)
        RS.create(role="User[Max]", db=db)

        # Subjects
        SS.create(subject="Alex", db=db)
        SS.create(subject="Max", db=db)

        # Assign roles to subjects
        SS.assign_role(subject="Alex", role="Admin", db=db)
        SS.assign_role(subject="Alex", role="User[Alex]", db=db)
        SS.assign_role(subject="Max", role="Mod", db=db)
        SS.assign_role(subject="Max", role="User[Max]", db=db)

        # Permissions
        view_all = Permission(resource_type="User", resource_id="*", action="view")
        edit_all = Permission(resource_type="User", resource_id="*", action="edit")

        view_alex = Permission(resource_type="User", resource_id="Alex", action="view")
        view_max = Permission(resource_type="User", resource_id="Max", action="view")
        edit_alex = Permission(resource_type="User", resource_id="Alex", action="edit")
        edit_max = Permission(resource_type="User", resource_id="Max", action="edit")

        RS.grant_permission(role="Mod", permission=view_all, db=db)
        RS.grant_permission(role="Admin", permission=view_all, db=db)
        RS.grant_permission(role="Admin", permission=edit_all, db=db)

        RS.grant_permission(role="User[Alex]", permission=view_alex, db=db)
        RS.grant_permission(role="User[Max]", permission=view_max, db=db)
        RS.grant_permission(role="User[Alex]", permission=edit_alex, db=db)
        RS.grant_permission(role="User[Max]", permission=edit_max, db=db)

    engine.dispose()
    return url
