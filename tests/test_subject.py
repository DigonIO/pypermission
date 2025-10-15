import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.models import Permission
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError, ERR_MSG
from collections import Counter

################################################################################
#### Test subject creation
################################################################################


def test_create__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)


def test_create__duplicate_subject(*, db: Session) -> None:
    subject = "Alex"
    SS.create(subject=subject, db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.create(subject=subject, db=db)

    assert ERR_MSG.subject_exists.format(subject=subject) == err.value.message


################################################################################
#### Test subject delete
################################################################################


def test_delete__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.delete(subject="Alex", db=db)


def test_delete__unknown_subject(db: Session) -> None:
    subject = "Alex"
    with pytest.raises(PyPermissionError) as err:
        SS.delete(subject=subject, db=db)

    assert ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message


################################################################################
#### Test subject list
################################################################################


def test_list__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.create(subject="Max", db=db)

    assert Counter(("Alex", "Max")) == Counter(SS.list(db=db))


################################################################################
#### Test subject assign_role
################################################################################


def test_assign_role__success(db: Session) -> None:
    subject = "Alex"
    role = "admin"
    SS.create(subject=subject, db=db)
    RS.create(role=role, db=db)

    SS.assign_role(subject=subject, role=role, db=db)


def test_assign_role__unknown_subject(db: Session) -> None:
    subject = "unknown"
    role = "admin"
    RS.create(role=role, db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.assign_role(subject=subject, role=role, db=db)

    assert (
        ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message
        or ERR_MSG.non_existent_subject_role.format(subject=subject, role=role)
        == err.value.message
    )


def test_assign_role__unknown_role(db: Session) -> None:
    subject = "Alex"
    role = "unknown"
    SS.create(subject=subject, db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.assign_role(subject=subject, role="unknown", db=db)

    assert (
        ERR_MSG.non_existent_role.format(role=role) == err.value.message
        or ERR_MSG.non_existent_subject_role.format(subject=subject, role=role)
        == err.value.message
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
    role = "admin"
    subject = "unknown"
    RS.create(role=role, db=db)

    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject=subject, role=role, db=db)
    assert ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message


def test_deassign_role__unknown_role(db: Session) -> None:
    subject = "Alex"
    role = "unknown"
    SS.create(subject=subject, db=db)

    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject=subject, role=role, db=db)

    assert ERR_MSG.non_existent_role.format(role=role) == err.value.message


def test_deassign_role__role_not_assigned(db: Session) -> None:
    subject = "Alex"
    role = "admin"
    SS.create(subject=subject, db=db)
    RS.create(role=role, db=db)

    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject=subject, role=role, db=db)

    assert (
        ERR_MSG.non_existent_role_assignment.format(role=role, subject=subject)
        == err.value.message
    )


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
    subject = "Alex"
    with pytest.raises(PyPermissionError) as err:
        SS.roles(subject=subject, db=db)
    assert ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message


################################################################################
#### Test subject assert_permission (and check_permission)
################################################################################


def test_check_permission__success(db: Session) -> None:
    subject = "Alex"
    SS.create(subject=subject, db=db)

    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="mod", child_role="admin", db=db)

    SS.assign_role(subject=subject, role="admin", db=db)

    view_all = Permission(resource_type="user", resource_id="*", action="view")
    view_123 = Permission(resource_type="user", resource_id="123", action="view")
    edit_all = Permission(resource_type="user", resource_id="*", action="edit")
    edit_123 = Permission(resource_type="user", resource_id="123", action="edit")
    del_all = Permission(resource_type="user", resource_id="*", action="del")
    del_123 = Permission(resource_type="user", resource_id="123", action="del")

    RS.grant_permission(role="mod", permission=edit_all, db=db)
    RS.grant_permission(role="admin", permission=del_all, db=db)

    with pytest.raises(PyPermissionNotGrantedError) as err:
        SS.assert_permission(subject=subject, permission=view_all, db=db)
    assert (
        ERR_MSG.permission_not_granted_for_subject.format(
            permission_str=str(view_all), subject=subject
        )
        == err.value.message
    )

    with pytest.raises(PyPermissionNotGrantedError) as err:
        SS.assert_permission(subject=subject, permission=view_123, db=db)

    assert (
        ERR_MSG.permission_not_granted_for_subject.format(
            permission_str=str(view_123), subject=subject
        )
        == err.value.message
    )
    SS.assert_permission(subject=subject, permission=edit_all, db=db)
    SS.assert_permission(subject=subject, permission=edit_123, db=db)
    SS.assert_permission(subject=subject, permission=del_all, db=db)
    SS.assert_permission(subject=subject, permission=del_123, db=db)


def test_check_permission__unknown_subject(db: Session) -> None:
    subject = "unknown"
    with pytest.raises(PyPermissionError) as err:
        SS.check_permission(
            subject=subject,
            permission=Permission(resource_type="user", resource_id="*", action="view"),
            db=db,
        )

    assert ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message


################################################################################
#### Test subject permissions
################################################################################


def test_permissions__success(*, db: Session) -> None:
    subject = "Alex"
    SS.create(subject=subject, db=db)

    view_all = Permission(resource_type="user", resource_id="*", action="view")
    edit_all = Permission(resource_type="user", resource_id="*", action="edit")

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)

    RS.grant_permission(role="user", permission=view_all, db=db)
    RS.grant_permission(role="mod", permission=edit_all, db=db)

    SS.assign_role(subject=subject, role="mod", db=db)

    assert Counter((str(view_all), str(edit_all))) == Counter(
        str(permission) for permission in SS.permissions(subject=subject, db=db)
    )


def test_permissions__unknown_subject(db: Session) -> None:
    subject = "unknown"
    with pytest.raises(PyPermissionError) as err:
        SS.permissions(subject=subject, db=db)
    assert ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message


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

    assert Counter((f"user:{view_all}", f"mod:{edit_all}")) == Counter(
        str(policies) for policies in SS.policies(subject="Alex", db=db)
    )


def test_policies__unknown_subject(db: Session) -> None:
    subject = "unknown"
    with pytest.raises(PyPermissionError) as err:
        SS.policies(subject=subject, db=db)
    assert ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message


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
    subject = "unknown"
    with pytest.raises(PyPermissionError) as err:
        SS.actions_on_resource(
            subject=subject, resource_type="user", resource_id="*", db=db
        )
    assert ERR_MSG.non_existent_subject.format(subject=subject) == err.value.message
