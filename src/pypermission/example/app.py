from sqlalchemy.engine.base import Engine

from pypermission.rbac import RBAC, Policy, Permission
from pypermission.example.models import Context
from pypermission.example.service.user import UserService
from pypermission.example.service.group import GroupService


class ExampleApp:
    _rbac: RBAC
    _user: UserService
    _group: GroupService

    def __init__(self, *, engine: Engine) -> None:
        self._rbac = RBAC(engine=engine)
        self._user = UserService(rbac=self._rbac)
        self._group = GroupService(rbac=self._rbac)

    # NOTE RBAC is only exposed here for testing purposes.
    # In a real application, the RBAC API should be wrapped with business logic.
    @property
    def rbac(self) -> RBAC:
        return self._rbac

    @property
    def user(self) -> UserService:
        return self._user

    @property
    def group(self) -> GroupService:
        return self._group

    def populate_example(self, *, ctx: Context) -> None:
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

        ctx.db.commit()

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

    def _create_moderator_role_policies(self, ctx: Context) -> None:
        self.rbac.create_policy(
            policy=Policy(
                role="moderator",
                permission=Permission(
                    resource_type="base",
                    resource_id="",
                    action="user:create",
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
