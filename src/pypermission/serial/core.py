import json
from pathlib import Path
from typing import Generic, Literal, TypeVar, Union, cast, overload

# typing_extensions for generic TypedDict support:
from typing_extensions import NotRequired, TypedDict

from pypermission.core import EID, PERMISSION_TREE, PID
from pypermission.core import Authority as _Authority
from pypermission.core import (
    EntityDict,
    EntityID,
    GroupDict,
    GroupInfo,
    GroupInfoDict,
    NodeMap,
    Permission,
    PermissionMap,
    PermissionNode,
    SubjectInfo,
    SubjectInfoDict,
    assertEntityIDType,
    build_entity_permission_nodes,
    entity_id_deserializer,
    entity_id_serializer,
    validate_payload_status,
)
from pypermission.error import EntityIDError, GroupCycleError, ParsingError, PathError

####################################################################################################
### Types
####################################################################################################


class SubjectStore(TypedDict, total=False):
    permission_nodes: list[str]


T = TypeVar("T")


class GroupStore(
    TypedDict,
    Generic[T],
    total=False,
):
    member_subjects: list[T]
    member_groups: list[T]
    permission_nodes: list[str]


GroupStoreYAML = GroupStore[EntityID]
GroupStoreJSON = GroupStore[str]


class DataStore(TypedDict, Generic[T], total=False):
    groups: dict[T, GroupStore[T]]
    subjects: dict[T, SubjectStore]


DataStoreYAML = DataStore[EntityID]
DataStoreJSON = DataStore[str]

####################################################################################################
### Permissionable entities
####################################################################################################


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

    _gids: set[EntityID]  # group IDs

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(id=id)
        self._gids = set()

    @property
    def gids(self) -> set[EntityID]:
        return self._gids


class Group(PermissionableEntity):

    _sids: set[EntityID]  # subject member IDs
    _parent_ids: set[EntityID]  # parent group IDs
    _child_ids: set[EntityID]  # child group IDs

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(id=id)
        self._sids = set()
        self._parent_ids = set()
        self._child_ids = set()

    @property
    def sids(self) -> set[EntityID]:
        return self._sids

    @property
    def parent_ids(self) -> set[EntityID]:
        return self._parent_ids

    @property
    def child_ids(self) -> set[EntityID]:
        return self._child_ids


####################################################################################################
### Authority
####################################################################################################


class SerialAuthority(_Authority):

    _subjects: dict[EntityID, Subject]
    _groups: dict[EntityID, Group]

    def __init__(self, *, nodes: type[PermissionNode] | None = None) -> None:
        super().__init__(nodes=nodes)

        self._subjects = {}
        self._groups = {}

    ################################################################################################
    ### IO
    ################################################################################################

    def save_file(self, *, path: Path | str) -> None:
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
        return json.dumps(self._dump_data_store_json())

    def dump_YAML(self) -> str:
        # TODO: try/except
        try:
            import yaml
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Dumping to YAML requires the installation of the optional dependency PyYAML."
                "To install PyYAML, use your preferred python package manager."
            )
        yaml_content = yaml.safe_dump(self._dump_data_store_yaml(), encoding=None)
        if isinstance(yaml_content, str):
            return yaml_content
        else:
            raise TypeError("This should never happen, please report!")

    def load_JSON(self, *, serial_data: str) -> None:
        data = json.loads(serial_data)
        self._load_data_store_json(data=data)

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
        self._load_data_store_yaml(data=data)

    def _dump_data_store_json(self) -> DataStoreJSON:
        """Save the current state to string formatted as YAML."""
        groups = {
            entity_id_serializer(gid): GroupStoreJSON(
                member_groups=[entity_id_serializer(eid) for eid in group.child_ids],
                member_subjects=[entity_id_serializer(eid) for eid in group.sids],
                permission_nodes=self._generate_permission_node_list(group),
            )
            for gid, group in self._groups.items()
        }

        subjects = {
            entity_id_serializer(sid): SubjectStore(
                permission_nodes=self._generate_permission_node_list(subject),
            )
            for sid, subject in self._subjects.items()
        }

        return DataStoreJSON(
            groups=groups,
            subjects=subjects,
        )

    def _dump_data_store_yaml(self) -> DataStoreYAML:
        """Save the current state to string formatted as YAML."""
        groups = {
            gid: GroupStoreYAML(
                member_groups=list(group.child_ids),
                member_subjects=list(group.sids),
                permission_nodes=self._generate_permission_node_list(group),
            )
            for gid, group in self._groups.items()
        }

        subjects = {
            sid: SubjectStore(
                permission_nodes=self._generate_permission_node_list(subject),
            )
            for sid, subject in self._subjects.items()
        }

        return DataStoreYAML(
            groups=groups,
            subjects=subjects,
        )

    def _load_data_store_json(self, *, data: DataStoreJSON) -> None:
        """Load state from DataStore dictionary."""

        # populate subjects
        for serial_sid, sdefs in (data.get("subjects") or {}).items():
            sid = entity_id_deserializer(serial_sid)
            sdefs = SubjectStore() if sdefs is None else sdefs
            # TODO sid sanity check
            subject = Subject(id=sid)
            self._subjects[sid] = subject

            # add permissions to a subject
            for node_str in sdefs.get("permission_nodes") or {}:
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
        for serial_gid, gdefs in (data.get("groups") or {}).items():
            gid = entity_id_deserializer(serial_gid)
            gdefs = {} if gdefs is None else gdefs
            # TODO giud sanity check
            group = Group(id=gid)
            self._groups[gid] = group

            # add permissions to a group
            for node_str in gdefs.get("permission_nodes") or []:
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
            for serial_sid in gdefs.get("member_subjects") or []:
                # TODO sanity checks
                sid = entity_id_deserializer(serial_sid)
                group.sids.add(sid)
                self._subjects[sid].gids.add(gid)

        # sub group loop
        for serial_gid, gdefs in (data.get("groups") or {}).items():
            gid = entity_id_deserializer(serial_gid)
            gdefs = {} if gdefs is None else gdefs
            group = self._groups[gid]
            for serial_member_gid in gdefs.get("member_groups") or []:
                member_gid = entity_id_deserializer(serial_member_gid)
                if member_gid not in self._groups:
                    raise ParsingError(f"Member group `{member_gid}` was never defined!")
                self.group_add_member_group(gid=gid, member_gid=member_gid)

    def _load_data_store_yaml(self, *, data: DataStoreYAML) -> None:
        """Load state from DataStoreYAML dictionary."""

        # populate subjects
        for sid, sdefs in (data.get("subjects") or {}).items():
            sdefs = {} if sdefs is None else sdefs
            # TODO sid sanity check
            subject = Subject(id=sid)
            self._subjects[sid] = subject

            # add permissions to a subject
            for node_str in sdefs.get("permission_nodes") or {}:
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
        for gid, gdefs in (data.get("groups") or {}).items():
            gdefs = {} if gdefs is None else gdefs
            # TODO giud sanity check
            group = Group(id=gid)
            self._groups[gid] = group

            # add permissions to a group
            for node_str in gdefs.get("permission_nodes") or []:
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
            for sid in gdefs.get("member_subjects") or []:
                # TODO sanity checks
                group.sids.add(sid)
                self._subjects[sid].gids.add(gid)

        # sub group loop
        for gid, gdefs in (data.get("groups") or {}).items():
            gdefs = {} if gdefs is None else gdefs
            group = self._groups[gid]
            for member_gid in gdefs.get("member_groups") or []:
                if member_gid not in self._groups:
                    raise ParsingError(f"Member group `{member_gid}` was never defined!")
                self.group_add_member_group(gid=gid, member_gid=member_gid)

    ################################################################################################
    ### Add
    ################################################################################################

    def new_subject(self, *, sid: EntityID) -> None:
        """Create a new subject for a given ID."""
        assertEntityIDType(eid=sid)

        if sid in self._subjects:
            raise EntityIDError(f"Subject ID `{sid}` is in use!")

        subject = Subject(id=sid)
        self._subjects[sid] = subject

    def new_group(self, *, gid: EntityID) -> None:
        """Create a new group for a given ID."""
        assertEntityIDType(eid=gid)

        if gid in self._subjects:
            raise EntityIDError(f"Group ID `{gid}` is in use!")

        group = Group(id=gid)
        self._groups[gid] = group

    def group_add_member_subject(self, *, gid: EntityID, member_sid: EntityID) -> None:
        """Add a subject to a group to inherit all its permissions."""
        assertEntityIDType(eid=gid)
        assertEntityIDType(eid=member_sid)

        group = self._get_group(gid=gid)
        subject = self._get_subject(sid=member_sid)

        group.sids.add(member_sid)
        subject.gids.add(gid)

    def group_add_member_group(self, *, gid: EntityID, member_gid: EntityID) -> None:
        """Add a group to a parent group to inherit all its permissions."""
        assertEntityIDType(eid=gid)
        assertEntityIDType(eid=member_gid)

        group = self._get_group(gid=gid)
        member = self._get_group(gid=member_gid)

        self._detect_group_cycle(group=group, member_gid=member_gid)

        group.child_ids.add(member_gid)
        member.parent_ids.add(gid)

    def subject_add_node(
        self, *, sid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> None:
        """Add a permission to a subject."""
        assertEntityIDType(eid=sid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(sid=sid).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_add_node(
        self, *, gid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> None:
        """Add a permission to a group."""
        assertEntityIDType(eid=gid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(gid=gid).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    ################################################################################################
    ### Get
    ################################################################################################

    def get_subjects(self) -> set[EntityID]:
        """Get the IDs for all known subjects."""
        return set(self._subjects.keys())

    def get_groups(self) -> set[EntityID]:
        """Get the IDs for all known groups."""
        return set(self._groups.keys())

    def subject_get_groups(self, *, sid: EntityID) -> set[EntityID]:
        """Get a set of a group IDs of a groups a subject is member of."""
        assertEntityIDType(eid=sid)

        subject = self._get_subject(sid=sid)
        return subject.gids.copy()

    def group_get_member_subjects(self, *, gid: EntityID) -> set[EntityID]:
        """Get a set of all subject IDs from a group."""
        assertEntityIDType(eid=gid)

        group = self._get_group(gid=gid)
        return group.sids.copy()

    def group_get_member_groups(self, *, gid: EntityID) -> set[EntityID]:
        """Get a set of all child group IDs of a group."""
        assertEntityIDType(eid=gid)

        group = self._get_group(gid=gid)
        return group.child_ids.copy()

    def group_get_parent_groups(self, *, gid: EntityID) -> set[EntityID]:
        """Get a set of all parent group IDs of a group."""
        assertEntityIDType(eid=gid)

        group = self._get_group(gid=gid)
        return group.parent_ids.copy()

    def subject_has_permission(
        self, *, sid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a subject has a wanted permission."""
        assertEntityIDType(eid=sid)
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
        self, *, gid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a group has a wanted permission."""
        assertEntityIDType(eid=gid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        group = self._get_group(gid=gid)

        return self._recursive_group_has_permission(
            group=group, permission=permission, payload=payload
        )

    # https://mypy.readthedocs.io/en/stable/literal_types.html

    @overload
    def subject_get_info(
        self, *, sid: str, serialize: Literal[False]
    ) -> SubjectInfoDict[PermissionNode, EntityID]:
        ...

    @overload
    def subject_get_info(self, *, sid: str, serialize: Literal[True]) -> SubjectInfoDict[str, str]:
        ...

    @overload
    def subject_get_info(self, *, sid: str, serialize: bool) -> SubjectInfo:
        ...

    def subject_get_info(
        self,
        *,
        sid: EntityID,
        serialize: bool = False,
    ) -> SubjectInfo:
        assertEntityIDType(eid=sid)
        subject: Subject = self._get_subject(sid=sid)

        if serialize is True:
            return self._subject_get_info(
                sid=sid, subject=subject, node_type=str, entity_id_type=str
            )
        else:  # serialize == False:
            return self._subject_get_info(
                sid=sid,
                subject=subject,
                node_type=PermissionNode,
                entity_id_type=EntityID,  # type:ignore
            )

    def _subject_get_info(
        self, *, sid: EntityID, subject: Subject, node_type: type[PID], entity_id_type: type[EID]
    ) -> SubjectInfo:  # TODO generic typing

        entity_id = cast(EID, entity_id_serializer(sid) if entity_id_type is str else sid)
        permission_nodes = build_entity_permission_nodes(
            permission_map=subject.permission_map, node_type=node_type
        )

        parent_ids = subject.gids
        member_groups = [
            cast(EID, entity_id_serializer(grp_id) if entity_id_type is str else grp_id)
            for grp_id in parent_ids
        ]

        subject_entity_dict: EntityDict[PID, EID] = {
            "entity_id": entity_id,
            "permission_nodes": permission_nodes,
            "groups": member_groups,
        }

        parents: set[Group] = {self._groups[gid] for gid in parent_ids}
        ancestors: list[Group] = self._topo_sort_parents(parents)

        groups: dict[EID, GroupDict[PID, EID]] = {}
        for ancestor in ancestors:
            permission_nodes = build_entity_permission_nodes(
                permission_map=ancestor.permission_map, node_type=node_type
            )
            grand_ancestors = [
                cast(
                    EID,
                    entity_id_serializer(grand_ancestor_id)
                    if entity_id_type is str
                    else grand_ancestor_id,
                )
                for grand_ancestor_id in ancestor.parent_ids
            ]

            group_dict: GroupDict[PID, EID] = {
                "permission_nodes": permission_nodes,
                "parents": grand_ancestors,
            }

            key = cast(
                EID, entity_id_serializer(ancestor.id) if entity_id_type is str else ancestor.id
            )
            groups[key] = group_dict

        permission_tree: PERMISSION_TREE[PID] = {}

        self._populate_permission_tree(
            permission_tree=permission_tree,
            permission_map=subject.permission_map,
            node_type=node_type,
        )

        for grp in ancestors:
            self._populate_permission_tree(
                permission_tree=permission_tree,
                permission_map=grp.permission_map,
                node_type=node_type,
            )

        return SubjectInfoDict[PID, EID](
            groups=groups, subject=subject_entity_dict, permission_tree=permission_tree
        )

    @overload
    def group_get_info(
        self, *, gid: str, serialize: Literal[False]
    ) -> GroupInfoDict[PermissionNode, EntityID]:
        ...

    @overload
    def group_get_info(self, *, gid: str, serialize: Literal[True]) -> GroupInfoDict[str, str]:
        ...

    @overload
    def group_get_info(self, *, gid: str, serialize: bool) -> GroupInfo:
        ...

    def group_get_info(
        self,
        *,
        gid: EntityID,
        serialize: bool = False,
    ) -> GroupInfo:
        assertEntityIDType(eid=gid)
        group: Group = self._get_group(gid=gid)

        if serialize is True:
            return self._group_get_info(gid=gid, group=group, node_type=str, entity_id_type=str)
        else:  # serialize == False:
            return self._group_get_info(
                gid=gid,
                group=group,
                node_type=PermissionNode,
                entity_id_type=EntityID,  # type:ignore
            )

    def _group_get_info(
        self, *, gid: EntityID, group: Group, node_type: type[PID], entity_id_type: type[EID]
    ) -> GroupInfo:  # TODO generic typing

        permission_nodes = build_entity_permission_nodes(
            permission_map=group.permission_map, node_type=node_type
        )
        entity_id = cast(EID, entity_id_serializer(gid) if entity_id_type is str else gid)
        member_groups = [
            cast(EID, entity_id_serializer(grp_id) if entity_id_type is str else grp_id)
            for grp_id in group.parent_ids
        ]

        group_entity_dict: EntityDict[PID, EID] = {
            "entity_id": entity_id,
            "permission_nodes": permission_nodes,
            "groups": member_groups,
        }

        parents: set[Group] = {self._groups[gid] for gid in group.parent_ids}
        ancestors: list[Group] = self._topo_sort_parents(parents)

        groups = {}
        for ancestor in ancestors:
            permission_nodes = build_entity_permission_nodes(
                permission_map=ancestor.permission_map, node_type=node_type
            )
            grand_ancestors = [
                cast(
                    EID,
                    entity_id_serializer(grand_ancestor_id)
                    if entity_id_type is str
                    else grand_ancestor_id,
                )
                for grand_ancestor_id in ancestor.parent_ids
            ]

            group_dict: GroupDict[PID, EID] = {
                "permission_nodes": permission_nodes,
                "parents": grand_ancestors,
            }

            key = cast(
                EID, entity_id_serializer(ancestor.id) if entity_id_type is str else ancestor.id
            )
            groups[key] = group_dict

        permission_tree: PERMISSION_TREE[PID] = {}

        self._populate_permission_tree(
            permission_tree=permission_tree,
            permission_map=group.permission_map,
            node_type=node_type,
        )

        for grp in ancestors:
            self._populate_permission_tree(
                permission_tree=permission_tree,
                permission_map=grp.permission_map,
                node_type=node_type,
            )

        return GroupInfoDict(
            groups=groups, group=group_entity_dict, permission_tree=permission_tree
        )

    def subject_get_nodes(self, *, sid: EntityID) -> NodeMap:
        """Get a copy of all permissions from a subject."""
        assertEntityIDType(eid=sid)

        perm_map = self._get_subject(sid=sid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    def group_get_nodes(self, *, gid: EntityID) -> NodeMap:
        """Get a copy of all permissions from a group."""
        assertEntityIDType(eid=gid)

        perm_map = self._get_group(gid=gid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    ################################################################################################
    ### Remove
    ################################################################################################

    def rm_subject(self, sid: EntityID) -> None:
        """Remove a subject for a given ID."""
        assertEntityIDType(eid=sid)

        subject = self._subjects.pop(sid)
        if subject is None:
            raise EntityIDError(f"Can not remove non existing subject `{sid}`!")
        for gid in subject.gids:
            self._groups[gid].sids.remove(sid)

    def rm_group(self, gid: EntityID) -> None:
        """Remove a group for a given ID."""
        assertEntityIDType(eid=gid)

        group = self._groups.pop(gid)
        if group is None:
            raise EntityIDError(f"Can not remove non existing group `{gid}`!")
        for sid in group.sids:
            self._subjects[sid].gids.remove(gid)
        for parent_id in group.parent_ids:
            self._groups[parent_id].child_ids.remove(gid)
        for child_id in group.child_ids:
            self._groups[child_id].parent_ids.remove(gid)

    def subject_rm_node(
        self, *, sid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> None:
        """Remove a permission from a subject."""
        assertEntityIDType(eid=sid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_subject(sid=sid).permission_map

        _rm_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rm_node(
        self, *, gid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> None:
        """Remove a permission from a group."""
        assertEntityIDType(eid=gid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_group(gid=gid).permission_map

        _rm_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def group_rm_member_subject(self, *, gid: EntityID, member_sid: EntityID) -> None:
        """Remove a subject from a group."""
        assertEntityIDType(eid=gid)
        assertEntityIDType(eid=member_sid)

        group = self._get_group(gid=gid)
        subject = self._get_subject(sid=member_sid)

        group.sids.remove(member_sid)
        subject.gids.remove(gid)

    def group_rm_member_group(self, *, gid: EntityID, member_gid: EntityID) -> None:
        """Remove a group from a group."""
        assertEntityIDType(eid=gid)
        assertEntityIDType(eid=member_gid)

        parent = self._get_group(gid=gid)
        child = self._get_group(gid=member_gid)

        parent.child_ids.remove(member_gid)
        child.parent_ids.remove(gid)

    ################################################################################################
    ### Private
    ################################################################################################

    def _get_subject(self, *, sid: EntityID) -> Subject:
        """Just a simple wrapper to avoid some boilerplate code while getting a subject."""
        try:
            return self._subjects[sid]
        except KeyError:
            raise EntityIDError(f"Can not find subject `{sid}`!")

    def _get_group(self, *, gid: EntityID) -> Group:
        """Just a simple wrapper to avoid some boilerplate code while getting a group."""
        try:
            return self._groups[gid]
        except KeyError:
            raise EntityIDError(f"Can not find group `{gid}`!")

    # TODO: build graph/subgraph ordering instead
    def _detect_group_cycle(self, group: Group, member_gid: EntityID) -> None:
        """Detect a cycle in nested group tree."""
        if member_gid in group.parent_ids:
            raise GroupCycleError(
                f"Cyclic dependencies detected between groups `{group.id}` and `{member_gid}`!"
            )
        for parent_parent_id in group.parent_ids:
            parent_parent = self._groups[parent_parent_id]
            self._detect_group_cycle(group=parent_parent, member_gid=member_gid)

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

    def _visit_group(
        self, group: Group, l: list[Group], perm: set[Group], temp: set[Group]
    ) -> None:
        if group in perm:
            return
        if group in temp:
            raise GroupCycleError()  # TODO msg

        temp.add(group)

        for parent_id in group.parent_ids:
            parent = self._groups[parent_id]
            self._visit_group(group=parent, l=l, perm=perm, temp=temp)

        temp.remove(group)
        perm.add(group)
        l.append(group)

    # NOTE: not using for now, keep - might still be useful, e.g. to find cycles
    def _topo_sort_groups(self) -> list[Group]:
        l: list[Group] = []
        perm: set[Group] = set()
        temp: set[Group] = set()
        groups = set(self._groups.values())
        while unmarked := groups - perm:
            self._visit_group(group=unmarked.pop(), l=l, perm=perm, temp=temp)
        return l

    def _topo_sort_parents(self, parents: set[Group]) -> list[Group]:
        l: list[Group] = []
        perm: set[Group] = set()
        temp: set[Group] = set()
        while unmarked := parents - perm:
            self._visit_group(group=unmarked.pop(), l=l, perm=perm, temp=temp)
        return l

    def _generate_permission_node_list(self, entity: PermissionableEntity) -> list[str]:
        permission_nodes: list[str] = []
        for permission, payload_set in entity.permission_map.items():
            if permission.has_payload:
                for payload in payload_set:
                    permission_nodes.append(
                        self._serialize_permission_node(permission=permission, payload=payload)
                    )
            else:
                permission_nodes.append(
                    self._serialize_permission_node(permission=permission, payload=None)
                )
        return permission_nodes


####################################################################################################
### Util
####################################################################################################


def _build_permission_node_map(*, perm_map: PermissionMap) -> NodeMap:
    node_map: NodeMap = {}
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
