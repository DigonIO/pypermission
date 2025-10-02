from sqlalchemy.sql import select
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError


from pypermission.orm import BaseORM, RoleORM, HierarchyORM
from pypermission.exc import PyPermissionError


class RBAC:
    def __init__(self, *, engine: Engine) -> None:
        BaseORM.metadata.create_all(bind=engine)

    def add_role(self, *, role: str, db: Session) -> None:
        try:
            role_orm = RoleORM(id=role)
            db.add(role_orm)
            db.flush()
        except IntegrityError:
            db.rollback()

    def delete_role(self, *, role: str, db: Session) -> None:
        role_orm = db.get(RoleORM, role)
        if role_orm is None:
            return
        db.delete(role_orm)
        db.flush()

    def get_roles(self, *, db: Session) -> tuple[str, ...]:
        role_orms = db.scalars(select(RoleORM)).all()
        return tuple(role_orm.id for role_orm in role_orms)

    def add_role_hierarchy(
        self, *, parent_role: str, child_role: str, db: Session
    ) -> None:
        if parent_role == child_role:
            raise PyPermissionError(
                "The parent role and the child role must not be the same!"
            )

        root_cte = (
            select(HierarchyORM)
            .where(HierarchyORM.parent_role_id == child_role)
            .cte(name="root_cte", recursive=True)
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
            raise PyPermissionError("The requested hierarchy would generate a loop!")

        try:
            hierarchy_orm = HierarchyORM(
                parent_role_id=parent_role, child_role_id=child_role
            )
            db.add(hierarchy_orm)
            db.flush()
        except IntegrityError:
            db.rollback()

    def delete_role_hierarchy(
        self, *, parent_role: str, child_role: str, db: Session
    ) -> None:
        hierarchy_orm = db.get(HierarchyORM, (parent_role, child_role))
        if hierarchy_orm is None:
            return
        db.delete(hierarchy_orm)
        db.flush()

    def get_role_parents(self, *, role: str, db: Session) -> tuple[str, ...]:
        relation_orms = db.scalars(
            select(HierarchyORM).where(HierarchyORM.child_role_id == role)
        ).all()
        return tuple(relation_orm.parent_role_id for relation_orm in relation_orms)

    def get_role_children(self, *, role: str, db: Session) -> tuple[str, ...]:
        relation_orms = db.scalars(
            select(HierarchyORM).where(HierarchyORM.parent_role_id == role)
        ).all()
        return tuple(relation_orm.child_role_id for relation_orm in relation_orms)

    def get_role_descendants(self, *, role: str, db: Session) -> tuple[str, ...]:
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

        return tuple(descendant_relations)

    def get_role_ancestors(self, *, role: str, db: Session) -> tuple[str, ...]:
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

        descendant_relations = (
            db.scalars(select(relations_cte.c.parent_role_id)).unique().all()
        )

        return tuple(descendant_relations)


# def assign_role(self, *, parent_role_id: str, child_role_id: str) -> None: ...
#
# def deassign_role(self, *, parent_role_id: str, child_role_id: str) -> None: ...
#
# def add_subject(self, *, subject_id: str) -> None: ...
#
# def delete_subject(self, *, subject_id: str) -> None: ...
#
# def assign_subject(self, *, role_id: str, subject_id: str) -> None: ...
#
# def deassign_subject(self, *, role_id: str, subject_id: str) -> None: ...
#
# def grant_permission(
#     self,
#     *,
#     role_id: str,
#     resource_type: str,
#     resource_id: str,
#     action: str,
#     db: Session,
# ) -> None: ...
#
# def revoke_permission(
#     self,
#     *,
#     role_id: str,
#     resource_type: str,
#     resource_id: str,
#     action: str,
#     db: Session,
# ) -> None: ...
