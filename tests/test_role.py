import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService
from pypermission.exc import PyPermissionError

################################################################################
#### Test role creation
################################################################################


def test_create_role__success(db: Session) -> None:
    RoleService.create(role="Alex", db=db)


def test_create_role__duplicate(*, db: Session) -> None:
    RoleService.create(role="Alex", db=db)
    with pytest.raises(PyPermissionError):
        RoleService.create(role="Alex", db=db)


################################################################################
#### Test role deletion
################################################################################


def test_delete_role__success(*, db: Session) -> None:
    RoleService.create(role="Alex", db=db)
    RoleService.delete(role="Alex", db=db)


def test_delete_role__unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError):
        RoleService.delete(role="Alex", db=db)


################################################################################
#### Test role list
################################################################################


def test_list__success(*, db: Session) -> None:
    assert RoleService.list(db=db) == tuple()
    RoleService.create(role="Alex", db=db)
    assert RoleService.list(db=db) == ("Alex",)
    RoleService.create(role="Max", db=db)
    assert RoleService.list(db=db) == ("Alex", "Max")
