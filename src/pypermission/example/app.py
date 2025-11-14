from typing import Final

from sqlalchemy.engine.base import Engine

from pypermission import RBAC
from pypermission.db import create_rbac_database_table
from pypermission.example.models import Context
from pypermission.example.service.group import GroupService
from pypermission.example.service.user import UserService
from pypermission.models import Permission


class ExampleApp:
    _user: Final = UserService
    _group: Final = GroupService

    def __init__(self, *, engine: Engine) -> None:
        create_rbac_database_table(engine=engine)

    @property
    def user(self) -> type[UserService]:
        return self._user

    @property
    def group(self) -> type[GroupService]:
        return self._group

    def populate_example(self, *, ctx: Context) -> None:
        RBAC.role.create(role="admin", db=ctx.db)
        RBAC.role.create(role="moderator", db=ctx.db)
        RBAC.role.create(role="user", db=ctx.db)
        RBAC.role.create(role="guest", db=ctx.db)

        RBAC.role.add_hierarchy(
            parent_role="guest",
            child_role="user",
            db=ctx.db,
        )
        RBAC.role.add_hierarchy(
            parent_role="user",
            child_role="moderator",
            db=ctx.db,
        )
        RBAC.role.add_hierarchy(
            parent_role="moderator",
            child_role="admin",
            db=ctx.db,
        )

        self._create_guest_role_policies(ctx=ctx)
        self._create_user_role_policies(ctx=ctx)
        self._create_moderator_role_policies(ctx=ctx)
        self._create_admin_role_policies(ctx=ctx)

        ctx.db.flush()

        self.user.create(
            username="Alex",
            email="alex@digon.io",
            role="admin",
            ctx=ctx,
            rbac=False,
        )
        self.user.create(
            username="Max",
            email="max@digon.io",
            role="moderator",
            ctx=ctx,
            rbac=False,
        )
        self.user.create(
            username="Ulrich",
            email="urlich@digon.io",
            role="user",
            ctx=ctx,
            rbac=False,
        )
        self.user.create(
            username="Uwe",
            email="Uwe@digon.io",
            role="user",
            ctx=ctx,
            rbac=False,
        )
        self.user.create(
            username="Georg",
            email="Georg@digon.io",
            role="guest",
            ctx=ctx,
            rbac=False,
        )

        self.group.create(
            groupname="BEF",
            description="Bergisches Entwicklerforum",
            owner="Alex",
            ctx=ctx,
            rbac=False,
        )
        self.group.create(
            groupname="PUGW",
            description="Python User Group Wuppertal",
            owner="Uwe",
            ctx=ctx,
            rbac=False,
        )
        ctx.db.flush()

    def _create_guest_role_policies(self, ctx: Context) -> None:
        RBAC.role.grant_permission(
            role="guest",
            permission=Permission(
                resource_type="group",
                resource_id="*",
                action="access",
            ),
            db=ctx.db,
        )

    def _create_user_role_policies(self, ctx: Context) -> None:
        RBAC.role.grant_permission(
            role="user",
            permission=Permission(
                resource_type="base",
                resource_id="",
                action="group:create",
            ),
            db=ctx.db,
        )

    def _create_moderator_role_policies(self, ctx: Context) -> None:
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

    def _create_admin_role_policies(self, ctx: Context) -> None:
        RBAC.role.grant_permission(
            role="admin",
            permission=Permission(
                resource_type="base",
                resource_id="",
                action="rbac",
            ),
            db=ctx.db,
        )
        RBAC.role.grant_permission(
            role="admin",
            permission=Permission(
                resource_type="user",
                resource_id="*",
                action="delete",
            ),
            db=ctx.db,
        )
        RBAC.role.grant_permission(
            role="admin",
            permission=Permission(
                resource_type="group",
                resource_id="*",
                action="delete",
            ),
            db=ctx.db,
        )
