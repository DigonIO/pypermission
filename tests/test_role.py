import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.exc import PyPermissionError

################################################################################
#### Test role creation
################################################################################


def test_create_role__success(db: Session) -> None:
    RS.create(role="user", db=db)


def test_create_role__duplicate(*, db: Session) -> None:
    RS.create(role="user", db=db)
    with pytest.raises(PyPermissionError):
        RS.create(role="user", db=db)


################################################################################
#### Test role deletion
################################################################################


def test_delete_role__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.delete(role="user", db=db)


def test_delete_role__unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError):
        RS.delete(role="user", db=db)


################################################################################
#### Test role list
################################################################################


def test_list__success(*, db: Session) -> None:
    assert RS.list(db=db) == tuple()
    RS.create(role="user", db=db)
    assert RS.list(db=db) == ("user",)
    RS.create(role="admin", db=db)
    assert RS.list(db=db) == ("user", "admin")


################################################################################
#### Test role add_hierarchy
################################################################################


def test_add_hierarchy__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)


def test_add_hierarchy__equal(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="user", db=db)

    assert "Both roles 'user' must not be the same!" == err.value.message


def test_add_hierarchy__loop(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="admin", child_role="user", db=db)

    assert "The desired hierarchy would generate a loop!" == err.value.message


def test_add_hierarchy__exists(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    assert "The hierarchy 'user' -> 'admin' exists!" == err.value.message


def test_add_hierarchy__two_unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    assert "Roles 'user' and 'admin' do not exist!" == err.value.message


@pytest.mark.parametrize(
    "known_role, unknown_role",
    [
        ("user", "admin"),
        ("admin", "user"),
    ],
)
def test_add_hierarchy__one_unknown(
    *, known_role: str, unknown_role: str, db: Session
) -> None:
    RS.create(role=known_role, db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role=known_role, child_role=unknown_role, db=db)

    assert f"Role '{unknown_role}' does not exist!" == err.value.message


################################################################################
#### Test role remove_hierarchy
################################################################################


def test_remove_hierarchy__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    RS.remove_hierarchy(parent_role="user", child_role="admin", db=db)


def test_remove_hierarchy__equal(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="user", child_role="user", db=db)

    assert "Both roles 'user' must not be the same!" == err.value.message


def test_remove_hierarchy__unknown(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="user", child_role="admin", db=db)

    assert "The hierarchy 'user' -> 'admin' does not exists!" == err.value.message


def test_remove_hierarchy__two_unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="user", child_role="admin", db=db)

    assert "Roles 'user' and 'admin' do not exist!" == err.value.message


@pytest.mark.parametrize(
    "known_role, unknown_role",
    [
        ("user", "admin"),
        ("admin", "user"),
    ],
)
def test_remove_hierarchy__one_unknown(
    *, known_role: str, unknown_role: str, db: Session
) -> None:
    RS.create(role=known_role, db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role=known_role, child_role=unknown_role, db=db)

    assert f"Role '{unknown_role}' does not exist!" == err.value.message


################################################################################
#### Test role parents
################################################################################


def test_parents__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="user_v2", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    RS.add_hierarchy(parent_role="user_v2", child_role="admin", db=db)

    assert ("user", "user_v2") == RS.parents(role="admin", db=db)


def test_parents__unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.parents(role="user", db=db)

    assert "Role 'user' does not exist!" == err.value.message


################################################################################
#### Test role children
################################################################################


def test_children__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.create(role="mod_v2", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod_v2", db=db)

    assert ("mod", "mod_v2") == RS.children(role="user", db=db)


def test_children__unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.children(role="user", db=db)

    assert "Role 'user' does not exist!" == err.value.message


################################################################################
#### Test role ancestors
################################################################################


def test_ancestors__success(*, db: Session) -> None:
    RS.create(role="guest", db=db)
    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.create(role="mod_v2", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="guest", child_role="user", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod_v2", db=db)
    RS.add_hierarchy(parent_role="mod", child_role="admin", db=db)
    RS.add_hierarchy(parent_role="mod_v2", child_role="admin", db=db)

    assert {"guest", "user", "mod", "mod_v2"} == set(RS.ancestors(role="admin", db=db))


def test_ancestors__unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.ancestors(role="user", db=db)

    assert "Role 'user' does not exist!" == err.value.message


################################################################################
#### Test role descendants
################################################################################


def test_descendants__success(*, db: Session) -> None:
    RS.create(role="guest", db=db)
    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.create(role="mod_v2", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="guest", child_role="user", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod_v2", db=db)
    RS.add_hierarchy(parent_role="mod", child_role="admin", db=db)
    RS.add_hierarchy(parent_role="mod_v2", child_role="admin", db=db)

    assert {"admin", "user", "mod", "mod_v2"} == set(
        RS.descendants(role="guest", db=db)
    )


def test_descendants__unknown(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.descendants(role="user", db=db)

    assert "Role 'user' does not exist!" == err.value.message
