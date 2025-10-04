from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.schema import ForeignKey


class BaseORM(DeclarativeBase): ...


class RoleORM(BaseORM):
    __tablename__ = "pp_role_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)


class HierarchyORM(BaseORM):
    __tablename__ = "pp_hierarchy_table"
    parent_role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )
    child_role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )


class SubjectORM(BaseORM):
    __tablename__ = "pp_subject_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)


class MemberORM(BaseORM):
    __tablename__ = "pp_member_table"
    role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )
    subject_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_subject_table.id", ondelete="CASCADE"), primary_key=True
    )


class PolicyORM(BaseORM):
    __tablename__ = "pp_policy_table"
    role_id: Mapped[str] = mapped_column(
        String, ForeignKey("pp_role_table.id", ondelete="CASCADE"), primary_key=True
    )
    resource_type: Mapped[str] = mapped_column(String, primary_key=True)
    resource_id: Mapped[str] = mapped_column(String, primary_key=True)
    action: Mapped[str] = mapped_column(String, primary_key=True)
