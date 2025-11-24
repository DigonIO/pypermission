from typing import Final

from sqlalchemy.engine.base import Engine
from sqlalchemy.event import contains
from sqlalchemy.orm import sessionmaker

from pypermission import RBAC
from pypermission.db import create_rbac_database_table, set_sqlite_pragma
from pypermission.example.exc import MeetDownError
from pypermission.example.model.orm import MeetDownORM
from pypermission.example.service.event import EventService
from pypermission.example.service.group import GroupService
from pypermission.example.service.user import UserService
from pypermission.example.types import Context
from pypermission.models import Permission


class MeetDownApp:
    user: Final = UserService
    group: Final = GroupService
    event: Final = EventService

    def __init__(self, *, engine: Engine) -> None:
        create_rbac_database_table(engine=engine)
        self._create_meetdown_database_table(engine=engine)

        db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        with db_factory.begin() as db:
            ctx = Context(db=db)
            self._initialize_application_rbac_data(ctx=ctx)

    def _create_meetdown_database_table(self, *, engine: Engine) -> None:
        if engine.driver == "pysqlite" and not contains(
            engine, "connect", set_sqlite_pragma
        ):
            raise MeetDownError(
                "Foreign keys pragma appears to not be set! Please use the 'set_sqlite_pragma' function"
                " on your SQLite engine before interacting with the database!"
            )

        MeetDownORM.metadata.create_all(bind=engine)

    def _initialize_application_rbac_data(self, *, ctx: Context) -> None:
        self._create_roles(ctx=ctx)
        self._create_hierarchies(ctx=ctx)

        self._create_guest_role_policies(ctx=ctx)
        self._create_user_role_policies(ctx=ctx)
        self._create_moderator_role_policies(ctx=ctx)

        ctx.db.flush()

    def _create_roles(self, *, ctx: Context) -> None:
        RBAC.role.create(role="guest", db=ctx.db)
        RBAC.role.create(role="user", db=ctx.db)
        RBAC.role.create(role="moderator", db=ctx.db)

    def _create_hierarchies(self, *, ctx: Context) -> None:
        RBAC.role.add_hierarchy(
            parent_role="guest",
            child_role="user",
            db=ctx.db,
        )

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
