import pytest

from pypermission import RBAC
from pypermission.service.role import RoleService
from pypermission.service.subject import SubjectService
from pypermission.service.policy import PolicyService


def test_rbac_service_imports() -> None:

    assert RBAC.role == RoleService
    assert RBAC.subject == SubjectService
    assert RBAC.policy == PolicyService
