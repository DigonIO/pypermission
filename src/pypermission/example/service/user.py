from typing import Sequence

from sqlalchemy.sql import select

from pypermission.rbac import RBAC, Policy, Permission
from pypermission.example.models import UserORM, Context, ExampleError, State

################################################################################
#### UserService
################################################################################


class UserService:
    _rbac: RBAC

    def __init__(self, *, rbac: RBAC):
        self._rbac = rbac

    def create(
        self,
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

                if not self._rbac.check_subject_permission(
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

        self._create_role_and_policies(username=username, role=role, ctx=ctx)

        return user_orm

    def list(
        self,
        *,
        ctx: Context,
        rbac: bool = True,
    ) -> Sequence[UserORM]:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not self._rbac.check_subject_permission(
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

    def get(
        self,
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

                if not self._rbac.check_subject_permission(
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

    def set_email(
        self,
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

                if not self._rbac.check_subject_permission(
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

    def set_state(
        self,
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

                if not self._rbac.check_subject_permission(
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

    def delete(
        self,
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

                if not self._rbac.check_subject_permission(
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
        self._rbac.delete_role(role=USER_ROLE, db=ctx.db)
        self._rbac.delete_subject(subject=username, db=ctx.db)

        for group_orm in user_orm.group_orms:
            GROUP_ROLE__OWNER = f"group[{group_orm.groupname}]:owner"
            self._rbac.delete_role(role=GROUP_ROLE__OWNER, db=ctx.db)

        ctx.db.delete(user_orm)
        ctx.db.flush()

        return user_orm

    ################################################################################
    #### Util
    ################################################################################

    def _create_role_and_policies(self, username: str, role: str, ctx: Context) -> None:
        self._rbac.create_subject(subject=username, db=ctx.db)
        self._rbac.assign_role(role=role, subject=username, db=ctx.db)

        USER_ROLE = f"user[{username}]"
        self._rbac.create_role(role=USER_ROLE, db=ctx.db)
        self._rbac.assign_role(subject=username, role=USER_ROLE, db=ctx.db)

        self._rbac.create_policy(
            policy=Policy(
                role=USER_ROLE,
                permission=Permission(
                    resource_type="user", resource_id=username, action="access"
                ),
            ),
            db=ctx.db,
        )
        self._rbac.create_policy(
            policy=Policy(
                role=USER_ROLE,
                permission=Permission(
                    resource_type="user", resource_id=username, action="edit"
                ),
            ),
            db=ctx.db,
        )
        self._rbac.create_policy(
            policy=Policy(
                role=USER_ROLE,
                permission=Permission(
                    resource_type="user", resource_id=username, action="deactivate"
                ),
            ),
            db=ctx.db,
        )
