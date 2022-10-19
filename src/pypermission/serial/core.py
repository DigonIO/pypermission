import json
from enum import Enum
from pathlib import Path
from typing import Any, Literal, TypedDict, cast

from pypermission.core import Authority as _Authority
from pypermission.core import (
    Permission,
    PermissionMap,
    PermissionNodeMap,
    PermissionNode,
    validate_payload_status,
)
from pypermission.error import (
    EntityIDCollisionError,
    GroupCycleError,
    PathError,
    UnknownSubjectIDError,
    PathError,
)

####################################################################################################
### Const
####################################################################################################

OutIDTypeDict = dict[str, Literal["str"] | Literal["int"]]
InIDTypeDict = dict[str, type[str | int]]


class GroupStore(TypedDict):
    member_subjects: list[str]
    member_groups: list[str]
    permission_nodes: list[str]


class SubjectStore(TypedDict):
    permission_nodes: list[str]


class DataStore(TypedDict):
    groups: dict[str, GroupStore]
    subjects: dict[str, SubjectStore]


####################################################################################################
### Permissionable entities
####################################################################################################


class PermissionableEntity:

    _id: str
    _permission_map: PermissionMap

    def __init__(self, *, id: str):
        self._id = id
        self._permission_map = {}

    @property
    def id(self) -> str:
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

    _gids: set[str]  # group IDs

    def __init__(self, *, id: str) -> None:
        super().__init__(id=id)
        self._gids = set()

    @property
    def gids(self) -> set[str]:
        return self._gids


class Group(PermissionableEntity):

    _sids: set[str]  # subject member IDs
    _parent_ids: set[str]  # parent group IDs
    _child_ids: set[str]  # child group IDs

    def __init__(self, *, id: str) -> None:
        super().__init__(id=id)
        self._sids = set()
        self._parent_ids = set()
        self._child_ids = set()

    @property
    def sids(self) -> set[str]:
        return self._sids

    @property
    def parent_ids(self) -> set[str]:
        return self._parent_ids

    @property
    def child_ids(self) -> set[str]:
        return self._child_ids


####################################################################################################
### Authority
####################################################################################################


class SerialAuthority(_Authority):

    _subjects: dict[str, Subject]
    _groups: dict[str, Group]
    _data_file: Path | str | None

    def __init__(
        self, *, nodes: type[PermissionNode] | None = None, data_file: Path | str | None = None
    ) -> None:
        super().__init__(nodes=nodes)

        self._subjects = {}
        self._groups = {}
        self._data_file = data_file

    ################################################################################################
    ### IO
    ################################################################################################

    def save_file(self, path: Path | str | None = None):
        """Save the current state to file formatted as JSON or YAML."""
        path = path or self._data_file
        if not path:
            raise PathError("No file path to save to has been specified!")

        path = Path(path)
        ftype = path.suffix[1:]

        if ftype == "json":
            serial_data = self.dump_JSON()
        elif ftype in ["yaml", "yml"]:
            serial_data = self.dump_YAML()
        else:
            raise PathError(
                f"Unknown file extension `{ftype}`! Possible extensions are: `json`, `yaml`"
            )

        with open(path, "w") as handle:
            handle.write(serial_data)

    def load_file(self, path: Path | str | None = None) -> None:
        """Load a previous state from a file formatted as JSON or YAML."""
        path = path or self._data_file
        if not path:
            raise PathError("No file path to load from has been specified!")

        path = Path(path)
        ftype = path.suffix[1:]

        if ftype == "json":
            with open(path, "r") as handle:
                serial_data = handle.read()
            self.load_JSON(serial_data=serial_data)
        elif ftype in ["yaml", "yml"]:
            with open(path, "r") as handle:
                serial_data = handle.read()
            self.load_YAML(serial_data=serial_data)
        else:
            raise PathError(
                f"Unknown file extension `{ftype}`! Possible extensions are: `json`, `yaml`"
            )

    def dump_JSON(self) -> str:
        return json.dumps(self._write_data_store())

    def dump_YAML(self) -> str:
        # TODO: try/except
        try:
            import yaml
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Dumping to YAML requires the installation of the optional dependency PyYAML."
                "To install PyYAML, use your preferred python package manager."
            )
        return yaml.safe_dump(self._write_data_store())

    def load_JSON(self, *, serial_data: str) -> None:
        data = json.loads(serial_data)
        self._load_data_store(data=data)

    def load_YAML(self, *, serial_data: str) -> None:
        # TODO: try/except
        try:
            import yaml
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Loading from YAML requires the installation of the optional dependency PyYAML."
                "To install PyYAML, use your preferred python package manager."
            )

        data = yaml.safe_load(serial_data)
        self._load_data_store(data=data)

    def _write_data_store(self) -> DataStore:
        """Save the current state to string formatted as JSON."""
        groups: dict[str, GroupStore] = {}

        for gid, group in self._groups.items():
            # TODO create a util function
            permission_nodes: list[str] = []
            for permission, payload_set in group.permission_map.items():
                if permission.has_payload:
                    for payload in payload_set:
                        permission_nodes.append(
                            self._serialize_permission_node(permission=permission, payload=payload)
                        )
                else:
                    permission_nodes.append(
                        self._serialize_permission_node(permission=permission, payload=None)
                    )

            groups[gid] = GroupStore(
                member_groups=list(group.child_ids),
                member_subjects=list(group.sids),
                permission_nodes=permission_nodes,
            )

        subjects: dict[str, SubjectStore] = {}

        for sid, subject in self._subjects.items():
            # TODO create a util function
            permission_nodes: list[str] = []
            for permission, payload_set in subject.permission_map.items():
                if permission.has_payload:
                    for payload in payload_set:
                        permission_nodes.append(
                            self._serialize_permission_node(permission=permission, payload=payload)
                        )
                else:
                    permission_nodes.append(
                        self._serialize_permission_node(permission=permission, payload=None)
                    )

            subjects[sid] = SubjectStore(
                permission_nodes=permission_nodes,
            )

        data = DataStore(
            groups=groups,
            subjects=subjects,
        )
        return data

    def _load_data_store(self, *, data: DataStore) -> None:
        """Load state from DataStore dictionary."""

        # populate subjects
        for sid, sdefs in data.get("subjects", {}).items():
            # TODO sid sanity check
            subject = Subject(id=sid)
            self._subjects[sid] = subject

            # add permissions to a subject
            for node_str in sdefs.get("permission_nodes", {}):
                # "chat.room.<Alice>" => payload = Alice

                permission, payload = self._deserialize_permission_node(node_str=node_str)
                # either permission leaf with or without payload
                # or permission parent without payload

                permission_map = subject.permission_map
                if payload:
                    payload_set = permission_map.get(permission, set())
                    if not payload_set:
                        permission_map[permission] = payload_set
                    payload_set.add(payload)
                else:
                    permission_map[permission] = None

        # populate groups
        for gid, gdefs in data.get("groups", {}).items():
            # TODO giud sanity check
            group = Group(id=gid)
            self._groups[gid] = group

            # add permissions to a group
            for node_str in gdefs.get("permission_nodes", []):
                permission, payload = self._deserialize_permission_node(node_str=node_str)
                permission_map = group.permission_map
                if payload:
                    payload_set = permission_map.get(permission, set())
                    if not payload_set:
                        permission_map[permission] = payload_set
                    payload_set.add(payload)
                else:
                    permission_map[permission] = None

            # add group ids to subjects of a group and vice versa
            for sid in gdefs.get("member_subjects", []):
                # TODO sanity checks
                group.sids.add(sid)
                self._subjects[sid].gids.add(gid)

        # sub group loop
        for gid, gdefs in data.get("groups", {}).items():
            group = self._groups[gid]
            for sub_gid in gdefs.get("member_groups", []):
                if sub_gid not in self._groups:
                    # TODO: more descriptive Error raising
                    raise ValueError  # TODO raise ParsingError?
                group.child_ids.add(sub_gid)
                child = self._groups[sub_gid]
                child.parent_ids.add(gid)

    ################################################################################################
    ### Add
    ################################################################################################

    def add_subject(self, sid: str) -> None:
        """Create a new subject for a given ID."""
        if sid in self._subjects:
            raise EntityIDCollisionError

        subject = Subject(id=sid)
        self._subjects[sid] = subject

    def add_group(self, gid: str) -> None:
        """Create a new group for a given ID."""
        if gid in self._subjects:
            raise EntityIDCollisionError

        group = Group(id=gid)
        self._groups[gid] = group

    def group_add_subject(self, *, gid: str, sid: str) -> None:
        """Add a subject to a group to inherit all its permissions."""
        group = self._get_group(gid=gid)
        subject = self._get_subject(sid=sid)

        group.sids.add(sid)
        subject.gids.add(gid)

    def group_add_child_group(self, *, gid: str, cid: str) -> None:
        """Add a group to a parent group to inherit all its permissions."""
        child = self._get_group(gid=cid)
        parent = self._get_group(gid=gid)

        self._detect_group_cycle(parent=parent, child_id=cid)

        parent.child_ids.add(cid)
        child.parent_ids.add(gid)

    def subject_add_permission(self, *, sid: str, node: PermissionNode, payload: str | None = None):
        """Add a permission to a subject."""
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(sid=sid).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_add_permission(self, *, gid: str, node: PermissionNode, payload: str | None = None):
        """Add a permission to a group."""
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(gid=gid).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    ################################################################################################
    ### Get
    ################################################################################################

    def get_subjects(self) -> set[str]:
        """Get the IDs for all known subjects."""
        return set(self._subjects.keys())

    def get_groups(self) -> set[str]:
        """Get the IDs for all known groups."""
        return set(self._groups.keys())

    def subject_get_groups(self, *, sid: str) -> set[str]:
        """Get a set of a group IDs of a groups a subject is member of."""
        subject = self._get_subject(sid=sid)
        return subject.gids.copy()

    def group_get_subjects(self, *, gid: str) -> set[str]:
        """Get a set of all subject IDs from a group."""
        group = self._get_group(gid=gid)
        return group.sids.copy()

    def group_get_child_groups(self, *, gid: str) -> set[str]:
        """Get a set of all child group IDs of a group."""
        group = self._get_group(gid=gid)
        return group.child_ids.copy()

    def group_get_parent_groups(self, *, gid: str) -> set[str]:
        """Get a set of all parent group IDs of a group."""
        group = self._get_group(gid=gid)
        return group.parent_ids.copy()

    def subject_has_permission(
        self, *, sid: str, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a subject has a wanted permission."""
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        subject = self._get_subject(sid=sid)

        if subject.has_permission(permission=permission, payload=payload):
            return True

        for gid in subject.gids:
            group = self._groups[gid]
            if self._recursive_group_has_permission(
                group=group, permission=permission, payload=payload
            ):
                return True

        return False

    def group_has_permission(
        self, *, gid: str, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a group has a wanted permission."""
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        group = self._get_group(gid=gid)

        return self._recursive_group_has_permission(
            group=group, permission=permission, payload=payload
        )

    def subject_get_permissions(self, *, sid: str) -> PermissionNodeMap:
        """Get a copy of all permissions from a subject."""
        perm_map = self._get_subject(sid=sid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    def group_get_permissions(self, *, gid: str) -> PermissionNodeMap:
        """Get a copy of all permissions from a group."""
        perm_map = self._get_group(gid=gid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    ################################################################################################
    ### Remove
    ################################################################################################

    def rem_subject(self, sid: str) -> None:
        """Remove a subject for a given ID."""
        subject = self._subjects.pop(sid, None)
        if subject is None:
            return
        for gid in subject.gids:
            self._groups[gid].sids.remove(sid)

    def rem_group(self, gid: str) -> None:
        """Remove a group for a given ID."""
        group = self._groups.pop(gid, None)
        if group is None:
            return
        for sid in group.sids:
            self._subjects[sid].gids.remove(gid)

    def subject_rem_permission(self, *, sid: str, node: PermissionNode, payload: str | None = None):
        """Remove a permission from a subject."""
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(sid=sid).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rem_permission(self, *, gid: str, node: PermissionNode, payload: str | None = None):
        """Remove a permission from a group."""
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(gid=gid).permission_map

        _rem_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rem_subject(self, *, gid: str, sid: str) -> None:
        """Remove a subject from a group."""
        group = self._get_group(gid=gid)
        subject = self._get_subject(sid=sid)

        group.sids.remove(sid)
        subject.gids.remove(gid)

    # TODO rename to group_rem_child_group
    def group_rem_group(self, *, pid: str, child_id: str) -> None:
        """Remove a group from a group."""
        parent = self._get_group(gid=pid)
        child = self._get_group(gid=child_id)

        parent.child_ids.remove(child_id)
        child.parent_ids.remove(pid)

    ################################################################################################
    ### Private
    ################################################################################################

    def _get_subject(self, *, sid: str) -> Subject:
        """Just a simple wrapper to avoid some boilerplate code while getting a subject."""
        try:
            return self._subjects[sid]
        except KeyError:
            raise UnknownSubjectIDError

    def _get_group(self, *, gid: str) -> Group:
        """Just a simple wrapper to avoid some boilerplate code while getting a group."""
        try:
            return self._groups[gid]
        except KeyError:
            raise UnknownSubjectIDError

    def _detect_group_cycle(self, parent: Group, child_id: str):
        """Detect a cycle in nested group tree."""
        if child_id in parent.parent_ids:
            raise GroupCycleError
        for parent_parent_id in parent.parent_ids:
            parent_parent = self._groups[parent_parent_id]
            self._detect_group_cycle(parent=parent_parent, child_id=child_id)

    def _recursive_group_has_permission(
        self, group: Group, permission: Permission, payload: str | None
    ) -> bool:
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


####################################################################################################
### Util
####################################################################################################


def _assertEntityIDType(eid: Any) -> None:
    if not isinstance(eid, str):
        raise ValueError  # TODO better Error


def _build_permission_node_map(*, perm_map: PermissionMap) -> PermissionNodeMap:
    node_map: PermissionNodeMap = {}
    for perm, payload in perm_map.items():
        if perm.node in node_map:
            payload_set = node_map[perm.node]
        else:
            payload_set = set()
        if perm.has_payload:
            payload_set.add(payload)
        node_map[perm.node] = payload_set
    return node_map


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
