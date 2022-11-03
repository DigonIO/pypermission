import pytest
from deepdiff import DeepDiff

from .helpers import SUBJECT_PERMISSIONS_ENUM, SUBJECT_PERMISSIONS_STR, USER
from .conftest import URL_SQLITE, URL_MARIADB


@pytest.mark.parametrize(
    "expected_permissions, to_str",
    [
        (SUBJECT_PERMISSIONS_ENUM, False),
        (SUBJECT_PERMISSIONS_STR, True),
    ],
)
def test_subject_get_permissions_serial(
    expected_permissions, to_str, serial_authority_get_permissions
):
    auth = serial_authority_get_permissions
    result = auth.subject_get_permissions(sid=USER, to_str=to_str)
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
    "expected_permissions, to_str",
    [
        (SUBJECT_PERMISSIONS_ENUM, False),
        (SUBJECT_PERMISSIONS_STR, True),
    ],
)
def test_subject_get_permissions_sql(expected_permissions, to_str, sql_authority_get_permissions):
    auth = sql_authority_get_permissions
    result = auth.subject_get_permissions(sid=USER, to_str=to_str)
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}
