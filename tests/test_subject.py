import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.models import Permission
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError
from collections import Counter

################################################################################
#### Test subject creation
################################################################################


def test_create__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)


def test_create__duplicate_subject(*, db: Session) -> None:
    SS.create(subject="Alex", db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.create(subject="Alex", db=db)

    assert "Subject 'Alex' already exists!" == err.value.message


################################################################################
#### Test subject delete
################################################################################


def test_delete__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.delete(subject="Alex", db=db)


def test_delete__unknown_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.delete(subject="Alex", db=db)
    assert "Subject 'Alex' does not exist!" == err.value.message


################################################################################
#### Test subject list
################################################################################


def test_list__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.create(subject="Max", db=db)

    assert ("Alex", "Max") == SS.list(db=db)


################################################################################
#### Test subject assign_role
################################################################################


def test_assign_role__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    RS.create(role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)


def test_assign_role__unknown_subject(db: Session) -> None:
    RS.create(role="admin", db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.assign_role(subject="unknown", role="admin", db=db)

    assert (
        "Subject 'unknown' does not exist!" == err.value.message
        or "Subject 'unknown' or Role 'admin' does not exist!" == err.value.message
    )


def test_assign_role__unknown_role(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.assign_role(subject="Alex", role="unknown", db=db)

    assert (
        "Role 'unknown' does not exist!" == err.value.message
        or "Subject 'Alex' or Role 'unknown' does not exist!" == err.value.message
    )


################################################################################
#### Test subject deassign_role
################################################################################


def test_deassign_role__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    RS.create(role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    assert Counter(SS.roles(subject="Alex", db=db)) == Counter(["admin"])

    SS.deassign_role(subject="Alex", role="admin", db=db)
    assert Counter(SS.roles(subject="Alex", db=db)) == Counter()


def test_deassign_role__unknown_subject(db: Session) -> None:
    RS.create(role="admin", db=db)

    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject="unknown", role="admin", db=db)
    assert "Subject 'unknown' does not exist!" == err.value.message


def test_deassign_role__unknown_role(db: Session) -> None:
    SS.create(subject="Alex", db=db)

    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject="Alex", role="unknown", db=db)
    assert "Role 'unknown' does not exist!" == err.value.message


def test_deassign_role__role_not_assigned(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    RS.create(role="admin", db=db)

    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject="Alex", role="admin", db=db)
    assert "Role 'admin' is not assigned to Subject 'Alex'!" == err.value.message


################################################################################
#### Test subject roles
################################################################################


def test_roles__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.create(subject="Uwe", db=db)

    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)

    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    SS.assign_role(subject="Uwe", role="user", db=db)

    assert Counter(("admin",)) == Counter(SS.roles(subject="Alex", db=db))
    assert Counter(("user",)) == Counter(SS.roles(subject="Uwe", db=db))


@pytest.mark.xfail(reason="Flag not yet implemented")
def test_roles_include_ascendant_next_neighbor__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.create(subject="Uwe", db=db)

    RS.create(role="user", db=db)
    RS.create(role="admin", db=db)

    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    SS.assign_role(subject="Uwe", role="user", db=db)

    assert Counter(("user", "admin")) == Counter(
        SS.roles(subject="Alex", include_ascendant_roles=True, db=db)
    )
    assert Counter(("user",)) == Counter(
        SS.roles(subject="Uwe", include_ascendant_roles=True, db=db)
    )


@pytest.mark.xfail(reason="Flag not yet implemented")
def test_roles_include_ascendant_n2n_neighbor__success(db: Session) -> None:
    SS.create(subject="Victor", db=db)

    RS.create(role="user", db=db)
    RS.create(role="premium", db=db)
    RS.create(role="vip", db=db)

    RS.add_hierarchy(parent_role="user", child_role="premium", db=db)
    RS.add_hierarchy(parent_role="premium", child_role="vip", db=db)

    SS.assign_role(subject="Victor", role="vip", db=db)

    assert Counter(("vip",)) == Counter(
        SS.roles(subject="Victor", include_ascendant_roles=False, db=db)
    )
    assert Counter(("user", "premium", "vip")) == Counter(
        SS.roles(subject="Victor", include_ascendant_roles=True, db=db)
    )


def test_roles__unknown_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.roles(subject="Alex", db=db)
    assert "Subject 'Alex' does not exist!" == err.value.message


################################################################################
#### Test subject assert_permission (and check_permission)
################################################################################


def test_check_permission__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)

    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="mod", child_role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)

    view_all = Permission(resource_type="user", resource_id="*", action="view")
    view_123 = Permission(resource_type="user", resource_id="123", action="view")
    edit_all = Permission(resource_type="user", resource_id="*", action="edit")
    edit_123 = Permission(resource_type="user", resource_id="123", action="edit")
    del_all = Permission(resource_type="user", resource_id="*", action="del")
    del_123 = Permission(resource_type="user", resource_id="123", action="del")

    RS.grant_permission(role="mod", permission=edit_all, db=db)
    RS.grant_permission(role="admin", permission=del_all, db=db)

    with pytest.raises(PyPermissionNotGrantedError) as err:
        SS.assert_permission(subject="Alex", permission=view_all, db=db)
    assert (
        f"Permission '{view_all}' is not granted for Subject 'Alex'!"
        == err.value.message
    )
    with pytest.raises(PyPermissionNotGrantedError) as err:
        SS.assert_permission(subject="Alex", permission=view_123, db=db)
    assert (
        f"Permission '{view_123}' is not granted for Subject 'Alex'!"
        == err.value.message
    )
    SS.assert_permission(subject="Alex", permission=edit_all, db=db)
    SS.assert_permission(subject="Alex", permission=edit_123, db=db)
    SS.assert_permission(subject="Alex", permission=del_all, db=db)
    SS.assert_permission(subject="Alex", permission=del_123, db=db)


def test_check_permission__unknown_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.check_permission(
            subject="unknown",
            permission=Permission(resource_type="user", resource_id="*", action="view"),
            db=db,
        )
    assert "Subject 'unknown' does not exist!" == err.value.message


################################################################################
#### Test subject permissions
################################################################################


def test_permissions__success(*, db: Session) -> None:
    SS.create(subject="Alex", db=db)

    view_all = Permission(resource_type="user", resource_id="*", action="view")
    edit_all = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    RS.grant_permission(role="user", permission=view_all, db=db)
    RS.grant_permission(role="mod", permission=edit_all, db=db)

    SS.assign_role(subject="Alex", role="mod", db=db)

    assert {str(view_all), str(edit_all)} == set(
        str(permission) for permission in SS.permissions(subject="Alex", db=db)
    )


def test_permissions__unknown_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.permissions(subject="unknown", db=db)
    assert "Subject 'unknown' does not exist!" == err.value.message


################################################################################
#### Test subject policies
################################################################################


def test_policies__success(*, db: Session) -> None:
    SS.create(subject="Alex", db=db)

    view_all = Permission(resource_type="user", resource_id="*", action="view")
    edit_all = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    RS.grant_permission(role="user", permission=view_all, db=db)
    RS.grant_permission(role="mod", permission=edit_all, db=db)

    SS.assign_role(subject="Alex", role="mod", db=db)

    assert {f"user:{view_all}", f"mod:{edit_all}"} == set(
        str(policies) for policies in SS.policies(subject="Alex", db=db)
    )


def test_policies__unknown_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.policies(subject="unknown", db=db)
    assert "Subject 'unknown' does not exist!" == err.value.message


################################################################################
#### Test actions on resource
################################################################################


@pytest.mark.xfail(reason="Not implemented")
def test_actions_on_resource(*, db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.create(subject="Uwe", db=db)

    RS.create(role="user", db=db)
    RS.create(role="user[Uwe]", db=db)
    RS.create(role="admin", db=db)

    RS.add_hierarchy(parent_role="user", child_role="admin", db=db)

    # Grant permissions
    p_view_group = Permission(resource_type="group", resource_id="*", action="view")
    p_edit_group = Permission(resource_type="group", resource_id="*", action="edit")
    p_edit_event = Permission(resource_type="event", resource_id="124", action="edit")

    RS.grant_permission(role="user", permission=p_view_group, db=db)
    RS.grant_permission(role="user[Uwe]", permission=p_edit_event, db=db)
    RS.grant_permission(role="admin", permission=p_edit_group, db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    SS.assign_role(subject="Uwe", role="user", db=db)

    assert Counter(
        SS.actions_on_resource(
            subject="Alex", resource_type="group", resource_id="*", db=db
        )
    ) == Counter(["view", "edit"])
    assert Counter(
        SS.actions_on_resource(
            subject="Alex", resource_type="group", resource_id="123", db=db
        )
    ) == Counter(["view", "edit"])

    assert Counter(
        SS.actions_on_resource(
            subject="Uwe", resource_type="group", resource_id="*", db=db
        )
    ) == Counter(["view"])
    assert Counter(
        SS.actions_on_resource(
            subject="Uwe", resource_type="group", resource_id="123", db=db
        )
    ) == Counter(["view"])

    assert (
        Counter(
            SS.actions_on_resource(
                subject="Uwe", resource_type="event", resource_id="*", db=db
            )
        )
        == Counter()
    )
    assert Counter(
        SS.actions_on_resource(
            subject="Uwe", resource_type="event", resource_id="123", db=db
        )
    ) == Counter(["edit"])


@pytest.mark.xfail(reason="Not implemented")
def test_actions_on_resource__unknown_subject(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.actions_on_resource(
            subject="unknown", resource_type="user", resource_id="*", db=db
        )
    assert "Subject 'unknown' does not exist!" == err.value.message
