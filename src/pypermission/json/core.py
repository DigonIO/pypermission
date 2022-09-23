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
)

OutIDTypeDict = dict[str, Literal["str"] | Literal["int"]]
InIDTypeDict = dict[str, type[str | int]]


class NonSerialGroup(TypedDict):
    subjects: set[str]
    nodes: list[str]


class NonSerialData(TypedDict):
    groups: dict[str, NonSerialGroup]
    subjects: dict[str, list[str]]
    group_id_types: dict[str, str]
    subject_id_types: dict[str, str]


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

    _group_ids: set[EntityID]

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(id=id)
        self._group_ids = set()

    @property
    def group_ids(self) -> set[EntityID]:
        return self._group_ids


class Group(PermissionableEntity):

    _subject_ids: set[EntityID]
    _parent_ids: set[EntityID]
    _child_ids: set[EntityID]

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(id=id)
        self._subject_ids = set()
        self._parent_ids = set()
        self._child_ids = set()

    @property
    def subject_ids(self) -> set[EntityID]:
        return self._subject_ids

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
        subject_id_types: OutIDTypeDict = {}
        group_id_types: OutIDTypeDict = {}
        data = NonSerialData(
            groups=groups,
            subjects=subjects,
            subject_id_types=subject_id_types,
            group_id_types=group_id_types,
        )

        for group_id, group in self._groups.items():
            if isinstance(group_id, str):
                group_id_types[str(group_id)] = "str"
            else:  # isinstance(group_id, int):
                group_id_types[str(group_id)] = "int"
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

            grouped_subjects: list[str] = [str(subject_id) for subject_id in group.subject_ids]
            groups[str(group_id)] = NonSerialGroup(subjects=grouped_subjects, nodes=nodes)

        for subject_id, subject in self._subjects.items():
            if isinstance(subject_id, str):
                subject_id_types[str(subject_id)] = "str"
            else:  # isinstance(group_id, int):
                subject_id_types[str(subject_id)] = "int"
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

            subjects[str(subject_id)] = nodes

        return self._serialize_data(non_serial_data=data)

    def load_from_str(self, *, serial_data: str) -> None:
        """Load a previous state from a JSON formatted string."""
        data: Any = self._deserialize_data(serial_data=serial_data)

        # populate subject id types
        subject_id_types: InIDTypeDict = {}
        for subject_id_str, type_str in data["subject_id_types"].items():
            if type_str == "str":
                subject_id_types[subject_id_str] = str
            else:
                subject_id_types[subject_id_str] = int

        # populate subject id types
        group_id_types: InIDTypeDict = {}
        for group_id_str, type_str in data["group_id_types"].items():
            if type_str == "str":
                group_id_types[group_id_str] = str
            else:
                group_id_types[group_id_str] = int

        # populate subjects
        for subject_id_str, nodes in data["subjects"].items():
            subject_id = subject_id_types[subject_id_str](subject_id_str)
            subject = Subject(id=subject_id)
            self._subjects[subject_id] = subject

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
        for group_id_str, group_data in data["groups"].items():
            group_id = group_id_types[group_id_str](group_id_str)
            group = Group(id=group_id)
            self._groups[group_id] = group

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
            for subject_id_str in group_data["subjects"]:
                subject_id = subject_id_types[subject_id_str](subject_id_str)
                group.subject_ids.add(subject_id)
                self._subjects[subject_id].group_ids.add(group_id)

    def add_subject(self, subject_id: EntityID) -> None:
        """Create a new subject for a given ID."""
        if subject_id in self._subjects:
            raise EntityIDCollisionError

        subject = Subject(id=subject_id)
        self._subjects[subject_id] = subject

    def add_group(self, group_id: EntityID) -> None:
        """Create a new group for a given ID."""
        if group_id in self._subjects:
            raise EntityIDCollisionError

        group = Group(id=group_id)
        self._groups[group_id] = group

    def rem_subject(self, subject_id: EntityID) -> None:
        """Remove a subject for a given ID."""
        subject = self._subjects.pop(subject_id, None)
        if subject is None:
            return
        for group_id in subject.group_ids:
            self._groups[group_id].subject_ids.remove(subject_id)

    def rem_group(self, group_id: EntityID) -> None:
        """Remove a group for a given ID."""
        group = self._groups.pop(group_id, None)
        if group is None:
            return
        for subject_id in group.subject_ids:
            self._subjects[subject_id].group_ids.remove(group_id)

    def subject_has_permission(
        self, *, subject_id: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a subject has a wanted permission."""
        permission = self._node_permission_map[node]  # TODO raise if unknown node
        _validate_payload_status(permission=permission, payload=payload)
        subject = self._get_subject(subject_id=subject_id)

        if subject.has_permission(permission=permission, payload=payload):
            return True

        for group_id in subject.group_ids:
            group = self._groups[group_id]
            if group.has_permission(permission=permission, payload=payload):
                return True

        return False

    def subject_add_permission(
        self, *, subject_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Add a permission to a subject."""
        permission = self._node_permission_map[node]  # TODO raise if unknown node
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(subject_id=subject_id).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def subject_rem_permission(
        self, *, subject_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Remove a permission from a subject."""
        permission = self._node_permission_map[node]  # TODO raise if unknown node
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(subject_id=subject_id).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def subject_get_permissions(self, *, subject_id: EntityID) -> PermissionMap:
        """Get a copy of all permissions from a subject."""
        return self._get_subject(subject_id=subject_id).permission_map.copy()

    def group_has_permission(
        self, *, group_id: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a group has a wanted permission."""
        permission = self._node_permission_map[node]  # TODO raise if unknown node
        _validate_payload_status(permission=permission, payload=payload)
        group = self._get_group(group_id=group_id)

        return group.has_permission(permission=permission, payload=payload)

    def group_add_permission(
        self, *, group_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Add a permission to a group."""
        permission = self._node_permission_map[node]  # TODO raise if unknown node
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(group_id=group_id).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rem_permission(
        self, *, group_id: EntityID, node: PermissionNode, payload: str | None = None
    ):
        """Remove a permission from a group."""
        permission = self._node_permission_map[node]  # TODO raise if unknown node
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(group_id=group_id).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_get_permissions(self, *, group_id: EntityID) -> PermissionMap:
        """Get a copy of all permissions from a group."""
        return self._get_group(group_id=group_id).permission_map.copy()

    def group_add_subject(self, *, group_id: EntityID, subject_id: EntityID) -> None:
        """Add a subject to a group."""
        group = self._get_group(group_id=group_id)
        subject = self._get_subject(subject_id=subject_id)

        group.subject_ids.add(subject_id)
        subject.group_ids.add(group_id)

    def group_add_group(self, *, parent_id: EntityID, child_id: EntityID) -> None:
        """Add a group to a group."""
        parent = self._get_group(group_id=parent_id)
        child = self._get_group(group_id=child_id)

        self._detect_group_cycle(parent=parent, child_id=child_id)

        parent.child_ids.add(child_id)
        child.parent_ids.add(parent_id)

    def group_rem_subject(self, *, group_id: EntityID, subject_id: EntityID) -> None:
        """Remove a subject from a group."""
        group = self._get_group(group_id=group_id)
        subject = self._get_subject(subject_id=subject_id)

        group.subject_ids.remove(subject_id)
        subject.group_ids.remove(group_id)

    def group_rem_group(self, *, parent_id: EntityID, child_id: EntityID) -> None:
        """Remove a group from a group."""
        parent = self._get_group(group_id=parent_id)
        child = self._get_group(group_id=child_id)

        parent.child_ids.remove(child_id)
        child.parent_ids.remove(parent_id)

    def _get_subject(self, *, subject_id: EntityID) -> Subject:
        """Just a simple wrapper to avoid some boilerplate code while getting a subject."""
        try:
            return self._subjects[subject_id]
        except KeyError:
            raise UnknownSubjectIDError

    def _get_group(self, *, group_id: EntityID) -> Group:
        """Just a simple wrapper to avoid some boilerplate code while getting a group."""
        try:
            return self._groups[group_id]
        except KeyError:
            raise UnknownSubjectIDError

    def _detect_group_cycle(self, parent: Group, child_id: EntityID):
        """Detect a cycle in nested group tree."""
        if child_id in parent.parent_ids:
            raise GroupCycleError
        for parent_parent_id in parent.parent_ids:
            parent_parent = self._groups[parent_parent_id]
            self._detect_group_cycle(parent=parent_parent, child_id=child_id)

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
