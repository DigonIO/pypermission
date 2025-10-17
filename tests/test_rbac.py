import pytest

from rbac import RBAC
from rbac.service.role import RoleService
from rbac.service.subject import SubjectService


def test_rbac_service_imports() -> None:
    assert RBAC.role == RoleService
    assert RBAC.subject == SubjectService
