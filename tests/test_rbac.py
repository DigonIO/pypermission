import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.event import listen

from pypermission import RBAC, Permission, create_rbac_database_table, set_sqlite_pragma
from pypermission.service.role import RoleService
from pypermission.service.subject import SubjectService
from pypermission.service.role import RoleService as RS
from pypermission.exc import PyPermissionError, ERR_MSG


def test_rbac_service_imports() -> None:
    assert RBAC.role == RoleService
    assert RBAC.subject == SubjectService


def test_frozen_attributes() -> None:
    with pytest.raises(AttributeError) as err:
        RBAC.role = RoleService  # type: ignore
    assert (ERR_MSG.frozen_attributes_cannot_be_modified,) == err.value.args

    with pytest.raises(AttributeError) as err:
        RBAC.role.create = RoleService.create  # type: ignore
    assert (ERR_MSG.frozen_attributes_cannot_be_modified,) == err.value.args

    with pytest.raises(AttributeError) as err:
        RBAC.subject = SubjectService  # type: ignore
    assert (ERR_MSG.frozen_attributes_cannot_be_modified,) == err.value.args

    with pytest.raises(AttributeError) as err:
        RBAC.subject.create = SubjectService.create  # type: ignore
    assert (ERR_MSG.frozen_attributes_cannot_be_modified,) == err.value.args

    # But this should be ok:
    RBAC.new_attribute = None  # type: ignore


@pytest.mark.parametrize("foreign_keys_enabled", [True, False])
def test_rbac_sqlite_pragma_foreign_keys(foreign_keys_enabled: bool) -> None:
    """Test the code we are usually running in our db fixture."""
    engine = create_engine("sqlite:///:memory:", future=True)
    role = "admin"
    permission = Permission(resource_type="event", resource_id="*", action="edit")
    try:
        db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        if foreign_keys_enabled:
            listen(
                engine, "connect", set_sqlite_pragma
            )  # needed for foreign key constraints (sqlite only)
            create_rbac_database_table(engine=engine)

            with db_factory() as db, pytest.raises(PyPermissionError) as err:
                RS.grant_permission(
                    role=role,
                    permission=permission,
                    db=db,
                )
            assert ERR_MSG.non_existent_role.format(role=role) == err.value.message
        else:
            with pytest.raises(PyPermissionError) as err:
                create_rbac_database_table(engine=engine)
            assert ERR_MSG.foreign_keys_pragma_not_set == err.value.message
            # NOTE: consider checking for the pragma in other relevant RBAC methods,
            # specifically have a look at how missing foreign key support impacts the following tests:
            # - test_delete_cleanup[sqlite]
            # - test_grant_permission__unknown_role[sqlite]
            # - test_assign_role__unknown_subject[sqlite]
            # - test_assign_role__unknown_role[sqlite]
    finally:
        engine.dispose()
