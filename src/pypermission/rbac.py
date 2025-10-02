from sqlalchemy.sql import select
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError


from pypermission.orm import BaseORM, RoleORM


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

    def get_roles(self, *, db: Session) -> tuple[str, ...]:
        roles_orm = db.scalars(select(RoleORM)).all()
        return tuple(role_orm.id for role_orm in roles_orm)

    def delete_role(self, *, role: str, db: Session) -> None:
        role_orm = db.get(RoleORM, role)
        if role_orm is None:
            return
        db.delete(role_orm)
        db.flush()


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
