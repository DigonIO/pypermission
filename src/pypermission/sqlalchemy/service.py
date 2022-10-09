from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pypermission.core import PermissionNode
from pypermission.sqlalchemy.models import (
    SubjectEntry,
    GroupEntry,
    SubjectPermissionEntry,
    GroupPermissionEntry,
)
from pypermission.error import EntityIDCollisionError, UnknownSubjectIDError, UnknownGroupIDError

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
    perm_entry = SubjectPermissionEntry(
        subject_db_id=subject_entry.db_id,
        node=node.value,
        payload="None" if payload is None else payload,
    )
    db.add(perm_entry)
    try:
        db.commit()
    except IntegrityError as err:
        # raised if the entry already exists
        ...


def create_group_permission(
    *, serial_gid: str, node: PermissionNode, payload: str | None, db: Session
) -> None:
    group_entry = read_group(serial_gid=serial_gid, db=db)
    perm_entry = GroupPermissionEntry(
        group_db_id=group_entry.db_id,
        node=node.value,
        payload="None" if payload is None else payload,
    )
    db.add(perm_entry)
    try:
        db.commit()
    except IntegrityError as err:
        # raised if the entry already exists
        ...


####################################################################################################
### Read
####################################################################################################


def read_subject(*, serial_sid: str, db: Session) -> SubjectEntry:
    subject_entry = db.query(SubjectEntry).filter(SubjectEntry.serial_eid == serial_sid).all()
    if subject_entry:
        return subject_entry[0]
    raise UnknownSubjectIDError  # TODO


def read_group(*, serial_gid: str, db: Session) -> GroupEntry:
    group_entry = db.query(GroupEntry).filter(GroupEntry.serial_eid == serial_gid)
    if group_entry:
        return group_entry[0]
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
