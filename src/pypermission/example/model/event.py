from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Enum as SqlEnum
from sqlalchemy.sql.sqltypes import UUID as SqlUUID
from sqlalchemy.sql.sqltypes import String

from pypermission.models import BaseORM
from pypermission.example.types import State
from pypermission.example.model.group import GroupORM

################################################################################
#### EventORM
################################################################################


class EventORM(BaseORM):
    __tablename__ = "app_event_table"
    id: Mapped[UUID] = mapped_column(SqlUUID, primary_key=True)
    group_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("app_group_table.id", ondelete="CASCADE"),
    )

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    state: Mapped[State] = mapped_column(
        SqlEnum(State, name="EventORM.State"), default=State.ACTIVE
    )

    group_orm: Mapped[GroupORM] = relationship(GroupORM, back_populates="event_orms")
