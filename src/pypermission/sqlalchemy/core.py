from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine.base import Engine

from pypermission.core import Authority as _Authority, validate_payload_status
from pypermission.core import EntityID, Permission, PermissionMap, PermissionNode
from pypermission.sqlalchemy.models import (
    ENTITY_ID_MAX_LENGHT,
    SERIAL_ENTITY_ID_LENGHT,
    DeclarativeMeta,
    SubjectEntry,
    GroupEntry,
)
from pypermission.error import EntityIDCollisionError, UnknownSubjectIDError, UnknownGroupIDError
from pypermission.sqlalchemy.service import (
    create_subject,
    create_group,
    delete_subject,
    delete_group,
    create_subject_permission,
    create_group_permission,
    delete_subject_permission,
    delete_group_permission,
    create_membership,
    delete_membership,
)


class Authority(_Authority):

    _engine: Engine
    _session_maker: sessionmaker

    def __init__(self, *, engine: Engine, nodes: type[PermissionNode] | None = None) -> None:
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
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(db)

        create_subject(serial_sid=serial_sid, db=db)

    def add_group(self, gid: EntityID, db: Session | None = None) -> None:
        """Create a new group for a given ID."""
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(db)

        create_group(serial_gid=serial_gid, db=db)

    def subject_add_permission(
        self,
        *,
        sid: EntityID,
        node: PermissionNode,
        payload: str | None = None,
        db: Session | None = None,
    ):
        """Add a permission to a subject."""
        serial_sid = entity_id_serializer(sid)
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
        serial_gid = entity_id_serializer(gid)
        db = self._setup_db_session(db)
        permission = self._get_permission(node=node)
        validate_payload_status(permission=permission, payload=payload)

        create_group_permission(serial_gid=serial_gid, node=node, payload=payload, db=db)

    def group_add_subject(
        self,
        *,
        gid: EntityID,
        sid: EntityID,
        db: Session | None = None,
    ) -> None:
        """Add a subject to a group to inherit all its permissions."""
        serial_gid = entity_id_serializer(gid)
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(db)

        create_membership(serial_sid=serial_sid, serial_gid=serial_gid, db=db)

    ################################################################################################
    ### Get
    ################################################################################################

    def get_subjects(self, db: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known subjects."""
        db = self._setup_db_session(db)

        subject_entries = db.query(SubjectEntry).all()
        return set(entity_id_deserializer(entry.serial_eid) for entry in subject_entries)

    def get_groups(self, db: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known groups."""
        db = self._setup_db_session(db)

        group_entries = db.query(GroupEntry).all()
        return set(entity_id_deserializer(entry.serial_eid) for entry in group_entries)

    ################################################################################################
    ### Remove
    ################################################################################################

    def rem_subject(self, sid: EntityID, db: Session | None = None) -> None:
        """Remove a subject for a given ID."""
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(db)

        delete_subject(serial_sid=serial_sid, db=db)

    def rem_group(self, gid: EntityID, db: Session | None = None) -> None:
        """Remove a group for a given ID."""
        serial_gid = entity_id_serializer(gid)
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
        serial_sid = entity_id_serializer(sid)
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
        serial_gid = entity_id_serializer(gid)
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
        serial_gid = entity_id_serializer(gid)
        serial_sid = entity_id_serializer(sid)
        db = self._setup_db_session(db)

        delete_membership(serial_sid=serial_sid, serial_gid=serial_gid, db=db)

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


def entity_id_serializer(eid: EntityID) -> str:
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


def entity_id_deserializer(serial_eid: str) -> EntityID:
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
