from typing import Literal, Sequence, cast, overload

try:
    from sqlalchemy.engine.base import Engine
    from sqlalchemy.orm import Session
    from sqlalchemy.orm.session import sessionmaker
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "The SQLAlchemyAuthority requires the installation of the optional dependency sqlalchemy."
        "To install sqlalchemy, use your preferred python package manager."
    )

from pypermission.core import (
    EID,
    PERMISSION_TREE,
    PID,
    Authority,
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
    build_entity_permission_nodes,
)
from pypermission.core import entity_id_deserializer as _entity_id_deserializer
from pypermission.core import entity_id_serializer as _entity_id_serializer
from pypermission.core import validate_payload_status
from pypermission.error import RoleCycleError
from pypermission.sqlalchemy.models import (
    ENTITY_ID_MAX_LENGHT,
    SERIAL_ENTITY_ID_LENGHT,
    DeclarativeMeta,
    PermissionableEntityMixin,
    PermissionPayloadMixin,
    RoleEntry,
    RolePermissionEntry,
    SubjectEntry,
)
from pypermission.sqlalchemy.service import (
    create_membership,
    create_parent_child_relationship,
    create_role,
    create_role_permission,
    create_subject,
    create_subject_permission,
    delete_membership,
    delete_parent_child_relationship,
    delete_role,
    delete_role_permission,
    delete_subject,
    delete_subject_permission,
    read_role,
    read_subject,
    serialize_payload,
)


class SQLAlchemyAuthority(Authority):
    def __init__(self, *, nodes: type[PermissionNode] | None = None, engine: Engine) -> None:
        super().__init__(nodes=nodes)

        self._session_maker = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
        )

        DeclarativeMeta.metadata.create_all(bind=engine)

    ################################################################################################
    ### Add
    ################################################################################################

    def add_subject(self, sid: EntityID, session: Session | None = None) -> None:
        """Create a new subject for a given ID."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        create_subject(serial_sid=serial_sid, db=db)

        _close_db_session(db, session)

    def add_role(self, rid: EntityID, session: Session | None = None) -> None:
        """Create a new role for a given ID."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)

        create_role(serial_rid=serial_rid, db=db)

        _close_db_session(db, session)

    def role_assign_subject(
        self, *, rid: EntityID, sid: EntityID, session: Session | None = None
    ) -> None:
        """Add a subject to a role to inherit all its permissions."""
        serial_rid = entity_id_serializer(rid)
        serial_member_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        create_membership(serial_sid=serial_member_sid, serial_rid=serial_rid, db=db)

        _close_db_session(db, session)

    def role_add_child_role(
        self, *, rid: EntityID, child_rid: EntityID, session: Session | None = None
    ) -> None:
        """Add a role to a parent role to inherit all its permissions."""
        serial_rid = entity_id_serializer(rid)
        serial_child_rid = entity_id_serializer(child_rid)
        db = self._setup_db_session(session)

        create_parent_child_relationship(serial_pid=serial_rid, serial_cid=serial_child_rid, db=db)

        _close_db_session(db, session)

    def subject_add_node(
        self,
        *,
        sid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> None:
        """Add a permission to a subject."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        create_subject_permission(
            serial_sid=serial_sid, permission=permission, payload=payload, db=db
        )

        _close_db_session(db, session)

    def role_grant_permission(
        self,
        *,
        rid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> None:
        """Add a permission to a role."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        create_role_permission(serial_rid=serial_rid, permission=permission, payload=payload, db=db)

        _close_db_session(db, session)

    ################################################################################################
    ### Get
    ################################################################################################

    def get_subjects(self, session: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known subjects."""
        db = self._setup_db_session(session)

        subject_entries: list[PermissionableEntityMixin] = db.query(SubjectEntry).all()

        result = set(
            entity_id_deserializer(entry.serial_eid)
            for entry in subject_entries
            if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def get_roles(self, session: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known roles."""
        db = self._setup_db_session(session)

        role_entries: list[PermissionableEntityMixin] = db.query(RoleEntry).all()
        result = set(
            entity_id_deserializer(entry.serial_eid) for entry in role_entries if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def subject_get_roles(self, sid: EntityID, session: Session | None = None) -> set[EntityID]:
        """Get a set of a role IDs of a roles a subject is member of."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        subject_entry = read_subject(serial_sid=serial_sid, db=db)
        result = set(
            entity_id_deserializer(entry.serial_eid)
            for entry in subject_entry.role_entries
            if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def role_get_subjects(self, rid: EntityID, session: Session | None = None) -> set[EntityID]:
        """Get a set of all subject IDs from a role."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)

        role_entry = read_role(serial_rid=serial_rid, db=db)
        result = set(
            entity_id_deserializer(entry.serial_eid)
            for entry in role_entry.subject_entries
            if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def role_get_child_roles(
        self, *, rid: EntityID, session: Session | None = None
    ) -> set[EntityID]:
        """Get a set of all child role IDs of a role."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)

        role_entry = read_role(serial_rid=serial_rid, db=db)
        child_entries = role_entry.child_entries
        result = set(
            entity_id_deserializer(entry.serial_eid) for entry in child_entries if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def role_get_parent_roles(
        self, *, rid: EntityID, session: Session | None = None
    ) -> set[EntityID]:
        """Get a set of all parent role IDs of a role."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)

        role_entry = read_role(serial_rid=serial_rid, db=db)
        parent_entries = role_entry.parent_entries
        result = set(
            entity_id_deserializer(entry.serial_eid) for entry in parent_entries if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def subject_has_permission(
        self,
        *,
        sid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> bool:
        """Check if a subject has a wanted permission."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        subject_entry = read_subject(serial_sid=serial_sid, db=db)

        perm_entries = subject_entry.permission_entries
        if _has_permission(perm_entries=perm_entries, permission=permission, payload=payload):
            _close_db_session(db, session)
            return True

        role_entries = subject_entry.role_entries
        for entry in role_entries:
            if _recursive_role_has_permission(
                role_entry=entry, permission=permission, payload=payload
            ):
                _close_db_session(db, session)
                return True

        _close_db_session(db, session)
        return False

    def role_has_permission(
        self,
        *,
        rid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> bool:
        """Check if a role has a wanted permission."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        role_entry = read_role(serial_rid=serial_rid, db=db)

        result = _recursive_role_has_permission(
            role_entry=role_entry, permission=permission, payload=payload
        )

        _close_db_session(db, session)
        return result

    # https://mypy.readthedocs.io/en/stable/literal_types.html
    @overload
    def subject_get_info(
        self,
        *,
        sid: EntityID,
        serialize: Literal[False],
        session: Session | None,
    ) -> SubjectInfoDict[PermissionNode, EntityID]:
        ...

    @overload
    def subject_get_info(
        self,
        *,
        sid: EntityID,
        serialize: Literal[True],
        session: Session | None,
    ) -> SubjectInfoDict[str, str]:
        ...

    @overload
    def subject_get_info(
        self,
        *,
        sid: EntityID,
        serialize: bool,
        session: Session | None,
    ) -> SubjectInfo:
        ...

    def subject_get_info(
        self,
        *,
        sid: EntityID,
        serialize: bool = False,
        session: Session | None = None,
    ) -> SubjectInfo:
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        if serialize is True:
            result = self._subject_get_info(
                sid=sid,
                serial_sid=serial_sid,
                node_type=str,
                entity_id_type=str,
                db=db,
            )
        else:  # serialize == False:
            result = self._subject_get_info(
                sid=sid,
                serial_sid=serial_sid,
                node_type=PermissionNode,
                entity_id_type=EntityID,  # type:ignore
                db=db,
            )
        _close_db_session(db, session)
        return result

    def _subject_get_info(
        self,
        *,
        sid: EntityID,
        serial_sid: str,
        node_type: type[PID],
        entity_id_type: type[EID],
        db: Session,
    ) -> SubjectInfo:  # TODO generic typing

        subject_entry = read_subject(serial_sid=serial_sid, db=db)

        entity_id = cast(EID, serial_sid if entity_id_type is str else sid)

        permission_map = self._build_permission_map(perm_entries=subject_entry.permission_entries)
        permission_nodes = build_entity_permission_nodes(
            permission_map=permission_map, node_type=node_type
        )

        parents_entries = subject_entry.role_entries
        child_roles = [
            cast(
                EID,
                entry.serial_eid
                if entity_id_type is str
                else entity_id_deserializer(entry.serial_eid),
            )
            for entry in parents_entries
        ]

        subject_entity_dict: EntityDict[PID, EID] = {
            "entity_id": entity_id,
            "permission_nodes": permission_nodes,
            "roles": child_roles,
        }

        parents: set[RoleEntry] = set(subject_entry.role_entries)
        ancestors: list[RoleEntry] = _topo_sort_parents(parents)

        roles: dict[EID, RoleDict[PID, EID]] = {}
        ancestor_permission_maps: dict[RoleEntry, PermissionMap] = {}
        for ancestor in ancestors:
            ancestor_permission_map = self._build_permission_map(
                perm_entries=ancestor.permission_entries
            )

            # NOTE: Stored for later usage
            ancestor_permission_maps[ancestor] = ancestor_permission_map

            permission_nodes = build_entity_permission_nodes(
                permission_map=ancestor_permission_map, node_type=node_type
            )
            grand_ancestors = [
                cast(
                    EID,
                    grand_ancestor.serial_eid
                    if entity_id_type is str
                    else entity_id_deserializer(grand_ancestor.serial_eid),
                )
                for grand_ancestor in ancestor.parent_entries
            ]

            role_dict: RoleDict[PID, EID] = {
                "permission_nodes": permission_nodes,
                "parents": grand_ancestors,
            }

            key = cast(
                EID,
                ancestor.serial_eid
                if entity_id_type is str
                else entity_id_deserializer(ancestor.serial_eid),
            )
            roles[key] = role_dict

        permission_tree: PERMISSION_TREE[PID] = {}

        self._populate_permission_tree(
            permission_tree=permission_tree,
            permission_map=permission_map,
            node_type=node_type,
        )

        for grp in ancestors:
            self._populate_permission_tree(
                permission_tree=permission_tree,
                permission_map=ancestor_permission_maps[grp],
                node_type=node_type,
            )

        return SubjectInfoDict[PID, EID](
            roles=roles, subject=subject_entity_dict, permission_tree=permission_tree
        )

    @overload
    def role_get_info(
        self,
        *,
        rid: EntityID,
        serialize: Literal[False],
        session: Session | None,
    ) -> RoleInfoDict[PermissionNode, EntityID]:
        ...

    @overload
    def role_get_info(
        self,
        *,
        rid: EntityID,
        serialize: Literal[True],
        session: Session | None,
    ) -> RoleInfoDict[str, str]:
        ...

    @overload
    def role_get_info(
        self,
        *,
        rid: EntityID,
        serialize: bool,
        session: Session | None,
    ) -> RoleInfo:
        ...

    def role_get_info(
        self,
        *,
        rid: EntityID,
        serialize: bool = False,
        session: Session | None = None,
    ) -> RoleInfo:
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)

        if serialize is True:
            result = self._role_get_info(
                rid=rid,
                serial_rid=serial_rid,
                node_type=str,
                entity_id_type=str,
                db=db,
            )
        else:  # serialize == False:
            result = self._role_get_info(
                rid=rid,
                serial_rid=serial_rid,
                node_type=PermissionNode,
                entity_id_type=EntityID,  # type:ignore
                db=db,
            )
        _close_db_session(db, session)
        return result

    def _role_get_info(
        self,
        *,
        rid: EntityID,
        serial_rid: str,
        node_type: type[PID],
        entity_id_type: type[EID],
        db: Session,
    ) -> RoleInfo:  # TODO generic typing

        role_entry: RoleEntry = read_role(serial_rid=serial_rid, db=db)

        entity_id = cast(EID, serial_rid if entity_id_type is str else rid)

        permission_map = self._build_permission_map(perm_entries=role_entry.permission_entries)
        permission_nodes = build_entity_permission_nodes(
            permission_map=permission_map, node_type=node_type
        )

        parents_entries = role_entry.parent_entries
        child_roles = [
            cast(
                EID,
                entry.serial_eid
                if entity_id_type is str
                else entity_id_deserializer(entry.serial_eid),
            )
            for entry in parents_entries
        ]

        role_entity_dict: EntityDict[PID, EID] = {
            "entity_id": entity_id,
            "permission_nodes": permission_nodes,
            "roles": child_roles,
        }

        parents: set[RoleEntry] = set(role_entry.parent_entries)
        ancestors: list[RoleEntry] = _topo_sort_parents(parents)

        roles: dict[EID, RoleDict[PID, EID]] = {}
        ancestor_permission_maps: dict[RoleEntry, PermissionMap] = {}
        for ancestor in ancestors:
            ancestor_permission_map = self._build_permission_map(
                perm_entries=ancestor.permission_entries
            )

            # NOTE: Stored for later usage
            ancestor_permission_maps[ancestor] = ancestor_permission_map

            permission_nodes = build_entity_permission_nodes(
                permission_map=ancestor_permission_map, node_type=node_type
            )
            grand_ancestors = [
                cast(
                    EID,
                    grand_ancestor.serial_eid
                    if entity_id_type is str
                    else entity_id_deserializer(grand_ancestor.serial_eid),
                )
                for grand_ancestor in ancestor.parent_entries
            ]

            role_dict: RoleDict[PID, EID] = {
                "permission_nodes": permission_nodes,
                "parents": grand_ancestors,
            }

            key = cast(
                EID,
                ancestor.serial_eid
                if entity_id_type is str
                else entity_id_deserializer(ancestor.serial_eid),
            )
            roles[key] = role_dict

        permission_tree: PERMISSION_TREE[PID] = {}

        self._populate_permission_tree(
            permission_tree=permission_tree,
            permission_map=permission_map,
            node_type=node_type,
        )

        for grp in ancestors:
            self._populate_permission_tree(
                permission_tree=permission_tree,
                permission_map=ancestor_permission_maps[grp],
                node_type=node_type,
            )

        return RoleInfoDict[PID, EID](
            roles=roles, role=role_entity_dict, permission_tree=permission_tree
        )

    def subject_get_nodes(
        self,
        *,
        sid: EntityID,
        session: Session | None = None,
    ) -> NodeMap:
        """Get a copy of all permissions from a subject."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        subject_entry = read_subject(serial_sid=serial_sid, db=db)
        perm_entries = subject_entry.permission_entries

        result = self._build_node_map(perm_entries=perm_entries)

        _close_db_session(db, session)
        return result

    def role_get_nodes(
        self,
        *,
        rid: EntityID,
        session: Session | None = None,
    ) -> NodeMap:
        """Get a copy of all permissions from a role."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)

        role_entry = read_role(serial_rid=serial_rid, db=db)
        perm_entries = role_entry.permission_entries

        result = self._build_node_map(perm_entries=perm_entries)

        _close_db_session(db, session)
        return result

    ################################################################################################
    ### Remove
    ################################################################################################

    def del_subject(self, sid: EntityID, session: Session | None = None) -> None:
        """Remove a subject for a given ID."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        delete_subject(serial_sid=serial_sid, db=db)

        _close_db_session(db, session)

    def del_role(self, rid: EntityID, session: Session | None = None) -> None:
        """Remove a role for a given ID."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)

        delete_role(serial_rid=serial_rid, db=db)

        _close_db_session(db, session)

    def subject_rm_node(
        self,
        *,
        sid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> None:
        """Remove a permission to a subject."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        delete_subject_permission(
            serial_sid=serial_sid, permission=permission, payload=payload, db=db
        )

        _close_db_session(db, session)

    def role_revoke_permission(
        self,
        *,
        rid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> None:
        """Remove a permission to a role."""
        serial_rid = entity_id_serializer(rid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        delete_role_permission(serial_rid=serial_rid, permission=permission, payload=payload, db=db)

        _close_db_session(db, session)

    def role_deassign_subject(
        self,
        *,
        rid: EntityID,
        sid: EntityID,
        session: Session | None = None,
    ) -> None:
        """Remove a subject from a role."""
        serial_rid = entity_id_serializer(rid)
        serial_member_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        delete_membership(serial_sid=serial_member_sid, serial_rid=serial_rid, db=db)

        _close_db_session(db, session)

    def role_rm_child_role(
        self, *, rid: EntityID, child_rid: EntityID, session: Session | None = None
    ) -> None:
        """Remove a role from a role."""
        serial_rid = entity_id_serializer(rid)
        serial_child_rid = entity_id_serializer(child_rid)
        db = self._setup_db_session(session)

        delete_parent_child_relationship(serial_pid=serial_rid, serial_cid=serial_child_rid, db=db)

        _close_db_session(db, session)

    ################################################################################################
    ### Private
    ################################################################################################

    def _setup_db_session(self, session: Session | None) -> Session:
        if session is None:
            return self._session_maker()
        if isinstance(session, Session):
            return session
        raise AttributeError("Attribute 'db' must be of type 'sqlalchemy.orm.Session'!")

    def _build_node_map(self, *, perm_entries: list[PermissionPayloadMixin]) -> NodeMap:
        node_map: NodeMap = {}
        for entry in perm_entries:
            permission = self._get_permission(node=entry.node)  # TODO handle unknown permissions
            if permission.node in node_map:
                payload_set = node_map[permission.node]
            else:
                payload_set = set()
            if permission.has_payload:
                payload_set.add(entry.payload)
            node_map[permission.node] = payload_set
        return node_map

    def _build_permission_map(self, *, perm_entries: list[PermissionPayloadMixin]) -> PermissionMap:
        perm_map: PermissionMap = {}
        for entry in perm_entries:
            permission = self._get_permission(node=entry.node)  # TODO handle unknown permissions
            if permission in perm_map:
                payload_set = perm_map[permission]
            else:
                payload_set = set()
            if permission.has_payload:
                payload_set.add(entry.payload)
            perm_map[permission] = payload_set
        return perm_map


####################################################################################################
### Util
####################################################################################################


def entity_id_serializer(
    eid: EntityID,
) -> str:
    return _entity_id_serializer(eid=eid, max_lenght=ENTITY_ID_MAX_LENGHT)


def entity_id_deserializer(
    serial_eid: str,
) -> EntityID:
    return _entity_id_deserializer(serial_eid=serial_eid, max_lenght=SERIAL_ENTITY_ID_LENGHT)


def _close_db_session(db: Session, session: Session | None) -> None:
    if session is None:
        db.close()


def _has_permission(
    perm_entries: Sequence[PermissionPayloadMixin],
    permission: Permission,
    payload: str | None,
) -> bool:
    for entry in perm_entries:
        if (entry.node == permission.node.value) and (entry.payload == serialize_payload(payload)):
            return True
    for ancestor in permission.ancestors:
        for entry in perm_entries:
            if entry.node == ancestor.node.value:  # ancestors carry no payload
                return True
    return False


def _recursive_role_has_permission(
    role_entry: RoleEntry, permission: Permission, payload: str | None
) -> bool:
    """Recursively check whether the role or one of its parents has the perm searched for."""
    perm_entries: list[RolePermissionEntry] = role_entry.permission_entries
    if _has_permission(perm_entries=perm_entries, permission=permission, payload=payload):
        return True

    parent_entries: Sequence[RoleEntry] = role_entry.parent_entries
    for entry in parent_entries:
        if _recursive_role_has_permission(role_entry=entry, permission=permission, payload=payload):
            return True

    return False


def _visit_role(
    role_entry: RoleEntry, l: list[RoleEntry], perm: set[RoleEntry], temp: set[RoleEntry]
) -> None:
    if role_entry in perm:
        return
    if role_entry in temp:
        raise RoleCycleError()  # TODO msg

    temp.add(role_entry)

    for parent_entry in role_entry.parent_entries:
        _visit_role(role_entry=parent_entry, l=l, perm=perm, temp=temp)

    temp.remove(role_entry)
    perm.add(role_entry)
    l.append(role_entry)


def _topo_sort_parents(parents: set[RoleEntry]) -> list[RoleEntry]:
    l: list[RoleEntry] = []
    perm: set[RoleEntry] = set()
    temp: set[RoleEntry] = set()
    while unmarked := parents - perm:
        _visit_role(role_entry=unmarked.pop(), l=l, perm=perm, temp=temp)
    return l
