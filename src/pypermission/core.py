from __future__ import annotations
from typing import TypeVar
from abc import ABC, abstractmethod

from pypermission.error import PermissionError


class Permission:
    def __init__(self):
        self._id: str = "*"
        self._parent: Permission | None = None
        self._ancestors: tuple[Permission, ...] = tuple()
        self._childs: set[Permission] = set()
        self._sub_graph: dict[str, Permission] = {}
        self._has_payload = False
        self._is_leave = False

    @property
    def id(self) -> str:
        return self._id

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
    def __init__(self, *, id: str, parent: Permission, has_payload: bool, is_leave: bool) -> None:
        self._id: str = id
        self._parent: Permission = parent
        self._ancestors: tuple[Permission, ...] = None
        self._childs: set[Permission] = set()
        self._sub_graph: dict[str, Permission] = {}
        self._has_payload = has_payload
        self._is_leave = is_leave


class Authority(ABC):
    _root_permission: Permission
    _id_permission_map: dict[str, Permission]

    def __init__(self):
        self._root_permission = Permission()
        self._id_permission_map = {}

    def _deserialize_permission(self, perm_id: str) -> tuple[Permission, str | None]:

        id_sections: list[str] = perm_id.split(".")
        last_section: str = id_sections[-1]

        payload = None
        if last_section[0] == "<" and last_section[-1] == ">":
            payload = last_section[1:-1]
            last_section = "<x>"

        perm_id = ".".join(id_sections) + "." + last_section
        try:
            return self._id_permission_map[perm_id], payload
        except KeyError:
            raise PermissionError("Unknown permission id!", perm_id)

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

    def register_permission(self, *, perm_id: str):
        "Register permission"

        if perm_id in self._id_permission_map:
            raise PermissionError("Permission has been registered before!")

        id_sections: list[str] = perm_id.split(".")
        last_section: str = id_sections[-1]

        if last_section == "*":
            parent_id_sections: list[str] = id_sections[0:-2]
            last_section: str = id_sections[-2]
            is_leave = False
        else:
            parent_id_sections: list[str] = id_sections[0:-1]
            is_leave = True

            if last_section == "<x>":
                has_payload = True

        parent = self._root_permission
        potential_parent_id = ""
        for section in parent_id_sections:
            potential_parent_id = potential_parent_id + "." + section
            try:
                parent: Permission = parent.sub_graph[section]
            except KeyError:
                raise PermissionError(
                    "A nested permission requires a parent permission!",
                    potential_parent_id[1:] + ".*",
                )

        if parent.is_leave:
            raise PermissionError("The desired parent permission is a leave permission!", parent.id)

        new_perm = CustomPermission(
            id=perm_id, parent=parent, has_payload=has_payload, is_leave=is_leave
        )

        if not parent_id_sections:
            new_perm._parent = self._root_permission
        new_perm._update_ancestors()

        parent.sub_graph[last_section] = new_perm
        parent.childs.add(new_perm)

        self._id_permission_map[perm_id] = new_perm
        return new_perm
