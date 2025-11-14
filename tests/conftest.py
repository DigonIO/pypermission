import os
from typing import Generator

import pytest
from _pytest.fixtures import FixtureRequest
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import Session, sessionmaker

from pypermission.db import set_sqlite_pragma
from pypermission.models import BaseORM


@pytest.fixture(params=["sqlite", "psql"])
def engine(request: FixtureRequest) -> Generator[Engine, None, None]:
    match request.param:
        case "sqlite":
            url = "sqlite:///:memory:"
            engine = create_engine(url, future=True)
            listen(engine, "connect", set_sqlite_pragma)
        case "psql":
            if os.getenv("CI") is None:
                url = "postgresql+psycopg://username:password@127.0.0.1:23000/database"
            else:
                url = "postgresql+psycopg://username:password@postgres:5432/database"
            engine = create_engine(url, future=True)
        case _:
            raise ValueError()

    BaseORM.metadata.create_all(engine)
    yield engine
    BaseORM.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db(engine: Engine) -> Generator[Session, None, None]:
    db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with db_factory() as db:
        try:
            yield db
        finally:
            db.rollback()
            db.close()
