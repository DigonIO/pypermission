from datetime import datetime

from sqlalchemy import Column, DateTime, event, String
from sqlalchemy.orm import declarative_base


EXTEND_EXISTING = True
ENTITY_ID_MAX_LENGHT = 100
SERIAL_ENTITY_ID_LENGHT = ENTITY_ID_MAX_LENGHT + 4

DeclarativeMeta: type = declarative_base()


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=None)
    # NOTE maybe this a better solution https://stackoverflow.com/questions/3923910/sqlalchemy-move-mixin-columns-to-end
    created_at._creation_order = 9998
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


class PermissionableEntityMixin(TimeStampMixin):
    """Permissionable entity mixin"""

    eid = Column(String(length=SERIAL_ENTITY_ID_LENGHT), primary_key=True)  # Entity ID


class SubjectEntry(DeclarativeMeta, PermissionableEntityMixin):
    __tablename__ = "token_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}


class GroupEntry(DeclarativeMeta, PermissionableEntityMixin):
    __tablename__ = "token_table"
    __table_args__ = {"extend_existing": EXTEND_EXISTING}
