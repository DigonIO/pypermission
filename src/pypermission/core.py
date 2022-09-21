from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pypermission.error import PermissionParsingError


class Permission:

    _node: str
    _parent: Permission | None
    _ancestors: tuple[Permission, ...]
    _childs: set[Permission]
    _sub_graph: dict[str, Permission]
    _has_payload: bool
    _is_leave: bool

    def __init__(self) -> None:
        self._node = "*"
        self._parent = None
        self._ancestors = tuple()
        self._childs = set()
        self._sub_graph = {}
        self._has_payload = False
        self._is_leave = False

    @property
    def node(self) -> str:
        return self._node

    @property
    def parent(self) -> Permission | None:
        return self._parent

    @property
    def ancestors(self) -> tuple[Permission, ...]:
        return self._ancestors

    @property
    def childs(self) -> set[Permission]:
        return self._childs

    @property
    def sub_graph(self) -> dict[str, Permission]:
        return self._sub_graph

    @property
    def has_payload(self) -> bool:
        return self._has_payload

    @property
    def is_leave(self) -> bool:
        return self._is_leave


PermissionMap = dict[Permission, set[str]]
EntityID = int | str


class CustomPermission(Permission):
    def __init__(self, *, node: str, parent: Permission, has_payload: bool, is_leave: bool) -> None:
        self._node = node
        self._parent = parent
        self._ancestors = tuple()
        self._childs = set()
        self._sub_graph = {}
        self._has_payload = has_payload
        self._is_leave = is_leave

    def _update_ancestors(self):
        self._ancestors = (*self._parent.ancestors, self._parent)


class Authority(ABC):
    _root_permission: Permission
    _node_permission_map: dict[str, Permission]

    def __init__(self) -> None:
        self._root_permission = Permission()
        self._node_permission_map = {}

    @property
    def root_permission(self) -> Permission:
        return self._root_permission

    @staticmethod
    def _serialize_permission_node(permission: Permission, payload: str | None) -> str:
        node: str = permission.node
        if permission.has_payload:
            node = f"{node[:-2]}{payload}>"
        return node

    def _deserialize_permission_node(self, node: str) -> tuple[Permission, str | None]:

        node_sections: list[str] = node.split(".")
        last_section: str = node_sections[-1]

        payload = None
        if last_section[0] == "<" and last_section[-1] == ">":
            payload = last_section[1:-1]
            last_section = "<x>"

        node = ".".join(node_sections[:-1]) + "." + last_section
        try:
            return self._node_permission_map[node], payload
        except KeyError:
            raise PermissionParsingError("Unknown permission id!", node)

    def register_permission(self, *, node: str):
        "Register permission"

        if node in self._node_permission_map:
            raise PermissionParsingError("Permission has been registered before!")

        node_sections: list[str] = node.split(".")
        last_section: str = node_sections[-1]

        has_payload = False
        if last_section == "*":
            parent_node_sections: list[str] = node_sections[0:-2]
            last_section = node_sections[-2]
            is_leave = False
        else:
            parent_node_sections = node_sections[0:-1]
            is_leave = True

            if last_section == "<x>":
                has_payload = True

        parent = self._root_permission
        potential_parent_node = ""
        for section in parent_node_sections:
            potential_parent_node = potential_parent_node + "." + section
            try:
                parent = parent.sub_graph[section]
            except KeyError:
                raise PermissionParsingError(
                    "A nested permission requires a parent permission!",
                    potential_parent_node[1:] + ".*",
                )

        if parent.is_leave:
            raise PermissionParsingError(
                "The desired parent permission is a leave permission!", parent.node
            )

        new_perm = CustomPermission(
            node=node, parent=parent, has_payload=has_payload, is_leave=is_leave
        )

        if not parent_node_sections:
            new_perm._parent = self._root_permission
        new_perm._update_ancestors()

        parent.sub_graph[last_section] = new_perm
        parent.childs.add(new_perm)

        self._node_permission_map[node] = new_perm
        return new_perm
