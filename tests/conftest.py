from typing import Generator

import pytest

from sqlalchemy.sql import text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from pypermission.models import BaseORM


@pytest.fixture()
def sqlite_engine() -> Generator[Engine, None, None]:
    url = "sqlite:///:memory:"
    engine = create_engine(url, future=True)
    BaseORM.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def psql_engine() -> Generator[Engine, None, None]:
    url = "postgresql+psycopg://username:password@127.0.0.1:23000/database"
    engine = create_engine(url, future=True)
    BaseORM.metadata.create_all(engine)
    yield engine
    BaseORM.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def sqlite_db(sqlite_engine: Engine) -> Generator[Session, None, None]:
    db_factory = sessionmaker(bind=sqlite_engine, autoflush=False, autocommit=False)

    with db_factory() as db:
        try:
            yield db
        finally:
            db.rollback()
            db.close()


@pytest.fixture()
def psql_db(psql_engine: Engine) -> Generator[Session, None, None]:
    db_factory = sessionmaker(bind=psql_engine, autoflush=False, autocommit=False)

    with db_factory() as db:
        try:
            yield db
        finally:
            db.rollback()
            db.close()
