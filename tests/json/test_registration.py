import pytest

from pypermission.json import Authority
from pypermission.typing import PermissionNode
from pypermission.core import Permission

from ..helpers import TownyPermissionNode


@pytest.mark.parametrize(
    "node, is_leaf, has_payload",
    [
        # (node, is_leaf, has_payload)
        (Authority.root_node(), False, False),
        (TownyPermissionNode.TOWNY_, False, False),
        (TownyPermissionNode.TOWNY_CHAT_, False, False),
        (TownyPermissionNode.TOWNY_CHAT_TOWN, True, False),
        (TownyPermissionNode.TOWNY_CHAT_NATION, True, False),
        (TownyPermissionNode.TOWNY_CHAT_GLOBAL, True, False),
        (TownyPermissionNode.TOWNY_WILD_, False, False),
        (TownyPermissionNode.TOWNY_WILD_BUILD_, False, False),
        (TownyPermissionNode.TOWNY_WILD_BUILD_X, True, True),
        (TownyPermissionNode.TOWNY_WILD_DESTROY_, False, False),
        (TownyPermissionNode.TOWNY_WILD_DESTROY_X, True, True),
    ],
)
def test_register_buildin_nodes(node: PermissionNode, is_leaf: bool, has_payload: bool):
    auth = Authority(nodes=TownyPermissionNode)

    permission: Permission = auth._node_permission_map[node]
    assert permission.node == node
    assert permission.is_leaf == is_leaf
    assert permission.has_payload == has_payload


@pytest.mark.parametrize(
    "node, is_leaf, has_payload",
    [
        # (node, is_leaf, has_payload)
        (Authority.root_node(), False, False),
        (TownyPermissionNode.TOWNY_, False, False),
        (TownyPermissionNode.TOWNY_CHAT_, False, False),
        (TownyPermissionNode.TOWNY_CHAT_TOWN, True, False),
        (TownyPermissionNode.TOWNY_CHAT_NATION, True, False),
        (TownyPermissionNode.TOWNY_CHAT_GLOBAL, True, False),
        (TownyPermissionNode.TOWNY_WILD_, False, False),
        (TownyPermissionNode.TOWNY_WILD_BUILD_, False, False),
        (TownyPermissionNode.TOWNY_WILD_BUILD_X, True, True),
        (TownyPermissionNode.TOWNY_WILD_DESTROY_, False, False),
        (TownyPermissionNode.TOWNY_WILD_DESTROY_X, True, True),
    ],
)
def test_register_plugin_nodes(node: PermissionNode, is_leaf: bool, has_payload: bool):
    auth = Authority()
    auth.register_permission_nodes(nodes=TownyPermissionNode)

    permission: Permission = auth._node_permission_map[node]
    assert permission.node == node
    assert permission.is_leaf == is_leaf
    assert permission.has_payload == has_payload
