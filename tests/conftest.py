from typing import Generator

import pytest
from _pytest.fixtures import FixtureRequest

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from pypermission.models import BaseORM


@pytest.fixture(params=["sqlite", "psql"])
def engine(request: FixtureRequest) -> Generator[Engine, None, None]:
    match request.param:
        case "sqlite":
            url = "sqlite:///:memory:"
        case "psql":
            url = "postgresql+psycopg://username:password@127.0.0.1:23000/database"
        case _:
            raise ValueError()
    engine = create_engine(url, future=True)
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
