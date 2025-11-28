import pytest
from pypermission.models import Permission
from pypermission.exc import ERR_STR_EMPTY, PyPermissionError
from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from sqlalchemy.orm import Session

################################################################################
#### Test SubjectService
################################################################################

# ------------------------------- empty_subject --------------------------------


def test_create__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.create(subject="", db=db)

    assert ERR_STR_EMPTY.subject == err.value.message


def test_delete__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.delete(subject="", db=db)
    assert ERR_STR_EMPTY.subject == err.value.message


def test_assign_role__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.assign_role(subject="", role="admin", db=db)

    assert ERR_STR_EMPTY.subject == err.value.message


def test_deassign_role__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject="", role="admin", db=db)

    assert ERR_STR_EMPTY.subject == err.value.message


def test_roles__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.roles(subject="", db=db)

    assert ERR_STR_EMPTY.subject == err.value.message


def test_assert_permission__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.assert_permission(
            subject="",
            permission=Permission(
                resource_type="event", resource_id="*", action="view"
            ),
            db=db,
        )
    assert ERR_STR_EMPTY.subject == err.value.message


def test_check_permission__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.check_permission(
            subject="",
            permission=Permission(
                resource_type="event", resource_id="*", action="view"
            ),
            db=db,
        )
    assert ERR_STR_EMPTY.subject == err.value.message


def test_permissions__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.permissions(subject="", db=db)

    assert ERR_STR_EMPTY.subject == err.value.message


def test_policies__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.policies(subject="", db=db)

    assert ERR_STR_EMPTY.subject == err.value.message


def test_actions_on_resource__empty_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.actions_on_resource(
            subject="", resource_type="event", resource_id="*", db=db
        )
    assert ERR_STR_EMPTY.subject == err.value.message
