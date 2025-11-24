from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import UUID as SqlUUID
from sqlalchemy.sql.sqltypes import Enum as SqlEnum
from sqlalchemy.sql.sqltypes import String

from pypermission.example.model.orm import MeetDownORM
from pypermission.example.model.user import UserORM
from pypermission.example.types import State

################################################################################
#### GroupORM
################################################################################


class GroupORM(MeetDownORM):
    __tablename__ = "app_group_table"
    id: Mapped[UUID] = mapped_column(SqlUUID, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    owner: Mapped[str] = mapped_column(
        String,
        ForeignKey("app_user_table.username", ondelete="CASCADE"),
    )
    state: Mapped[State] = mapped_column(
        SqlEnum(State, name="GroupORM.State"), default=State.ACTIVE
    )

    owner_orm: Mapped[UserORM] = relationship(UserORM, back_populates="group_orms")
    event_orms: Mapped[list["EventORM"]] = relationship(
        "EventORM", back_populates="group_orm"
    )
