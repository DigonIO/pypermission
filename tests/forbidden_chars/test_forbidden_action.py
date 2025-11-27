import pytest
from pypermission.models import Permission
from pypermission.exc import ERR_STR_CHARS, PyPermissionError

################################################################################
#### Test Permission
################################################################################


def test_permission__empty_action() -> None:
    with pytest.raises(PyPermissionError) as err:
        _p = Permission(resource_type="event", resource_id="", action="")
    assert ERR_STR_CHARS.empty_action == err.value.message
