from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pypermission.models import (
    Policy,
    Permission,
    RoleORM,
    HierarchyORM,
    SubjectORM,
    MemberORM,
    PolicyORM,
    FrozenClass,
)
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError

################################################################################
#### SubjectService
################################################################################


class SubjectService(metaclass=FrozenClass):

    @classmethod
    def create(cls, *, subject: str, db: Session) -> None:
        try:
            subject_orm = SubjectORM(id=subject)
            db.add(subject_orm)
            db.flush()
        except IntegrityError:
            db.rollback()

    @classmethod
    def delete(cls, *, subject: str, db: Session) -> None:
        subject_orm = db.get(SubjectORM, subject)
        if subject_orm is None:
            return
        db.delete(subject_orm)
        db.flush()

    @classmethod
    def list(cls, *, db: Session) -> tuple[str, ...]:
        subjects = db.scalars(select(SubjectORM.id)).all()
        return tuple(subject for subject in subjects)

    @classmethod
    def assign_role(cls, *, subject: str, role: str, db: Session) -> None:
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

    @classmethod
    def deassign_role(cls, *, subject: str, role: str, db: Session) -> None:
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

    @classmethod
    def assigned_roles(cls, *, subject: str, db: Session) -> tuple[str, ...]:
        roles = db.scalars(
            select(MemberORM.role_id).where(MemberORM.subject_id == subject)
        ).all()
        if len(roles) == 0 and db.get(SubjectORM, subject) is None:
            raise PyPermissionError(f"Subject ('{subject}') does not exist!")
        return tuple(roles)

    @classmethod
    def check_permission(
        cls,
        *,
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

    @classmethod
    def assert_permission(
        cls,
        *,
        subject: str,
        permission: Permission,
        db: Session,
    ) -> None:
        if not cls.check_permission(subject=subject, permission=permission, db=db):
            raise PyPermissionNotGrantedError()

    @classmethod
    def permissions(cls, *, subject: str, db: Session) -> tuple[Permission, ...]:
        # TODO
        return tuple()

    @classmethod
    def policies(cls, *, subject: str, db: Session) -> tuple[Policy, ...]:
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
