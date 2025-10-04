from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.engine.base import Engine


class BaseORM(DeclarativeBase): ...


################################################################################
#### Types
################################################################################


class Permission:
    resource_type: str
    resource_id: str
    action: str

    def __init__(self, *, resource_type: str, resource_id: str, action: str) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action

    def __str__(self) -> str:
        if not self.resource_id:
            return f"{self.resource_type}:{self.action}"
        return f"{self.resource_type}[{self.resource_id}]:{self.action}"


class Policy:
    role: str
    permission: Permission

    def __init__(self, *, role: str, permission: Permission) -> None:
        self.role = role
        self.permission = permission

    def __str__(self) -> str:
        return f"{self.role}:{self.permission}"


class FrozenClass(type):
    def __setattr__(cls, key, value):
        if key in cls.__dict__:
            raise AttributeError(f"FrozenClass attributes cannot be overwrite!")
        super().__setattr__(key, value)


################################################################################
#### RoleORM
################################################################################


class RoleORM(BaseORM):
    __tablename__ = "pp_role_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)


################################################################################
#### HierarchyORM
################################################################################


class HierarchyORM(BaseORM):
    __tablename__ = "pp_hierarchy_table"
    parent_role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )
    child_role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )


################################################################################
#### SubjectORM
################################################################################


class SubjectORM(BaseORM):
    __tablename__ = "pp_subject_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)


################################################################################
#### MemberORM
################################################################################


class MemberORM(BaseORM):
    __tablename__ = "pp_member_table"
    role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )
    subject_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_subject_table.id", ondelete="CASCADE"), primary_key=True
    )


################################################################################
#### PolicyORM
################################################################################


class PolicyORM(BaseORM):
    __tablename__ = "pp_policy_table"
    role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )
    resource_type: Mapped[str] = mapped_column(String, primary_key=True)
    resource_id: Mapped[str] = mapped_column(String, primary_key=True)
    action: Mapped[str] = mapped_column(String, primary_key=True)


################################################################################
#### Util
################################################################################


def create_rbac_database_table(*, engine: Engine) -> None:
    BaseORM.metadata.create_all(bind=engine)
