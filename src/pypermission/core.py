"""
Core definitions for the PyPermission package.

Including the permission node object, an internal permission class and a base permission authority.
"""

from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import cast

from pypermission.error import (
    PermissionParsingError,
    UnknownPermissionNodeError,
    MissingPayloadError,
    UnusedPayloadError,
)


# NOTE in 3.11 there will be a StrEnum class, that enforces the enum values type as str
# We just have to wait until 3.11 ist the last supported version :)
# Currently we have to check if the permission node enum has only string values
class PermissionNode(Enum):
    """Abstract permission node definition. Inherit from this to define custom permission nodes."""

    ...


class RootPermissionNode(PermissionNode):
    """Internal permission node definition. Required for the root of the permission tree."""

    ROOT_ = "*"


class Permission:
    """Internal permission class. Represents a node in the tree based permission graph."""

    _node: PermissionNode
    _parent: Permission | None
    _ancestors: tuple[Permission, ...]
    _childs: set[Permission]
    _sub_graph: dict[str, Permission]
    _has_payload: bool
    _is_leaf: bool

    def __init__(self) -> None:
        self._node = RootPermissionNode.ROOT_
        self._parent = None
        self._ancestors = tuple()
        self._childs = set()
        self._sub_graph = {}
        self._has_payload = False
        self._is_leaf = False

    @property
    def node(self) -> PermissionNode:
        """Get the permission node."""
        return self._node

    @property
    def parent(self) -> Permission | None:
        """Get the parent permission."""
        return self._parent

    @property
    def ancestors(self) -> tuple[Permission, ...]:
        """Get ancestor permissions."""
        return self._ancestors

    @property
    def childs(self) -> set[Permission]:
        """Get child permissions."""
        return self._childs

    @property
    def sub_graph(self) -> dict[str, Permission]:
        """Get sub graph."""
        return self._sub_graph

    @property
    def has_payload(self) -> bool:
        """Checks if a permission can carry a payload."""
        return self._has_payload

    @property
    def is_leaf(self) -> bool:
        """Checks if a permission is leaf permission."""
        return self._is_leaf

    def __str__(self) -> str:
        val = self._node.value
        return cast(str, val)  # NOTE would be nice without casting


PermissionMap = dict[Permission, set[str]]
EntityID = int | str


class CustomPermission(Permission):
    """Internal permission class for custom permission nodes. Have to be registered externally."""

    def __init__(
        self, *, node: PermissionNode, parent: Permission, has_payload: bool, is_leaf: bool
    ) -> None:
        self._node = node
        self._parent = parent
        self._ancestors = tuple()
        self._childs = set()
        self._sub_graph = {}
        self._has_payload = has_payload
        self._is_leaf = is_leaf

    def _update_ancestors(self):
        self._ancestors = (*self._parent.ancestors, self._parent)


class Authority(ABC):
    """
    Base permission authority implementation.

    It provides permission node registration, serialization and deserialization methods.
    """

    _root_permission: Permission
    _node_permission_map: dict[PermissionNode, Permission]
    _node_str_permission_map: dict[str, Permission]

    def __init__(self, nodes: type[PermissionNode] | None) -> None:
        self._node_permission_map = {}
        self._node_str_permission_map = {}

        # setup the root permission
        self._root_permission = Permission()
        self._node_permission_map[RootPermissionNode.ROOT_] = self._root_permission
        self._node_str_permission_map[RootPermissionNode.ROOT_.value] = self._root_permission

        # TODO check that all enum values are strings
        if nodes:
            for node in nodes:
                self._register_permission(node=node)

    def register_permission_nodes(self, nodes: type[PermissionNode]) -> None:
        """
        Register permission nodes.

        Parameters
        ----------

        nodes : type[PermissionNode]
            The permission nodes to be registered.
        """
        # TODO check that all enum values are strings
        for node in nodes:
            self._register_permission(node=node)

    @staticmethod
    def root_node() -> PermissionNode:
        """
        Get the root permission node of the root permission.

        A subject or a group with the root permission has access to all permissions.
        """
        return RootPermissionNode.ROOT_

    @staticmethod
    def _serialize_permission_node(permission: Permission, payload: str | None) -> str:
        """Serialize a permission node and its payload."""
        node_str: str = permission.node.value
        if permission.has_payload:
            node_str = f"{node_str[:-2]}{payload}>"
        return node_str

    def _deserialize_permission_node(self, node_str: str) -> tuple[Permission, str | None]:
        """Deserialize a permission node and its payload."""

        node_str_sections: list[str] = node_str.split(".")
        last_section: str = node_str_sections[-1]

        payload = None
        if last_section[0] == "<" and last_section[-1] == ">":
            payload = last_section[1:-1]
            last_section = "<x>"

        node_str = ".".join(node_str_sections[:-1]) + "." + last_section
        try:
            return self._node_str_permission_map[node_str], payload
        except KeyError as err:
            raise PermissionParsingError("Unknown permission node!", node_str) from err

    def _register_permission(self, *, node: PermissionNode):
        "Register a permission node."

        node_str = node.value

        if node_str in self._node_str_permission_map:
            raise PermissionParsingError("Permission has been registered before!", node)

        node_str_sections: list[str] = node_str.split(".")
        last_str_section: str = node_str_sections[-1]

        has_payload = False
        if last_str_section == "*":
            parent_node_str_sections: list[str] = node_str_sections[0:-2]
            last_str_section = node_str_sections[-2]
            is_leaf = False
        else:
            parent_node_str_sections = node_str_sections[0:-1]
            is_leaf = True

            if last_str_section == "<x>":
                has_payload = True

        parent = self._root_permission
        potential_parent_node = ""
        for section in parent_node_str_sections:
            potential_parent_node = potential_parent_node + "." + section
            try:
                parent = parent.sub_graph[section]
            except KeyError as err:
                raise PermissionParsingError(
                    "A nested permission requires a parent permission!",
                    potential_parent_node[1:] + ".*",
                ) from err

        if parent.is_leaf:
            raise PermissionParsingError(
                "The desired parent permission is a leave permission!", parent.node
            )

        new_perm = CustomPermission(
            node=node, parent=parent, has_payload=has_payload, is_leaf=is_leaf
        )

        if not parent_node_str_sections:
            new_perm._parent = self._root_permission  # pylint: disable=protected-access
        new_perm._update_ancestors()  # pylint: disable=protected-access

        parent.sub_graph[last_str_section] = new_perm
        parent.childs.add(new_perm)

        self._node_permission_map[node] = new_perm
        self._node_str_permission_map[node_str] = new_perm
        return new_perm

    def _get_permission(self, *, node: PermissionNode) -> Permission:
        """Just a simple wrapper to avoid some boilerplate code while getting a node."""
        try:
            return self._node_permission_map[node]
        except KeyError:
            raise UnknownPermissionNodeError


def validate_payload_status(*, permission: Permission, payload: str | None):
    """Check the permission payload combinatorics."""
    if permission.has_payload and payload is None:
        raise MissingPayloadError

    if not permission.has_payload and payload is not None:
        raise UnusedPayloadError

    # TODO raise if not str
