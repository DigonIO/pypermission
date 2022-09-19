from typing import Hashable

from pypermission.core import Authority as _Authority
from pypermission.core import Permission, PermissionMap, EntityID
from pypermission.error import (
    UnknownSubjectIDError,
    UnusedPayloadError,
    MissingPayloadError,
    EntityIDCollisionError,
)


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

    @property
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

    def __init__(self, *, id: EntityID):
        super().__init__(self, id=id)
        self._group_ids = set()

    @property
    def group_ids(self) -> set[EntityID]:
        return self._group_ids


class Group(PermissionableEntity):

    _subject_ids: set[EntityID]

    def __init__(self, *, id: EntityID):
        super().__init__(self, id=id)
        self._subject_ids = set()

    @property
    def subject_ids(self) -> set[EntityID]:
        return self._subject_ids


def validate_payload_status(*, permission: Permission, payload: str | None):
    if permission.has_payload and payload is None:
        raise MissingPayloadError

    if not permission.has_payload and payload is not None:
        raise UnusedPayloadError


class Authority(_Authority):

    _subjects: dict[EntityID, Subject]
    _groups: dict[EntityID, Group]

    def __init__(self):
        super().__init__(self)

        self._subjects = {}

    def subject_add(self, new_subject_id: EntityID) -> None:
        """Create a new subject for a given ID."""
        if new_subject_id in self._subjects:
            raise EntityIDCollisionError

        subject = Subject(id=new_subject_id)
        self._subjects[new_subject_id] = subject

    def subject_del(self, subject_id: EntityID) -> None:
        """Delete a new subject for a given ID."""

    def subject_has_permission(
        self, *, subject_id: EntityID, permission: Permission, payload: str | None = None
    ) -> bool:
        """Check if a subject has a wanted permission."""
        validate_payload_status(permission=permission, payload=payload)
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
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(subject_id=subject_id).permission_map

        try:
            payload_set = permission_map[permission]
        except KeyError:
            payload_set = set()
            permission_map[permission] = payload_set

        if payload:
            payload_set.add(payload)

    def subject_del_permission(
        self, *, subject_id: EntityID, permission: Permission, payload: str | None = None
    ):
        """Delete a permission from a subject."""
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(subject_id=subject_id).permission_map

        try:
            payload_set = permission_map[permission]
        except KeyError:
            return None
        if payload in payload_set:
            payload_set.remove(payload)
        if not payload:
            permission_map.pop(permission)

    def subject_get_permissions(self, *, subject_id: EntityID) -> PermissionMap:
        """Get a copy of all permissions from a subject."""
        return self._get_subject(subject_id=subject_id).permission_map.copy()

    def subject_set_permissions(self, *, subject_id: EntityID, permissions: PermissionMap) -> None:
        """Overwrite all permissions for a subject."""
        return self._get_subject(subject_id=subject_id).set_permission_map(
            new_permission_map=permissions
        )

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
