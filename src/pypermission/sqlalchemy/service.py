from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pypermission.sqlalchemy.models import SubjectEntry, GroupEntry
from pypermission.error import EntityIDCollisionError, UnknownSubjectIDError, UnknownGroupIDError


def create_subject(*, serial_sid: str, db: Session) -> None:
    subject_entry = SubjectEntry(eid=serial_sid)
    db.add(subject_entry)
    try:
        db.commit()
    except IntegrityError as err:
        raise EntityIDCollisionError from None  # TODO


def create_group(*, serial_gid: str, db: Session) -> None:
    group_entry = GroupEntry(eid=serial_gid)
    db.add(group_entry)

    try:
        db.commit()
    except IntegrityError as err:
        raise EntityIDCollisionError from None  # TODO


def delete_subject(*, serial_sid: str, db: Session) -> None:
    subject_entry = db.query(SubjectEntry).get(serial_sid)
    if subject_entry is None:
        raise UnknownSubjectIDError  # TODO

    db.delete(subject_entry)
    db.commit()


def delete_group(serial_gid: str, db: Session) -> None:
    group_entry = db.query(GroupEntry).get(serial_gid)
    if group_entry is None:
        raise UnknownGroupIDError  # TODO

    db.delete(group_entry)
    db.commit()
