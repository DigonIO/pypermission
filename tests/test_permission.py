import pytest
from pypermission.models import Permission
from pypermission.exc import PyPermissionError, ERR_MSG


################################################################################
#### Test Permission
################################################################################


@pytest.mark.parametrize(
    "resource_type,resource_id,action, str_representation",
    [
        ("user", "18", "read", "user[18]:read"),
        ("admin", "", "write", "admin:write"),
    ],
)
def test_permission__str(
    *, resource_type: str, resource_id: str, action: str, str_representation: str
) -> None:
    p = Permission(resource_type=resource_type, resource_id=resource_id, action=action)
    assert str(p) == str_representation


def test_permission__empty_resource_type() -> None:
    with pytest.raises(PyPermissionError) as err:
        _p = Permission(resource_type="", resource_id="", action="view")
    assert ERR_MSG.empty_resource_type == err.value.message


def test_permission__empty_action() -> None:
    with pytest.raises(PyPermissionError) as err:
        _p = Permission(resource_type="user", resource_id="", action="")
    assert ERR_MSG.empty_action == err.value.message
