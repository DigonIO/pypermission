from uuid import UUID
from enum import StrEnum

from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

################################################################################
#### Types
################################################################################


class ExampleError(Exception): ...


class Context:
    user_id: UUID | None
    db: Session

    def __init__(self, *, user_id: UUID | None = None, db: Session):
        self.user_id = user_id
        self.db = db


class State(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
