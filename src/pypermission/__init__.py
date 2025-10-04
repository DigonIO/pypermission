"""
A `RBAC` library for projects where `sqlalchemy` is a valid option.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.1.0"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

from typing import Final
from types import ModuleType

from pypermission.models import Policy, Permission, create_rbac_database_table
import pypermission.service.role as role_service
import pypermission.service.subject as subject_service
import pypermission.service.policy as policy_service


class _FrozenNamespace(type):
    def __setattr__(cls, key, value):
        if key in cls.__dict__:
            raise AttributeError(f"Cannot overwrite any attribute of RBAC")
        super().__setattr__(key, value)


class RBAC(metaclass=_FrozenNamespace):
    role: Final[ModuleType] = role_service
    subject: Final[ModuleType] = subject_service
    policy: Final[ModuleType] = policy_service


__all__ = ["RBAC", "Policy", "Permission", "create_rbac_database_table"]
