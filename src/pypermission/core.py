"""
Core definitions for the PyPermission package.

Including the permission node object, an internal permission class and a base permission authority.
"""

# annotations needed for classes with self referential type hints
from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import cast, overload, Generic, TypeVar, Union, Literal, TypeGuard, Type

# typing_extensions for generic TypedDict support:
from typing_extensions import TypedDict

from pypermission.error import (
    MissingPayloadError,
    ParsingError,
    UnknownPermissionNodeError,
    UnusedPayloadError,
)
from pypermission.error import EntityIDError


# NOTE in 3.11 there will be a StrEnum class, that enforces the enum values type as str
# We just have to wait until 3.11 ist the last supported version :)
# Currently we have to check if the permission node enum has only string values
class PermissionNode(str, Enum):
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
    _children: set[Permission]
    _sub_graph: dict[str, Permission]
    _has_payload: bool
    _is_leaf: bool

    def __init__(self) -> None:
        self._node = RootPermissionNode.ROOT_
        self._parent = None
        self._ancestors = tuple()
        self._children = set()
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
    def children(self) -> set[Permission]:
        """Get child permissions."""
        return self._children

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


EntityID = int | str
PID = TypeVar("PID", str, PermissionNode)
_PID = TypeVar("_PID", str, PermissionNode)
EID = TypeVar("EID", str, EntityID)

PERMISSION_NODES = dict[PID, None | list[str]]
PERMISSION_TREE = dict[PID, Union[None, list[str], "PERMISSION_TREE[PID]"]]


def perm_tree_matches_key_type(
    perm_tree: PERMISSION_TREE[PID], key_type: Type[_PID]
) -> TypeGuard[PERMISSION_TREE[_PID]]:
    if perm_tree:
        return isinstance(next(iter(perm_tree)), key_type)
    return True


class PermissionableEntityDict(TypedDict, Generic[PID]):
    permission_nodes: PERMISSION_NODES[PID]


class GroupDict(PermissionableEntityDict[PID], Generic[PID, EID]):
    parents: list[EID]


class EntityDict(PermissionableEntityDict[PID], Generic[PID, EID]):
    entity_id: EID
    groups: list[EID]


class SubjectPermissionDict(TypedDict, Generic[PID, EID]):
    groups: dict[EID, GroupDict[PID, EID]]
    subject: EntityDict[PID, EID]
    permission_tree: PERMISSION_TREE[PID]


class GroupPermissionDict(TypedDict, Generic[PID, EID]):
    groups: dict[EID, GroupDict[PID, EID]]
    group: EntityDict[PID, EID]
    permission_tree: PERMISSION_TREE[PID]


SubjectPermissions = (
    SubjectPermissionDict[PermissionNode, EntityID]
    | SubjectPermissionDict[str, EntityID]
    | SubjectPermissionDict[PermissionNode, str]
    | SubjectPermissionDict[str, str]
)

GroupPermissions = (
    GroupPermissionDict[PermissionNode, EntityID]
    | GroupPermissionDict[str, EntityID]
    | GroupPermissionDict[PermissionNode, str]
    | GroupPermissionDict[str, str]
)

PermissionMap = dict[Permission, set[str]]
NodeMap = dict[PermissionNode, set[str]]


class CustomPermission(Permission):
    """Internal permission class for custom permission nodes. Have to be registered externally."""

    def __init__(
        self, *, node: PermissionNode, parent: Permission, has_payload: bool, is_leaf: bool
    ) -> None:
        self._node: PermissionNode = node
        self._parent: Permission = parent
        self._ancestors = tuple()
        self._children = set()
        self._sub_graph = {}
        self._has_payload = has_payload
        self._is_leaf: bool = is_leaf

    def _update_ancestors(self) -> None:
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

    ################################################################################################
    ### Private
    ################################################################################################

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
            raise ParsingError("Unknown permission node!", node_str) from err

    def _register_permission(self, *, node: PermissionNode) -> CustomPermission:
        "Register a permission node."

        node_str = node.value

        if node_str in self._node_str_permission_map:
            raise ParsingError("Permission has been registered before!", node)

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
                raise ParsingError(
                    "A nested permission requires a parent permission!",
                    potential_parent_node[1:] + ".*",
                ) from err

        if parent.is_leaf:
            raise ParsingError("The desired parent permission is a leave permission!", parent.node)

        new_perm = CustomPermission(
            node=node, parent=parent, has_payload=has_payload, is_leaf=is_leaf
        )

        if not parent_node_str_sections:
            new_perm._parent = self._root_permission  # pylint: disable=protected-access
        new_perm._update_ancestors()  # pylint: disable=protected-access

        parent.sub_graph[last_str_section] = new_perm
        parent.children.add(new_perm)

        self._node_permission_map[node] = new_perm
        self._node_str_permission_map[node_str] = new_perm
        return new_perm

    def _get_permission(self, *, node: PermissionNode | str) -> Permission:
        """Just a simple wrapper to avoid some boilerplate code while getting a node."""

        try:
            if isinstance(node, PermissionNode):
                return self._node_permission_map[node]
            else:
                return self._node_str_permission_map[node]
        except KeyError:
            raise UnknownPermissionNodeError

    def _populate_permission_tree(
        self,
        *,
        permission_tree: PERMISSION_TREE[PID],
        permission_map: PermissionMap,
        serialize_nodes: bool = False,
    ) -> None:
        branch: Union[None, list[str], "PERMISSION_TREE[PID]"]
        permission_tree
        key_type = str if serialize_nodes else PermissionNode
        tree__serialize: tuple[PERMISSION_TREE[str], Literal[True]] | tuple[
            PERMISSION_TREE[PermissionNode], Literal[False]
        ]
        if perm_tree_matches_key_type(permission_tree, str):
            if key_type is str:
                tree__serialize = permission_tree, True
            else:
                raise ValueError
        elif perm_tree_matches_key_type(permission_tree, PermissionNode):
            if key_type is PermissionNode:
                tree__serialize = permission_tree, False
            else:
                raise ValueError
        else:
            raise ValueError

        for perm, payload_set in permission_map.items():
            key = str(perm.node.value) if serialize_nodes else perm.node
            if key in permission_tree:
                continue

            if perm.is_leaf:
                if perm.has_payload:
                    branch = [payload for payload in payload_set]
                else:
                    branch = None
            else:
                branch = self._build_permission_subtree(
                    permission=perm, serialize_nodes=serialize_nodes, node_type=str
                )

            if tree__serialize[1] == True:  # str
                if isinstance(key, str):
                    tree__serialize[0][key] = branch
            else:  # PermissionNode
                if isinstance(key, PermissionNode):
                    tree__serialize[0][key] = branch
            # permission_tree[key] = branch

    def _build_permission_subtree(
        self, *, permission: Permission, serialize_nodes: bool = False, node_type: type[PID]
    ) -> PERMISSION_TREE[PID] | list[str] | None:
        if permission.is_leaf:
            if permission.has_payload:
                return []
            return None
        return {
            str(child.node.value)
            if serialize_nodes
            else child.node: self._build_permission_subtree(
                permission=child, serialize_nodes=serialize_nodes
            )
            for child in permission.children
        }


####################################################################################################
### Util
####################################################################################################


def validate_payload_status(*, permission: Permission, payload: str | None) -> None:
    """Check the permission payload combinatorics."""
    if permission.has_payload and payload is None:
        raise MissingPayloadError

    if not permission.has_payload and payload is not None:
        raise UnusedPayloadError

    # TODO raise if not str


def entity_id_serializer(eid: EntityID, max_lenght: int | None = None) -> str:
    assertEntityIDType(eid=eid)

    if isinstance(eid, int):
        serial_type = "int"
        serial_eid = str(eid)
    elif isinstance(eid, str):
        serial_type = "str"
        serial_eid = eid

    if max_lenght and (len(serial_eid) > max_lenght):
        raise ValueError  # TODO

    return f"{serial_type}:{serial_eid}"


def entity_id_deserializer(serial_eid: str, max_lenght: int | None = None) -> EntityID:
    if max_lenght and (len(serial_eid) > max_lenght):
        raise ValueError  # TODO

    serial_type = serial_eid[:3]
    serial_eid = serial_eid[4:]

    if serial_type == "int":
        return int(serial_eid)
    elif serial_type == "str":
        return serial_eid
    else:
        raise ValueError  # TODO


def assertEntityIDType(eid: EntityID) -> None:
    if not isinstance(eid, int | str):
        raise EntityIDError(
            f"Subject and group IDs have to be of type int or string! Got type `{type(eid)}` for `{eid}`."
        )


def istype(node_type: type[PID], target: type[_PID]) -> TypeGuard[type[_PID]]:
    return node_type is target


def build_entity_permission_nodes(
    *, permission_map: PermissionMap, node_type: type[PID]
) -> PERMISSION_NODES[PID]:
    if istype(node_type, PermissionNode):
        node_type
        result_PE: PERMISSION_NODES[PermissionNode] = {
            perm.node: [val for val in payload] if payload else None
            for perm, payload in permission_map.items()
        }
        return result_PE
    if istype(node_type, str):
        result_ST: PERMISSION_NODES[str] = {
            str(perm.node.value): [val for val in payload] if payload else None
            for perm, payload in permission_map.items()
        }
        return result_ST
    raise ValueError

def build_entity_permission_nodes(
    *, permission_map: PermissionMap, node_type: type[PID]
) -> PERMISSION_NODES[PID]:
    if istype(node_type, PermissionNode):
        node_type
        return 2
    if istype(node_type, str):
        node_type
        return 1
    raise ValueError
