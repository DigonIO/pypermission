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
    NodeMap,
    Permission,
    PermissionMap,
    PermissionNode,
    RoleDict,
    RoleInfo,
    RoleInfoDict,
    SubjectInfo,
    SubjectInfoDict,
    assertEntityIDType,
    build_entity_permission_nodes,
    entity_id_deserializer,
    entity_id_serializer,
    validate_payload_status,
)
from pypermission.error import EntityIDError, ParsingError, PathError, RoleCycleError

####################################################################################################
### Types
####################################################################################################


class SubjectStore(TypedDict, total=False):
    permission_nodes: list[str]


T = TypeVar("T")


class RoleStore(
    TypedDict,
    Generic[T],
    total=False,
):
    subjects: list[T]
    child_roles: list[T]
    permission_nodes: list[str]


RoleStoreYAML = RoleStore[EntityID]
RoleStoreJSON = RoleStore[str]


class DataStore(TypedDict, Generic[T], total=False):
    roles: dict[T, RoleStore[T]]
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

    _rids: set[EntityID]  # role IDs

    def __init__(self, *, id: EntityID) -> None:
        super().__init__(id=id)
        self._rids = set()

    @property
    def rids(self) -> set[EntityID]:
        return self._rids


class Role(PermissionableEntity):

    _sids: set[EntityID]  # subject member IDs
    _parent_ids: set[EntityID]  # parent role IDs
    _child_ids: set[EntityID]  # child role IDs

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
    _roles: dict[EntityID, Role]

    def __init__(self, *, nodes: type[PermissionNode] | None = None) -> None:
        super().__init__(nodes=nodes)

        self._subjects = {}
        self._roles = {}

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
        """Dumps the authorities current state to a JSON formatted string."""
        return json.dumps(self._dump_data_store_json())

    def dump_YAML(self) -> str:
        """Dumps the authorities current state to a YAML formatted string."""
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
        """Load a previous state from a JSON formatted string."""
        data = json.loads(serial_data)
        self._load_data_store_json(data=data)

    def load_YAML(self, *, serial_data: str) -> None:
        """Load a previous state from a YAML formatted string."""
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
        roles = {
            entity_id_serializer(rid): RoleStoreJSON(
                child_roles=[entity_id_serializer(eid) for eid in role.child_ids],
                subjects=[entity_id_serializer(eid) for eid in role.sids],
                permission_nodes=self._generate_permission_node_list(role),
            )
            for rid, role in self._roles.items()
        }

        subjects = {
            entity_id_serializer(sid): SubjectStore(
                permission_nodes=self._generate_permission_node_list(subject),
            )
            for sid, subject in self._subjects.items()
        }

        return DataStoreJSON(
            roles=roles,
            subjects=subjects,
        )

    def _dump_data_store_yaml(self) -> DataStoreYAML:
        """Save the current state to string formatted as YAML."""
        roles = {
            rid: RoleStoreYAML(
                child_roles=list(role.child_ids),
                subjects=list(role.sids),
                permission_nodes=self._generate_permission_node_list(role),
            )
            for rid, role in self._roles.items()
        }

        subjects = {
            sid: SubjectStore(
                permission_nodes=self._generate_permission_node_list(subject),
            )
            for sid, subject in self._subjects.items()
        }

        return DataStoreYAML(
            roles=roles,
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

        # populate roles
        for serial_rid, gdefs in (data.get("roles") or {}).items():
            rid = entity_id_deserializer(serial_rid)
            gdefs = {} if gdefs is None else gdefs
            # TODO giud sanity check
            role = Role(id=rid)
            self._roles[rid] = role

            # add permissions to a role
            for node_str in gdefs.get("permission_nodes") or []:
                permission, payload = self._deserialize_permission_node(node_str=node_str)
                permission_map = role.permission_map
                if payload:
                    payload_set = permission_map.get(permission, set())
                    if not payload_set:
                        permission_map[permission] = payload_set
                    payload_set.add(payload)
                else:
                    permission_map[permission] = set()

            # add role ids to subjects of a role and vice versa
            for serial_sid in gdefs.get("subjects") or []:
                # TODO sanity checks
                sid = entity_id_deserializer(serial_sid)
                role.sids.add(sid)
                self._subjects[sid].rids.add(rid)

        # sub role loop
        for serial_rid, gdefs in (data.get("roles") or {}).items():
            rid = entity_id_deserializer(serial_rid)
            gdefs = {} if gdefs is None else gdefs
            role = self._roles[rid]
            for serial_child_rid in gdefs.get("child_roles") or []:
                child_rid = entity_id_deserializer(serial_child_rid)
                if child_rid not in self._roles:
                    raise ParsingError(f"Child role `{child_rid}` was never defined!")
                self.role_add_inheritance(rid=rid, child_rid=child_rid)

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

        # populate roles
        for rid, gdefs in (data.get("roles") or {}).items():
            gdefs = {} if gdefs is None else gdefs
            # TODO giud sanity check
            role = Role(id=rid)
            self._roles[rid] = role

            # add permissions to a role
            for node_str in gdefs.get("permission_nodes") or []:
                permission, payload = self._deserialize_permission_node(node_str=node_str)
                permission_map = role.permission_map
                if payload:
                    payload_set = permission_map.get(permission, set())
                    if not payload_set:
                        permission_map[permission] = payload_set
                    payload_set.add(payload)
                else:
                    permission_map[permission] = set()

            # add role ids to subjects of a role and vice versa
            for sid in gdefs.get("subjects") or []:
                # TODO sanity checks
                role.sids.add(sid)
                self._subjects[sid].rids.add(rid)

        # sub role loop
        for rid, gdefs in (data.get("roles") or {}).items():
            gdefs = {} if gdefs is None else gdefs
            role = self._roles[rid]
            for child_rid in gdefs.get("child_roles") or []:
                if child_rid not in self._roles:
                    raise ParsingError(f"Child role `{child_rid}` was never defined!")
                self.role_add_inheritance(rid=rid, child_rid=child_rid)

    ################################################################################################
    ### Add
    ################################################################################################

    def add_subject(self, *, sid: EntityID) -> None:
        """Create a new subject for a given ID."""
        assertEntityIDType(eid=sid)

        if sid in self._subjects:
            raise EntityIDError(f"Subject ID `{sid}` is in use!")

        subject = Subject(id=sid)
        self._subjects[sid] = subject

    def add_role(self, *, rid: EntityID) -> None:
        """Create a new role for a given ID."""
        assertEntityIDType(eid=rid)

        if rid in self._subjects:
            raise EntityIDError(f"Role ID `{rid}` is in use!")

        role = Role(id=rid)
        self._roles[rid] = role

    def role_assign_subject(self, *, rid: EntityID, sid: EntityID) -> None:
        """Add a subject to a role to inherit all its permissions."""
        assertEntityIDType(eid=rid)
        assertEntityIDType(eid=sid)

        role = self._get_role(rid=rid)
        subject = self._get_subject(sid=sid)

        role.sids.add(sid)
        subject.rids.add(rid)

    def role_add_inheritance(self, *, rid: EntityID, child_rid: EntityID) -> None:
        """Add a role to a parent role to inherit all its permissions."""
        assertEntityIDType(eid=rid)
        assertEntityIDType(eid=child_rid)

        role = self._get_role(rid=rid)
        child = self._get_role(rid=child_rid)

        self._detect_role_cycle(role=role, child_rid=child_rid)

        role.child_ids.add(child_rid)
        child.parent_ids.add(rid)

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

    def role_grant_permission(
        self, *, rid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> None:
        """Add a permission to a role."""
        assertEntityIDType(eid=rid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_role(rid=rid).permission_map

        _add_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    ################################################################################################
    ### Get
    ################################################################################################

    def get_subjects(self) -> set[EntityID]:
        """Get the IDs for all known subjects."""
        return set(self._subjects.keys())

    def get_roles(self) -> set[EntityID]:
        """Get the IDs for all known roles."""
        return set(self._roles.keys())

    def subject_get_roles(self, *, sid: EntityID) -> set[EntityID]:
        """Get a set of a role IDs of a roles a subject is member of."""
        assertEntityIDType(eid=sid)

        subject = self._get_subject(sid=sid)
        return subject.rids.copy()

    def role_get_subjects(self, *, rid: EntityID) -> set[EntityID]:
        """Get a set of all subject IDs from a role."""
        assertEntityIDType(eid=rid)

        role = self._get_role(rid=rid)
        return role.sids.copy()

    def role_get_child_roles(self, *, rid: EntityID) -> set[EntityID]:
        """Get a set of all child role IDs of a role."""
        assertEntityIDType(eid=rid)

        role = self._get_role(rid=rid)
        return role.child_ids.copy()

    def role_get_parent_roles(self, *, rid: EntityID) -> set[EntityID]:
        """Get a set of all parent role IDs of a role."""
        assertEntityIDType(eid=rid)

        role = self._get_role(rid=rid)
        return role.parent_ids.copy()

    def subject_obtains_permission(
        self, *, sid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a subject has the wanted permission within the hierarchy."""
        assertEntityIDType(eid=sid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        subject = self._get_subject(sid=sid)

        if subject.has_permission(permission=permission, payload=payload):
            return True

        for rid in subject.rids:
            role = self._roles[rid]
            if self._recursive_role_obtains_permission(
                role=role, permission=permission, payload=payload
            ):
                return True

        return False

    def role_obtains_permission(
        self, *, rid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> bool:
        """Check if a role has the wanted permission within the hierarchy."""
        assertEntityIDType(eid=rid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        role = self._get_role(rid=rid)

        return self._recursive_role_obtains_permission(
            role=role, permission=permission, payload=payload
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

        parent_ids = subject.rids
        child_roles = [
            cast(EID, entity_id_serializer(grp_id) if entity_id_type is str else grp_id)
            for grp_id in parent_ids
        ]

        subject_entity_dict: EntityDict[PID, EID] = {
            "entity_id": entity_id,
            "permission_nodes": permission_nodes,
            "roles": child_roles,
        }

        parents: set[Role] = {self._roles[rid] for rid in parent_ids}
        ancestors: list[Role] = self._topo_sort_parents(parents)

        roles: dict[EID, RoleDict[PID, EID]] = {}
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

            role_dict: RoleDict[PID, EID] = {
                "permission_nodes": permission_nodes,
                "parents": grand_ancestors,
            }

            key = cast(
                EID, entity_id_serializer(ancestor.id) if entity_id_type is str else ancestor.id
            )
            roles[key] = role_dict

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
            roles=roles, subject=subject_entity_dict, permission_tree=permission_tree
        )

    @overload
    def role_get_info(
        self, *, rid: str, serialize: Literal[False]
    ) -> RoleInfoDict[PermissionNode, EntityID]:
        ...

    @overload
    def role_get_info(self, *, rid: str, serialize: Literal[True]) -> RoleInfoDict[str, str]:
        ...

    @overload
    def role_get_info(self, *, rid: str, serialize: bool) -> RoleInfo:
        ...

    def role_get_info(
        self,
        *,
        rid: EntityID,
        serialize: bool = False,
    ) -> RoleInfo:
        assertEntityIDType(eid=rid)
        role: Role = self._get_role(rid=rid)

        if serialize is True:
            return self._role_get_info(rid=rid, role=role, node_type=str, entity_id_type=str)
        else:  # serialize == False:
            return self._role_get_info(
                rid=rid,
                role=role,
                node_type=PermissionNode,
                entity_id_type=EntityID,  # type:ignore
            )

    def _role_get_info(
        self, *, rid: EntityID, role: Role, node_type: type[PID], entity_id_type: type[EID]
    ) -> RoleInfo:  # TODO generic typing

        permission_nodes = build_entity_permission_nodes(
            permission_map=role.permission_map, node_type=node_type
        )
        entity_id = cast(EID, entity_id_serializer(rid) if entity_id_type is str else rid)
        child_roles = [
            cast(EID, entity_id_serializer(grp_id) if entity_id_type is str else grp_id)
            for grp_id in role.parent_ids
        ]

        role_entity_dict: EntityDict[PID, EID] = {
            "entity_id": entity_id,
            "permission_nodes": permission_nodes,
            "roles": child_roles,
        }

        parents: set[Role] = {self._roles[rid] for rid in role.parent_ids}
        ancestors: list[Role] = self._topo_sort_parents(parents)

        roles = {}
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

            role_dict: RoleDict[PID, EID] = {
                "permission_nodes": permission_nodes,
                "parents": grand_ancestors,
            }

            key = cast(
                EID, entity_id_serializer(ancestor.id) if entity_id_type is str else ancestor.id
            )
            roles[key] = role_dict

        permission_tree: PERMISSION_TREE[PID] = {}

        self._populate_permission_tree(
            permission_tree=permission_tree,
            permission_map=role.permission_map,
            node_type=node_type,
        )

        for grp in ancestors:
            self._populate_permission_tree(
                permission_tree=permission_tree,
                permission_map=grp.permission_map,
                node_type=node_type,
            )

        return RoleInfoDict(roles=roles, role=role_entity_dict, permission_tree=permission_tree)

    def subject_get_permissions(self, *, sid: EntityID) -> NodeMap:
        """Get a copy of all permissions from a subject."""
        assertEntityIDType(eid=sid)

        perm_map = self._get_subject(sid=sid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    def role_get_permissions(self, *, rid: EntityID) -> NodeMap:
        """Get a copy of all permissions from a role."""
        assertEntityIDType(eid=rid)

        perm_map = self._get_role(rid=rid).permission_map
        return _build_permission_node_map(perm_map=perm_map)

    ################################################################################################
    ### Remove
    ################################################################################################

    def del_subject(self, sid: EntityID) -> None:
        """Remove a subject for a given ID."""
        assertEntityIDType(eid=sid)

        subject = self._subjects.pop(sid)
        if subject is None:
            raise EntityIDError(f"Can not remove non existing subject `{sid}`!")
        for rid in subject.rids:
            self._roles[rid].sids.remove(sid)

    def del_role(self, rid: EntityID) -> None:
        """Remove a role for a given ID."""
        assertEntityIDType(eid=rid)

        role = self._roles.pop(rid)
        if role is None:
            raise EntityIDError(f"Can not remove non existing role `{rid}`!")
        for sid in role.sids:
            self._subjects[sid].rids.remove(rid)
        for parent_id in role.parent_ids:
            self._roles[parent_id].child_ids.remove(rid)
        for child_id in role.child_ids:
            self._roles[child_id].parent_ids.remove(rid)

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

    def role_revoke_permission(
        self, *, rid: EntityID, node: PermissionNode, payload: str | None = None
    ) -> None:
        """Remove a permission from a role."""
        assertEntityIDType(eid=rid)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)
        permission_map = self._get_role(rid=rid).permission_map

        _rm_permission_map_entry(
            permission_map=permission_map, permission=permission, payload=payload
        )

    def role_deassign_subject(self, *, rid: EntityID, sid: EntityID) -> None:
        """Remove a subject from a role."""
        assertEntityIDType(eid=rid)
        assertEntityIDType(eid=sid)

        role = self._get_role(rid=rid)
        subject = self._get_subject(sid=sid)

        role.sids.remove(sid)
        subject.rids.remove(rid)

    def role_del_inheritance(self, *, rid: EntityID, child_rid: EntityID) -> None:
        """Remove a role from a role."""
        assertEntityIDType(eid=rid)
        assertEntityIDType(eid=child_rid)

        parent = self._get_role(rid=rid)
        child = self._get_role(rid=child_rid)

        parent.child_ids.remove(child_rid)
        child.parent_ids.remove(rid)

    ################################################################################################
    ### Private
    ################################################################################################

    def _get_subject(self, *, sid: EntityID) -> Subject:
        """Just a simple wrapper to avoid some boilerplate code while getting a subject."""
        try:
            return self._subjects[sid]
        except KeyError:
            raise EntityIDError(f"Can not find subject `{sid}`!")

    def _get_role(self, *, rid: EntityID) -> Role:
        """Just a simple wrapper to avoid some boilerplate code while getting a role."""
        try:
            return self._roles[rid]
        except KeyError:
            raise EntityIDError(f"Can not find role `{rid}`!")

    # TODO: build graph/subgraph ordering instead
    def _detect_role_cycle(self, role: Role, child_rid: EntityID) -> None:
        """Detect a cycle in nested role tree."""
        if child_rid in role.parent_ids:
            raise RoleCycleError(
                f"Cyclic dependencies detected between roles `{role.id}` and `{child_rid}`!"
            )
        for parent_parent_id in role.parent_ids:
            parent_parent = self._roles[parent_parent_id]
            self._detect_role_cycle(role=parent_parent, child_rid=child_rid)

    def _recursive_role_obtains_permission(
        self, role: Role, permission: Permission, payload: str | None
    ) -> bool:
        """Recursively check whether the role or one of its parents has the perm searched for."""
        if role.has_permission(permission=permission, payload=payload):
            return True

        for parent_id in role.parent_ids:
            parent = self._roles[parent_id]
            if self._recursive_role_obtains_permission(
                role=parent, permission=permission, payload=payload
            ):
                return True

        return False

    def _visit_role(self, role: Role, l: list[Role], perm: set[Role], temp: set[Role]) -> None:
        if role in perm:
            return
        if role in temp:
            raise RoleCycleError()  # TODO msg

        temp.add(role)

        for parent_id in role.parent_ids:
            parent = self._roles[parent_id]
            self._visit_role(role=parent, l=l, perm=perm, temp=temp)

        temp.remove(role)
        perm.add(role)
        l.append(role)

    # NOTE: not using for now, keep - might still be useful, e.g. to find cycles
    def _topo_sort_roles(self) -> list[Role]:
        l: list[Role] = []
        perm: set[Role] = set()
        temp: set[Role] = set()
        roles = set(self._roles.values())
        while unmarked := roles - perm:
            self._visit_role(role=unmarked.pop(), l=l, perm=perm, temp=temp)
        return l

    def _topo_sort_parents(self, parents: set[Role]) -> list[Role]:
        l: list[Role] = []
        perm: set[Role] = set()
        temp: set[Role] = set()
        while unmarked := parents - perm:
            self._visit_role(role=unmarked.pop(), l=l, perm=perm, temp=temp)
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
