from typing import Type, cast

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pypermission.core import Permission
from pypermission.error import EntityIDError, RoleCycleError
from pypermission.sqlalchemy.models import (
    RoleEntry,
    RolePermissionEntry,
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


def create_role(*, serial_rid: str, db: Session) -> None:
    role_entry = RoleEntry(serial_eid=serial_rid)
    db.add(role_entry)
    try:
        db.commit()
    except IntegrityError as err:
        raise EntityIDError(
            "ID collision: Role with ID `{serial_rid}` already exists in database!"
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


def create_role_permission(
    *, serial_rid: str, permission: Permission, payload: str | None, db: Session
) -> None:
    role_entry = read_role(serial_rid=serial_rid, db=db)
    _create_permission_entry(
        table=RolePermissionEntry,
        entity_db_id=role_entry.entity_db_id,
        permission=permission,
        payload=payload,
        db=db,
    )


def create_membership(*, serial_sid: str, serial_rid: str, db: Session) -> None:
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    role_entry = read_role(serial_rid=serial_rid, db=db)

    ms_entry = MembershipEntry(
        subject_db_id=subject_entry.entity_db_id, role_db_id=role_entry.entity_db_id
    )
    db.add(ms_entry)
    try:
        db.commit()
    except IntegrityError:
        # don't raise here, desired state already exists
        ...


def create_parent_child_relationship(*, serial_pid: str, serial_cid: str, db: Session) -> None:
    parent_entry = read_role(serial_rid=serial_pid, db=db)
    child_entry = read_role(serial_rid=serial_cid, db=db)

    _detect_role_cycle(
        parent_entry=parent_entry,
        child_entry=child_entry,
    )

    rs_entry = RelationshipEntry(
        parent_db_id=parent_entry.entity_db_id, child_db_id=child_entry.entity_db_id
    )

    db.add(rs_entry)
    try:
        db.commit()
    except IntegrityError:
        # don't raise here, desired state already exists
        ...


####################################################################################################
### Read
####################################################################################################


def read_subject(*, serial_sid: str, db: Session) -> SubjectEntry:
    try:
        subject_entry = (
            db.query(SubjectEntry).filter(SubjectEntry.serial_eid == serial_sid).all()[0]
        )
    except IndexError:
        raise EntityIDError(f"Unknown subject ID `{serial_sid}`!")
    return cast(SubjectEntry, subject_entry)


def read_role(*, serial_rid: str, db: Session) -> RoleEntry:
    try:
        role_entry = db.query(RoleEntry).filter(RoleEntry.serial_eid == serial_rid).all()[0]
    except IndexError:
        raise EntityIDError(f"Unknown role ID `{serial_rid}`!")
    return cast(RoleEntry, role_entry)


####################################################################################################
### Delete
####################################################################################################


def delete_subject(*, serial_sid: str, db: Session) -> None:
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    db.delete(subject_entry)
    db.commit()


def delete_role(*, serial_rid: str, db: Session) -> None:
    role_entry = read_role(serial_rid=serial_rid, db=db)
    db.delete(role_entry)
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
        db=db,
    )


def delete_role_permission(
    *, serial_rid: str, permission: Permission, payload: str | None, db: Session
) -> None:
    role_entry: RoleEntry = read_role(serial_rid=serial_rid, db=db)
    _delete_permission_entry(
        table=RolePermissionEntry,
        entity_db_id=role_entry.entity_db_id,
        permission=permission,
        payload=payload,
        db=db,
    )


def delete_membership(*, serial_sid: str, serial_rid: str, db: Session) -> None:
    subject_entry = read_subject(serial_sid=serial_sid, db=db)
    role_entry = read_role(serial_rid=serial_rid, db=db)

    entries = (
        db.query(MembershipEntry)
        .filter(
            MembershipEntry.subject_db_id == subject_entry.entity_db_id,
            MembershipEntry.role_db_id == role_entry.entity_db_id,
        )
        .all()  # Should only have one entry
    )

    if entries:
        db.delete(entries[0])
    db.commit()


def delete_parent_child_relationship(*, serial_pid: str, serial_cid: str, db: Session) -> None:
    parent_entry = read_role(serial_rid=serial_pid, db=db)
    child_entry = read_role(serial_rid=serial_cid, db=db)

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
    table: Type[SubjectPermissionEntry] | Type[RolePermissionEntry],
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
    except IntegrityError:
        # don't raise here, desired state already exists
        ...


def _delete_permission_entry(
    *,
    table: Type[SubjectPermissionEntry] | Type[RolePermissionEntry],
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


def _detect_role_cycle(*, parent_entry: RoleEntry, child_entry: RoleEntry) -> None:
    if parent_entry == child_entry:
        raise RoleCycleError  # TODO single node, single edge graph error message

    parent_entries = parent_entry.parent_entries  # parents of this "parent" role

    if child_entry in parent_entries:
        raise RoleCycleError(
            f"Cyclic dependencies detected between roles `{parent_entry.serial_eid}` and `{child_entry.serial_eid}`!"
        )
    for entry in parent_entries:
        _detect_role_cycle(parent_entry=entry, child_entry=child_entry)
