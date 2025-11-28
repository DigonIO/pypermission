import pytest
from sqlalchemy.orm import Session

from pypermission.exc import ERR_STR_EMPTY, PyPermissionError
from pypermission.models import Permission, Policy
from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS

################################################################################
#### Test Policy
################################################################################


def test_policy__empty_role() -> None:
    permission = Permission(resource_type="admin", resource_id="", action="edit")
    with pytest.raises(PyPermissionError) as err:
        Policy(role="", permission=permission)
    assert ERR_STR_EMPTY.role == err.value.message


################################################################################
#### Test RoleService
################################################################################

# --------------------------------- empty_role ---------------------------------


def test_create__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.create(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_delete__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.delete(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_parents__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.parents(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_children__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.children(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_ascendants__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.ascendants(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_descendants__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.descendants(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_subjects_include_descendants__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.subjects(role="", include_descendant_subjects=True, db=db)
    assert ERR_STR_EMPTY.role == err.value.message

    with pytest.raises(PyPermissionError) as err:
        RS.subjects(role="", include_descendant_subjects=False, db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_grant_permission__empty_role(*, db: Session) -> None:
    permission = Permission(resource_type="event", resource_id="*", action="edit")

    with pytest.raises(PyPermissionError) as err:
        RS.grant_permission(role="", permission=permission, db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_revoke_permission__empty_role(*, db: Session) -> None:
    permission = Permission(resource_type="event", resource_id="*", action="edit")
    with pytest.raises(PyPermissionError) as err:
        RS.revoke_permission(role="", permission=permission, db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_check_permission__empty_role(db: Session) -> None:
    p_view_all = Permission(resource_type="event", resource_id="*", action="view")

    with pytest.raises(PyPermissionError) as err:
        RS.check_permission(role="", permission=p_view_all, db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_assert_permission__empty_role(*, db: Session) -> None:
    p_view_all = Permission(resource_type="event", resource_id="*", action="view")
    with pytest.raises(PyPermissionError) as err:
        RS.assert_permission(role="", permission=p_view_all, db=db)
    assert ERR_STR_EMPTY.role == err.value.message


def test_permissions__empty_role(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.permissions(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_policies__empty_role(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.policies(role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_actions_on_resource__empty_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.actions_on_resource(role="", resource_type="group", resource_id="123", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


# ----------------------------- empty_parent_role ------------------------------


def test_add_hierarchy__empty_parent_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="", child_role="admin", db=db)

    assert ERR_STR_EMPTY.parent_role == err.value.message


def test_remove_hierarchy__empty_parent_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="", child_role="admin", db=db)

    assert ERR_STR_EMPTY.parent_role == err.value.message


# ----------------------------- empty_child_role ------------------------------


def test_add_hierarchy__empty_child_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.add_hierarchy(parent_role="user", child_role="", db=db)

    assert ERR_STR_EMPTY.child_role == err.value.message


def test_remove_hierarchy__empty_child_role(*, db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        RS.remove_hierarchy(parent_role="user", child_role="", db=db)

    assert ERR_STR_EMPTY.child_role == err.value.message


################################################################################
#### Test SubjectService
################################################################################

# --------------------------------- empty_role ---------------------------------


def test_assign_role__empty_role(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.assign_role(subject="Alex", role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message


def test_deassign_role__empty_role(db: Session) -> None:
    with pytest.raises(PyPermissionError) as err:
        SS.deassign_role(subject="Alex", role="", db=db)

    assert ERR_STR_EMPTY.role == err.value.message
