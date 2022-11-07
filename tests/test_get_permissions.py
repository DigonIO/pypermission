import pytest
from deepdiff import DeepDiff
from pypermission.sqlalchemy import SQLAlchemyAuthority
from pypermission.serial import SerialAuthority

from .helpers import (
    SUBJECT_PERMISSIONS_NODES_EID,
    SUBJECT_PERMISSIONS_STR_STR,
    USER,
)
from .conftest import URL_SQLITE, URL_MARIADB


@pytest.mark.parametrize(
    "expected_permissions, serialize",
    [
        (SUBJECT_PERMISSIONS_NODES_EID, False),
        (SUBJECT_PERMISSIONS_STR_STR, True),
    ],
)
def test_subject_get_permissions_serial(
    expected_permissions, serialize, serial_authority_get_permissions
):
    auth: SerialAuthority = serial_authority_get_permissions
    result = auth.subject_get_permissions(sid=USER, serialize=serialize)
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}


@pytest.mark.skip()
@pytest.mark.parametrize(
    "sql_authority_get_permissions",
    (
        URL_SQLITE,
        URL_MARIADB,
    ),
    indirect=["sql_authority_get_permissions"],
)
@pytest.mark.parametrize(
    "expected_permissions, serialize",
    [
        (SUBJECT_PERMISSIONS_NODES_EID, False),
        (SUBJECT_PERMISSIONS_STR_STR, True),
    ],
)
def test_subject_get_permissions_sql(
    expected_permissions, serialize, sql_authority_get_permissions
):
    auth: SQLAlchemyAuthority = sql_authority_get_permissions
    result = auth.subject_get_permissions(sid=USER, serialize=serialize)
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}
