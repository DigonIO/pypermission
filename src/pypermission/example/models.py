from enum import StrEnum

from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Enum as SqlEnum
from sqlalchemy.sql.sqltypes import String

from pypermission.models import BaseORM

################################################################################
#### Types
################################################################################


class ExampleError(Exception): ...


class Context:
    username: str | None
    db: Session

    def __init__(self, *, user: str | None = None, db: Session):
        self.username = user
        self.db = db


class State(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


################################################################################
#### UserORM
################################################################################


class UserORM(BaseORM):
    __tablename__ = "app_user_table"
    username: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    state: Mapped[State] = mapped_column(
        SqlEnum(State, name="UserORM.State"), default=State.ACTIVE
    )

    group_orms: Mapped[list["GroupORM"]] = relationship(
        "GroupORM", back_populates="owner_orm"
    )


################################################################################
#### GroupORM
################################################################################


class GroupORM(BaseORM):
    __tablename__ = "app_group_table"
    groupname: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str] = mapped_column(String)
    owner: Mapped[str] = mapped_column(
        String,
        ForeignKey("app_user_table.username", ondelete="CASCADE"),
    )
    state: Mapped[State] = mapped_column(
        SqlEnum(State, name="GroupORM.State"), default=State.ACTIVE
    )

    owner_orm: Mapped["UserORM"] = relationship("UserORM", back_populates="group_orms")
