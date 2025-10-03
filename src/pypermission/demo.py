from typing import Literal

from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine

from pypermission.rbac import RBAC, Policy, Permission


# "Emma"
# "James"
# "Sophia"
# "Henry"
# "Charlotte"
# "Benjamin"
# "Olivia"
# "Thomas"


class DemoError(Exception): ...


class Context:
    username: str | None
    db: Session

    def __init__(self, *, user: str | None = None, db: Session):
        self.username = user
        self.db = db


class User:
    username: str
    email: str
    role: str
    state: Literal["active", "inactive"] = "active"

    def __init__(
        self,
        *,
        username: str,
        email: str,
        role: str,
    ):
        self.username = username
        self.email = email
        self.role = role


class Group:
    groupname: str
    description: str
    owner: str
    state: Literal["active", "inactive"] = "active"

    def __init__(
        self,
        *,
        groupname: str,
        description: str,
        owner: str,
    ):
        self.groupname = groupname
        self.description = description
        self.owner = owner


class DemoApp:
    rbac: RBAC

    _users: dict[str, User] = {}
    _groups: dict[str, Group] = {}

    def __init__(self, *, engine: Engine) -> None:
        self.rbac = RBAC(engine=engine)

    def create_user(
        self,
        *,
        username: str,
        email: str,
        role: str = "guest",
        ctx: Context,
        rbac: bool = True,
    ) -> User:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="base", resource_id="", action="user:create"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        user = User(username=username, email=email, role=role)
        self._users[username] = user

        self._create_user_role_and_policies(username=username, role=role, ctx=ctx)

        return user

    def get_user(
        self,
        *,
        username: str,
        ctx: Context,
        rbac: bool = True,
    ) -> User:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="access"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            return self._users[username]
        except KeyError:
            raise DemoError(f"Unknown user '{username}'!")

    def edit_user_email(
        self,
        *,
        username: str,
        email: str,
        ctx: Context,
        rbac: bool = True,
    ) -> User:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="edit"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            user = self._users[username]
            user.email = email
            return user
        except KeyError:
            raise DemoError(f"Unknown user '{username}'!")

    def set_user_state(
        self,
        *,
        username: str,
        state: Literal["active", "inactive"],
        ctx: Context,
        rbac: bool = True,
    ) -> User:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="deactivate"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            user = self._users[username]
            user.state = state
            return user
        except KeyError:
            raise DemoError(f"Unknown user '{username}'!")

    def delete_user(
        self,
        *,
        username: str,
        ctx: Context,
        rbac: bool = True,
    ) -> User:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="user", resource_id=username, action="delete"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            user = self._users[username]

            USER_ROLE = f"user[{username}]"
            self.rbac.delete_role(role=USER_ROLE, db=ctx.db)
            self.rbac.delete_subject(subject=username, db=ctx.db)

            groups = tuple(
                group
                for groupname, group in self._groups.items()
                if group.owner == username
            )
            for group in groups:
                self.delete_group(groupname=group.groupname, ctx=ctx, rbac=False)

            del self._users[username]
            return user
        except KeyError:
            raise DemoError(f"Unknown user '{username}'!")

    def create_group(
        self,
        *,
        groupname: str,
        description: str = "A new group.",
        owner: str,
        ctx: Context,
        rbac: bool = True,
    ) -> Group:
        match rbac, owner, ctx.username:
            case True, str(), str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")
                if ctx.username != owner:
                    raise DemoError(
                        f"User '{ctx.username}' cannot create a group on behalf of '{owner}'."
                    )

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="base",
                        resource_id="",
                        action="group:create",
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case True, str(), None:
                raise DemoError("No user in context!")
            case False, str(), None:
                ...
            case False, str(), str():
                ...
            case _:
                raise DemoError("Invalid combination of arguments!")

        group = Group(groupname=groupname, description=description, owner=owner)
        self._create_group_role_and_policies(groupname=groupname, owner=owner, ctx=ctx)
        return group

    def get_group(
        self,
        *,
        groupname: str,
        ctx: Context,
        rbac: bool = True,
    ) -> Group:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group", resource_id=groupname, action="access"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            return self._groups[groupname]
        except KeyError:
            raise DemoError(f"Unknown group '{groupname}'!")

    def edit_group_description(
        self,
        *,
        groupname: str,
        description: str,
        ctx: Context,
        rbac: bool = True,
    ) -> Group:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group", resource_id=groupname, action="edit"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            group = self._groups[groupname]
            group.description = description
            return group
        except KeyError:
            raise DemoError(f"Unknown group '{groupname}'!")

    def set_group_state(
        self,
        *,
        groupname: str,
        state: Literal["active", "inactive"],
        ctx: Context,
        rbac: bool = True,
    ) -> Group:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group",
                        resource_id=groupname,
                        action="deactivate",
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            group = self._groups[groupname]
            group.state = state
            return group
        except KeyError:
            raise DemoError(f"Unknown group '{groupname}'!")

    def delete_group(
        self,
        *,
        groupname: str,
        ctx: Context,
        rbac: bool = True,
    ) -> Group:

        match rbac, ctx.username:
            case True, str():
                if ctx.username not in self._users:
                    raise DemoError(f"Unknown user '{ctx.username}' in context!")

                if not self.rbac.check_subject_permission(
                    subject=ctx.username,
                    permission=Permission(
                        resource_type="group", resource_id=groupname, action="delete"
                    ),
                    db=ctx.db,
                ):
                    raise DemoError("Permission not granted!")
            case False, None:
                ...
            case False, str():
                ...
            case True, None:
                raise DemoError("No user in context!")

        try:
            group = self._groups[groupname]

            GROUP_ROLE__OWNER = f"group[{groupname}]:owner"
            self.rbac.delete_role(role=GROUP_ROLE__OWNER, db=ctx.db)

            del self._groups[groupname]
            return group
        except KeyError:
            raise DemoError(f"Unknown group '{groupname}'!")

    def populate_scenario(self, *, ctx: Context) -> None:
        self.rbac.create_role(role="admin", db=ctx.db)
        self.rbac.create_role(role="moderator", db=ctx.db)
        self.rbac.create_role(role="user", db=ctx.db)
        self.rbac.create_role(role="guest", db=ctx.db)

        self.rbac.add_role_hierarchy(
            parent_role="guest",
            child_role="user",
            db=ctx.db,
        )
        self.rbac.add_role_hierarchy(
            parent_role="user",
            child_role="moderator",
            db=ctx.db,
        )
        self.rbac.add_role_hierarchy(
            parent_role="moderator",
            child_role="admin",
            db=ctx.db,
        )

        self._create_guest_role_policies(ctx=ctx)
        self._create_user_role_policies(ctx=ctx)
        self._create_moderator_role_policies(ctx=ctx)
        self._create_admin_role_policies(ctx=ctx)

        self.create_user(
            username="Emma",
            email="emma@digon.io",
            role="admin",
            ctx=ctx,
            rbac=False,
        )
        self.create_user(
            username="James",
            email="james@digon.io",
            role="moderator",
            ctx=ctx,
            rbac=False,
        )

    def _create_guest_role_policies(self, ctx: Context) -> None:
        self.rbac.create_policy(
            policy=Policy(
                role="guest",
                permission=Permission(
                    resource_type="group",
                    resource_id="*",
                    action="access",
                ),
            ),
            db=ctx.db,
        )

    def _create_user_role_policies(self, ctx: Context) -> None:
        self.rbac.create_policy(
            policy=Policy(
                role="user",
                permission=Permission(
                    resource_type="base",
                    resource_id="",
                    action="group:create",
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role="moderator",
                permission=Permission(
                    resource_type="group",
                    resource_id="*",
                    action="deactivate",
                ),
            ),
            db=ctx.db,
        )

    def _create_moderator_role_policies(self, ctx: Context) -> None:
        self.rbac.create_policy(
            policy=Policy(
                role="moderator",
                permission=Permission(
                    resource_type="user",
                    resource_id="*",
                    action="access",
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role="moderator",
                permission=Permission(
                    resource_type="user",
                    resource_id="*",
                    action="edit",
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role="moderator",
                permission=Permission(
                    resource_type="user",
                    resource_id="*",
                    action="deactivate",
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role="moderator",
                permission=Permission(
                    resource_type="group",
                    resource_id="*",
                    action="deactivate",
                ),
            ),
            db=ctx.db,
        )

    def _create_admin_role_policies(self, ctx: Context) -> None:
        self.rbac.create_policy(
            policy=Policy(
                role="admin",
                permission=Permission(
                    resource_type="base",
                    resource_id="",
                    action="rbac",
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role="admin",
                permission=Permission(
                    resource_type="user",
                    resource_id="*",
                    action="delete",
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role="admin",
                permission=Permission(
                    resource_type="group",
                    resource_id="*",
                    action="delete",
                ),
            ),
            db=ctx.db,
        )

    def _create_user_role_and_policies(
        self, username: str, role: str, ctx: Context
    ) -> None:
        self.rbac.create_subject(subject=username, db=ctx.db)
        self.rbac.assign_role(role=role, subject=username, db=ctx.db)

        USER_ROLE = f"user[{username}]"
        self.rbac.create_role(role=USER_ROLE, db=ctx.db)
        self.rbac.assign_role(subject=username, role=USER_ROLE, db=ctx.db)

        self.rbac.create_policy(
            policy=Policy(
                role=USER_ROLE,
                permission=Permission(
                    resource_type="user", resource_id=username, action="access"
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role=USER_ROLE,
                permission=Permission(
                    resource_type="user", resource_id=username, action="edit"
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role=USER_ROLE,
                permission=Permission(
                    resource_type="user", resource_id=username, action="deactivate"
                ),
            ),
            db=ctx.db,
        )

    def _create_group_role_and_policies(
        self, groupname: str, owner: str, ctx: Context
    ) -> None:
        GROUP_ROLE__OWNER = f"group[{groupname}]:owner"
        self.rbac.create_role(role=GROUP_ROLE__OWNER, db=ctx.db)
        self.rbac.assign_role(subject=owner, role=GROUP_ROLE__OWNER, db=ctx.db)

        self.rbac.create_policy(
            policy=Policy(
                role=GROUP_ROLE__OWNER,
                permission=Permission(
                    resource_type="group", resource_id=groupname, action="edit"
                ),
            ),
            db=ctx.db,
        )
        self.rbac.create_policy(
            policy=Policy(
                role=GROUP_ROLE__OWNER,
                permission=Permission(
                    resource_type="group", resource_id=groupname, action="deactivate"
                ),
            ),
            db=ctx.db,
        )
