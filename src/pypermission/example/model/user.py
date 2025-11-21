from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SqlEnum
from sqlalchemy.sql.sqltypes import UUID as SqlUUID
from sqlalchemy.sql.sqltypes import String, Boolean

from pypermission.models import BaseORM
from pypermission.example.types import State

################################################################################
#### UserORM
################################################################################


class UserORM(BaseORM):
    __tablename__ = "app_user_table"
    id: Mapped[UUID] = mapped_column(SqlUUID, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean)
    state: Mapped[State] = mapped_column(
        SqlEnum(State, name="UserORM.State"), default=State.ACTIVE
    )

    group_orms: Mapped[list["GroupORM"]] = relationship(
        "GroupORM", back_populates="owner_orm"
    )
