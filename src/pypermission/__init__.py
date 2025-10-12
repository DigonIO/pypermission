"""
The python `RBAC` library for projects where `sqlalchemy` is a valid option.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.1.0"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

from typing import Final

from pypermission.service.role import RoleService
from pypermission.service.subject import SubjectService
from pypermission.models import (
    Policy,
    Permission,
    FrozenClass,
    create_rbac_database_table,
)
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError


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
    "PyPermissionError",
    "PyPermissionNotGrantedError",
]
