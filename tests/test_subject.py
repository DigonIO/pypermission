import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.models import Permission
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError

################################################################################
#### Test subject creation
################################################################################


def test_create__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)


def test_create__duplicate(*, db: Session) -> None:
    SS.create(subject="Alex", db=db)
    with pytest.raises(PyPermissionError) as err:
        SS.create(subject="Alex", db=db)

    assert "The Subject 'Alex' already exists!" == err.value.message


################################################################################
#### Test subject delete
################################################################################


def test_delete__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    SS.delete(subject="Alex", db=db)


def test_delete__unknown(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.delete(subject="Alex", db=db)
    assert "The Subject 'Alex' does not exists!" == err.value.message


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


# TODO Test unknown subject and unknown role

################################################################################
#### Test subject deassign_role
################################################################################


def test_deassign_role__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)
    RS.create(role="admin", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    SS.deassign_role(subject="Alex", role="admin", db=db)


# TODO Test unknown subject and unknown role

################################################################################
#### Test subject roles
################################################################################


def test_roles__success(db: Session) -> None:
    SS.create(subject="Alex", db=db)

    RS.create(role="user", db=db)
    RS.create(role="premium", db=db)

    SS.assign_role(subject="Alex", role="user", db=db)
    SS.assign_role(subject="Alex", role="premium", db=db)

    assert ("user", "premium") == SS.roles(subject="Alex", db=db)


def test_roles__unknown(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.roles(subject="Alex", db=db)
    assert "The Subject 'Alex' does not exist!" == err.value.message


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


# TODO Test unknown subject

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

    assert  {f"user:{view_all}", f"mod:{edit_all}"} == set(
        str(policies) for policies in SS.policies(subject="Alex", db=db)
    )
