from enum import StrEnum

from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

################################################################################
#### Types
################################################################################


class ExampleError(Exception): ...


class Context:
    username: str | None
    db: Session

    def __init__(self, *, user: str | None = None, db: Session):
        self.username = user
        self.db = db


class State(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
