from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pypermission.error import PermissionError


class Permission:
    def __init__(self):
        self._node: str = "*"
        self._parent: Permission | None = None
        self._ancestors: tuple[Permission, ...] = tuple()
        self._childs: set[Permission] = set()
        self._sub_graph: dict[str, Permission] = {}
        self._has_payload = False
        self._is_leave = False

    @property
    def node(self) -> str:
        return self._node

    @property
    def parent(self) -> Permission | None:
        return self._parent

    @property
    def ancestors(self) -> tuple[Permission]:
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

    def _update_ancestors(self):
        self._ancestors = (*self._parent.ancestors, self._parent)


PermissionMap = dict[Permission, set[str]]
EntityID = TypeVar("EntityID", int, str)


class CustomPermission(Permission):
    def __init__(self, *, node: str, parent: Permission, has_payload: bool, is_leave: bool) -> None:
        self._node: str = node
        self._parent: Permission = parent
        self._ancestors: tuple[Permission, ...] = None
        self._childs: set[Permission] = set()
        self._sub_graph: dict[str, Permission] = {}
        self._has_payload = has_payload
        self._is_leave = is_leave


class Authority(ABC):
    _root_permission: Permission
    _node_permission_map: dict[str, Permission]

    def __init__(self) -> None:
        self._root_permission = Permission()
        self._node_permission_map = {}

    @staticmethod
    def _serialize_permission_node(permission: Permission, payload: str | None) -> str:
        node: str = permission.id
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

        node = ".".join(node_sections) + "." + last_section
        try:
            return self._node_permission_map[node], payload
        except KeyError:
            raise PermissionError("Unknown permission id!", node)

    @abstractmethod
    def subject_has_permission(
        self, *, subject_id: EntityID, perm: Permission, payload: str | None = None
    ) -> set[str]:
        """
        Check if a subject has a given permission and return its potential payload.

        Returns
        -------

        set[str] : Payload of a permission. Set can be empty.

        Raises
        ------

        PermissionError
        """
        # TODO multiple errors

    @abstractmethod
    def subject_get_permissions(self, *, subject_id: EntityID) -> PermissionMap:
        """
        Get all permissions and there potential payload for a subject.

        Returns
        -------

        PermissionMap : Payload of a permission. Set can be empty.

        Raises
        ------

        PermissionError
        """
        # TODO multiple errors

    def register_permission(self, *, node: str):
        "Register permission"

        if node in self._node_permission_map:
            raise PermissionError("Permission has been registered before!")

        node_sections: list[str] = node.split(".")
        last_section: str = node_sections[-1]

        if last_section == "*":
            parent_node_sections: list[str] = node_sections[0:-2]
            last_section: str = node_sections[-2]
            is_leave = False
        else:
            parent_node_sections: list[str] = node_sections[0:-1]
            is_leave = True

            if last_section == "<x>":
                has_payload = True

        parent = self._root_permission
        potential_parent_node = ""
        for section in parent_node_sections:
            potential_parent_node = potential_parent_node + "." + section
            try:
                parent: Permission = parent.sub_graph[section]
            except KeyError:
                raise PermissionError(
                    "A nested permission requires a parent permission!",
                    potential_parent_node[1:] + ".*",
                )

        if parent.is_leave:
            raise PermissionError("The desired parent permission is a leave permission!", parent.node)

        new_perm = CustomPermission(
            id=node, parent=parent, has_payload=has_payload, is_leave=is_leave
        )

        if not parent_node_sections:
            new_perm._parent = self._root_permission
        new_perm._update_ancestors()

        parent.sub_graph[last_section] = new_perm
        parent.childs.add(new_perm)

        self._node_permission_map[node] = new_perm
        return new_perm
