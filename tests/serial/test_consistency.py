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
    def common_yaml(self):
        return """
groups:
  A:
    member_subjects:
      - B
      - C
  B:
    member_subjects:
      - F
  C:
    member_subjects:
      - D
      - E
  D:
    member_subjects:
      - F
"""

    @pytest.fixture
    def acyclic_yaml(self, common_yaml):
        return (
            common_yaml
            + """  E:
  F:
"""
        )

    @pytest.fixture
    def cyclic_a_yaml(self, common_yaml):
        return (
            common_yaml
            + """  E:
    member_subjects:
      - A
  F:
"""
        )

    @pytest.fixture
    def cyclic_b_yaml(self, common_yaml):
        return (
            common_yaml
            + """  E:
  F:
    member_subjects:
      - A
"""
        )

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
