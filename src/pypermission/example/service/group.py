from typing import Sequence

from sqlalchemy.sql import select

from pypermission import RBAC, Permission
from pypermission.example.models import Context, ExampleError, GroupORM, State, UserORM

################################################################################
#### UserService
################################################################################


class GroupService:

    @classmethod
    def create(
        cls,
        *,
        groupname: str,
        description: str = "A new group.",
        owner: str,
        ctx: Context,
        rbac: bool = True,
    ) -> GroupORM:
        match rbac, owner, ctx.username:
            case True, str(), str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if ctx.username != owner:
                    raise ExampleError(
                        f"User '{ctx.username}' cannot create a group on behalf of '{owner}'."
                    )

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="base",
                        resource_id="",
                        action="group:create",
                    ),
                    db=ctx.db,
                ):
                    raise ExampleError("Permission not granted!")
            case True, str(), None:
                raise ExampleError("No user in context!")
            case False, str(), None:
                ...
            case False, str(), str():
                ...
            case _:
                raise ExampleError("Invalid combination of arguments!")

        group_orm = GroupORM(groupname=groupname, description=description, owner=owner)
        ctx.db.add(group_orm)
        cls._create_group_role_and_policies(groupname=groupname, owner=owner, ctx=ctx)
        return group_orm

    @classmethod
    def list(
        cls,
        *,
        ctx: Context,
        rbac: bool = True,
    ) -> Sequence[GroupORM]:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group", resource_id="*", action="access"
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

        return ctx.db.scalars(select(GroupORM)).all()

    @classmethod
    def get(
        cls,
        *,
        groupname: str,
        ctx: Context,
        rbac: bool = True,
    ) -> GroupORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group", resource_id=groupname, action="access"
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

        group_orm = ctx.db.get(GroupORM, groupname)
        if group_orm is None:
            raise ExampleError(f"Unknown group '{groupname}'!")
        return group_orm

    @classmethod
    def set_description(
        cls,
        *,
        groupname: str,
        description: str,
        ctx: Context,
        rbac: bool = True,
    ) -> GroupORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group", resource_id=groupname, action="edit"
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

        group_orm = ctx.db.get(GroupORM, groupname)
        if group_orm is None:
            raise ExampleError(f"Unknown group '{groupname}'!")
        group_orm.description = description
        ctx.db.flush()
        return group_orm

    @classmethod
    def set_state(
        cls,
        *,
        groupname: str,
        state: State,
        ctx: Context,
        rbac: bool = True,
    ) -> GroupORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group",
                        resource_id=groupname,
                        action="deactivate",
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

        group_orm = ctx.db.get(GroupORM, groupname)
        if group_orm is None:
            raise ExampleError(f"Unknown group '{groupname}'!")
        group_orm.state = state
        ctx.db.flush()
        return group_orm

    @classmethod
    def delete(
        cls,
        *,
        groupname: str,
        ctx: Context,
        rbac: bool = True,
    ) -> GroupORM:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not RBAC.subject.check_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group", resource_id=groupname, action="delete"
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

        group_orm = ctx.db.get(GroupORM, groupname)
        if group_orm is None:
            raise ExampleError(f"Unknown group '{groupname}'!")

        GROUP_ROLE__OWNER = f"group[{groupname}]:owner"
        RBAC.role.delete(role=GROUP_ROLE__OWNER, db=ctx.db)

        ctx.db.delete(group_orm)
        ctx.db.flush()
        return group_orm

    ################################################################################
    #### Util
    ################################################################################

    @classmethod
    def _create_group_role_and_policies(
        cls, groupname: str, owner: str, ctx: Context
    ) -> None:
        GROUP_ROLE__OWNER = f"group[{groupname}]_owner"
        RBAC.role.create(role=GROUP_ROLE__OWNER, db=ctx.db)
        RBAC.subject.assign_role(subject=owner, role=GROUP_ROLE__OWNER, db=ctx.db)

        RBAC.role.grant_permission(
            role=GROUP_ROLE__OWNER,
            permission=Permission(
                resource_type="group", resource_id=groupname, action="edit"
            ),
            db=ctx.db,
        )
        RBAC.role.grant_permission(
            role=GROUP_ROLE__OWNER,
            permission=Permission(
                resource_type="group", resource_id=groupname, action="deactivate"
            ),
            db=ctx.db,
        )
