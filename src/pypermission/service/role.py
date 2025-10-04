from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pypermission.models import (
    Permission,
    RoleORM,
    HierarchyORM,
    PolicyORM,
    FrozenClass,
)
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError

################################################################################
#### RoleService
################################################################################


class RoleService(metaclass=FrozenClass):

    @classmethod
    def create(cls, *, role: str, db: Session) -> None:
        try:
            role_orm = RoleORM(id=role)
            db.add(role_orm)
            db.flush()
        except IntegrityError:
            db.rollback()

    @classmethod
    def delete(cls, *, role: str, db: Session) -> None:
        role_orm = db.get(RoleORM, role)
        if role_orm is None:
            return
        db.delete(role_orm)
        db.flush()

    @classmethod
    def list(cls, *, db: Session) -> tuple[str, ...]:
        role_orms = db.scalars(select(RoleORM)).all()
        return tuple(role_orm.id for role_orm in role_orms)

    @classmethod
    def add_hierarchy(cls, *, parent_role: str, child_role: str, db: Session) -> None:
        if parent_role == child_role:
            raise PyPermissionError(
                f"Both roles ('{parent_role}') must not be the same!"
            )

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

    @classmethod
    def remove_hierarchy(
        cls, *, parent_role: str, child_role: str, db: Session
    ) -> None:
        if parent_role == child_role:
            raise PyPermissionError(
                f"Both roles ('{parent_role}') must not be the same!"
            )

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

    @classmethod
    def parents(cls, *, role: str, db: Session) -> tuple[str, ...]:
        parents = db.scalars(
            select(HierarchyORM.parent_role_id).where(
                HierarchyORM.child_role_id == role
            )
        ).all()
        if len(parents) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role ('{role}') does not exist!")
        return tuple(parents)

    @classmethod
    def children(cls, *, role: str, db: Session) -> tuple[str, ...]:
        children = db.scalars(
            select(HierarchyORM.child_role_id).where(
                HierarchyORM.parent_role_id == role
            )
        ).all()
        if len(children) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role ('{role}') does not exist!")
        return tuple(children)

    @classmethod
    def ancestors(cls, *, role: str, db: Session) -> tuple[str, ...]:
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

    @classmethod
    def descendants(cls, *, role: str, db: Session) -> tuple[str, ...]:
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

    @classmethod
    def check_permission(
        cls,
        *,
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

    @classmethod
    def assert_permission(
        cls,
        *,
        role: str,
        permission: Permission,
        db: Session,
    ) -> None:
        if not cls.check_permission(role=role, permission=permission, db=db):
            raise PyPermissionNotGrantedError()
