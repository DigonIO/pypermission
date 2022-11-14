"""
Core definitions for the PyPermission package.

Including the permission node object, an internal permission class and a base permission authority.
"""

# annotations needed for classes with self referential type hints
from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Generic, Literal, Type, TypeGuard, TypeVar, Union, cast, overload

# typing_extensions for generic TypedDict support:
from typing_extensions import NotRequired, TypedDict

from pypermission.error import (
    EntityIDError,
    MissingPayloadError,
    ParsingError,
    UnknownPermissionNodeError,
    UnusedPayloadError,
)


# NOTE in 3.11 there will be a StrEnum class, that enforces the enum values type as str
# We just have to wait until 3.11 ist the last supported version :)
# Currently we have to check if the permission node enum has only string values
class PermissionNode(str, Enum):
    """Abstract permission node definition. Inherit from this to define custom permission nodes."""

    @property
    def value(self) -> str:
        return cast(str, self._value_)


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
        return val


EntityID = int | str  # NOTE: this leads to a lot of type ignores

PID = TypeVar("PID", str, PermissionNode)
_PID = TypeVar("_PID", str, PermissionNode)
EID = TypeVar("EID", str, EntityID)  # NOTE: thats illegal
# WARNING: EntityID is an instance not a type
# type(int | str) == types.UnionType

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


class RoleDict(PermissionableEntityDict[PID], Generic[PID, EID]):
    parents: list[EID]


# NOTE: technically entity_id should not be ommitted
class EntityDict(PermissionableEntityDict[PID], Generic[PID, EID]):
    entity_id: EID
    roles: NotRequired[list[EID]]


class SubjectInfoDict(TypedDict, Generic[PID, EID]):
    roles: dict[EID, RoleDict[PID, EID]]
    subject: EntityDict[PID, EID]
    permission_tree: PERMISSION_TREE[PID]


class RoleInfoDict(TypedDict, Generic[PID, EID]):
    roles: dict[EID, RoleDict[PID, EID]]
    role: EntityDict[PID, EID]
    permission_tree: PERMISSION_TREE[PID]


SubjectInfo = (
    SubjectInfoDict[PermissionNode, EntityID]
    | SubjectInfoDict[str, EntityID]
    | SubjectInfoDict[PermissionNode, str]
    | SubjectInfoDict[str, str]
)

RoleInfo = (
    RoleInfoDict[PermissionNode, EntityID]
    | RoleInfoDict[str, EntityID]
    | RoleInfoDict[PermissionNode, str]
    | RoleInfoDict[str, str]
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
        # TODO check that all enum values are strings, and have a valid pattern
        for node in nodes:
            self._register_permission(node=node)

    @staticmethod
    def root_node() -> PermissionNode:
        """
        Get the root permission node of the root permission.

        A subject or a role with the root permission has access to all permissions.
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

        if len(node_str_sections) > 1:
            node_str = ".".join(node_str_sections[:-1]) + "." + last_section
        else:
            node_str = last_section

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
                # TODO: improve message
                raise ParsingError(
                    "A nested permission requires a parent permission!",
                    potential_parent_node[1:] + ".*",
                ) from err

        if parent.is_leaf:
            # TODO: improve message
            raise ParsingError("The desired parent permission is a leaf permission!", parent.node)

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
        node_type: type[PID],
    ) -> None:
        branch: Union[None, list[str], "PERMISSION_TREE[PID]"]

        for perm, payload_set in permission_map.items():
            key: PID = perm.node.value if node_type is str else perm.node  # type:ignore
            if key in permission_tree:
                continue

            if perm.is_leaf:
                if perm.has_payload:
                    branch = [payload for payload in payload_set]
                else:
                    branch = None
            else:
                branch = self._build_permission_subtree(permission=perm, node_type=node_type)

            permission_tree[key] = branch

    def _build_permission_subtree(
        self,
        *,
        permission: Permission,
        node_type: type[PID],
    ) -> PERMISSION_TREE[PID] | list[str] | None:
        if permission.is_leaf:
            if permission.has_payload:
                return []
            return None
        return {
            child.node.value
            if node_type is str
            else child.node: self._build_permission_subtree(  # type:ignore
                permission=child, node_type=node_type
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
            f"Subject and role IDs have to be of type int or string! Got type `{type(eid)}` for `{eid}`."
        )


def build_entity_permission_nodes(
    *, permission_map: PermissionMap, node_type: type[PID]
) -> PERMISSION_NODES[PID]:
    return {
        perm.node.value
        if node_type is str  # type:ignore
        else perm.node: [val for val in payload]
        if payload
        else None
        for perm, payload in permission_map.items()
    }
