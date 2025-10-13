import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError
from pypermission.models import Permission
from collections import Counter

################################################################################
#### Test role creation
################################################################################


def test_create__success(db: Session) -> None:
    RS.create(role="user", db=db)


def test_create__duplicate(*, db: Session) -> None:
    RS.create(role="user", db=db)
    with pytest.raises(PyPermissionError):
        RS.create(role="user", db=db)


################################################################################
#### Test role deletion
################################################################################


def test_delete__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.delete(role="user", db=db)


def test_delete__unknown(*, db: Session) -> None:
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

    assert "RoleIDs must not be equal: 'user'!" == err.value.message


def test_add_hierarchy__cycle(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="admin", child_role="user", db=db)

    assert "Desired hierarchy would create a cycle!" == err.value.message


def test_add_hierarchy__exists(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    assert "Hierarchy 'user' -> 'admin' exists!" == err.value.message


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

    assert "RoleIDs must not be equal: 'user'!" == err.value.message


def test_remove_hierarchy__unknown(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="user", child_role="admin", db=db)

    assert "Hierarchy 'user' -> 'admin' does not exist!" == err.value.message


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


################################################################################
#### Test role subjects
################################################################################


def test_subjects__success(*, db: Session) -> None:
    SS.create(subject="Oscar", db=db)
    SS.create(subject="Charlie", db=db)
    SS.create(subject="Mike", db=db)

    RS.create(role="user", db=db)

    SS.assign_role(subject="Oscar", role="user", db=db)
    SS.assign_role(subject="Charlie", role="user", db=db)
    SS.assign_role(subject="Mike", role="user", db=db)

    assert Counter(("Oscar", "Charlie", "Mike")) == Counter(
        RS.subjects(role="user", db=db)
    )


@pytest.mark.xfail(reason="Flag not yet implemented")
def test_subjects_include_descendant__success(*, db: Session) -> None:
    SS.create(subject="Oscar", db=db)
    SS.create(subject="Charlie", db=db)
    SS.create(subject="Mike", db=db)

    RS.create(role="user", db=db)
    RS.create(role="moderator", db=db)
    RS.add_hierarchy(parent_role="user", child_role="moderator", db=db)

    SS.assign_role(subject="Oscar", role="user", db=db)
    SS.assign_role(subject="Mike", role="user", db=db)
    SS.assign_role(subject="Charlie", role="moderator", db=db)
    SS.assign_role(subject="Mike", role="moderator", db=db)

    assert Counter(("Oscar", "Mike")) == Counter(RS.subjects(role="user", db=db))
    assert Counter(("Charlie", "Mike")) == Counter(RS.subjects(role="moderator", db=db))

    assert Counter(("Oscar", "Charlie", "Mike")) == Counter(
        RS.subjects(role="user", include_descendant_subjects=True, db=db)
    )
    assert Counter(("Charlie", "Mike")) == Counter(
        RS.subjects(role="moderator", include_descendant_subjects=True, db=db)
    )


################################################################################
#### Test role grant_permission
################################################################################


def test_grant_permission__success(*, db: Session) -> None:
    role = "admin"
    permission = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role=role, db=db)
    RS.grant_permission(role=role, permission=permission, db=db)


@pytest.mark.xfail(reason="Error cause detection not implemented yet")
def test_grant_permission__duplication(*, db: Session) -> None:
    role = "admin"
    permission = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role=role, db=db)
    RS.grant_permission(role=role, permission=permission, db=db)

    with pytest.raises(PyPermissionError) as err:
        RS.grant_permission(role=role, permission=permission, db=db)
    assert "Permission 'user[*]:edit' does already exist!" == err.value.message


# TODO Test unknown role


################################################################################
#### Test role revoke_permission
################################################################################


def test_revoke_permission__success(*, db: Session) -> None:
    permission = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role="admin", db=db)
    RS.grant_permission(role="admin", permission=permission, db=db)
    RS.revoke_permission(role="admin", permission=permission, db=db)


@pytest.mark.xfail(reason="Error cause detection not implemented yet")
def test_revoke_permission__unknown(*, db: Session) -> None:
    permission = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.revoke_permission(role="admin", permission=permission, db=db)

    assert "Permission 'user[*]:edit' does not exist!" == err.value.message


# TODO Test unknown role


################################################################################
#### Test role check_permission
################################################################################


def test_check_permission__success(*, db: Session) -> None:
    p_view_all = Permission(resource_type="user", resource_id="*", action="view")
    p_view_123 = Permission(resource_type="user", resource_id="123", action="view")
    p_edit_all = Permission(resource_type="user", resource_id="*", action="edit")
    p_edit_123 = Permission(resource_type="user", resource_id="123", action="edit")
    p_del_all = Permission(resource_type="user", resource_id="*", action="del")

    # Generic roles
    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)
    RS.grant_permission(role="user", permission=p_view_all, db=db)
    RS.grant_permission(role="mod", permission=p_edit_all, db=db)
    RS.grant_permission(role="admin", permission=p_del_all, db=db)

    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)
    RS.add_hierarchy(parent_role="mod", child_role="admin", db=db)

    # Application instance role
    RS.create(role="user[123]", db=db)
    RS.create(role="user[124]", db=db)

    RS.grant_permission(role="user[123]", permission=p_view_123, db=db)
    RS.grant_permission(role="user[123]", permission=p_edit_123, db=db)

    # Test generic roles
    assert RS.check_permission(role="user", permission=p_view_all, db=db) == True
    assert RS.check_permission(role="user", permission=p_view_123, db=db) == True
    assert RS.check_permission(role="user", permission=p_edit_all, db=db) == False

    assert RS.check_permission(role="admin", permission=p_view_all, db=db) == True
    assert RS.check_permission(role="admin", permission=p_edit_all, db=db) == True
    assert RS.check_permission(role="admin", permission=p_edit_123, db=db) == True
    assert RS.check_permission(role="admin", permission=p_del_all, db=db) == True

    # Test application instance role
    assert RS.check_permission(role="user[123]", permission=p_view_123, db=db) == True
    assert RS.check_permission(role="user[123]", permission=p_edit_123, db=db) == True

    assert RS.check_permission(role="user[124]", permission=p_view_123, db=db) == False
    assert RS.check_permission(role="user[124]", permission=p_edit_123, db=db) == False


# TODO Test unknown role

################################################################################
#### Test role assert_permission
################################################################################


def test_assert_permission__success(*, db: Session) -> None:
    p_view_all = Permission(resource_type="user", resource_id="*", action="view")
    p_edit_all = Permission(resource_type="user", resource_id="*", action="edit")
    p_edit_123 = Permission(resource_type="user", resource_id="123", action="edit")
    p_del_all = Permission(resource_type="user", resource_id="*", action="del")

    # Generic roles
    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.grant_permission(role="user", permission=p_view_all, db=db)
    RS.grant_permission(role="mod", permission=p_edit_all, db=db)

    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    RS.assert_permission(role="mod", permission=p_view_all, db=db)
    RS.assert_permission(role="mod", permission=p_edit_all, db=db)
    RS.assert_permission(role="mod", permission=p_edit_123, db=db)
    with pytest.raises(PyPermissionNotGrantedError) as err:
        RS.assert_permission(role="mod", permission=p_del_all, db=db)
    assert (
        "Permission 'user[*]:del' is not granted for Role 'mod'!" == err.value.message
    )


################################################################################
#### Test role permissions
################################################################################


def test_permissions__success(*, db: Session) -> None:
    p_view_all = Permission(resource_type="user", resource_id="*", action="view")
    p_edit_all = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)

    RS.grant_permission(role="user", permission=p_view_all, db=db)
    RS.grant_permission(role="mod", permission=p_edit_all, db=db)

    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    assert {str(p_view_all)} == set(
        str(permission) for permission in RS.permissions(role="user", db=db)
    )

    assert {str(p_view_all), str(p_edit_all)} == set(
        str(permission) for permission in RS.permissions(role="mod", db=db)
    )

    assert {str(p_edit_all)} == set(
        str(permission)
        for permission in RS.permissions(role="mod", inherited=False, db=db)
    )


################################################################################
#### Test role policies
################################################################################


def test_policies__success(*, db: Session) -> None:
    p_view_all = Permission(resource_type="user", resource_id="*", action="view")
    p_edit_all = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)

    RS.grant_permission(role="user", permission=p_view_all, db=db)
    RS.grant_permission(role="mod", permission=p_edit_all, db=db)

    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    assert {f"user:{p_view_all}"} == set(
        str(policies) for policies in RS.policies(role="user", db=db)
    )

    assert {f"user:{p_view_all}", f"mod:{p_edit_all}"} == set(
        str(policies) for policies in RS.policies(role="mod", db=db)
    )

    assert {f"mod:{p_edit_all}"} == set(
        str(policies) for policies in RS.policies(role="mod", inherited=False, db=db)
    )
