import pytest
from pypermission.models import Permission, Policy
from pypermission.exc import PyPermissionError, ERR_MSG

################################################################################
#### Test Policy
################################################################################


def test_policy__empty_role() -> None:
    permission = Permission(resource_type="admin", resource_id="", action="edit")
    with pytest.raises(PyPermissionError) as err:
        Policy(role="", permission=permission)
    assert ERR_MSG.empty_role == err.value.message


@pytest.mark.parametrize(
    "role, resource_type, resource_id, action",
    [
        ("admin", "group", "18", "read"),
        ("admin", "event", "18", "edit"),
        ("admin", "event", "19", "read"),
        ("admin", "event", "", "read"),
        ("owner", "group", "18", "read"),
        ("owner", "event", "18", "edit"),
        ("owner", "event", "19", "read"),
        ("owner", "event", "", "read"),
    ],
)
def test_policy__eq(
    *, role: str, resource_type: str, resource_id: str, action: str
) -> None:
    perm = Permission(
        resource_type=resource_type, resource_id=resource_id, action=action
    )
    p1 = Policy(role=role, permission=perm)
    p2 = Policy(role=role, permission=perm)
    assert p1 == p2
    assert p2 == p1
    assert not (p1 != p2)
    assert not (p2 != p1)


@pytest.mark.parametrize(
    "role, resource_type, resource_id, action",
    [
        ("admin", "event", "18", "read"),
        ("admin", "group", "18", "read"),
        ("admin", "event", "18", "edit"),
        ("admin", "event", "19", "read"),
        ("admin", "event", "", "read"),
        ("owner", "group", "18", "read"),
        ("owner", "event", "18", "edit"),
        ("owner", "event", "19", "read"),
        ("owner", "event", "", "read"),
    ],
)
def test_policy__neq(
    *, role: str, resource_type: str, resource_id: str, action: str
) -> None:
    p1 = Policy(
        role="owner",
        permission=Permission(resource_type="event", resource_id="18", action="read"),
    )
    p2 = Policy(
        role=role,
        permission=Permission(
            resource_type=resource_type, resource_id=resource_id, action=action
        ),
    )
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