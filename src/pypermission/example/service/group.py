from typing import Sequence

from sqlalchemy.sql import select

from pypermission.rbac import RBAC, Policy, Permission
from pypermission.example.models import UserORM, GroupORM, Context, ExampleError, State

################################################################################
#### UserService
################################################################################


class GroupService:
    _rbac: RBAC

    def __init__(self, *, rbac: RBAC):
        self._rbac = rbac

    def create(
        self,
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

                if not self._rbac.check_subject_permission(
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
        self._create_group_role_and_policies(groupname=groupname, owner=owner, ctx=ctx)
        return group_orm

    def list(
        self,
        *,
        ctx: Context,
        rbac: bool = True,
    ) -> Sequence[GroupORM]:

        match rbac, ctx.username:
            case True, str():
                # NOTE Only needed, because no real authentication is present.
                if ctx.db.get(UserORM, ctx.username) is None:
                    raise ExampleError(f"Unknown user '{ctx.username}' in context!")

                if not self._rbac.check_subject_permission(
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

    def get(
        self,
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

                if not self._rbac.check_subject_permission(
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

    def set_description(
        self,
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

                if not self._rbac.check_subject_permission(
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

    def set_state(
        self,
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

                if not self._rbac.check_subject_permission(
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

    def delete(
        self,
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

                if not self._rbac.check_subject_permission(
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
        self._rbac.delete_role(role=GROUP_ROLE__OWNER, db=ctx.db)

        ctx.db.delete(group_orm)
        ctx.db.flush()
        return group_orm

    ################################################################################
    #### Util
    ################################################################################

    def _create_group_role_and_policies(
        self, groupname: str, owner: str, ctx: Context
    ) -> None:
        GROUP_ROLE__OWNER = f"group[{groupname}]:owner"
        self._rbac.create_role(role=GROUP_ROLE__OWNER, db=ctx.db)
        self._rbac.assign_role(subject=owner, role=GROUP_ROLE__OWNER, db=ctx.db)

        self._rbac.create_policy(
            policy=Policy(
                role=GROUP_ROLE__OWNER,
                permission=Permission(
                    resource_type="group", resource_id=groupname, action="edit"
                ),
            ),
            db=ctx.db,
        )
        self._rbac.create_policy(
            policy=Policy(
                role=GROUP_ROLE__OWNER,
                permission=Permission(
                    resource_type="group", resource_id=groupname, action="deactivate"
                ),
            ),
            db=ctx.db,
        )
