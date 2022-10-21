import pytest
from pypermission.serial import SerialAuthority


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

    @pytest.fixture
    def acyclic_yaml(self):
        return """
groups:
  A:
    member_groups:
      - B
      - C
  B:

    member_groups:
      - F
  C:
    member_groups:
      - D
      - E
  D:
    member_groups:
      - F
  E:
  F:
"""

    @pytest.fixture
    def cyclic_a_yaml(self):
        return """
groups:
  A:
    member_groups:
      - B
      - C
  B:

    member_groups:
      - F
  C:
    member_groups:
      - D
      - E
  D:
    member_groups:
      - F
  E:
    member_groups:
      - A
  F:
"""

    @pytest.fixture
    def cyclic_b_yaml(self):
        return """
groups:
  A:
    member_groups:
      - B
      - C
  B:
    member_groups:
      - F
  C:
    member_groups:
      - D
      - E
  D:
    member_groups:
      - F
  E:
  F:
    member_groups:
      - A
"""

    # TODO: exception handling
    def test_acyclic_groups(self, acyclic_yaml):
        # No permission nodes needed for testing group hierarchy
        auth = SerialAuthority(nodes=None)
        auth.load_YAML(serial_data=acyclic_yaml)

    # TODO: exception handling
    def test_cyclic_groups(self, cyclic_a_yaml, cyclic_b_yaml):
        # No permission nodes needed for testing group hierarchy
        auth_a = SerialAuthority(nodes=None)
        auth_a.load_YAML(serial_data=cyclic_a_yaml)

        auth_b = SerialAuthority(nodes=None)
        auth_b.load_YAML(serial_data=cyclic_b_yaml)
