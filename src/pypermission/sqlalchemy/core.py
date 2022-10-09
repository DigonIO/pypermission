from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError

from pypermission.core import Authority as _Authority
from pypermission.core import EntityID, Permission, PermissionMap, PermissionNode
from pypermission.sqlalchemy.models import (
    ENTITY_ID_MAX_LENGHT,
    SERIAL_ENTITY_ID_LENGHT,
    DeclarativeMeta,
    SubjectEntry,
    GroupEntry,
)
from pypermission.error import EntityIDCollisionError, UnknownSubjectIDError, UnknownGroupIDError


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

    def add_subject(self, sid: EntityID, db: Session | None = None) -> None:
        """Create a new subject for a given ID."""
        serial_eid = entity_id_serializer(sid)
        db = self._setup_db_session(db)

        subject_entry = SubjectEntry(eid=serial_eid)
        db.add(subject_entry)

        try:
            db.commit()
        except IntegrityError as err:
            raise EntityIDCollisionError from None  # TODO

    def add_group(self, gid: EntityID, db: Session | None = None) -> None:
        """Create a new group for a given ID."""
        serial_eid = entity_id_serializer(gid)
        db = self._setup_db_session(db)

        group_entry = GroupEntry(eid=serial_eid)
        db.add(group_entry)

        try:
            db.commit()
        except IntegrityError as err:
            raise EntityIDCollisionError from None  # TODO

    def rem_subject(self, sid: EntityID, db: Session | None = None) -> None:
        """Remove a subject for a given ID."""
        serial_eid = entity_id_serializer(sid)
        db = self._setup_db_session(db)

        subject_entry = db.query(SubjectEntry).get(serial_eid)
        if subject_entry is None:
            raise UnknownSubjectIDError  # TODO

        db.delete(subject_entry)
        db.commit()

    def rem_group(self, gid: EntityID, db: Session | None = None) -> None:
        """Remove a group for a given ID."""
        serial_eid = entity_id_serializer(gid)
        db = self._setup_db_session(db)

        group_entry = db.query(GroupEntry).get(serial_eid)
        if group_entry is None:
            raise UnknownGroupIDError  # TODO

        db.delete(group_entry)
        db.commit()

    def get_subjects(self, db: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known subjects."""
        db = self._setup_db_session(db)

        subject_entries = db.query(SubjectEntry).all()
        return set(entity_id_deserializer(entry.eid) for entry in subject_entries)

    def get_groups(self, db: Session | None = None) -> set[EntityID]:
        """Get the IDs for all known groups."""
        db = self._setup_db_session(db)

        group_entries = db.query(GroupEntry).all()
        return set(entity_id_deserializer(entry.eid) for entry in group_entries)

    def _setup_db_session(self, db: Session | None) -> Session:
        if db is None:
            return self._session_maker()
        if isinstance(db, Session):
            return db
        raise AttributeError("Attribute 'db' must be of type 'sqlalchemy.orm.Session'!")


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
