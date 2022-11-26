import pytest
from deepdiff import DeepDiff

from pypermission.serial import SerialAuthority

from ..helpers import (
    GROUP_INFO_NODES_EID,
    GROUP_INFO_STR_STR,
    SUBJECT_INFO_NODES_EID,
    SUBJECT_INFO_STR_STR,
    USER,
    USER_GROUP,
)


@pytest.mark.parametrize(
    "expected_permissions, serialize",
    [
        (SUBJECT_INFO_NODES_EID, False),
        (SUBJECT_INFO_STR_STR, True),
    ],
)
def test_subject_get_info_serial(
    expected_permissions, serialize, serial_authority_get_info_subject
):
    auth: SerialAuthority = serial_authority_get_info_subject
    result = auth.subject_get_info(sid=USER, serialize=serialize)
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}


@pytest.mark.parametrize(
    "expected_permissions, serialize",
    [
        (GROUP_INFO_NODES_EID, False),
        (GROUP_INFO_STR_STR, True),
    ],
)
def test_role_get_info_serial(expected_permissions, serialize, serial_authority_get_info_role):
    auth: SerialAuthority = serial_authority_get_info_role
    result = auth.role_get_info(rid=USER_GROUP, serialize=serialize)
    assert DeepDiff(result, expected_permissions, ignore_order=True) == {}
