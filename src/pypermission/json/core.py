import json
from pathlib import Path
from typing import TypedDict

from pypermission.core import Authority as _Authority
from pypermission.core import EntityID, Permission, PermissionMap
from pypermission.error import (
    EntityIDCollisionError,
    MissingPayloadError,
    UnknownSubjectIDError,
    UnusedPayloadError,
)


class NonSerialGroup(TypedDict):
    subjects: set[EntityID]
    nodes: list[str]


class NonSerialData(TypedDict):
    groups: dict[EntityID, NonSerialGroup]
    subjects: dict[EntityID, list[str]]


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

    def set_permission_map(self, *, new_permission_map: dict[Permission, str | None]) -> None:
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
        super().__init__(self, id=id)
        self._group_ids = set()

    @property
    def group_ids(self) -> set[EntityID]:
        return self._group_ids


class Group(PermissionableEntity):

    _subject_ids: set[EntityID]

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(self, id=id)
        self._subject_ids = set()

    @property
    def subject_ids(self) -> set[EntityID]:
        return self._subject_ids


class Authority(_Authority):

    _subjects: dict[EntityID, Subject]
    _groups: dict[EntityID, Group]
    _data_file: Path | str

    def __init__(self, *, data_file: Path | str | None = None) -> None:
        super().__init__(self)

        self._subjects = {}
        self._groups = {}
        self._data_file = data_file

    def save_to_file(self, path: Path | str | None):
        """Save the current state to file formatted as JSON."""
        if not path:
            path = self._data_file

        serial_data = self.save_to_str()
        with open(path, "r") as handle:
            handle.write(serial_data)

    def load_from_file(self, path: Path | str | None) -> None:
        """Load a previous state from a JSON formatted file."""
        if not path:
            path = self._data_file

        with open(path, "r") as handle:
            serial_data = handle.read()
        self.load_from_str(serial_data=serial_data)

    def save_to_str(self) -> str:
        """Save the current state to string formatted as JSON."""
        groups = {}
        subjects = {}
        data = NonSerialData(groups=groups, subjects=subjects)

        for group_id, group in self._groups.items():
            nodes: list[str] = [
                self._serialize_permission_node(permission=permission, payload=payload)
                for permission, payload in group.permission_map
            ]
            groups[group_id] = NonSerialGroup(subjects=group.subject_ids, nodes=nodes)

        for subject_id, subject in self._subjects.items():
            subjects[subject_id] = subject.group_ids

        return self._serialize_data(non_serial_data=data)

    def load_from_str(self, *, serial_data: str) -> None:
        """Load a previous state from a JSON formatted string."""
        data: NonSerialData = self._deserialize_data(serial_data=serial_data)

        # populate subjects
        for subject_id, nodes in data["subjects"].items():
            subject = Subject(id=subject_id)
            self._subjects[subject_id] = subject

            # add permissions to a subject
            for node in nodes:
                permission, payload = self._deserialize_permission_node(node=node)
                subject.permission_map[permission] = payload

        # populate groups
        for group_id, group_data in data["groups"].items():
            group = Group(id=group_id)
            self._groups[group_id] = group

            # add permissions to a group
            for node in group_data["nodes"]:
                permission, payload = self._deserialize_permission_node(node=node)
                subject.permission_map[permission] = payload

            # add group ids to subjects of a group and vice versa
            for subject_id in group_data["subjects"]:
                group.subject_ids.add(subject_id)
                self._subjects[subject_id].group_ids.add(group_id)

    def subject_add(self, new_subject_id: EntityID) -> None:
        """Create a new subject for a given ID."""
        if new_subject_id in self._subjects:
            raise EntityIDCollisionError

        subject = Subject(id=new_subject_id)
        self._subjects[new_subject_id] = subject

    def subject_rem(self, subject_id: EntityID) -> None:
        """Remove a subject for a given ID."""
        subject = self._subjects.pop(subject_id, None)
        if subject is None:
            return
        for group_id in subject.group_ids:
            self._groups[group_id].subject_ids.remove(subject_id)

    def subject_has_permission(
        self, *, subject_id: EntityID, permission: Permission, payload: str | None = None
    ) -> bool:
        """Check if a subject has a wanted permission."""
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
        self, *, subject_id: EntityID, permission: Permission, payload: str | None = None
    ):
        """Add a permission to a subject."""
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(subject_id=subject_id).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def subject_rem_permission(
        self, *, subject_id: EntityID, permission: Permission, payload: str | None = None
    ):
        """Remove a permission from a subject."""
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(subject_id=subject_id).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def subject_get_permissions(self, *, subject_id: EntityID) -> PermissionMap:
        """Get a copy of all permissions from a subject."""
        return self._get_subject(subject_id=subject_id).permission_map.copy()

    def subject_set_permissions(self, *, subject_id: EntityID, permissions: PermissionMap) -> None:
        """Overwrite all permissions for a subject."""
        return self._get_subject(subject_id=subject_id).set_permission_map(
            new_permission_map=permissions
        )

    def group_add(self, new_group_id: EntityID) -> None:
        """Create a new group for a given ID."""
        if new_group_id in self._subjects:
            raise EntityIDCollisionError

        group = Group(id=new_group_id)
        self._groups[new_group_id] = group

    def group_rem(self, group_id: EntityID) -> None:
        """Remove a group for a given ID."""
        group = self._groups.pop(group_id, None)
        if group is None:
            return
        for subject_id in group.subject_ids:
            self._subjects[subject_id].group_ids.remove(group_id)

    def group_has_permission(
        self, *, group_id: EntityID, permission: Permission, payload: str | None = None
    ) -> bool:
        """Check if a group has a wanted permission."""
        _validate_payload_status(permission=permission, payload=payload)
        group = self._get_group(group_id=group_id)

        return group.has_permission(permission=permission, payload=payload)

    def group_add_permission(
        self, *, group_id: EntityID, permission: Permission, payload: str | None = None
    ):
        """Add a permission to a group."""
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(group_id=group_id).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rem_permission(
        self, *, group_id: EntityID, permission: Permission, payload: str | None = None
    ):
        """Remove a permission from a group."""
        _validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(group_id=group_id).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_get_permissions(self, *, group_id: EntityID) -> PermissionMap:
        """Get a copy of all permissions from a group."""
        return self._get_group(group_id=group_id).permission_map.copy()

    def group_set_permissions(self, *, group_id: EntityID, permissions: PermissionMap) -> None:
        """Overwrite all permissions for a group."""
        return self._get_group(group_id=group_id).set_permission_map(new_permission_map=permissions)

    def group_add_subject(self, group_id: EntityID, subject_id: EntityID) -> None:
        """Add a subject to a group."""
        group = self._get_group(group_id=group_id)
        subject = self._get_subject(subject_id=subject_id)

        group.subject_ids.add(subject_id)
        subject.group_ids.add(group_id)

    def group_rem_subject(self, group_id: EntityID, subject_id: EntityID) -> None:
        """Remove a subject from a group."""
        group = self._get_group(group_id=group_id)
        subject = self._get_subject(subject_id=subject_id)

        group.subject_ids.remove(subject_id)
        subject.group_ids.remove(group_id)

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

    @staticmethod
    def _serialize_data(*, non_serial_data: NonSerialData) -> str:
        return json.dumps(non_serial_data)

    @staticmethod
    def _deserialize_data(*, serial_data: str) -> NonSerialData:
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
        permission_map[permission] = set()

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
