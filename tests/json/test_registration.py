import pytest

from pypermission.json import Authority
from pypermission.typing import Permission

# Permission nodes for testing inspired be the towny permission nodes
# https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java

test_data = (
    # (node, is_leaf, has_payload)
    ("towny.*", False, False),
    ("towny.chat.*", False, False),
    ("towny.chat.town", True, False),
    ("towny.chat.nation", True, False),
    ("towny.chat.global", True, False),
    ("towny.wild.*", False, False),
    ("towny.wild.build.*", False, False),
    ("towny.wild.build.<x>", True, True),
    ("towny.wild.destroy.*", False, False),
    ("towny.wild.destroy.<x>", True, True),
)


def test_perm_reg():
    auth = Authority()

    def r(node: str):
        return auth.register_permission(node=node)

    permissions: list[Permission] = []

    for entry in test_data:
        permissions.append(r(entry[0]))

    for permission, entry in zip(permissions, test_data):
        assert permission.node == entry[0]
        assert permission.is_leaf == entry[1]
        assert permission.has_payload == entry[2]
