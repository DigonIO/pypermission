import pytest

from pypermission.error import RoleCycleError
from pypermission.serial import SerialAuthority

ACYCLIC_YAML = """
roles:
  A:
    child_roles:
      - B
      - C
  B:
    child_roles:
      - F
  C:
    child_roles:
      - D
      - E
  D:
    child_roles:
      - F
  E:
  F:
"""

CYCLIC_A_YAML = """
roles:
  A:
    child_roles:
      - B
      - C
  B:
    child_roles:
      - F
  C:
    child_roles:
      - D
      - E
  D:
    child_roles:
      - F
  E:
    child_roles:
      - A
  F:
"""

CYCLIC_B_YAML = """
roles:
  A:
    child_roles:
      - B
      - C
  B:
    child_roles:
      - F
  C:
    child_roles:
      - D
      - E
  D:
    child_roles:
      - F
  E:
  F:
    child_roles:
      - A
"""


class TestCycleDetection:
    r"""
    |  Acyclic case  |  Cyclic case a)  |  Cyclic case b)  |
    | -------------- | ---------------- | ---------------- |
    |       A        |        A         |        A         |
    |      / \       |       / \        |       / \        |
    |     B   C      |      B   C       |      B   C       |
    |    /   / \     |     /   / \      |     /   / \      |
    |   |   D   E    |    |   D   E     |    |   D   E     |
    |   | /          |    | /     |     |    | /           |
    |   F            |    F       A     |    F             |
    |                |                  |    |             |
    |                |                  |    A             |
    """

    # TODO: exception handling
    def test_acyclic_roles(self):
        # No permission nodes needed for testing role hierarchy
        auth = SerialAuthority(nodes=None)
        auth.load_YAML(serial_data=ACYCLIC_YAML)

    @pytest.mark.parametrize(
        "yaml_str, err_msg",
        (
            [
                CYCLIC_A_YAML,
                "Cyclic dependencies detected between roles `C` and `A`!",
            ],
            [
                CYCLIC_B_YAML,
                "Cyclic dependencies detected between roles `[CB]` and `A`!",
            ],
        ),
    )
    def test_cyclic_roles(self, yaml_str, err_msg):
        # No permission nodes needed for testing role hierarchy
        auth = SerialAuthority(nodes=None)
        with pytest.raises(RoleCycleError, match=err_msg):
            auth.load_YAML(serial_data=yaml_str)

    @pytest.mark.parametrize(
        "rid, err_msg",
        (
            ["E", "Cyclic dependencies detected between roles `C` and `A`!"],
            ["F", "Cyclic dependencies detected between roles `[CB]` and `A`!"],
        ),
    )
    def test_cyclic_roles_inserts(self, rid, err_msg):
        # No permission nodes needed for testing role hierarchy
        auth = SerialAuthority(nodes=None)
        auth.load_YAML(serial_data=ACYCLIC_YAML)

        with pytest.raises(RoleCycleError, match=err_msg):
            auth.role_add_inheritance(rid=rid, child_rid="A")
