import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError, ERR_MSG
from pypermission.models import Permission
from collections import Counter

################################################################################
#### Test role creation
################################################################################


def test_create__success(db: Session) -> None:
    RS.create(role="user", db=db)


def test_create__duplicate_role(*, db: Session) -> None:
    RS.create(role="user", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.create(role="user", db=db)

    assert ERR_MSG.role_exists.format(role="user") == err.value.message


################################################################################
#### Test role deletion
################################################################################


def test_delete__success(*, db: Session) -> None:
    role = "user"
    RS.create(role=role, db=db)
    RS.delete(role=role, db=db)


def test_delete__unknown_role(*, db: Session) -> None:
    role = "user"
    with pytest.raises(PyPermissionError) as err:
        RS.delete(role=role, db=db)
    assert ERR_MSG.non_existent_role.format(role=role) == err.value.message


################################################################################
#### Test role list
################################################################################


def test_list__success(*, db: Session) -> None:
    r_user = "user"
    r_admin = "admin"
    assert Counter(RS.list(db=db)) == Counter()
    RS.create(role=r_user, db=db)
    assert Counter(RS.list(db=db)) == Counter({r_user: 1})
    RS.create(role=r_admin, db=db)
    assert Counter(RS.list(db=db)) == Counter({r_user: 1, r_admin: 1})


################################################################################
#### Test role add_hierarchy
################################################################################


def test_add_hierarchy__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)


def test_add_hierarchy__conflict(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="user", db=db)
    assert ERR_MSG.conflicting_role_ids.format(role="user") == err.value.message


def test_add_hierarchy__cycle(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="admin", child_role="user", db=db)
    assert ERR_MSG.cycle_detected == err.value.message


def test_add_hierarchy__exists(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    assert (
        ERR_MSG.hierarchy_exists.format(parent_role="user", child_role="admin")
        == err.value.message
    )


def test_add_hierarchy__two_unknown_role_and_user(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    assert (
        ERR_MSG.non_existent_parent_child_roles.format(
            parent_role="user", child_role="admin"
        )
        == err.value.message
    )


@pytest.mark.parametrize(
    "known_role, unknown_role, known_is_parent",
    [
        ("user", "admin", True),
        ("admin", "user", False),
    ],
)
def test_add_hierarchy__one_unknown_role(
    *, known_role: str, unknown_role: str, known_is_parent: bool, db: Session
) -> None:
    RS.create(role=known_role, db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(
            parent_role=known_role if known_is_parent else unknown_role,
            child_role=unknown_role if known_is_parent else known_role,
            db=db,
        )

    assert ERR_MSG.non_existent_role.format(role=unknown_role) == err.value.message


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

    assert ERR_MSG.conflicting_role_ids.format(role="user") == err.value.message


def test_remove_hierarchy__unknown_hierarchy(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="user", child_role="admin", db=db)

    assert (
        ERR_MSG.non_existent_hierarchy.format(parent_role="user", child_role="admin")
        == err.value.message
    )


def test_remove_hierarchy__two_unknown_roles(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="user", child_role="admin", db=db)

    assert (
        ERR_MSG.non_existent_parent_child_roles.format(
            parent_role="user", child_role="admin"
        )
        == err.value.message
    )


@pytest.mark.parametrize(
    "known_role, unknown_role, known_is_parent",
    [
        ("user", "admin", True),
        ("admin", "user", False),
    ],
)
def test_remove_hierarchy_one_unknown_role(
    *,
    known_role: str,
    unknown_role: str,
    known_is_parent: bool,
    db: Session,
) -> None:
    RS.create(role=known_role, db=db)

    with pytest.raises(PyPermissionError) as exc:
        RS.remove_hierarchy(
            parent_role=known_role if known_is_parent else unknown_role,
            child_role=unknown_role if known_is_parent else known_role,
            db=db,
        )

    assert ERR_MSG.non_existent_role.format(role=unknown_role) == exc.value.message


################################################################################
#### Test role parents
################################################################################


def test_parents__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="user_v2", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)
    RS.add_hierarchy(parent_role="user_v2", child_role="admin", db=db)

    assert Counter(user=1, user_v2=1) == Counter(RS.parents(role="admin", db=db))


def test_parents__unknown_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.parents(role="user", db=db)

    assert ERR_MSG.non_existent_role.format(role="user") == err.value.message


################################################################################
#### Test role children
################################################################################


def test_children__success(*, db: Session) -> None:
    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.create(role="mod_v2", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod_v2", db=db)

    assert Counter(("mod", "mod_v2")) == Counter((RS.children(role="user", db=db)))


def test_children__unknown_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.children(role="user", db=db)

    assert ERR_MSG.non_existent_role.format(role="user") == err.value.message


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

    assert Counter(("guest", "user", "mod", "mod_v2")) == Counter(
        RS.ancestors(role="admin", db=db)
    )


def test_ancestors__unknown_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.ancestors(role="user", db=db)

    assert ERR_MSG.non_existent_role.format(role="user") == err.value.message


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

    assert Counter(("admin", "user", "mod", "mod_v2")) == Counter(
        RS.descendants(role="guest", db=db)
    )


def test_descendants__unknown_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.descendants(role="user", db=db)

    assert ERR_MSG.non_existent_role.format(role="user") == err.value.message


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


def test_subjects_include_descendants__success(*, db: Session) -> None:
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


def test_subjects_include_descendants__unknown_role(*, db: Session) -> None:
    role = "unknown"
    with pytest.raises(PyPermissionError) as err:
        RS.subjects(role=role, include_descendant_subjects=True, db=db)
    assert ERR_MSG.non_existent_role.format(role=role) == err.value.message

    with pytest.raises(PyPermissionError) as err:
        RS.subjects(role=role, include_descendant_subjects=False, db=db)

    assert ERR_MSG.non_existent_role.format(role=role) == err.value.message


################################################################################
#### Test role grant_permission
################################################################################


# TODO: test if access granted
def test_grant_permission__success(*, db: Session) -> None:
    role = "admin"
    permission = Permission(resource_type="event", resource_id="*", action="edit")

    RS.create(role=role, db=db)
    RS.grant_permission(role=role, permission=permission, db=db)
    RS.assert_permission(role=role, permission=permission, db=db)


@pytest.mark.xfail(reason="Error cause detection not implemented yet")
def test_grant_permission__duplication(*, db: Session) -> None:
    role = "admin"
    permission = Permission(resource_type="event", resource_id="*", action="edit")

    RS.create(role=role, db=db)
    RS.grant_permission(role=role, permission=permission, db=db)

    with pytest.raises(PyPermissionError) as err:
        RS.grant_permission(role=role, permission=permission, db=db)

    assert (
        ERR_MSG.permission_exists.format(permission_str=str(permission))
        == err.value.message
    )


def test_grant_permission__unknown_role(*, db: Session) -> None:
    role = "unknown"
    permission = Permission(resource_type="event", resource_id="*", action="edit")

    with pytest.raises(PyPermissionError) as err:
        RS.grant_permission(role=role, permission=permission, db=db)

    assert ERR_MSG.non_existent_role.format(role=role) == err.value.message


################################################################################
#### Test role revoke_permission
################################################################################


def test_revoke_permission__success(*, db: Session) -> None:
    permission = Permission(resource_type="event", resource_id="*", action="edit")

    RS.create(role="admin", db=db)
    RS.grant_permission(role="admin", permission=permission, db=db)
    RS.revoke_permission(role="admin", permission=permission, db=db)


@pytest.mark.xfail(reason="Error cause detection not implemented yet")
def test_revoke_permission__unknown_permission(*, db: Session) -> None:
    permission = Permission(resource_type="event", resource_id="*", action="edit")

    RS.create(role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        RS.revoke_permission(role="admin", permission=permission, db=db)

    assert (
        ERR_MSG.permission_exists.format(permission_str=str(permission))
        == err.value.message
    )


def test_revoke_permission__unknown_role(*, db: Session) -> None:
    permission = Permission(resource_type="event", resource_id="*", action="edit")
    with pytest.raises(PyPermissionError) as err:
        RS.revoke_permission(role="unknown", permission=permission, db=db)

    assert ERR_MSG.non_existent_role.format(role="unknown") == err.value.message


################################################################################
#### Test role check_permission
################################################################################


def test_check_permission__success(*, db: Session) -> None:
    p_view_all = Permission(resource_type="event", resource_id="*", action="view")
    p_view_123 = Permission(resource_type="event", resource_id="123", action="view")
    p_edit_all = Permission(resource_type="event", resource_id="*", action="edit")
    p_edit_123 = Permission(resource_type="event", resource_id="123", action="edit")
    p_del_all = Permission(resource_type="event", resource_id="*", action="del")

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
    assert RS.check_permission(role="user", permission=p_view_all, db=db) is True
    assert RS.check_permission(role="user", permission=p_view_123, db=db) is True
    assert RS.check_permission(role="user", permission=p_edit_all, db=db) is False

    assert RS.check_permission(role="admin", permission=p_view_all, db=db) is True
    assert RS.check_permission(role="admin", permission=p_edit_all, db=db) is True
    assert RS.check_permission(role="admin", permission=p_edit_123, db=db) is True
    assert RS.check_permission(role="admin", permission=p_del_all, db=db) is True

    # Test application instance role
    assert RS.check_permission(role="user[123]", permission=p_view_123, db=db) is True
    assert RS.check_permission(role="user[123]", permission=p_edit_123, db=db) is True

    assert RS.check_permission(role="user[124]", permission=p_view_123, db=db) is False
    assert RS.check_permission(role="user[124]", permission=p_edit_123, db=db) is False


@pytest.mark.xfail(reason="Not implemented")
def test_check_permission__unknown_role(db: Session) -> None:
    p_view_all = Permission(resource_type="event", resource_id="*", action="view")

    with pytest.raises(PyPermissionError) as err:
        RS.check_permission(role="unknown", permission=p_view_all, db=db)

    assert ERR_MSG.non_existent_role.format(role="unknown") == err.value.message


################################################################################
#### Test role assert_permission
################################################################################


def test_assert_permission__success(*, db: Session) -> None:
    r_user = "user"
    r_mod = "mod"
    p_view_all = Permission(resource_type="event", resource_id="*", action="view")
    p_edit_all = Permission(resource_type="event", resource_id="*", action="edit")
    p_edit_123 = Permission(resource_type="event", resource_id="123", action="edit")
    p_del_all = Permission(resource_type="event", resource_id="*", action="del")

    # Generic roles
    RS.create(role=r_user, db=db)
    RS.create(role=r_mod, db=db)
    RS.grant_permission(role=r_user, permission=p_view_all, db=db)
    RS.grant_permission(role=r_mod, permission=p_edit_all, db=db)

    RS.add_hierarchy(parent_role=r_user, child_role=r_mod, db=db)

    RS.assert_permission(role=r_mod, permission=p_view_all, db=db)
    RS.assert_permission(role=r_mod, permission=p_edit_all, db=db)
    RS.assert_permission(role=r_mod, permission=p_edit_123, db=db)

    with pytest.raises(PyPermissionNotGrantedError) as err:
        RS.assert_permission(role=r_mod, permission=p_del_all, db=db)

    assert (
        ERR_MSG.permission_not_granted_for_role.format(
            permission_str=str(p_del_all), role=r_mod
        )
        == err.value.message
    )


################################################################################
#### Test role permissions
################################################################################


def test_permissions__success(*, db: Session) -> None:
    p_view_all = Permission(resource_type="event", resource_id="*", action="view")
    p_edit_all = Permission(resource_type="event", resource_id="*", action="edit")

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)

    RS.grant_permission(role="user", permission=p_view_all, db=db)
    RS.grant_permission(role="mod", permission=p_edit_all, db=db)

    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    assert Counter((str(p_view_all),)) == Counter(
        str(permission) for permission in RS.permissions(role="user", db=db)
    )

    assert Counter((str(p_view_all), str(p_edit_all))) == Counter(
        str(permission) for permission in RS.permissions(role="mod", db=db)
    )

    assert Counter((str(p_edit_all),)) == Counter(
        str(permission)
        for permission in RS.permissions(role="mod", inherited=False, db=db)
    )


@pytest.mark.xfail(reason="Not implemented")
def test_permissions__unknown_role(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.permissions(role="unknown", db=db)

    assert ERR_MSG.non_existent_role.format(role="unknown") == err.value.message


################################################################################
#### Test role policies
################################################################################


def test_policies__success(*, db: Session) -> None:
    p_view_all = Permission(resource_type="event", resource_id="*", action="view")
    p_edit_all = Permission(resource_type="event", resource_id="*", action="edit")

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)

    RS.grant_permission(role="user", permission=p_view_all, db=db)
    RS.grant_permission(role="mod", permission=p_edit_all, db=db)

    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    assert Counter((f"user:{p_view_all}",)) == Counter(
        str(policies) for policies in RS.policies(role="user", db=db)
    )

    assert Counter((f"user:{p_view_all}", f"mod:{p_edit_all}")) == Counter(
        str(policies) for policies in RS.policies(role="mod", db=db)
    )

    assert Counter((f"mod:{p_edit_all}",)) == Counter(
        str(policies) for policies in RS.policies(role="mod", inherited=False, db=db)
    )


@pytest.mark.xfail(reason="Not implemented")
def test_policies__unknown_role(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.policies(role="unknown", db=db)

    assert ERR_MSG.non_existent_role.format(role="unknown") == err.value.message


################################################################################
#### Test actions on resource
################################################################################


def test_actions_on_resource_inherited__success(*, db: Session) -> None:
    RS.create(role="admin", db=db)
    RS.create(role="user", db=db)
    RS.create(role="user[Uwe]", db=db)

    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    # Grant permissions
    p_view_group = Permission(resource_type="group", resource_id="*", action="view")
    p_edit_group = Permission(resource_type="group", resource_id="*", action="edit")
    p_edit_event = Permission(resource_type="event", resource_id="124", action="edit")

    RS.grant_permission(role="user", permission=p_view_group, db=db)
    RS.grant_permission(role="user[Uwe]", permission=p_edit_event, db=db)
    RS.grant_permission(role="admin", permission=p_edit_group, db=db)

    assert Counter(
        RS.actions_on_resource(
            role="user", resource_type="group", resource_id="*", db=db
        )
    ) == Counter(["view"])
    assert Counter(
        RS.actions_on_resource(
            role="user", resource_type="group", resource_id="123", db=db
        )
    ) == Counter(["view"])

    assert Counter(
        RS.actions_on_resource(
            role="admin", resource_type="group", resource_id="*", db=db
        )
    ) == Counter(["view", "edit"])
    assert Counter(
        RS.actions_on_resource(
            role="admin", resource_type="group", resource_id="123", db=db
        )
    ) == Counter(["view", "edit"])

    assert Counter(
        RS.actions_on_resource(
            role="user[Uwe]", resource_type="event", resource_id="*", db=db
        )
    ) == Counter([])
    assert Counter(
        RS.actions_on_resource(
            role="user[Uwe]", resource_type="event", resource_id="124", db=db
        )
    ) == Counter(["edit"])


def test_actions_on_resource_not_inherited__success(*, db: Session) -> None:
    RS.create(role="admin", db=db)
    RS.create(role="user", db=db)
    RS.create(role="user[Uwe]", db=db)

    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    p_view_group = Permission(resource_type="group", resource_id="*", action="view")
    p_edit_group = Permission(resource_type="group", resource_id="*", action="edit")

    RS.grant_permission(role="user", permission=p_view_group, db=db)
    RS.grant_permission(role="admin", permission=p_edit_group, db=db)

    assert Counter(
        RS.actions_on_resource(
            role="user", resource_type="group", resource_id="*", inherited=False, db=db
        )
    ) == Counter(["view"])
    assert Counter(
        RS.actions_on_resource(
            role="user",
            resource_type="group",
            resource_id="123",
            inherited=False,
            db=db,
        )
    ) == Counter(["view"])

    assert Counter(
        RS.actions_on_resource(
            role="admin", resource_type="group", resource_id="*", inherited=False, db=db
        )
    ) == Counter(["edit"])
    assert Counter(
        RS.actions_on_resource(
            role="admin",
            resource_type="group",
            resource_id="123",
            inherited=False,
            db=db,
        )
    ) == Counter(["edit"])


@pytest.mark.xfail(reason="Not implemented")
def test_actions_on_resource__unknown_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.actions_on_resource(
            role="unknown", resource_type="group", resource_id="123", db=db
        )

    assert ERR_MSG.non_existent_role.format(role="unknown") == err.value.message
