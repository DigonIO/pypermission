from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pypermission.core import PermissionNode
from pypermission.error import EntityIDCollisionError, UnknownGroupIDError, UnknownSubjectIDError
from pypermission.sqlalchemy.models import (
    GroupEntry,
    GroupPermissionEntry,
    MembershipEntry,
    RelationshipEntry,
    SubjectEntry,
    SubjectPermissionEntry,
)

####################################################################################################
### Create
####################################################################################################


def create_subject(*, serial_sid: str, db: Session) -> None:
    ### /* Prevents SQLAlchemy ID skipping
    try:
        read_subject(serial_sid=serial_sid, db=db)
    except UnknownSubjectIDError:
        ...
    else:
        raise EntityIDCollisionError from None  # TODO
    ### */

    subject_entry = SubjectEntry(serial_eid=serial_sid)
    db.add(subject_entry)
    try:
        db.commit()
    except IntegrityError as err:
        raise EntityIDCollisionError from None  # TODO
        # Skips a SQLAlchemy ID if raised


def create_group(*, serial_gid: str, db: Session) -> None:
    ### /* Prevents SQLAlchemy ID skipping
    try:
        read_group(serial_gid=serial_gid, db=db)
    except UnknownGroupIDError:
        ...
    else:
        raise EntityIDCollisionError from None  # TODO
    ### */

    group_entry = GroupEntry(serial_eid=serial_gid)
    db.add(group_entry)
    try:
        db.commit()
    except IntegrityError as err:
        raise EntityIDCollisionError from None  # TODO
        # Skips a SQLAlchemy ID if raised


def create_subject_permission(
    *, serial_sid: str, node: PermissionNode, payload: str | None, db: Session
) -> None:
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    _create_permission_entry(
        table=SubjectPermissionEntry,
        entity_db_id=subject_entry.entity_db_id,
        node=node,
        payload=payload,
    )


def create_group_permission(
    *, serial_gid: str, node: PermissionNode, payload: str | None, db: Session
) -> None:
    group_entry = read_group(serial_gid=serial_gid, db=db)
    _create_permission_entry(
        table=GroupPermissionEntry,
        entity_db_id=group_entry.entity_db_id,
        node=node,
        payload=payload,
    )


def create_membership(*, serial_sid: str, serial_gid: str, db: Session) -> None:
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    group_entry = read_group(serial_gid=serial_gid, db=db)

    ms_entry = MembershipEntry(
        subject_db_id=subject_entry.entity_db_id, group_db_id=group_entry.entity_db_id
    )
    db.add(ms_entry)
    try:
        db.commit()
    except IntegrityError as err:
        # raised if the entry already exists
        ...


def create_parent_child_relationship(*, serial_pid: str, serial_cid: str, db: Session) -> None:
    parent_entry = read_group(serial_gid=serial_pid, db=db)
    child_entry = read_group(serial_gid=serial_cid, db=db)

    parent_entry = RelationshipEntry(
        parent_db_id=parent_entry.entity_db_id, child_db_id=child_entry.entity_db_id
    )

    db.add(parent_entry)
    try:
        db.commit()
    except IntegrityError as err:
        # raised if the entry already exists
        ...


####################################################################################################
### Read
####################################################################################################


def read_subject(*, serial_sid: str, db: Session) -> SubjectEntry:
    subject_entries = db.query(SubjectEntry).filter(SubjectEntry.serial_eid == serial_sid).all()
    if subject_entries:
        return subject_entries[0]
    raise UnknownSubjectIDError  # TODO


def read_group(*, serial_gid: str, db: Session) -> GroupEntry:
    group_entries = db.query(GroupEntry).filter(GroupEntry.serial_eid == serial_gid).all()
    if group_entries:
        return group_entries[0]
    raise UnknownGroupIDError  # TODO


####################################################################################################
### Delete
####################################################################################################


def delete_subject(*, serial_sid: str, db: Session) -> None:
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    db.delete(subject_entry)
    db.commit()


def delete_group(*, serial_gid: str, db: Session) -> None:
    group_entry = read_group(serial_gid=serial_gid, db=db)
    db.delete(group_entry)
    db.commit()


def delete_subject_permission(
    *, serial_sid: str, node: PermissionNode, payload: str | None, db: Session
) -> None:
    subject_entry: SubjectPermissionEntry = read_subject(serial_sid=serial_sid, db=db)
    _delete_permission_entry(
        table=SubjectPermissionEntry,
        entity_db_id=subject_entry.entity_db_id,
        node=node,
        payload=payload,
    )


def delete_group_permission(
    *, serial_gid: str, node: PermissionNode, payload: str | None, db: Session
) -> None:
    group_entry: GroupPermissionEntry = read_subject(serial_gid=serial_gid, db=db)
    _delete_permission_entry(
        table=GroupPermissionEntry,
        entity_db_id=group_entry.entity_db_id,
        node=node,
        payload=payload,
    )


def delete_membership(*, serial_sid: str, serial_gid: str, db: Session):
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    group_entry = read_group(serial_gid=serial_gid, db=db)

    entries = (
        db.query(MembershipEntry)
        .filter(
            MembershipEntry.subject_db_id == subject_entry.entity_db_id,
            MembershipEntry.group_db_id == group_entry.entity_db_id,
        )
        .all()  # Should only have one entry
    )

    if entries:
        db.delete(entries[0])
    db.commit()


def delete_parent_child_relationship(*, serial_pid: str, serial_cid: str, db: Session) -> None:
    parent_entry = read_group(serial_gid=serial_pid, db=db)
    child_entry = read_group(serial_gid=serial_cid, db=db)

    parent_entry = RelationshipEntry(
        parent_db_id=parent_entry.entity_db_id, child_db_id=child_entry.entity_db_id
    )

    entries = (
        db.query(RelationshipEntry)
        .filter(
            RelationshipEntry.parent_db_id == parent_entry.entity_db_id,
            RelationshipEntry.child_db_id == child_entry.entity_db_id,
        )
        .all()  # Should only have one entry
    )

    if entries:
        db.delete(entries[0])
    db.commit()


####################################################################################################
### Util
####################################################################################################


def serialize_payload(payload: str | None):
    return "None" if payload is None else payload


def _create_permission_entry(
    *,
    table: SubjectPermissionEntry | GroupPermissionEntry,
    entity_db_id: int,
    node: PermissionNode,
    payload: str | None,
    db: Session,
) -> None:

    perm_entry = table(
        entity_db_id=entity_db_id,
        node=node.value,
        payload=serialize_payload(payload),
    )

    db.add(perm_entry)
    try:
        db.commit()
    except IntegrityError as err:
        # raised if the entry already exists
        ...


def _delete_permission_entry(
    *,
    table: SubjectPermissionEntry | GroupPermissionEntry,
    entity_db_id: int,
    node: PermissionNode,
    payload: str | None,
    db: Session,
) -> None:

    entries = (
        db.query(table)
        .filter(
            table.entity_db_id == entity_db_id,
            table.node == node.value,
            table.payload == serialize_payload(payload),
        )
        .all()  # Should only have one entry
    )

    if entries:
        db.delete(entries[0])
    db.commit()
