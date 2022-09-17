from typing import Hashable

from pypermission.core import Authority as _Authority
from pypermission.core import Permission, PermissionMap
from pypermission.error import UnknownSubjectIDError, UnusedPayloadError, MissingPayloadError


class PermissionableEntity:

    _id: Hashable
    _permission_map: PermissionMap

    def __init__(self, *, id: Hashable):
        self._id = id
        self._permission_map = {}

    @property
    def id(self) -> Hashable:
        return self._id

    @property
    def permission_map(self) -> PermissionMap:
        return self._permission_map


class Subject(PermissionableEntity):

    _group_ids: set[Hashable]

    def __init__(self, *, id: Hashable):
        super().__init__(self, id=id)
        self._group_ids = set()

    @property
    def group_ids(self) -> set[Hashable]:
        return self._group_ids


class Group(PermissionableEntity):

    _name: str
    _subject_ids: set[Hashable]

    def __init__(self, *, id: Hashable, name: str):
        super().__init__(self, id=id)
        self._name
        self._subject_ids = set()

    @property
    def name(self) -> str:
        return self._name

    @property
    def subject_ids(self) -> set[Hashable]:
        return self._subject_ids


def has_permissions(
    *, entity: PermissionableEntity, permission: Permission, payload: str | None = None
) -> bool:

    permission_map = entity.permission_map
    for ancestor in permission.ancestors:
        if ancestor in permission_map:
            return True

    try:
        payload_set = entity.permission_map[permission]
    except KeyError:
        return False

    if payload:
        return payload in payload_set

    return True


def validate_payload_status(*, permission: Permission, payload: str | None):
    if permission.has_payload and payload is None:
        raise MissingPayloadError

    if not permission.has_payload and payload is not None:
        raise UnusedPayloadError


class Authority(_Authority):

    _subjects: dict[Hashable, Subject]
    _groups: dict[Hashable, Group]

    def __init__(self):
        super().__init__(self)

        self._subjects = {}

    def subject_has_permission(
        self, *, subject_id: Hashable, permission: Permission, payload: str | None = None
    ) -> bool:

        validate_payload_status(permission=permission, payload=payload)

        try:
            subject = self._subjects[subject_id]
        except KeyError:
            raise UnknownSubjectIDError

        return has_permissions(entity=subject, permission=permission, payload=payload)

    def subject_get_permissions(self, *, subject_id: Hashable) -> PermissionMap:
        try:
            return self._subjects[subject_id].permission_map
        except KeyError:
            raise UnknownSubjectIDError

    def subject_add_permission(
        self, *, subject_id: Hashable, permission: Permission, payload: str | None = None
    ):
        validate_payload_status(permission=permission, payload=payload)

        try:
            subject = self._subjects[subject_id]
        except KeyError:
            raise UnknownSubjectIDError

        permission_map = subject.permission_map

        try:
            payload_set = permission_map[permission]
        except KeyError:
            payload_set = set()
            permission_map[permission] = payload_set

        if payload:
            payload_set.add(payload)

    def subject_del_permission():
        ...
