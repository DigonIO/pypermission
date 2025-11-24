from pypermission.example.service.group import GroupService
from pypermission.example.service.user import UserService
from pypermission.example.types import Context

# from pypermission.example.service.event import EventService


def populate_scenario(*, ctx: Context) -> None:
    UserService.create(
        username="Alex",
        email="alex@digon.io",
        role="admin",
        ctx=ctx,
        rbac=False,
    )
    UserService.create(
        username="Max",
        email="max@digon.io",
        role="moderator",
        ctx=ctx,
        rbac=False,
    )
    UserService.create(
        username="Ulrich",
        email="urlich@digon.io",
        role="user",
        ctx=ctx,
        rbac=False,
    )
    UserService.create(
        username="Uwe",
        email="Uwe@digon.io",
        role="user",
        ctx=ctx,
        rbac=False,
    )
    UserService.create(
        username="Georg",
        email="Georg@digon.io",
        role="guest",
        ctx=ctx,
        rbac=False,
    )

    GroupService.create(
        groupname="BEF",
        description="Bergisches Entwicklerforum",
        owner="Alex",
        ctx=ctx,
        rbac=False,
    )
    GroupService.create(
        groupname="PUGW",
        description="Python User Group Wuppertal",
        owner="Uwe",
        ctx=ctx,
        rbac=False,
    )
    ctx.db.flush()
