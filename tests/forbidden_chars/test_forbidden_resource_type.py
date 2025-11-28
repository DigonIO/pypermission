import pytest
from pypermission.models import Permission
from pypermission.exc import ERR_STR_EMPTY, PyPermissionError
from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from sqlalchemy.orm import Session

################################################################################
#### Test Permission
################################################################################


def test_permission__empty_resource_type() -> None:
    with pytest.raises(PyPermissionError) as err:
        _p = Permission(resource_type="", resource_id="", action="edit")
    assert ERR_STR_EMPTY.resource_type == err.value.message


################################################################################
#### Test RoleService
################################################################################


def test_role_actions_on_resource__empty_resource_type(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.actions_on_resource(
            role="unknown", resource_type="", resource_id="123", db=db
        )

    assert ERR_STR_EMPTY.resource_type == err.value.message


################################################################################
#### Test SubjectService
################################################################################


def test_subject_actions_on_resource__empty_resource_type(db: Session) -> None:
    subject = "Uwe"
    with pytest.raises(PyPermissionError) as err:
        SS.actions_on_resource(
            subject=subject, resource_type="", resource_id="*", db=db
        )
    assert ERR_STR_EMPTY.resource_type == err.value.message
