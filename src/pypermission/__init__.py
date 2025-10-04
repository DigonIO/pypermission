"""
The python `RBAC` library for projects where `sqlalchemy` is a valid option.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.1.0"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

from typing import Final
from types import ModuleType

from pypermission.service.role import RoleService
from pypermission.service.subject import SubjectService
from pypermission.service.policy import PolicyService
from pypermission.models import (
    Policy,
    Permission,
    FrozenClass,
    create_rbac_database_table,
)
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError


class Namespace(type):
    def __setattr__(cls, key, value):
        if key in cls.__dict__:
            raise AttributeError(f"Cannot overwrite any attribute!")
        super().__setattr__(key, value)


class RBAC(metaclass=FrozenClass):
    role: Final = RoleService
    subject: Final = SubjectService
    policy: Final = PolicyService


__all__ = [
    "RBAC",
    "Policy",
    "Permission",
    "create_rbac_database_table",
    "PyPermissionError",
    "PyPermissionNotGrantedError",
]
