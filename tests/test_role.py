import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService
from pypermission.exc import PyPermissionError

################################################################################
#### Test role creation
################################################################################


def test_sqlite_create_role__success(sqlite_db: Session):
    _create_role__success(db=sqlite_db)


def test_postgres_create_role__success(psql_db: Session):
    _create_role__success(db=psql_db)


def _create_role__success(*, db: Session) -> None:
    RoleService.create(role="Alex", db=db)


def test_sqlite_create_role__duplicate(sqlite_db: Session):
    _create_role__duplicate(db=sqlite_db)


def test_postgres_create_role__duplicate(psql_db: Session):
    _create_role__duplicate(db=psql_db)


def _create_role__duplicate(*, db: Session) -> None:
    RoleService.create(role="Alex", db=db)
    with pytest.raises(PyPermissionError):
        RoleService.create(role="Alex", db=db)


################################################################################
#### Test role deletion
################################################################################


def test_sqlite_delete_role__success(sqlite_db: Session):
    _delete_role__success(db=sqlite_db)


def test_postgres_delete_role__success(psql_db: Session):
    _delete_role__success(db=psql_db)


def _delete_role__success(*, db: Session) -> None:
    RoleService.create(role="Alex", db=db)
    RoleService.delete(role="Alex", db=db)


def test_sqlite_delete_role__unknown(sqlite_db: Session):
    _delete_role__unknown(db=sqlite_db)


def test_postgres_delete_role__unknown(psql_db: Session):
    _delete_role__unknown(db=psql_db)


def _delete_role__unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError):
        RoleService.delete(role="Alex", db=db)
