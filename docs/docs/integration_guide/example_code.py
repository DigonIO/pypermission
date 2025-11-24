from enum import StrEnum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from uuid import UUID
from uuid import UUID
from typing import Literal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Enum as SqlEnum
from sqlalchemy.sql.sqltypes import UUID as SqlUUID
from sqlalchemy.sql.sqltypes import String, Boolean
from pypermission import RBAC, Permission


################################################################################
#### Types
################################################################################


class MeetDownORM(DeclarativeBase): ...


class ExampleError(Exception): ...


class Context:
    user_orm: UserORM | None
    db: Session

    def __init__(self, *, user_orm: UserORM | None = None, db: Session):
        self.user_orm = user_orm
        self.db = db


type Role = Literal["guest", "user", "moderator"]


class State(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


################################################################################
#### UserORM
################################################################################


class UserORM(MeetDownORM):
    __tablename__ = "app_user_table"
    id: Mapped[UUID] = mapped_column(SqlUUID, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean)
    state: Mapped[State] = mapped_column(
        SqlEnum(State, name="UserORM.State"), default=State.ACTIVE
    )


################################################################################
#### UserService
################################################################################


def create(
    *,
    username: str,
    email: str,
    role: Role = "user",
    is_admin: bool = False,
    ctx: Context,
    rbac: bool = True,
) -> UserORM:
    is_adm_or_mod = is_admin or (role == "moderator")

    match rbac, ctx.user_orm:
        case True, UserORM(is_admin=True):
            ...
        case True, UserORM():
            subject = f"User[{ctx.user_orm.id}]"
            permission = Permission(
                resource_type="User", resource_id="", action="create"
            )
            if is_adm_or_mod or not RBAC.subject.check_permission(
                subject=subject,
                permission=permission,
                db=ctx.db,
            ):
                raise ExampleError(
                    f"Permission '{permission}' not granted for Subject '{subject}'!"
                )
        case True, None:
            raise ExampleError("No 'user_id' in Context!")
        case False, _:
            ...

    user_orm = UserORM(username=username, email=email, role=role)
    ctx.db.add(user_orm)
    ctx.db.flush()
    create_role_and_policies(user_orm=user_orm, role=role, ctx=ctx)
    return user_orm


################################################################################
#### UserService Util
################################################################################


def create_role_and_policies(user_orm: UserORM, role: str, ctx: Context) -> None:
    USER_UUID = f"User[{user_orm.id}]"

    RBAC.subject.create(subject=USER_UUID, db=ctx.db)
    RBAC.subject.assign_role(role=role, subject=user_orm.username, db=ctx.db)

    RBAC.role.create(role=USER_UUID, db=ctx.db)
    RBAC.subject.assign_role(subject=USER_UUID, role=USER_UUID, db=ctx.db)

    RBAC.role.grant_permission(
        role=USER_UUID,
        permission=Permission(
            resource_type="User", resource_id=str(user_orm.id), action="access"
        ),
        db=ctx.db,
    )
    RBAC.role.grant_permission(
        role=USER_UUID,
        permission=Permission(
            resource_type="User", resource_id=str(user_orm.id), action="edit"
        ),
        db=ctx.db,
    )
    RBAC.role.grant_permission(
        role=USER_UUID,
        permission=Permission(
            resource_type="User", resource_id=str(user_orm.id), action="deactivate"
        ),
        db=ctx.db,
    )
