import pytest
from pypermission.models import Permission
from pypermission.exc import PyPermissionError, ERR_MSG


################################################################################
#### Test Permission
################################################################################


@pytest.mark.parametrize(
    "resource_type, resource_id, action, str_representation",
    [
        ("event", "18", "read", "event[18]:read"),
        ("group", "", "write", "group:write"),
    ],
)
def test_permission__str(
    *, resource_type: str, resource_id: str, action: str, str_representation: str
) -> None:
    p = Permission(resource_type=resource_type, resource_id=resource_id, action=action)
    assert str(p) == str_representation


@pytest.mark.parametrize(
    "resource_type, resource_id, action",
    [
        ("group", "18", "read"),
        ("event", "18", "edit"),
        ("event", "19", "read"),
        ("event", "", "read"),
    ],
)
def test_permission__eq(*, resource_type: str, resource_id: str, action: str) -> None:
    p1 = Permission(resource_type=resource_type, resource_id=resource_id, action=action)
    p2 = Permission(resource_type=resource_type, resource_id=resource_id, action=action)
    assert p1 == p2
    assert p2 == p1
    assert not (p1 != p2)
    assert not (p2 != p1)


@pytest.mark.parametrize(
    "resource_type, resource_id, action",
    [
        ("group", "18", "read"),
        ("event", "18", "edit"),
        ("event", "19", "read"),
        ("event", "", "read"),
    ],
)
def test_permission__neq(*, resource_type: str, resource_id: str, action: str) -> None:
    p1 = Permission(resource_type="event", resource_id="18", action="read")
    p2 = Permission(resource_type=resource_type, resource_id=resource_id, action=action)

    assert not (p1 == p2)
    assert not (p2 == p1)
    assert p1 != p2
    assert p2 != p1

    other: object
    for other in [  # pyright: ignore[reportUnknownVariableType]
        None,
        True,
        False,
        6,
        -3.1,
        "",
        "5",
        [],
        {},
        set(),
        tuple(),
        object(),
    ]:
        assert not (p2 == other)
        assert not (other == p2)

        assert other != p2
        assert p2 != other


def test_permission__empty_resource_type() -> None:
    with pytest.raises(PyPermissionError) as err:
        _p = Permission(resource_type="", resource_id="", action="edit")
    assert ERR_MSG.empty_resource_type == err.value.message


def test_permission__empty_action() -> None:
    with pytest.raises(PyPermissionError) as err:
        _p = Permission(resource_type="event", resource_id="", action="")
    assert ERR_MSG.empty_action == err.value.message
