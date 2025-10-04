from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.sqltypes import Enum as SqlEnum
from sqlalchemy.sql.schema import ForeignKey


from pypermission.models import BaseORM


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
    state: Mapped[State] = mapped_column(SqlEnum(State, name="UserORM.State"))


################################################################################
#### GroupORM
################################################################################


class GroupORM(BaseORM):
    __tablename__ = "app_group_table"
    groupname: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str] = mapped_column(String)
    state: Mapped[State] = mapped_column(SqlEnum(State, name="GroupORM.State"))
