from datetime import datetime

from sqlalchemy import Column, DateTime, event, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

####################################################################################################
### Const
####################################################################################################

DeclarativeMeta: type = declarative_base()

EXTEND_EXISTING = True
ENTITY_ID_MAX_LENGHT = 60
SERIAL_ENTITY_ID_LENGHT = ENTITY_ID_MAX_LENGHT + 4
PERMISSION_NODE_LENGTH = 64
PERMISSION_PAYLOAD_LENGTH = 64

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
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


class PermissionableEntityMixin(TimeStampMixin):
    """Permissionable entity mixin."""

    entity_db_id = Column(Integer, primary_key=True)
    serial_eid = Column(String(length=SERIAL_ENTITY_ID_LENGHT), unique=True)  # Entity ID


class PermissionPayloadMixin(TimeStampMixin):
    """Permission and payload mixin."""

    node = Column(String(length=PERMISSION_NODE_LENGTH), primary_key=True)
    payload = Column(String(length=PERMISSION_PAYLOAD_LENGTH), primary_key=True)
    node._creation_order = 9988
    payload._creation_order = 9989


####################################################################################################
### Table
####################################################################################################


class SubjectEntry(DeclarativeMeta, PermissionableEntityMixin):
    __tablename__ = "subject_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}

    permission_entries = relationship("SubjectPermissionEntry", cascade="all,delete")


class GroupEntry(DeclarativeMeta, PermissionableEntityMixin):
    __tablename__ = "group_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}

    permission_entries = relationship("GroupPermissionEntry", cascade="all,delete")


class SubjectPermissionEntry(DeclarativeMeta, PermissionPayloadMixin):
    __tablename__ = "subject_permission_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}
    entity_db_id = Column(Integer, ForeignKey("subject_table.db_id"), primary_key=True)


class GroupPermissionEntry(DeclarativeMeta, PermissionPayloadMixin):
    __tablename__ = "group_permission_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}
    entity_db_id = Column(Integer, ForeignKey("group_table.db_id"), primary_key=True)
