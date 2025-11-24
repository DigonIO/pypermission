from enum import StrEnum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
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


class ExampleError(Exception): ...


class Context:
    user_orm: UserORM | None
    db: Session

    def __init__(self, *, user_orm: UserORM | None = None, db: Session):
        self.user_orm = user_orm
        self.db = db


type ApplicationRole = Literal["Guest", "User", "Moderator"]


class State(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


################################################################################
#### UserORM
################################################################################


class MeetDownORM(DeclarativeBase): ...


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
    role: ApplicationRole = "User",
    is_admin: bool = False,
    ctx: Context,
    rbac: bool = True,
) -> UserORM:
    # Permission check (check against the User in the Context).
    match rbac, ctx.user_orm:
        case True, UserORM(is_admin=True):
            # Pass the Permission check if the Context User is an admin.
            ...
        case True, UserORM():
            subject = f"User[{ctx.user_orm.id}]"
            permission = Permission(
                resource_type="User", resource_id="", action="create"
            )
            create_adm_or_mod = is_admin or (role == "Moderator")
            if create_adm_or_mod or not RBAC.subject.check_permission(
                subject=subject,
                permission=permission,
                db=ctx.db,
            ):
                raise ExampleError(
                    f"Permission '{permission}' not granted for Subject '{subject}'!"
                )
        case True, None:
            raise ExampleError("No User in Context!")
        case False, _:
            # Pass the Permission check if the 'rbac' flag is disabled!
            ...

    # Create the application level Resource for the User.
    user_orm = UserORM(username=username, email=email, role=role)
    ctx.db.add(user_orm)
    ctx.db.flush()

    # Create all RBAC level Resources for the User.
    create_role_and_policies(user_orm=user_orm, role=role, ctx=ctx)

    return user_orm


def get(
    *,
    user_id: UUID,
    ctx: Context,
    rbac: bool = True,
) -> UserORM:
    # Permission check (check against the User in the Context).
    match rbac, ctx.user_orm:
        case True, UserORM(is_admin=True):
            ...
            # Pass the Permission check if the Context User is an admin.
        case True, UserORM():
            subject = f"User[{ctx.user_orm.id}]"
            permission = Permission(
                resource_type="User",
                resource_id=str(user_id),
                action="access",
            )

            if not RBAC.subject.check_permission(
                subject=subject,
                permission=permission,
                db=ctx.db,
            ):
                raise ExampleError(
                    f"Permission '{permission}' not granted for Subject '{subject}'!"
                )
        case True, None:
            raise ExampleError("No User in Context!")
        case False, _:
            # Pass the Permission check if the 'rbac' flag is disabled!
            ...

    user_orm = ctx.db.get(UserORM, user_id)
    if user_orm is None:
        raise ExampleError(f"Unknown User with ID '{user_id}'!")

    return user_orm


def delete(
    *,
    user_id: UUID,
    ctx: Context,
    rbac: bool = True,
) -> UserORM:
    # Permission check (check against the User in the Context).
    match rbac, ctx.user_orm:
        case True, UserORM(is_admin=True, id=admin_id):
            if admin_id == user_id:
                raise ExampleError("An admin can't delete itself!")
            # Pass the Permission check if the Context User is an admin.
        case True, UserORM():
            subject = f"User[{ctx.user_orm.id}]"
            permission = Permission(
                resource_type="User",
                resource_id=str(user_id),
                action="delete",
            )

            if not RBAC.subject.check_permission(
                subject=subject,
                permission=permission,
                db=ctx.db,
            ):
                raise ExampleError(
                    f"Permission '{permission}' not granted for Subject '{subject}'!"
                )
        case True, None:
            raise ExampleError("No User in context!")
        case False, _:
            # Pass the Permission check if the 'rbac' flag is disabled!
            ...

    user_orm = ctx.db.get(UserORM, user_id)
    if user_orm is None:
        raise ExampleError(f"Unknown User with ID '{user_id}'!")

    # Delete all RBAC level Resources for the User.
    USER_UUID = f"User[{user_id}]"
    RBAC.role.delete(role=USER_UUID, db=ctx.db)
    RBAC.subject.delete(subject=USER_UUID, db=ctx.db)

    # Delete the application level Resource for the User.
    ctx.db.delete(user_orm)
    ctx.db.flush()

    return user_orm


################################################################################
#### UserService Util
################################################################################


def create_role_and_policies(
    user_orm: UserORM, role: ApplicationRole, ctx: Context
) -> None:
    USER_UUID = f"User[{user_orm.id}]"

    # Create the instance exclusive Subject for the User.
    RBAC.subject.create(subject=USER_UUID, db=ctx.db)

    # Assign the application Role 'Guest' | 'User' | 'Moderator'.
    RBAC.subject.assign_role(subject=USER_UUID, role=role, db=ctx.db)

    # Create and assign the instance exclusive Role for the User.
    RBAC.role.create(role=USER_UUID, db=ctx.db)
    RBAC.subject.assign_role(subject=USER_UUID, role=USER_UUID, db=ctx.db)

    # Grand all instance exclusive Permissions for the User.
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


################################################################################
#### Population
################################################################################


def populate(*, ctx: Context) -> None:
    create_roles(ctx=ctx)
    create_hierarchies(ctx=ctx)

    create_guest_role_policies(ctx=ctx)
    create_user_role_policies(ctx=ctx)
    create_moderator_role_policies(ctx=ctx)


def create_roles(*, ctx: Context) -> None:
    RBAC.role.create(role="guest", db=ctx.db)
    RBAC.role.create(role="user", db=ctx.db)
    RBAC.role.create(role="moderator", db=ctx.db)


def create_hierarchies(*, ctx: Context) -> None:
    RBAC.role.add_hierarchy(
        parent_role="guest",
        child_role="user",
        db=ctx.db,
    )


def create_guest_role_policies(*, ctx: Context) -> None:
    RBAC.role.grant_permission(
        role="guest",
        permission=Permission(
            resource_type="group",
            resource_id="*",
            action="access",
        ),
        db=ctx.db,
    )


def create_user_role_policies(*, ctx: Context) -> None:
    RBAC.role.grant_permission(
        role="user",
        permission=Permission(
            resource_type="base",
            resource_id="",
            action="group:create",
        ),
        db=ctx.db,
    )


def create_moderator_role_policies(*, ctx: Context) -> None:
    RBAC.role.grant_permission(
        role="moderator",
        permission=Permission(
            resource_type="base",
            resource_id="",
            action="user:create",
        ),
        db=ctx.db,
    )
    RBAC.role.grant_permission(
        role="moderator",
        permission=Permission(
            resource_type="user",
            resource_id="*",
            action="access",
        ),
        db=ctx.db,
    )
    RBAC.role.grant_permission(
        role="moderator",
        permission=Permission(
            resource_type="user",
            resource_id="*",
            action="edit",
        ),
        db=ctx.db,
    )
    RBAC.role.grant_permission(
        role="moderator",
        permission=Permission(
            resource_type="user",
            resource_id="*",
            action="deactivate",
        ),
        db=ctx.db,
    )
    RBAC.role.grant_permission(
        role="moderator",
        permission=Permission(
            resource_type="group",
            resource_id="*",
            action="deactivate",
        ),
        db=ctx.db,
    )
