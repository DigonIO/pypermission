import json
from enum import Enum
from pathlib import Path
from typing import Any, Literal, TypedDict, cast

from pypermission.core import Authority as _Authority
from pypermission.core import EntityID, Permission, PermissionMap, PermissionNode
from pypermission.error import (
    EntityIDCollisionError,
    MissingPathError,
    MissingPayloadError,
    UnknownSubjectIDError,
    UnusedPayloadError,
    GroupCycleError,
    UnknownPermissionNodeError,
)

OutIDTypeDict = dict[str, Literal["str"] | Literal["int"]]
InIDTypeDict = dict[str, type[str | int]]


class NonSerialGroup(TypedDict):
    subjects: list[str]
    nodes: list[str]
    childs: list[str]


class NonSerialData(TypedDict):
    groups: dict[str, NonSerialGroup]
    subjects: dict[str, list[str]]
    g_id_types: dict[str, str]
    s_id_types: dict[str, str]


class PermissionableEntity:

    _id: EntityID
    _permission_map: PermissionMap

    def __init__(self, *, id: EntityID):
        self._id = id
        self._permission_map = {}

    @property
    def id(self) -> EntityID:
        return self._id

    @property
    def permission_map(self) -> PermissionMap:
        return self._permission_map

    def set_permission_map(self, *, new_permission_map: PermissionMap) -> None:
        self._permission_map = new_permission_map

    def has_permission(self, *, permission: Permission, payload: str | None = None) -> bool:
        for ancestor in permission.ancestors:
            if ancestor in self._permission_map:
                return True

        try:
            payload_set = self._permission_map[permission]
        except KeyError:
            return False

        if payload:
            return payload in payload_set

        return True


class Subject(PermissionableEntity):

    _g_ids: set[EntityID]

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(id=id)
        self._g_ids = set()

    @property
    def g_ids(self) -> set[EntityID]:
        return self._g_ids


class Group(PermissionableEntity):

    _s_ids: set[EntityID]
    _parent_ids: set[EntityID]
    _child_ids: set[EntityID]

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(id=id)
        self._s_ids = set()
        self._parent_ids = set()
        self._child_ids = set()

    @property
    def s_ids(self) -> set[EntityID]:
        return self._s_ids

    @property
    def parent_ids(self) -> set[EntityID]:
        return self._parent_ids

    @property
    def child_ids(self) -> set[EntityID]:
        return self._child_ids


class Authority(_Authority):

    _subjects: dict[EntityID, Subject]
    _groups: dict[EntityID, Group]
    _data_file: Path | str | None

    def __init__(
        self, *, nodes: type[Enum] | None = None, data_file: Path | str | None = None
    ) -> None:
        super().__init__(nodes=nodes)

        self._subjects = {}
        self._groups = {}
        self._data_file = data_file

    def save_to_file(self, path: Path | str | None):
        """Save the current state to file formatted as JSON."""
        if not path:
            path = self._data_file
        if not path:
            raise MissingPathError

        serial_data = self.save_to_str()
        with open(path, "r") as handle:
            handle.write(serial_data)

    def load_from_file(self, path: Path | str | None) -> None:
        """Load a previous state from a JSON formatted file."""
        if not path:
            path = self._data_file
        if not path:
            raise MissingPathError

        with open(path, "r") as handle:
            serial_data = handle.read()
        self.load_from_str(serial_data=serial_data)

    def save_to_str(self) -> str:
        """Save the current state to string formatted as JSON."""
        groups: dict[str, NonSerialGroup] = {}
        subjects: dict[str, list[str]] = {}
        s_id_types: OutIDTypeDict = {}
        g_id_types: OutIDTypeDict = {}
        data = NonSerialData(
            groups=groups,
            subjects=subjects,
            s_id_types=s_id_types,
            g_id_types=g_id_types,
        )

        for g_id, group in self._groups.items():
            if isinstance(g_id, str):
                g_id_types[str(g_id)] = "str"
            else:  # isinstance(g_id, int):
                g_id_types[str(g_id)] = "int"
            nodes: list[str] = []
            for permission, payload_set in group.permission_map.items():
                if payload_set:
                    for payload in payload_set:
                        node = self._serialize_permission_node(
                            permission=permission, payload=payload
                        )
                else:
                    node = self._serialize_permission_node(permission=permission, payload=None)
                nodes.append(node)

            grouped_subjects: list[str] = [str(s_id) for s_id in group.s_ids]
            childs: list[str] = [str(child_id) for child_id in group.child_ids]
            groups[str(g_id)] = NonSerialGroup(
                subjects=grouped_subjects, nodes=nodes, childs=childs
            )

        for s_id, subject in self._subjects.items():
            if isinstance(s_id, str):
                s_id_types[str(s_id)] = "str"
            else:  # isinstance(g_id, int):
                s_id_types[str(s_id)] = "int"
            nodes = []
            for permission, payload_set in subject.permission_map.items():
                if payload_set:
                    for payload in payload_set:
                        node = self._serialize_permission_node(
                            permission=permission, payload=payload
                        )
                else:
                    node = self._serialize_permission_node(permission=permission, payload=None)
                nodes.append(node)

            subjects[str(s_id)] = nodes

        return self._serialize_data(non_serial_data=data)

    def load_from_str(self, *, serial_data: str) -> None:
        """Load a previous state from a JSON formatted string."""
        data: Any = self._deserialize_data(serial_data=serial_data)

        # populate subject id types
        s_id_types: InIDTypeDict = {}
        for s_id_str, type_str in data["s_id_types"].items():
            if type_str == "str":
                s_id_types[s_id_str] = str
            else:
                s_id_types[s_id_str] = int

        # populate group id types
        g_id_types: InIDTypeDict = {}
        for g_id_str, type_str in data["g_id_types"].items():
            if type_str == "str":
                g_id_types[g_id_str] = str
            else:
                g_id_types[g_id_str] = int

        # populate subjects
        for s_id_str, nodes in data["subjects"].items():
            s_id = s_id_types[s_id_str](s_id_str)
            subject = Subject(id=s_id)
            self._subjects[s_id] = subject

            # add permissions to a subject
            for node_str in nodes:
                permission, payload = self._deserialize_permission_node(node_str=node_str)
                permission_map = subject.permission_map
                if payload:
                    payload_set = permission_map.get(permission, None)
                    if not payload_set:
                        payload_set = set()
                        permission_map[permission] = payload_set
                    payload_set.add(payload)
                else:
                    permission_map[permission] = set()

        # populate groups
        for g_id_str, group_data in data["groups"].items():
            g_id = g_id_types[g_id_str](g_id_str)
            group = Group(id=g_id)
            self._groups[g_id] = group

            # add permissions to a group
            for node_str in group_data["nodes"]:
                permission, payload = self._deserialize_permission_node(node_str=node_str)
                permission_map = group.permission_map
                if payload:
                    payload_set = permission_map.get(permission, None)
                    if not payload_set:
                        payload_set = set()
                        permission_map[permission] = payload_set
                    payload_set.add(payload)
                else:
                    permission_map[permission] = set()

            # add group ids to subjects of a group and vice versa
            for s_id_str in group_data["subjects"]:
                s_id = s_id_types[s_id_str](s_id_str)
                group.s_ids.add(s_id)
                self._subjects[s_id].g_ids.add(g_id)

            # add child ids to this group
            for child_id_str in group_data["childs"]:
                child_id = g_id_types[child_id_str](child_id_str)
                group.child_ids.add(child_id)

        # populate group parent_ids
        for g_id, group in self._groups.items():
            for child_id in group.child_ids:
                child = self._groups[child_id]
                child.parent_ids.add(g_id)

    def add_subject(self, s_id: EntityID) -> None:
        """Create a new subject for a given ID."""
        if s_id in self._subjects:
            raise EntityIDCollisionError

        subject = Subject(id=s_id)
        self._subjects[s_id] = subject

    def add_group(self, g_id: EntityID) -> None:
        """Create a new group for a given ID."""
        if g_id in self._subjects:
            raise EntityIDCollisionError

        group = Group(id=g_id)
        self._groups[g_id] = group

    def rem_subject(self, s_id: EntityID) -> None:
        """Remove a subject for a given ID."""
        subject = self._subjects.pop(s_id, None)
        if subject is None:
            return
        for g_id in subject.g_ids:
            self._groups[g_id].s_ids.remove(s_id)

    def rem_group(self, g_id: EntityID) -> None:
        """Remove a group for a given ID."""
        group = self._groups.pop(g_id, None)
        if group is None:
            return
        for s_id in group.s_ids:
            self._subjects[s_id].g_ids.remove(g_id)

    def subject_has_permission(
        self, *, s_id: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a subject has a wanted permission."""
        permission = self._get_permission(node=node)
        _validate_payload_status(permission=permission, payload=payload)
        subject = self._get_subject(s_id=s_id)

        if subject.has_permission(permission=permission, payload=payload):
            return True

        for g_id in subject.g_ids:
            group = self._groups[g_id]
            if self._recursive_group_has_permission(
                group=group, permission=permission, payload=payload
            ):
                return True

        return False

    def subject_add_permission(
        self, *, s_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Add a permission to a subject."""
        permission = self._get_permission(node=node)
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(s_id=s_id).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def subject_rem_permission(
        self, *, s_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Remove a permission from a subject."""
        permission = self._get_permission(node=node)
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(s_id=s_id).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def subject_get_permissions(self, *, s_id: EntityID) -> PermissionMap:
        """Get a copy of all permissions from a subject."""
        return self._get_subject(s_id=s_id).permission_map.copy()

    def subject_get_groups(self, *, s_id: EntityID) -> set[EntityID]:
        """Get a set of a group IDs of a groups a subject is member of."""
        subject = self._get_subject(s_id=s_id)
        return subject.g_ids.copy()

    def group_has_permission(
        self, *, g_id: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a group has a wanted permission."""
        permission = self._get_permission(node=node)
        _validate_payload_status(permission=permission, payload=payload)
        group = self._get_group(g_id=g_id)

        return self._recursive_group_has_permission(
            group=group, permission=permission, payload=payload
        )

    def group_add_permission(
        self, *, g_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Add a permission to a group."""
        permission = self._get_permission(node=node)
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(g_id=g_id).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rem_permission(
        self, *, g_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Remove a permission from a group."""
        permission = self._get_permission(node=node)
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(g_id=g_id).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_get_permissions(self, *, g_id: EntityID) -> PermissionMap:
        """Get a copy of all permissions from a group."""
        return self._get_group(g_id=g_id).permission_map.copy()

    def group_get_groups(self, *, g_id: EntityID) -> set[EntityID]:
        """Get a set of all parent group IDs of a group."""
        group = self._get_group(g_id=g_id)
        return group.parent_ids.copy()

    def group_add_subject(self, *, g_id: EntityID, s_id: EntityID) -> None:
        """Add a subject to a group."""
        group = self._get_group(g_id=g_id)
        subject = self._get_subject(s_id=s_id)

        group.s_ids.add(s_id)
        subject.g_ids.add(g_id)

    def group_add_group(self, *, parent_id: EntityID, child_id: EntityID) -> None:
        """Add a group to a group."""
        parent = self._get_group(g_id=parent_id)
        child = self._get_group(g_id=child_id)

        self._detect_group_cycle(parent=parent, child_id=child_id)

        parent.child_ids.add(child_id)
        child.parent_ids.add(parent_id)

    def group_rem_subject(self, *, g_id: EntityID, s_id: EntityID) -> None:
        """Remove a subject from a group."""
        group = self._get_group(g_id=g_id)
        subject = self._get_subject(s_id=s_id)

        group.s_ids.remove(s_id)
        subject.g_ids.remove(g_id)

    def group_rem_group(self, *, parent_id: EntityID, child_id: EntityID) -> None:
        """Remove a group from a group."""
        parent = self._get_group(g_id=parent_id)
        child = self._get_group(g_id=child_id)

        parent.child_ids.remove(child_id)
        child.parent_ids.remove(parent_id)

    def _get_subject(self, *, s_id: EntityID) -> Subject:
        """Just a simple wrapper to avoid some boilerplate code while getting a subject."""
        try:
            return self._subjects[s_id]
        except KeyError:
            raise UnknownSubjectIDError

    def _get_group(self, *, g_id: EntityID) -> Group:
        """Just a simple wrapper to avoid some boilerplate code while getting a group."""
        try:
            return self._groups[g_id]
        except KeyError:
            raise UnknownSubjectIDError

    def _get_permission(self, *, node: PermissionNode) -> Permission:
        """Just a simple wrapper to avoid some boilerplate code while getting a node."""
        try:
            return self._node_permission_map[node]
        except KeyError:
            raise UnknownPermissionNodeError

    def _detect_group_cycle(self, parent: Group, child_id: EntityID):
        """Detect a cycle in nested group tree."""
        if child_id in parent.parent_ids:
            raise GroupCycleError
        for parent_parent_id in parent.parent_ids:
            parent_parent = self._groups[parent_parent_id]
            self._detect_group_cycle(parent=parent_parent, child_id=child_id)

    def _recursive_group_has_permission(
        self, group: Group, permission: Permission, payload: str | None
    ):
        """Recursively check whether the group or one of its parents has the perm searched for."""
        if group.has_permission(permission=permission, payload=payload):
            return True

        for parent_id in group.parent_ids:
            parent = self._groups[parent_id]
            if self._recursive_group_has_permission(
                group=parent, permission=permission, payload=payload
            ):
                return True

        return False

    @staticmethod
    def _serialize_data(*, non_serial_data: NonSerialData) -> str:
        # cast only valid with one argument to dumps
        return cast(str, json.dumps(non_serial_data))

    @staticmethod
    def _deserialize_data(*, serial_data: str) -> Any:
        return json.loads(serial_data)


def _validate_payload_status(*, permission: Permission, payload: str | None):
    """Check the permission payload combinatorics."""
    if permission.has_payload and payload is None:
        raise MissingPayloadError

    if not permission.has_payload and payload is not None:
        raise UnusedPayloadError


def _add_permission_map_entry(
    *, permission_map: PermissionMap, permission: Permission, payload: str | None
) -> None:
    """Add a permission to a permission map."""
    try:
        payload_set = permission_map[permission]
    except KeyError:
        payload_set = set()
        permission_map[permission] = payload_set

    if payload:
        payload_set.add(payload)


def _rem_permission_map_entry(
    *, permission_map: PermissionMap, permission: Permission, payload: str | None
) -> None:
    """Remove a permission from a permission map."""
    try:
        payload_set = permission_map[permission]
    except KeyError:
        return
    if payload in payload_set:
        payload_set.remove(payload)
    if not payload:
        permission_map.pop(permission)
