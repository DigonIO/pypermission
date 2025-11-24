from typing import Literal, Sequence
from uuid import UUID

from sqlalchemy.sql import select

from pypermission import RBAC, Permission
from pypermission.example.model.user import UserORM
from pypermission.example.types import Context, ExampleError, State

type Role = Literal["guest", "user", "moderator"]

################################################################################
#### UserService
################################################################################


class UserService:
    @staticmethod
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
        UserService._create_role_and_policies(username=username, role=role, ctx=ctx)

        return user_orm

    @staticmethod
    def list(
        *,
        ctx: Context,
        rbac: bool = True,
    ) -> Sequence[UserORM]:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id="*", action="access"
                    ),
                    db=ctx.db,
                ):
                    raise ExampleError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise ExampleError("No user in context!")

        return ctx.db.scalars(select(UserORM)).all()

    @staticmethod
    def get(
        *,
        username: str,
        ctx: Context,
        rbac: bool = True,
    ) -> UserORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="access"
                    ),
                    db=ctx.db,
                ):
                    raise ExampleError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise ExampleError("No user in context!")

        user_orm = ctx.db.get(UserORM, username)
        if user_orm is None:
            raise ExampleError(f"Unknown user '{username}'!")
        return user_orm

    @staticmethod
    def set_email(
        *,
        username: str,
        email: str,
        ctx: Context,
        rbac: bool = True,
    ) -> UserORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="edit"
                    ),
                    db=ctx.db,
                ):
                    raise ExampleError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise ExampleError("No user in context!")

        user_orm = ctx.db.get(UserORM, username)
        if user_orm is None:
            raise ExampleError(f"Unknown user '{username}'!")
        user_orm.email = email
        ctx.db.flush()
        return user_orm

    @staticmethod
    def set_state(
        *,
        username: str,
        state: State,
        ctx: Context,
        rbac: bool = True,
    ) -> UserORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="deactivate"
                    ),
                    db=ctx.db,
                ):
                    raise ExampleError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise ExampleError("No user in context!")

        user_orm = ctx.db.get(UserORM, username)
        if user_orm is None:
            raise ExampleError(f"Unknown user '{username}'!")
        user_orm.state = state
        ctx.db.flush()
        return user_orm

    @staticmethod
    def delete(
        *,
        username: str,
        ctx: Context,
        rbac: bool = True,
    ) -> UserORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="delete"
                    ),
                    db=ctx.db,
                ):
                    raise ExampleError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise ExampleError("No user in context!")

        user_orm = ctx.db.get(UserORM, username)
        if user_orm is None:
            raise ExampleError(f"Unknown user '{username}'!")

        USER_ROLE = f"user[{username}]"
        RBAC.role.delete(role=USER_ROLE, db=ctx.db)
        RBAC.subject.delete(subject=username, db=ctx.db)

        for group_orm in user_orm.group_orms:
            GROUP_ROLE__OWNER = f"group[{group_orm.groupname}]:owner"
            RBAC.role.delete(role=GROUP_ROLE__OWNER, db=ctx.db)

        ctx.db.delete(user_orm)
        ctx.db.flush()

        return user_orm

    ################################################################################
    #### Util
    ################################################################################

    @staticmethod
    def _create_role_and_policies(username: str, role: str, ctx: Context) -> None:
        RBAC.subject.create(subject=f"User[{user.id}]", db=ctx.db)
        RBAC.subject.assign_role(role=role, subject=username, db=ctx.db)

        USER_ROLE = f"User[{user.id}]"
        RBAC.role.create(role=USER_ROLE, db=ctx.db)
        RBAC.subject.assign_role(subject=username, role=USER_ROLE, db=ctx.db)

        RBAC.role.grant_permission(
            role=USER_ROLE,
            permission=Permission(
                resource_type="user", resource_id=username, action="access"
            ),
            db=ctx.db,
        )
        RBAC.role.grant_permission(
            role=USER_ROLE,
            permission=Permission(
                resource_type="user", resource_id=username, action="edit"
            ),
            db=ctx.db,
        )
        RBAC.role.grant_permission(
            role=USER_ROLE,
            permission=Permission(
                resource_type="user", resource_id=username, action="deactivate"
            ),
            db=ctx.db,
        )
