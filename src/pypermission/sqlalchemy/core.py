from typing import Sequence, overload, Literal
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker

from pypermission.core import Authority
from pypermission.core import (
    Permission,
    NodeMap,
    PermissionNode,
    validate_payload_status,
    EntityID,
    EntityDict,
    SubjectInfoDict,
    SubjectInfo,
    build_entity_permission_nodes,
    PermissionMap,
)
from pypermission.core import entity_id_serializer as _entity_id_serializer
from pypermission.core import entity_id_deserializer as _entity_id_deserializer
from pypermission.sqlalchemy.models import (
    ENTITY_ID_MAX_LENGHT,
    SERIAL_ENTITY_ID_LENGHT,
    DeclarativeMeta,
    GroupEntry,
    SubjectEntry,
    GroupPermissionEntry,
    PermissionableEntityMixin,
    PermissionPayloadMixin,
)
from pypermission.sqlalchemy.service import (
    create_group,
    create_group_permission,
    create_membership,
    create_parent_child_relationship,
    create_subject,
    create_subject_permission,
    delete_group,
    delete_group_permission,
    delete_membership,
    delete_parent_child_relationship,
    delete_subject,
    delete_subject_permission,
    read_group,
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

    def new_subject(self, sid: EntityID, session: Session | None = None) -> None:
        """Create a new subject for a given ID."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        create_subject(serial_sid=serial_sid, db=db)

        _close_db_session(db, session)

    def new_group(self, gid: EntityID, session: Session | None = None) -> None:
        """Create a new group for a given ID."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)

        create_group(serial_gid=serial_gid, db=db)

        _close_db_session(db, session)

    def group_add_member_subject(
        self, *, gid: EntityID, member_sid: EntityID, session: Session | None = None
    ) -> None:
        """Add a subject to a group to inherit all its permissions."""
        serial_gid = entity_id_serializer(gid)
        serial_member_sid = entity_id_serializer(member_sid)
        db = self._setup_db_session(session)

        create_membership(serial_sid=serial_member_sid, serial_gid=serial_gid, db=db)

        _close_db_session(db, session)

    def group_add_member_group(
        self, *, gid: EntityID, member_gid: EntityID, session: Session | None = None
    ) -> None:
        """Add a group to a parent group to inherit all its permissions."""
        serial_gid = entity_id_serializer(gid)
        serial_member_gid = entity_id_serializer(member_gid)
        db = self._setup_db_session(session)

        create_parent_child_relationship(serial_pid=serial_gid, serial_cid=serial_member_gid, db=db)

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

    def group_add_node(
        self,
        *,
        gid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> None:
        """Add a permission to a group."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        create_group_permission(
            serial_gid=serial_gid, permission=permission, payload=payload, db=db
        )

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

    def get_groups(self, session: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known groups."""
        db = self._setup_db_session(session)

        group_entries: list[PermissionableEntityMixin] = db.query(GroupEntry).all()
        result = set(
            entity_id_deserializer(entry.serial_eid) for entry in group_entries if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def subject_get_groups(self, sid: EntityID, session: Session | None = None) -> set[EntityID]:
        """Get a set of a group IDs of a groups a subject is member of."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        subject_entry = read_subject(serial_sid=serial_sid, db=db)
        result = set(
            entity_id_deserializer(entry.serial_eid)
            for entry in subject_entry.group_entries
            if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def group_get_member_subjects(
        self, gid: EntityID, session: Session | None = None
    ) -> set[EntityID]:
        """Get a set of all subject IDs from a group."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)

        group_entry = read_group(serial_gid=serial_gid, db=db)
        result = set(
            entity_id_deserializer(entry.serial_eid)
            for entry in group_entry.subject_entries
            if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def group_get_member_groups(
        self, *, gid: EntityID, session: Session | None = None
    ) -> set[EntityID]:
        """Get a set of all child group IDs of a group."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)

        group_entry = read_group(serial_gid=serial_gid, db=db)
        child_entries = group_entry.child_entries
        result = set(
            entity_id_deserializer(entry.serial_eid) for entry in child_entries if entry.serial_eid
        )

        _close_db_session(db, session)
        return result

    def group_get_parent_groups(
        self, *, gid: EntityID, session: Session | None = None
    ) -> set[EntityID]:
        """Get a set of all parent group IDs of a group."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)

        group_entry = read_group(serial_gid=serial_gid, db=db)
        parent_entries = group_entry.parent_entries
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

        group_entries = subject_entry.group_entries
        for entry in group_entries:
            if _recursive_group_has_permission(
                group_entry=entry, permission=permission, payload=payload
            ):
                _close_db_session(db, session)
                return True

        _close_db_session(db, session)
        return False

    def group_has_permission(
        self,
        *,
        gid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> bool:
        """Check if a group has a wanted permission."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        group_entry = read_group(serial_gid=serial_gid, db=db)

        result = _recursive_group_has_permission(
            group_entry=group_entry, permission=permission, payload=payload
        )

        _close_db_session(db, session)
        return result

    # https://mypy.readthedocs.io/en/stable/literal_types.html
    @overload
    def subject_get_info(
        self,
        *,
        sid: str,
        serialize: Literal[False],
        session: Session | None,
    ) -> SubjectInfoDict[PermissionNode, EntityID]:
        ...

    @overload
    def subject_get_info(
        self,
        *,
        sid: str,
        serialize: Literal[True],
        session: Session | None,
    ) -> SubjectInfoDict[str, str]:
        ...

    @overload
    def subject_get_info(
        self,
        *,
        sid: str,
        serialize: bool,
        session: Session | None,
    ) -> SubjectInfo:
        ...

    def subject_get_info(
        self,
        *,
        sid: str,
        serialize: bool = False,
        session: Session | None = None,
    ) -> SubjectInfo:
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        subject_entry = read_subject(serial_sid=serial_sid, db=db)

        parents_entries = subject_entry.group_entries

        subject_entity_dict = EntityDict(
            permission_nodes=build_entity_permission_nodes(
                permission_map=self._build_permission_map(
                    perm_entries=subject_entry.permission_entries
                ),
                serialize_nodes=serialize_nodes,
            ),
            entity_id=entity_id_serializer(sid) if serialize_eid else sid,
            groups=[
                entry.serial_eid if serialize_eid else entity_id_deserializer(entry.serial_eid)
                for entry in parents_entries
            ],
        )

        if not subject_entity_dict["groups"]:  # NOTE ugly but working solution, rm empty objects
            subject_entity_dict.pop("groups")
        if not subject_entity_dict["permission_nodes"]:
            subject_entity_dict.pop("permission_nodes")

        # ancestors: list[Group] = self._topo_sort_parents(parents) # TODO WIP

        raise NotImplementedError

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

    def group_get_nodes(
        self,
        *,
        gid: EntityID,
        session: Session | None = None,
    ) -> NodeMap:
        """Get a copy of all permissions from a group."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)

        group_entry = read_group(serial_gid=serial_gid, db=db)
        perm_entries = group_entry.permission_entries

        result = self._build_node_map(perm_entries=perm_entries)

        _close_db_session(db, session)
        return result

    ################################################################################################
    ### Remove
    ################################################################################################

    def rm_subject(self, sid: EntityID, session: Session | None = None) -> None:
        """Remove a subject for a given ID."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(session)

        delete_subject(serial_sid=serial_sid, db=db)

        _close_db_session(db, session)

    def rm_group(self, gid: EntityID, session: Session | None = None) -> None:
        """Remove a group for a given ID."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)

        delete_group(serial_gid=serial_gid, db=db)

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

    def group_rm_node(
        self,
        *,
        gid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        session: Session | None = None,
    ) -> None:
        """Remove a permission to a group."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(session)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        delete_group_permission(
            serial_gid=serial_gid, permission=permission, payload=payload, db=db
        )

        _close_db_session(db, session)

    def group_rm_member_subject(
        self,
        *,
        gid: EntityID,
        member_sid: EntityID,
        session: Session | None = None,
    ) -> None:
        """Remove a subject from a group."""
        serial_gid = entity_id_serializer(gid)
        serial_member_sid = entity_id_serializer(member_sid)
        db = self._setup_db_session(session)

        delete_membership(serial_sid=serial_member_sid, serial_gid=serial_gid, db=db)

        _close_db_session(db, session)

    def group_rm_member_group(
        self, *, gid: EntityID, member_gid: EntityID, session: Session | None = None
    ) -> None:
        """Remove a group from a group."""
        serial_gid = entity_id_serializer(gid)
        serial_member_gid = entity_id_serializer(member_gid)
        db = self._setup_db_session(session)

        delete_parent_child_relationship(serial_pid=serial_gid, serial_cid=serial_member_gid, db=db)

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
            perm_map[permission.node] = payload_set


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


def _recursive_group_has_permission(
    group_entry: GroupEntry, permission: Permission, payload: str | None
) -> bool:
    """Recursively check whether the group or one of its parents has the perm searched for."""
    perm_entries: list[GroupPermissionEntry] = group_entry.permission_entries
    if _has_permission(perm_entries=perm_entries, permission=permission, payload=payload):
        return True

    parent_entries: Sequence[GroupEntry] = group_entry.parent_entries
    for entry in parent_entries:
        if _recursive_group_has_permission(
            group_entry=entry, permission=permission, payload=payload
        ):
            return True

    return False
