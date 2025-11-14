from typing import Never

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import String

from pypermission.exc import PyPermissionError


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
        The ResourceID. The star '*' acts as a wildcard matching all ResourceIDs of the same ResourceType. The empty string can be used for Actions on Resources that do not have an ResourceID.
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
            The ID of the resource instance. The start '*' acts as a wildcard matching all IDs of the resource. The empty string can be used for actions on resources that do not have an ID.
        action : str
            The action allowed on the resource (e.g., "read", "write", "delete").
        """
        if resource_type == "":
            raise PyPermissionError("Resource type cannot be empty!")
        if action == "":
            raise PyPermissionError("Action cannot be empty!")

        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action

    def __str__(self) -> str:
        if not self.resource_id:
            return f"{self.resource_type}:{self.action}"
        return f"{self.resource_type}[{self.resource_id}]:{self.action}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Permission):
            return False

        return (
            self.resource_type == other.resource_type
            and self.resource_id == other.resource_id
            and self.action == other.action
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


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
        if role == "":
            raise PyPermissionError("Role name cannot be empty!")
        self.role = role
        self.permission = permission

    def __str__(self) -> str:
        return f"{self.role}:{self.permission}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Policy):
            return False

        return self.role == other.role and self.permission == other.permission

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class FrozenClass(type):
    def __setattr__(cls, key: str, value: Never) -> None:
        if key in cls.__dict__:
            raise AttributeError("Frozen attributes cannot be modified!")
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
