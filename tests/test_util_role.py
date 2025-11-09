import pytest
from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.exc import RBACError
from pypermission.models import Permission
from pypermission.util.role import role_dag

################################################################################
#### Test util role_dag
################################################################################


def test_role_dag_only_roles__success(db: Session) -> None:

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)
    RS.add_hierarchy(parent_role="mod", child_role="admin", db=db)

    RS.create(role="user[Alex]", db=db)

    dag = role_dag(include_subjects=False, include_permissions=False, db=db)

    assert {"admin", "mod", "user", "user[Alex]"} == set(dag.nodes)
    assert {("user", "mod"), ("mod", "admin")} == set(dag.edges)


def test_role_dag_constrained__success(db: Session) -> None:

    RS.create(role="user", db=db)
    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)
    RS.add_hierarchy(parent_role="user", child_role="mod", db=db)
    RS.add_hierarchy(parent_role="mod", child_role="admin", db=db)

    RS.create(role="user[Alex]", db=db)

    dag = role_dag(
        root_roles={"mod"}, include_subjects=False, include_permissions=False, db=db
    )

    assert {"mod", "user"} == set(dag.nodes)
    assert {("user", "mod")} == set(dag.edges)


def test_role_dag_constrained__unknown(db: Session) -> None:

    with pytest.raises(RBACError) as err:
        dag = role_dag(
            root_roles={"mod"}, include_subjects=False, include_permissions=False, db=db
        )
    assert r"Requested role does not exist: {'mod'}!" == err.value.message

    with pytest.raises(RBACError) as err:
        dag = role_dag(
            root_roles={"mod", "admin"},
            include_subjects=False,
            include_permissions=False,
            db=db,
        )
    assert (
        "Requested roles do not exist:" in err.value.message
        and "mod" in err.value.message
        and "admin" in err.value.message
    )


def test_role_dag_with_subjects__success(db: Session) -> None:

    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)

    SS.create(subject="Alex", db=db)
    SS.create(subject="Max", db=db)

    RS.create(role="user[Alex]", db=db)
    RS.create(role="user[Max]", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    SS.assign_role(subject="Alex", role="user[Alex]", db=db)
    SS.assign_role(subject="Max", role="mod", db=db)
    SS.assign_role(subject="Max", role="user[Max]", db=db)

    dag = role_dag(include_subjects=True, include_permissions=False, db=db)

    assert {"admin", "mod", "user[Alex]", "user[Max]", "Alex", "Max"} == set(dag.nodes)
    assert {
        ("admin", "Alex"),
        ("mod", "Max"),
        ("user[Alex]", "Alex"),
        ("user[Max]", "Max"),
    } == set(dag.edges)


def test_role_dag_with_permissions__success(db: Session) -> None:

    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)

    view_all = Permission(resource_type="user", resource_id="*", action="view")
    edit_all = Permission(resource_type="user", resource_id="*", action="edit")

    RS.grant_permission(role="mod", permission=view_all, db=db)
    RS.grant_permission(role="admin", permission=edit_all, db=db)

    dag = role_dag(include_subjects=False, include_permissions=True, db=db)

    view_all_str = str(view_all)
    edit_all_str = str(edit_all)
    assert {"admin", "mod", view_all_str, edit_all_str} == set(dag.nodes)
    assert {
        ("mod", view_all_str),
        ("admin", edit_all_str),
    } == set(dag.edges)
