import pytest
from deepdiff import DeepDiff
from pypermission.sqlalchemy import SQLAlchemyAuthority

from ..helpers import (
    SUBJECT_INFO_NODES_EID,
    SUBJECT_INFO_STR_STR,
    GROUP_INFO_NODES_EID,
    GROUP_INFO_STR_STR,
    USER,
    USER_GROUP,
    URL_SQLITE,
    URL_MARIADB,
)


@pytest.mark.parametrize(
    "sql_authority_get_info_subject",
    (
        URL_SQLITE,
        URL_MARIADB,
    ),
    indirect=["sql_authority_get_info_subject"],
)
@pytest.mark.parametrize(
    "expected_permissions, serialize",
    [
        (SUBJECT_INFO_NODES_EID, False),
        (SUBJECT_INFO_STR_STR, True),
    ],
)
def test_subject_get_info_sql(expected_permissions, serialize, sql_authority_get_info_subject):
    auth: SQLAlchemyAuthority = sql_authority_get_info_subject
    result = auth.subject_get_info(sid=USER, serialize=serialize)
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}


@pytest.mark.parametrize(
    "sql_authority_get_info_role",
    (
        URL_SQLITE,
        URL_MARIADB,
    ),
    indirect=["sql_authority_get_info_role"],
)
@pytest.mark.parametrize(
    "expected_permissions, serialize",
    [
        (GROUP_INFO_NODES_EID, False),
        (GROUP_INFO_STR_STR, True),
    ],
)
def test_role_get_info_sql(expected_permissions, serialize, sql_authority_get_info_role):
    auth: SQLAlchemyAuthority = sql_authority_get_info_role
    result = auth.role_get_info(rid=USER_GROUP, serialize=serialize)
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}
