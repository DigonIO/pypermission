from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker

from pypermission.core import Authority as _Authority
from pypermission.core import (
    EntityID,
    Permission,
    PermissionMap,
    PermissionNode,
    validate_payload_status,
)
from pypermission.sqlalchemy.models import (
    ENTITY_ID_MAX_LENGHT,
    SERIAL_ENTITY_ID_LENGHT,
    DeclarativeMeta,
    GroupEntry,
    SubjectEntry,
    SubjectPermissionEntry,
    GroupPermissionEntry,
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


class Authority(_Authority):

    _engine: Engine
    _session_maker: sessionmaker

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

    def add_subject(self, sid: EntityID, db: Session | None = None) -> None:
        """Create a new subject for a given ID."""
        serial_sid = _entity_id_serializer(sid)
        db = self._setup_db_session(db)

        create_subject(serial_sid=serial_sid, db=db)

    def add_group(self, gid: EntityID, db: Session | None = None) -> None:
        """Create a new group for a given ID."""
        serial_gid = _entity_id_serializer(gid)
        db = self._setup_db_session(db)

        create_group(serial_gid=serial_gid, db=db)

    def group_add_subject(self, *, gid: EntityID, sid: EntityID, db: Session | None = None) -> None:
        """Add a subject to a group to inherit all its permissions."""
        serial_gid = _entity_id_serializer(gid)
        serial_sid = _entity_id_serializer(sid)
        db = self._setup_db_session(db)

        create_membership(serial_sid=serial_sid, serial_gid=serial_gid, db=db)

    def group_add_child_group(
        self, *, gid: EntityID, cid: EntityID, db: Session | None = None
    ) -> None:
        """Add a group to a parent group to inherit all its permissions."""
        serial_gid = _entity_id_serializer(gid)
        serial_cid = _entity_id_serializer(cid)
        db = self._setup_db_session(db)

        create_parent_child_relationship(serial_pid=serial_gid, serial_cid=serial_cid, db=db)

    def subject_add_permission(
        self,
        *,
        sid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        db: Session | None = None,
    ):
        """Add a permission to a subject."""
        serial_sid = _entity_id_serializer(sid)
        db = self._setup_db_session(db)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        create_subject_permission(serial_sid=serial_sid, node=node, payload=payload, db=db)

    def group_add_permission(
        self,
        *,
        gid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        db: Session | None = None,
    ):
        """Add a permission to a group."""
        serial_gid = _entity_id_serializer(gid)
        db = self._setup_db_session(db)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        create_group_permission(serial_gid=serial_gid, node=node, payload=payload, db=db)

    ################################################################################################
    ### Get
    ################################################################################################

    def get_subjects(self, db: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known subjects."""
        db = self._setup_db_session(db)

        subject_entries = db.query(SubjectEntry).all()
        return set(_entity_id_deserializer(entry.serial_eid) for entry in subject_entries)

    def get_groups(self, db: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known groups."""
        db = self._setup_db_session(db)

        group_entries = db.query(GroupEntry).all()
        return set(_entity_id_deserializer(entry.serial_eid) for entry in group_entries)

    # TODO subject_get_groups

    # TODO group_get_subjects

    def group_get_child_groups(self, *, gid: EntityID, db: Session | None = None) -> set[EntityID]:
        """Get a set of all child group IDs of a group."""
        serial_gid = _entity_id_serializer(gid)
        db = self._setup_db_session(db)

        group_entry = read_group(serial_gid=serial_gid, db=db)
        child_entries: list[GroupEntry] = group_entry.child_entries
        return set(_entity_id_deserializer(entry.serial_eid) for entry in child_entries)

    def group_get_parent_groups(self, *, gid: EntityID, db: Session | None = None) -> set[EntityID]:
        """Get a set of all parent group IDs of a group."""
        serial_gid = _entity_id_serializer(gid)
        db = self._setup_db_session(db)

        group_entry = read_group(serial_gid=serial_gid, db=db)
        parent_entries: list[GroupEntry] = group_entry.parent_entries
        return set(_entity_id_deserializer(entry.serial_eid) for entry in parent_entries)

    def subject_has_permission(
        self, *, sid: EntityID, node: PermissionNode, payload: str | None = None, db: Session
    ) -> bool:
        serial_sid = _entity_id_serializer(sid)
        db = self._setup_db_session(db)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        subject_entry = read_subject(serial_sid=serial_sid, db=db)

        perm_entries: list[SubjectPermissionEntry] = subject_entry.permission_entries
        if _has_permission(perm_entries=perm_entries, permission=permission, payload=payload):
            return True

        ms_entries: list[GroupEntry] = subject_entry.membership_entries
        for entry in ms_entries:
            if _recursive_group_has_permission(
                group_entry=entry, permission=permission, payload=payload
            ):
                return True

        return False

    def group_has_permission(
        self, *, gid: EntityID, node: PermissionNode, payload: str | None = None, db: Session
    ) -> bool:
        serial_gid = _entity_id_serializer(gid)
        db = self._setup_db_session(db)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        group_entry = read_group(serial_gid=serial_gid, db=db)

        return _recursive_group_has_permission(
            group_entry=group_entry, permission=permission, payload=payload
        )

    # TODO subject_get_permissions

    # TODO group_get_permissions

    ################################################################################################
    ### Remove
    ################################################################################################

    def rem_subject(self, sid: EntityID, db: Session | None = None) -> None:
        """Remove a subject for a given ID."""
        serial_sid = _entity_id_serializer(sid)
        db = self._setup_db_session(db)

        delete_subject(serial_sid=serial_sid, db=db)

    def rem_group(self, gid: EntityID, db: Session | None = None) -> None:
        """Remove a group for a given ID."""
        serial_gid = _entity_id_serializer(gid)
        db = self._setup_db_session(db)

        delete_group(serial_gid=serial_gid, db=db)

    def subject_rem_permission(
        self,
        *,
        sid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        db: Session | None = None,
    ):
        """Remove a permission to a subject."""
        serial_sid = _entity_id_serializer(sid)
        db = self._setup_db_session(db)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        delete_subject_permission(serial_sid=serial_sid, node=node, payload=payload, db=db)

    def group_rem_permission(
        self,
        *,
        gid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        db: Session | None = None,
    ):
        """Remove a permission to a group."""
        serial_gid = _entity_id_serializer(gid)
        db = self._setup_db_session(db)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        delete_group_permission(serial_gid=serial_gid, node=node, payload=payload, db=db)

    def group_rem_subject(
        self,
        *,
        gid: EntityID,
        sid: EntityID,
        db: Session | None = None,
    ) -> None:
        """Remove a subject from a group."""
        serial_gid = _entity_id_serializer(gid)
        serial_sid = _entity_id_serializer(sid)
        db = self._setup_db_session(db)

        delete_membership(serial_sid=serial_sid, serial_gid=serial_gid, db=db)

    def group_rem_child_group(
        self, *, gid: EntityID, cid: EntityID, db: Session | None = None
    ) -> None:
        """Remove a group from a group."""
        serial_gid = _entity_id_serializer(gid)
        serial_cid = _entity_id_serializer(cid)

        delete_parent_child_relationship(serial_pid=serial_gid, serial_cid=serial_cid, db=db)

    ################################################################################################
    ### Private
    ################################################################################################

    def _setup_db_session(self, db: Session | None) -> Session:
        if db is None:
            return self._session_maker()
        if isinstance(db, Session):
            return db
        raise AttributeError("Attribute 'db' must be of type 'sqlalchemy.orm.Session'!")


####################################################################################################
### Util
####################################################################################################


def _entity_id_serializer(eid: EntityID) -> str:
    if isinstance(eid, int):
        serial_type = "int"
        serial_eid = str(eid)
    elif isinstance(eid, str):
        serial_type = "str"
        serial_eid = eid
    else:
        raise ValueError  # TODO

    if len(serial_eid) > ENTITY_ID_MAX_LENGHT:
        raise ValueError  # TODO

    return f"{serial_eid}:{serial_type}"


def _entity_id_deserializer(serial_eid: str) -> EntityID:
    if len(serial_eid) > (SERIAL_ENTITY_ID_LENGHT):
        raise ValueError  # TODO

    serial_type = serial_eid[-3:]
    serial_eid = serial_eid[:-4]

    if serial_type == "int":
        return int(serial_eid)
    elif serial_type == "str":
        return serial_eid
    else:
        raise ValueError  # TODO


def _has_permission(
    perm_entries: list[SubjectPermissionEntry] | list[GroupPermissionEntry],
    permission: Permission,
    payload: str | None,
) -> bool:
    for entry in perm_entries:
        if (entry.node == permission.node.value) and (entry.payload == serialize_payload(payload)):
            return True
    return False


def _recursive_group_has_permission(
    group_entry: GroupEntry, permission: Permission, payload: str | None
) -> bool:
    """Recursively check whether the group or one of its parents has the perm searched for."""
    perm_entries: list[GroupPermissionEntry] = group_entry.permission_entries
    if _has_permission(perm_entries=perm_entries, permission=permission, payload=payload):
        return True

    parent_entries: list[GroupEntry] = group_entry.parent_entries
    for entry in parent_entries:
        if _recursive_group_has_permission(
            group_entry=entry, permission=permission, payload=payload
        ):
            return True

    return False
