from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError

from pypermission.orm import (
    BaseORM,
    RoleORM,
    HierarchyORM,
    SubjectORM,
    MemberORM,
    PolicyORM,
)
from pypermission.exc import PyPermissionError


class Permission:
    resource_type: str
    resource_id: str
    action: str

    def __init__(self, *, resource_type: str, resource_id: str, action: str) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action

    def __str__(self) -> str:
        if self.resource_id is None:
            return f"{self.resource_type} - {self.action}"
        return f"{self.resource_type}[{self.resource_id}] - {self.action}"


class Policy:
    role: str
    permission: Permission

    def __init__(self, *, role: str, permission: Permission) -> None:
        self.role = role
        self.permission = permission

    def __str__(self) -> str:
        return f"{self.role} - {self.permission}"


class RBAC:
    def __init__(self, *, engine: Engine) -> None:
        BaseORM.metadata.create_all(bind=engine)

    def create_role(self, *, role: str, db: Session) -> None:
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
            raise PyPermissionError("The desired hierarchy would generate a loop!")

        try:
            hierarchy_orm = HierarchyORM(
                parent_role_id=parent_role, child_role_id=child_role
            )
            db.add(hierarchy_orm)
            db.flush()
        except IntegrityError as err:

            db.rollback()

    def remove_role_hierarchy(
        self, *, parent_role: str, child_role: str, db: Session
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

    def get_role_parents(self, *, role: str, db: Session) -> tuple[str, ...]:
        parents = db.scalars(
            select(HierarchyORM.parent_role_id).where(
                HierarchyORM.child_role_id == role
            )
        ).all()
        if len(parents) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role ('{role}') does not exist!")
        return tuple(parents)

    def get_role_children(self, *, role: str, db: Session) -> tuple[str, ...]:
        children = db.scalars(
            select(HierarchyORM.child_role_id).where(
                HierarchyORM.parent_role_id == role
            )
        ).all()
        if len(children) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role ('{role}') does not exist!")
        return tuple(children)

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

        ancestor_relations = (
            db.scalars(select(relations_cte.c.parent_role_id)).unique().all()
        )

        if len(ancestor_relations) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role ('{role}') does not exist!")
        return tuple(ancestor_relations)

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

        if len(descendant_relations) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role ('{role}') does not exist!")
        return tuple(descendant_relations)

    def create_subject(self, *, subject: str, db: Session) -> None:
        try:
            subject_orm = SubjectORM(id=subject)
            db.add(subject_orm)
            db.flush()
        except IntegrityError:
            db.rollback()

    def delete_subject(self, *, subject: str, db: Session) -> None:
        subject_orm = db.get(SubjectORM, subject)
        if subject_orm is None:
            return
        db.delete(subject_orm)
        db.flush()

    def get_subjects(self, *, db: Session) -> tuple[str, ...]:
        subjects = db.scalars(select(SubjectORM.id)).all()
        return tuple(subject for subject in subjects)

    def assign_role(self, *, subject: str, role: str, db: Session) -> None:
        try:
            member_orm = MemberORM(role_id=role, subject_id=subject)
            db.add(member_orm)
            db.flush()
        except IntegrityError as err:
            db.rollback()
            # TODO 'psycopg.errors.UniqueViolation'

            subject_orm = db.get(SubjectORM, subject)
            if subject_orm is None:
                raise PyPermissionError(f"Subject ('{subject}') does not exist!")
            role_orm = db.get(RoleORM, role)
            if role_orm is None:
                raise PyPermissionError(f"Role ('{role}') does not exist!")

    def deassign_role(self, *, subject: str, role: str, db: Session) -> None:
        member_orm = db.get(MemberORM, (role, subject))
        if member_orm is None:
            subject_orm = db.get(SubjectORM, subject)
            if subject_orm is None:
                raise PyPermissionError(f"Subject ('{subject}') does not exist!")
            role_orm = db.get(RoleORM, role)
            if role_orm is None:
                raise PyPermissionError(f"Role ('{role}') does not exist!")
        db.delete(member_orm)
        db.flush()

    def get_assigned_roles(self, *, subject: str, db: Session) -> tuple[str, ...]:
        roles = db.scalars(
            select(MemberORM.role_id).where(MemberORM.subject_id == subject)
        ).all()
        if len(roles) == 0 and db.get(SubjectORM, subject) is None:
            raise PyPermissionError(f"Subject ('{subject}') does not exist!")
        return tuple(roles)

    def create_policy(
        self,
        *,
        policy: Policy,
        db: Session,
    ) -> None:
        try:
            policy_orm = PolicyORM(
                role_id=policy.role,
                resource_type=policy.permission.resource_type,
                resource_id=policy.permission.resource_id,
                action=policy.permission.action,
            )
            db.add(policy_orm)
            db.flush()
        except IntegrityError as err:
            db.rollback()
            # TODO 'psycopg.errors.UniqueViolation'

    def delete_policy(
        self,
        *,
        policy: Policy,
        db: Session,
    ) -> None: ...

    def check_subject_permission(
        self,
        subject: str,
        permission: Permission,
        db: Session,
    ) -> bool:
        root_cte = (
            select(MemberORM.role_id)
            .where(MemberORM.subject_id == subject)
            .cte(recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM.parent_role_id).join(
                traversing_cte, HierarchyORM.child_role_id == traversing_cte.c.role_id
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

    def check_role_permission(
        self,
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

    def get_subject_policies(self, *, subject: str, db: Session) -> tuple[Policy, ...]:
        root_cte = (
            select(MemberORM.role_id)
            .where(MemberORM.subject_id == subject)
            .cte(recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM.parent_role_id).join(
                traversing_cte, HierarchyORM.child_role_id == traversing_cte.c.role_id
            )
        )

        policy_orms = (
            db.scalars(
                select(PolicyORM).join(
                    relations_cte, PolicyORM.role_id == relations_cte.c.role_id
                )
            )
            .unique()
            .all()
        )

        return tuple(
            Policy(
                role=policy_orm.role_id,
                permission=Permission(
                    resource_type=policy_orm.resource_type,
                    resource_id=policy_orm.resource_id,
                    action=policy_orm.action,
                ),
            )
            for policy_orm in policy_orms
        )


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
