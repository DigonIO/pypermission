"""
`PyPermission` - The python RBAC authorization library for projects where `sqlalchemy` is a valid option.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.2.1"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

from typing import Final

from pypermission.service.role import RoleService
from pypermission.service.subject import SubjectService
from pypermission.models import (
    Policy,
    Permission,
    FrozenClass,
    create_rbac_database_table,
    set_sqlite_pragma,
)
from pypermission.exc import PyPermissionError, PermissionNotGrantedError


class RBAC(metaclass=FrozenClass):
    """
    Namespace for the Role and Subject services.

    Attributes
    ----------
    role : RoleService
        Shorthand for all RoleService functions.
    subject : SubjectService
        Shorthand for all SubjectService functions.
    """

    role: Final = RoleService
    subject: Final = SubjectService


__all__ = [
    "RBAC",
    "Policy",
    "Permission",
    "create_rbac_database_table",
    "set_sqlite_pragma",
    "PyPermissionError",
    "PermissionNotGrantedError",
]
