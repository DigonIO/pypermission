import json
from pathlib import Path
from typing import Any, Literal, TypedDict, cast, TypeVar

from pypermission.core import Authority as _Authority
from pypermission.core import (
    Permission,
    PermissionMap,
    PermissionNodeMap,
    PermissionNode,
    validate_payload_status,
)
from pypermission.error import (
    EntityIDError,
    GroupCycleError,
    PathError,
    ParsingError,
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

    def __init__(self, *, nodes: type[PermissionNode] | None = None) -> None:
        super().__init__(nodes=nodes)

        self._subjects = {}
        self._groups = {}

    ################################################################################################
    ### IO
    ################################################################################################

    def save_file(self, *, path: Path | str):
        """Save the current state to file formatted as JSON or YAML."""
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

    def load_file(self, *, path: Path | str) -> None:
        """Load a previous state from a file formatted as JSON or YAML."""
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
        for sid, sdefs in _dict_get_or_default(data, "subjects", {}).items():
            sdefs = {} if sdefs is None else sdefs
            # TODO sid sanity check
            subject = Subject(id=sid)
            self._subjects[sid] = subject

            # add permissions to a subject
            for node_str in _dict_get_or_default(sdefs, "permission_nodes", {}):
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
                    permission_map[permission] = set()

        # populate groups
        for gid, gdefs in _dict_get_or_default(data, "groups", {}).items():
            gdefs = {} if gdefs is None else gdefs
            # TODO giud sanity check
            group = Group(id=gid)
            self._groups[gid] = group

            # add permissions to a group
            if gdefs is None:
                import pdb

                pdb.set_trace()

            for node_str in _dict_get_or_default(gdefs, "permission_nodes", []):
                permission, payload = self._deserialize_permission_node(node_str=node_str)
                permission_map = group.permission_map
                if payload:
                    payload_set = permission_map.get(permission, set())
                    if not payload_set:
                        permission_map[permission] = payload_set
                    payload_set.add(payload)
                else:
                    permission_map[permission] = set()

            # add group ids to subjects of a group and vice versa
            for sid in _dict_get_or_default(gdefs, "member_subjects", []):
                # TODO sanity checks
                group.sids.add(sid)
                self._subjects[sid].gids.add(gid)

        # sub group loop
        for gid, gdefs in _dict_get_or_default(data, "groups", {}).items():
            gdefs = {} if gdefs is None else gdefs
            group = self._groups[gid]
            for sub_gid in _dict_get_or_default(gdefs, "member_groups", []):
                if sub_gid not in self._groups:
                    raise ParsingError(f"Member group `{sub_gid}` was never defined!")
                group.child_ids.add(sub_gid)
                child = self._groups[sub_gid]
                child.parent_ids.add(gid)

    ################################################################################################
    ### Add
    ################################################################################################

    def add_subject(self, *, sid: str) -> None:
        """Create a new subject for a given ID."""
        _assertEntityIDType(eid=sid)

        if sid in self._subjects:
            raise EntityIDError(f"Subject ID `{sid}` is in use!")

        subject = Subject(id=sid)
        self._subjects[sid] = subject

    def add_group(self, *, gid: str) -> None:
        """Create a new group for a given ID."""
        _assertEntityIDType(eid=gid)

        if gid in self._subjects:
            raise EntityIDError(f"Group ID `{gid}` is in use!")

        group = Group(id=gid)
        self._groups[gid] = group

    def group_add_member_subject(self, *, gid: str, member_sid: str) -> None:
        """Add a subject to a group to inherit all its permissions."""
        _assertEntityIDType(eid=gid)
        _assertEntityIDType(eid=member_sid)

        group = self._get_group(gid=gid)
        subject = self._get_subject(sid=member_sid)

        group.sids.add(member_sid)
        subject.gids.add(gid)

    def group_add_member_group(self, *, gid: str, member_gid: str) -> None:
        """Add a group to a parent group to inherit all its permissions."""
        _assertEntityIDType(eid=gid)
        _assertEntityIDType(eid=member_gid)

        child = self._get_group(gid=member_gid)
        parent = self._get_group(gid=gid)

        self._detect_group_cycle(parent=parent, child_id=member_gid)

        parent.child_ids.add(member_gid)
        child.parent_ids.add(gid)

    def subject_add_permission(self, *, sid: str, node: PermissionNode, payload: str | None = None):
        """Add a permission to a subject."""
        _assertEntityIDType(eid=sid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(sid=sid).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_add_permission(self, *, gid: str, node: PermissionNode, payload: str | None = None):
        """Add a permission to a group."""
        _assertEntityIDType(eid=gid)
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
        _assertEntityIDType(eid=sid)

        subject = self._get_subject(sid=sid)
        return subject.gids.copy()

    def group_get_member_subjects(self, *, gid: str) -> set[str]:
        """Get a set of all subject IDs from a group."""
        _assertEntityIDType(eid=gid)

        group = self._get_group(gid=gid)
        return group.sids.copy()

    def group_get_member_groups(self, *, gid: str) -> set[str]:
        """Get a set of all child group IDs of a group."""
        _assertEntityIDType(eid=gid)

        group = self._get_group(gid=gid)
        return group.child_ids.copy()

    def group_get_parent_groups(self, *, gid: str) -> set[str]:
        """Get a set of all parent group IDs of a group."""
        _assertEntityIDType(eid=gid)

        group = self._get_group(gid=gid)
        return group.parent_ids.copy()

    def subject_has_permission(
        self, *, sid: str, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a subject has a wanted permission."""
        _assertEntityIDType(eid=sid)
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
        _assertEntityIDType(eid=gid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        group = self._get_group(gid=gid)

        return self._recursive_group_has_permission(
            group=group, permission=permission, payload=payload
        )

    def subject_get_permissions(self, *, sid: str) -> PermissionNodeMap:
        """Get a copy of all permissions from a subject."""
        _assertEntityIDType(eid=sid)

        perm_map = self._get_subject(sid=sid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    def group_get_permissions(self, *, gid: str) -> PermissionNodeMap:
        """Get a copy of all permissions from a group."""
        _assertEntityIDType(eid=gid)

        perm_map = self._get_group(gid=gid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    ################################################################################################
    ### Remove
    ################################################################################################

    def rm_subject(self, sid: str) -> None:
        """Remove a subject for a given ID."""
        _assertEntityIDType(eid=sid)

        subject = self._subjects.pop(sid)
        if subject is None:
            raise EntityIDError(f"Can not remove non existing subject `{sid}`!")
        for gid in subject.gids:
            self._groups[gid].sids.remove(sid)

    def rm_group(self, gid: str) -> None:
        """Remove a group for a given ID."""
        _assertEntityIDType(eid=gid)

        group = self._groups.pop(gid)
        if group is None:
            raise EntityIDError(f"Can not remove non existing group `{gid}`!")
        for sid in group.sids:
            self._subjects[sid].gids.remove(gid)
        for parent_id in group.parent_ids:
            self._groups[parent_id].child_ids.remove(gid)
        for child_id in group.child_ids:
            self._groups[child_id].parent_ids.remove(gid)

    def subject_rm_permission(self, *, sid: str, node: PermissionNode, payload: str | None = None):
        """Remove a permission from a subject."""
        _assertEntityIDType(eid=sid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(sid=sid).permission_map

        _rm_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rm_permission(self, *, gid: str, node: PermissionNode, payload: str | None = None):
        """Remove a permission from a group."""
        _assertEntityIDType(eid=gid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(gid=gid).permission_map

        _rm_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rm_member_subject(self, *, gid: str, member_sid: str) -> None:
        """Remove a subject from a group."""
        _assertEntityIDType(eid=gid)
        _assertEntityIDType(eid=member_sid)

        group = self._get_group(gid=gid)
        subject = self._get_subject(sid=member_sid)

        group.sids.remove(member_sid)
        subject.gids.remove(gid),

    def group_rm_member_group(self, *, gid: str, member_gid: str) -> None:
        """Remove a group from a group."""
        _assertEntityIDType(eid=gid)
        _assertEntityIDType(eid=member_gid)

        parent = self._get_group(gid=gid)
        child = self._get_group(gid=member_gid)

        parent.child_ids.remove(member_gid)
        child.parent_ids.remove(gid)

    ################################################################################################
    ### Private
    ################################################################################################

    def _get_subject(self, *, sid: str) -> Subject:
        """Just a simple wrapper to avoid some boilerplate code while getting a subject."""
        try:
            return self._subjects[sid]
        except KeyError:
            raise EntityIDError(f"Can not find subject `{sid}`!")

    def _get_group(self, *, gid: str) -> Group:
        """Just a simple wrapper to avoid some boilerplate code while getting a group."""
        try:
            return self._groups[gid]
        except KeyError:
            raise EntityIDError(f"Can not find group `{gid}`!")

    def _detect_group_cycle(self, parent: Group, child_id: str):
        """Detect a cycle in nested group tree."""
        if child_id in parent.parent_ids:
            raise GroupCycleError(
                f"Cyclic dependencies detected between groups `{parent.id}` and `{child_id}`!"
            )
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

T = TypeVar("T")


def _dict_get_or_default(d: dict[str, T], key: str, default: T) -> T:
    # if value for key is falsy, returns default as well
    return d.get(key, default) or default


def _assertEntityIDType(eid: str) -> None:
    if not isinstance(eid, str):
        raise EntityIDError(
            f"Subject and group IDs have to be of type string! Got type `{type(eid)}` for `{eid}`."
        )


def _build_permission_node_map(*, perm_map: PermissionMap) -> PermissionNodeMap:
    node_map: PermissionNodeMap = {}
    for perm, payload_set in perm_map.items():
        node_map[perm.node] = payload_set.copy()
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


def _rm_permission_map_entry(
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
