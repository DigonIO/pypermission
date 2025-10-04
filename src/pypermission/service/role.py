from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pypermission.models import Permission, RoleORM, HierarchyORM, PolicyORM
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError

################################################################################
#### Role Service
################################################################################


def create(*, role: str, db: Session) -> None:
    try:
        role_orm = RoleORM(id=role)
        db.add(role_orm)
        db.flush()
    except IntegrityError:
        db.rollback()


def delete(*, role: str, db: Session) -> None:
    role_orm = db.get(RoleORM, role)
    if role_orm is None:
        return
    db.delete(role_orm)
    db.flush()


def list(*, db: Session) -> tuple[str, ...]:
    role_orms = db.scalars(select(RoleORM)).all()
    return tuple(role_orm.id for role_orm in role_orms)


def add_hierarchy(*, parent_role: str, child_role: str, db: Session) -> None:
    if parent_role == child_role:
        raise PyPermissionError(f"Both roles ('{parent_role}') must not be the same!")

    roles = db.scalars(
        select(RoleORM.id).where(RoleORM.id.in_([parent_role, child_role]))
    ).all()
    if len(roles) < 2:
        raise PyPermissionError(
            f"One or both roles ('{parent_role}', '{child_role}') do not exist!"
        )

    root_cte = (
        select(HierarchyORM)
        .where(HierarchyORM.parent_role_id == child_role)
        .cte(recursive=True)
    )

    traversing_cte = root_cte.alias()
    relations_cte = root_cte.union_all(
        select(HierarchyORM).where(
            HierarchyORM.parent_role_id == traversing_cte.c.child_role_id
        )
    )

    critical_leaf_relations = db.execute(
        select(relations_cte).where(relations_cte.c.child_role_id == parent_role)
    ).all()

    if critical_leaf_relations:
        raise PyPermissionError("The desired hierarchy would generate a loop!")

    try:
        hierarchy_orm = HierarchyORM(
            parent_role_id=parent_role, child_role_id=child_role
        )
        db.add(hierarchy_orm)
        db.flush()
    except IntegrityError as err:

        db.rollback()


def remove_hierarchy(*, parent_role: str, child_role: str, db: Session) -> None:
    if parent_role == child_role:
        raise PyPermissionError(f"Both roles ('{parent_role}') must not be the same!")

    hierarchy_orm = db.get(HierarchyORM, (parent_role, child_role))
    if hierarchy_orm is None:
        roles = db.scalars(
            select(RoleORM.id).where(RoleORM.id.in_([parent_role, child_role]))
        ).all()
        if len(roles) < 2:
            raise PyPermissionError(
                f"One or both roles ('{parent_role}', '{child_role}') do not exist!"
            )
    db.delete(hierarchy_orm)
    db.flush()


def parents(*, role: str, db: Session) -> tuple[str, ...]:
    parents = db.scalars(
        select(HierarchyORM.parent_role_id).where(HierarchyORM.child_role_id == role)
    ).all()
    if len(parents) == 0 and db.get(RoleORM, role) is None:
        raise PyPermissionError(f"Role ('{role}') does not exist!")
    return tuple(parents)


def children(*, role: str, db: Session) -> tuple[str, ...]:
    children = db.scalars(
        select(HierarchyORM.child_role_id).where(HierarchyORM.parent_role_id == role)
    ).all()
    if len(children) == 0 and db.get(RoleORM, role) is None:
        raise PyPermissionError(f"Role ('{role}') does not exist!")
    return tuple(children)


def ancestors(*, role: str, db: Session) -> tuple[str, ...]:
    root_cte = (
        select(HierarchyORM)
        .where(HierarchyORM.child_role_id == role)
        .cte(name="root_cte", recursive=True)
    )

    traversing_cte = root_cte.alias()
    relations_cte = root_cte.union_all(
        select(HierarchyORM).where(
            HierarchyORM.child_role_id == traversing_cte.c.parent_role_id
        )
    )

    ancestor_relations = (
        db.scalars(select(relations_cte.c.parent_role_id)).unique().all()
    )

    if len(ancestor_relations) == 0 and db.get(RoleORM, role) is None:
        raise PyPermissionError(f"Role ('{role}') does not exist!")
    return tuple(ancestor_relations)


def descendants(*, role: str, db: Session) -> tuple[str, ...]:
    root_cte = (
        select(HierarchyORM)
        .where(HierarchyORM.parent_role_id == role)
        .cte(name="root_cte", recursive=True)
    )

    traversing_cte = root_cte.alias()
    relations_cte = root_cte.union_all(
        select(HierarchyORM).where(
            HierarchyORM.parent_role_id == traversing_cte.c.child_role_id
        )
    )

    descendant_relations = (
        db.scalars(select(relations_cte.c.child_role_id)).unique().all()
    )

    if len(descendant_relations) == 0 and db.get(RoleORM, role) is None:
        raise PyPermissionError(f"Role ('{role}') does not exist!")
    return tuple(descendant_relations)


def check_permission(
    role: str,
    permission: Permission,
    db: Session,
) -> bool:
    root_cte = (
        select(RoleORM.id.label("role_id"))
        .where(RoleORM.id == role)
        .cte(recursive=True)
    )

    traversing_cte = root_cte.alias()
    relations_cte = root_cte.union_all(
        select(HierarchyORM.parent_role_id).where(  # NOTE Magic here???
            HierarchyORM.child_role_id == traversing_cte.c.role_id
        )
    )
    policy_orms = db.scalars(
        select(PolicyORM)
        .join(relations_cte, PolicyORM.role_id == relations_cte.c.role_id)
        .where(
            PolicyORM.resource_type == permission.resource_type,
            PolicyORM.resource_id.in_((permission.resource_id, "*")),
            PolicyORM.action == permission.action,
        )
    ).all()

    return len(policy_orms) > 0


def assert_permission(
    *,
    role: str,
    permission: Permission,
    db: Session,
) -> None:
    if not check_permission(role=role, permission=permission, db=db):
        raise PyPermissionNotGrantedError()
