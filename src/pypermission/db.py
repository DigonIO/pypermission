from sqlite3 import Connection

from sqlalchemy.engine.base import Engine
from sqlalchemy.event import contains
from sqlalchemy.pool.base import (
    _ConnectionRecord,  # pyright: ignore[reportPrivateUsage]
)

from pypermission.exc import PyPermissionError
from pypermission.models import BaseORM


def create_rbac_database_table(*, engine: Engine) -> None:
    """
    Create all required database tables via. SQLAlchemy for PyPermission.

    Parameters
    ----------
    engine : Engine
        The SQLAlchemy engine.
    """
    if engine.driver == "pysqlite" and not contains(
        engine, "connect", set_sqlite_pragma
    ):
        raise PyPermissionError(
            "Foreign keys pragma appears to not be set! Please use the 'set_sqlite_pragma' function"
            " on your SQLite engine before interacting with the database!"
        )

    BaseORM.metadata.create_all(bind=engine)


# https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support
def set_sqlite_pragma(
    dbapi_connection: Connection, _connection_record: _ConnectionRecord
) -> None:
    """
    Enable foreign key constraints for SQLite connections.

    This function ensures that SQLite foreign key constraints are enabled.

    Notes
    -----
    SQLite's foreign key support is disabled by default and requires explicit
    enabling. The sqlite driver will not set PRAGMA foreign_keys if
    autocommit=False, which is why this function temporarily enables it.

    References
    ----------
    - SQLAlchemy SQLite Foreign Key Support:
      https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support

    Examples
    --------
    >>> from sqlalchemy import create_engine
    >>> from sqlalchemy.event import listen
    >>> engine = create_engine('sqlite:///example.db')
    >>> listen(engine, 'connect', set_sqlite_pragma)
    """
    ac = dbapi_connection.autocommit
    dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    dbapi_connection.autocommit = ac
