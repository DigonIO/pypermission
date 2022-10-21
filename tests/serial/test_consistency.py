import pytest
from pypermission.serial import SerialAuthority
from pypermission.error import GroupCycleError

ACYCLIC_YAML = """
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

CYCLIC_A_YAML = """
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

CYCLIC_B_YAML = """
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
    def test_acyclic_groups(self):
        # No permission nodes needed for testing group hierarchy
        auth = SerialAuthority(nodes=None)
        auth.load_YAML(serial_data=ACYCLIC_YAML)

    @pytest.mark.parametrize(
        "yaml_str, err_msg",
        (
            [
                CYCLIC_A_YAML,
                "Cyclic dependencies detected between groups `C` and `A`!",
            ],
            [
                CYCLIC_B_YAML,
                "Cyclic dependencies detected between groups `[CB]` and `A`!",
            ],
        ),
    )
    def test_cyclic_groups(self, yaml_str, err_msg):
        # No permission nodes needed for testing group hierarchy
        auth = SerialAuthority(nodes=None)
        with pytest.raises(GroupCycleError, match=err_msg):
            auth.load_YAML(serial_data=yaml_str)

    @pytest.mark.parametrize(
        "gid, err_msg",
        (
            ["E", "Cyclic dependencies detected between groups `C` and `A`!"],
            ["F", "Cyclic dependencies detected between groups `[CB]` and `A`!"],
        ),
    )
    def test_cyclic_groups_inserts(self, gid, err_msg):
        # No permission nodes needed for testing group hierarchy
        auth = SerialAuthority(nodes=None)
        auth.load_YAML(serial_data=ACYCLIC_YAML)

        with pytest.raises(GroupCycleError, match=err_msg):
            auth.group_add_member_group(gid=gid, member_gid="A")
