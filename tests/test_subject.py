import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.exc import PyPermissionError

################################################################################
#### Test subject creation
################################################################################


def test_create__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)


def test_create__duplicate(*, db: Session) -> None:
    SS.create(subject="Alex", db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.create(subject="Alex", db=db)

    assert "The Subject 'Alex' already exists!" == err.value.message


################################################################################
#### Test subject delete
################################################################################


def test_delete__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.delete(subject="Alex", db=db)


def test_delete__unknown(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.delete(subject="Alex", db=db)
    assert "The Subject 'Alex' does not exists!" == err.value.message


################################################################################
#### Test subject list
################################################################################


def test_list__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.create(subject="Max", db=db)

    assert ("Alex", "Max") == SS.list(db=db)


################################################################################
#### Test subject assign_role
################################################################################


def test_assign_role__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    RS.create(role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)


# TODO Test unknown subject and unknown role

################################################################################
#### Test subject deassign_role
################################################################################


def test_deassign_role__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    RS.create(role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    SS.deassign_role(subject="Alex", role="admin", db=db)


# TODO Test unknown subject and unknown role

################################################################################
#### Test subject roles
################################################################################


def test_roles__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)

    RS.create(role="user", db=db)
    RS.create(role="premium", db=db)

    SS.assign_role(subject="Alex", role="user", db=db)
    SS.assign_role(subject="Alex", role="premium", db=db)

    assert ("user", "premium") == SS.roles(subject="Alex", db=db)


def test_roles__unknown(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.roles(subject="Alex", db=db)
    assert "The Subject 'Alex' does not exist!" == err.value.message
