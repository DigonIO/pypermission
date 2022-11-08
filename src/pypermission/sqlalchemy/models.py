from __future__ import annotations
from datetime import datetime
from typing import cast

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.orm import declarative_base, relationship, Mapped

####################################################################################################
### Const
####################################################################################################

DeclarativeMeta: type = declarative_base()

PREFIX = "pp_"
# The table prefix allows to distinguish between your own tables and PyPermission tables
# if they are used in the same database.

EXTEND_EXISTING = True
ENTITY_ID_MAX_LENGHT = 60
SERIAL_ENTITY_ID_LENGHT = ENTITY_ID_MAX_LENGHT + 4
PERMISSION_NODE_LENGTH = 64  # TODO raise if node is to long while registration
PERMISSION_PAYLOAD_LENGTH = 64  # TODO raise if payload is to long

####################################################################################################
### Mixin
####################################################################################################


class TimeStampMixin(object):
    """Timestamping mixin."""

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=None)
    # NOTE maybe this a better solution https://stackoverflow.com/questions/3923910/sqlalchemy-move-mixin-columns-to-end
    created_at._creation_order = 9998
    updated_at._creation_order = 9999

    @staticmethod
    def _updated_at(mapper, connection, target) -> None:
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls) -> None:
        event.listen(cls, "before_update", cls._updated_at)


class PermissionableEntityMixin(TimeStampMixin):
    """Permissionable entity mixin."""

    entity_db_id: Mapped[int] = Column(Integer, primary_key=True)
    serial_eid: Mapped[str] = Column(
        String(length=SERIAL_ENTITY_ID_LENGHT), unique=True
    )  # Entity ID


class PermissionPayloadMixin(TimeStampMixin):
    """Permission and payload mixin."""

    node: Mapped[str] = Column(String(length=PERMISSION_NODE_LENGTH), primary_key=True)
    payload: Mapped[str] = Column(String(length=PERMISSION_PAYLOAD_LENGTH), primary_key=True)
    node._creation_order = 9988
    payload._creation_order = 9989


####################################################################################################
### Table
####################################################################################################


class SubjectEntry(DeclarativeMeta, PermissionableEntityMixin):
    __tablename__ = PREFIX + "subject_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}

    permission_entries: Mapped[list[SubjectPermissionEntry]] = relationship(
        "SubjectPermissionEntry", cascade="all,delete"
    )

    _membership_entries: Mapped[list[MembershipEntry]] = relationship(
        "MembershipEntry", cascade="all,delete"
    )

    @property
    def group_entries(self) -> list[GroupEntry]:
        return [membership.group_entry for membership in self._membership_entries]


class GroupEntry(DeclarativeMeta, PermissionableEntityMixin):
    __tablename__ = PREFIX + "group_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}

    permission_entries: Mapped[list[GroupPermissionEntry]] = relationship(
        "GroupPermissionEntry", cascade="all,delete"
    )

    _membership_entries: Mapped[list[MembershipEntry]] = relationship(
        "MembershipEntry", cascade="all,delete"
    )

    _parent_relationship_entries: Mapped[list[RelationshipEntry]] = relationship(
        "RelationshipEntry",
        cascade="all,delete",
        primaryjoin="and_(RelationshipEntry.child_db_id==GroupEntry.entity_db_id)",
        # do not use viewonly=True, instead use backpopulate in the linked table to allow cascade
    )
    _child_relationship_entries: Mapped[list[RelationshipEntry]] = relationship(
        "RelationshipEntry",
        cascade="all,delete",
        primaryjoin="and_(RelationshipEntry.parent_db_id==GroupEntry.entity_db_id)",
        # do not use viewonly=True, instead use backpopulate in the linked table to allow cascade
    )

    @property
    def subject_entries(self) -> list[SubjectEntry]:
        return [membership.subject_entry for membership in self._membership_entries]

    @property
    def parent_entries(self) -> list[GroupEntry]:
        return [relation.parent_entry for relation in self._parent_relationship_entries]

    @property
    def child_entries(self) -> list[GroupEntry]:
        return [relation.child_entry for relation in self._child_relationship_entries]


class SubjectPermissionEntry(DeclarativeMeta, PermissionPayloadMixin):
    __tablename__ = PREFIX + "subject_permission_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}
    entity_db_id: Mapped[int] = Column(
        Integer, ForeignKey(PREFIX + "subject_table.entity_db_id"), primary_key=True
    )


class GroupPermissionEntry(DeclarativeMeta, PermissionPayloadMixin):
    __tablename__ = PREFIX + "group_permission_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}
    entity_db_id: Mapped[int] = Column(
        Integer, ForeignKey(PREFIX + "group_table.entity_db_id"), primary_key=True
    )


class MembershipEntry(DeclarativeMeta, TimeStampMixin):
    __tablename__ = PREFIX + "membership_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}
    subject_db_id: Mapped[int] = Column(
        Integer, ForeignKey(PREFIX + "subject_table.entity_db_id"), primary_key=True
    )
    group_db_id: Mapped[int] = Column(
        Integer, ForeignKey(PREFIX + "group_table.entity_db_id"), primary_key=True
    )

    subject_entry: Mapped[SubjectEntry] = relationship(
        "SubjectEntry", back_populates="_membership_entries"
    )
    group_entry: Mapped[GroupEntry] = relationship(
        "GroupEntry", back_populates="_membership_entries"
    )


class RelationshipEntry(DeclarativeMeta, TimeStampMixin):
    __tablename__ = PREFIX + "relationship_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}

    parent_db_id: Mapped[int] = Column(
        Integer, ForeignKey(PREFIX + "group_table.entity_db_id"), primary_key=True
    )
    child_db_id = Column(Integer, ForeignKey(PREFIX + "group_table.entity_db_id"), primary_key=True)

    parent_entry: GroupEntry = relationship(
        "GroupEntry", foreign_keys=[parent_db_id], back_populates="_child_relationship_entries"
    )
    child_entry: GroupEntry = relationship(
        "GroupEntry", foreign_keys=[child_db_id], back_populates="_parent_relationship_entries"
    )
