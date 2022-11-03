from typing import Type, cast
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pypermission.core import Permission
from pypermission.error import (
    EntityIDError,
    GroupCycleError,
)
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
    subject_entry = SubjectEntry(serial_eid=serial_sid)
    db.add(subject_entry)
    try:
        db.commit()
    except IntegrityError as err:
        raise EntityIDError(
            "ID collision: Subject with ID `{serial_sid}` already exists in database!"
        ) from err
        # Skips a SQLAlchemy ID if raised


def create_group(*, serial_gid: str, db: Session) -> None:
    group_entry = GroupEntry(serial_eid=serial_gid)
    db.add(group_entry)
    try:
        db.commit()
    except IntegrityError as err:
        raise EntityIDError(
            "ID collision: Group with ID `{serial_gid}` already exists in database!"
        ) from err
        # Skips a SQLAlchemy ID if raised


def create_subject_permission(
    *, serial_sid: str, permission: Permission, payload: str | None, db: Session
) -> None:
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    _create_permission_entry(
        table=SubjectPermissionEntry,
        entity_db_id=subject_entry.entity_db_id,
        permission=permission,
        payload=payload,
        db=db,
    )


def create_group_permission(
    *, serial_gid: str, permission: Permission, payload: str | None, db: Session
) -> None:
    group_entry = read_group(serial_gid=serial_gid, db=db)
    _create_permission_entry(
        table=GroupPermissionEntry,
        entity_db_id=group_entry.entity_db_id,
        permission=permission,
        payload=payload,
        db=db,
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
        # don't raise here, desired state already exists
        ...


def create_parent_child_relationship(*, serial_pid: str, serial_cid: str, db: Session) -> None:
    parent_entry = read_group(serial_gid=serial_pid, db=db)
    child_entry = read_group(serial_gid=serial_cid, db=db)

    _detect_group_cycle(
        parent_entry=parent_entry,
        child_entry=child_entry,
    )

    rs_entry = RelationshipEntry(
        parent_db_id=parent_entry.entity_db_id, child_db_id=child_entry.entity_db_id
    )

    db.add(rs_entry)
    try:
        db.commit()
    except IntegrityError as err:
        # don't raise here, desired state already exists
        ...


####################################################################################################
### Read
####################################################################################################


def read_subject(*, serial_sid: str, db: Session) -> SubjectEntry:
    try:
        subject_entry, *_ = (
            db.query(SubjectEntry).filter(SubjectEntry.serial_eid == serial_sid).all()
        )
    except ValueError:
        raise EntityIDError(f"Unknown subject ID `{serial_sid}`!")
    return cast(SubjectEntry, subject_entry)


def read_group(*, serial_gid: str, db: Session) -> GroupEntry:
    try:
        group_entry, *_ = db.query(GroupEntry).filter(GroupEntry.serial_eid == serial_gid).all()
    except ValueError:
        raise EntityIDError(f"Unknown group ID `{serial_gid}`!")
    return cast(GroupEntry, group_entry)


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
    *, serial_sid: str, permission: Permission, payload: str | None, db: Session
) -> None:
    subject_entry: SubjectEntry = read_subject(serial_sid=serial_sid, db=db)
    _delete_permission_entry(
        table=SubjectPermissionEntry,
        entity_db_id=subject_entry.entity_db_id,
        permission=permission,
        payload=payload,
    )


def delete_group_permission(
    *, serial_gid: str, permission: Permission, payload: str | None, db: Session
) -> None:
    group_entry: GroupPermissionEntry = read_subject(serial_gid=serial_gid, db=db)
    _delete_permission_entry(
        table=GroupPermissionEntry,
        entity_db_id=group_entry.entity_db_id,
        permission=permission,
        payload=payload,
    )


def delete_membership(*, serial_sid: str, serial_gid: str, db: Session) -> None:
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


def serialize_payload(payload: str | None) -> str:
    return "None" if payload is None else payload


def _create_permission_entry(
    *,
    table: Type[SubjectPermissionEntry] | Type[GroupPermissionEntry],
    entity_db_id: int,
    permission: Permission,
    payload: str | None,
    db: Session,
) -> None:

    perm_entry = table(
        entity_db_id=entity_db_id,
        node=permission.node.value,
        payload=serialize_payload(payload),
    )

    db.add(perm_entry)
    try:
        db.commit()
    except IntegrityError as err:
        # don't raise here, desired state already exists
        ...


def _delete_permission_entry(
    *,
    table: Type[SubjectPermissionEntry] | Type[GroupPermissionEntry],
    entity_db_id: int,
    permission: Permission,
    payload: str | None,
    db: Session,
) -> None:

    entries = (
        db.query(table)
        .filter(
            table.entity_db_id == entity_db_id,
            table.node == permission.node.value,
            table.payload == serialize_payload(payload),
        )
        .all()  # Should only have one entry
    )

    if entries:
        db.delete(entries[0])
    db.commit()


def _detect_group_cycle(*, parent_entry: GroupEntry, child_entry: GroupEntry) -> None:
    if parent_entry == child_entry:
        raise GroupCycleError  # TODO single node, single edge graph error message

    parent_entries = parent_entry.parent_entries  # parents of this "parent" group

    if child_entry in parent_entries:
        raise GroupCycleError(
            f"Cyclic dependencies detected between groups `{parent_entry.serial_eid}` and `{child_entry.serial_eid}`!"
        )
    for entry in parent_entries:
        _detect_group_cycle(parent_entry=entry, child_entry=child_entry)
