from enum import StrEnum

from sqlalchemy.orm import Session

from pypermission.example.model.user import UserORM

################################################################################
#### Types
################################################################################


class ExampleError(Exception): ...


class Context:
    user_orm: UserORM | None
    db: Session

    def __init__(self, *, user_orm: UserORM | None = None, db: Session):
        self.user_orm = user_orm
        self.db = db


class State(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
