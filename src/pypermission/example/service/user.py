from typing import Sequence

from sqlalchemy.sql import select

from pypermission import RBAC, Permission
from pypermission.example.models import Context, ExampleError, State, UserORM

################################################################################
#### UserService
################################################################################


class UserService:
    @classmethod
    def create(
        cls,
        *,
        username: str,
        email: str,
        role: str = "guest",
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
                        resource_type="base", resource_id="", action="user:create"
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

        user_orm = UserORM(username=username, email=email, role=role)
        ctx.db.add(user_orm)
        ctx.db.flush()

        cls._create_role_and_policies(username=username, role=role, ctx=ctx)

        return user_orm

    @classmethod
    def list(
        cls,
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

    @classmethod
    def get(
        cls,
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

    @classmethod
    def set_email(
        cls,
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

    @classmethod
    def set_state(
        cls,
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

    @classmethod
    def delete(
        cls,
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

    @classmethod
    def _create_role_and_policies(cls, username: str, role: str, ctx: Context) -> None:
        RBAC.subject.create(subject=username, db=ctx.db)
        RBAC.subject.assign_role(role=role, subject=username, db=ctx.db)

        USER_ROLE = f"user[{username}]"
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
