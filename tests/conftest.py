from typing import Generator

import pytest
from _pytest.fixtures import FixtureRequest

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from pypermission.models import BaseORM

from sqlalchemy.event import listen
from sqlite3 import Connection
from sqlalchemy.pool.base import (
    _ConnectionRecord,  # pyright: ignore[reportPrivateUsage]
)


# https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support
def set_sqlite_pragma(
    dbapi_connection: Connection, _connection_record: _ConnectionRecord
) -> None:
    # the sqlite3 driver will not set PRAGMA foreign_keys
    # if autocommit=False; set to True temporarily
    ac = dbapi_connection.autocommit
    dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    # restore previous autocommit setting
    dbapi_connection.autocommit = ac


@pytest.fixture(params=["sqlite", "psql"])
def engine(request: FixtureRequest) -> Generator[Engine, None, None]:
    match request.param:
        case "sqlite":
            url = "sqlite:///:memory:"
            engine = create_engine(url, future=True)
            listen(engine, "connect", set_sqlite_pragma)
        case "psql":
            url = "postgresql+psycopg://username:password@127.0.0.1:23000/database"
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
