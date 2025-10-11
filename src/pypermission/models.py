from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.engine.base import Engine


class BaseORM(DeclarativeBase): ...


################################################################################
#### Types
################################################################################


class Permission:
    """
    Represents a Resource paired with an Action.

    Attributes
    ----------
    resource_type : str
        The ResourceType (e.g., "document", "user").
    resource_id : str
        The ResourceID. The star ('*') acts as a wildcard matching all ResourceIDs of the same ResourceType. The empty string ('') can be used for Actions on Resources that do not have an ResourceID.
    action : str
        The Action allowed on the Resource (e.g., "read", "write", "delete").
    """

    resource_type: str
    resource_id: str
    action: str

    def __init__(self, *, resource_type: str, resource_id: str, action: str) -> None:
        """
        Initialize the Permission.

        Parameters
        ----------
        resource_type : str
            The type of the resource (e.g., "document", "user").
        resource_id : str
            The ID of the resource instance. The start ('*') acts as a wildcard matching all IDs of the resource. The empty string ('') can be used for actions on resources that do not have an ID.
        action : str
            The action allowed on the resource (e.g., "read", "write", "delete").
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action

    def __str__(self) -> str:
        if not self.resource_id:
            return f"{self.resource_type}:{self.action}"
        return f"{self.resource_type}[{self.resource_id}]:{self.action}"


class Policy:
    """
    Represents a Role paired with a Permission.

    Attributes
    ----------
    role : str
        The target RoleID.
    permission : Permission
        The target Permission.
    """

    role: str
    permission: Permission

    def __init__(self, *, role: str, permission: Permission) -> None:
        """
        Initialize the Policy.

        Parameters
        ----------
        role : str
            The target RoleID.
        permission : Permission
            The target Permission.
        """
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
    """
    Create all for PyPermission required database table via. SQLAlchemy.

    Parameters
    ----------
    engine : Engine
        The SQLAlchemy engine.

    """
    BaseORM.metadata.create_all(bind=engine)
