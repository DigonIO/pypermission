import pytest
from deepdiff import DeepDiff
from pypermission.sqlalchemy import SQLAlchemyAuthority
from pypermission.serial import SerialAuthority

from .helpers import (
    SUBJECT_PERMISSIONS_NODES_EID,
    SUBJECT_PERMISSIONS_STR_EID,
    SUBJECT_PERMISSIONS_NODES_STR,
    SUBJECT_PERMISSIONS_STR_STR,
    USER,
)
from .conftest import URL_SQLITE, URL_MARIADB


@pytest.mark.parametrize(
    "expected_permissions, serialize_nodes, serialize_eid",
    [
        (SUBJECT_PERMISSIONS_NODES_EID, False, False),
        (SUBJECT_PERMISSIONS_STR_EID, True, False),
        (SUBJECT_PERMISSIONS_NODES_STR, False, True),
        (SUBJECT_PERMISSIONS_STR_STR, True, True),
    ],
)
def test_subject_get_permissions_serial(
    expected_permissions, serialize_nodes, serialize_eid, serial_authority_get_permissions
):
    auth: SerialAuthority = serial_authority_get_permissions
    result = auth.subject_get_permissions(
        sid=USER, serialize_nodes=serialize_nodes, serialize_eid=serialize_eid
    )
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}


@pytest.mark.parametrize(
    "sql_authority_get_permissions",
    (
        URL_SQLITE,
        URL_MARIADB,
    ),
    indirect=["sql_authority_get_permissions"],
)
@pytest.mark.parametrize(
    "expected_permissions, serialize_nodes, serialize_eid",
    [
        (SUBJECT_PERMISSIONS_NODES_EID, False, False),
        (SUBJECT_PERMISSIONS_STR_EID, True, False),
        (SUBJECT_PERMISSIONS_NODES_STR, False, True),
        (SUBJECT_PERMISSIONS_STR_STR, True, True),
    ],
)
def test_subject_get_permissions_sql(
    expected_permissions, serialize_nodes, serialize_eid, sql_authority_get_permissions
):
    auth: SQLAlchemyAuthority = sql_authority_get_permissions
    result = auth.subject_get_permissions(
        sid=USER, serialize_nodes=serialize_nodes, serialize_eid=serialize_eid
    )
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}
