import pytest

from pypermission.exc import ERR_STR_EMPTY, PyPermissionError
from pypermission.models import Permission

################################################################################
#### Test Permission
################################################################################


def test_permission__empty_action() -> None:
    with pytest.raises(PyPermissionError) as err:
        _p = Permission(resource_type="event", resource_id="", action="")
    assert ERR_STR_EMPTY.action == err.value.message
