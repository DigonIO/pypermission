from sqlite3 import IntegrityError as Sqlite3IntegrityError
from typing import TYPE_CHECKING, Never

from sqlalchemy.exc import IntegrityError

from pypermission.exc import PyPermissionError
from pypermission.models import Permission

if TYPE_CHECKING:
    from psycopg.errors import Diagnostic as PsycopgDiagnostic
    from psycopg.errors import ForeignKeyViolation as PsycopgForeignKeyViolation
    from psycopg.errors import UniqueViolation as PsycopgUniqueViolation
else:
    try:
        from psycopg.errors import Diagnostic as PsycopgDiagnostic
        from psycopg.errors import ForeignKeyViolation as PsycopgForeignKeyViolation
        from psycopg.errors import UniqueViolation as PsycopgUniqueViolation
    except ModuleNotFoundError:

        class PsycopgForeignKeyViolation(Exception): ...

        class PsycopgUniqueViolation(Exception): ...

        class PsycopgDiagnostic: ...


################################################################################
#### Error Utilities
################################################################################


def process_subject_role_integrity_error(
    *, err: IntegrityError, subject: str | None = None, role: str | None = None
) -> Never:
    match err:
        case IntegrityError(orig=Sqlite3IntegrityError()):
            if subject is not None and role is not None:
                raise PyPermissionError(
                    f"Subject '{subject}' or Role '{role}' does not exist!"
                )
            if subject is not None:
                raise PyPermissionError(f"Subject '{subject}' does not exist!")
            if role is not None:
                raise PyPermissionError(f"Role '{role}' does not exist!")
        case IntegrityError(
            orig=PsycopgForeignKeyViolation(
                diag=PsycopgDiagnostic(message_detail=str(msg))
            )
        ):
            if f"Key (role_id)=({role}) is not present in table" in msg:
                raise PyPermissionError(f"Role '{role}' does not exist!")
            if f"Key (subject_id)=({subject}) is not present in table" in msg:
                raise PyPermissionError(f"Subject '{subject}' does not exist!")
        case _:
            ...
    raise PyPermissionError("Unexpected IntegrityError")


def process_policy_integrity_error(
    *,
    err: IntegrityError,
    role: str,
    permission: Permission,
) -> Never:
    match err:
        case IntegrityError(
            orig=Sqlite3IntegrityError(sqlite_errorname="SQLITE_CONSTRAINT_PRIMARYKEY")
        ):
            raise PyPermissionError(
                f"Permission '{str(permission)}' does already exist!"
            ) from err
        case IntegrityError(
            orig=Sqlite3IntegrityError(sqlite_errorname="SQLITE_CONSTRAINT_FOREIGNKEY")
        ):
            raise PyPermissionError(f"Role '{role}' does not exist!") from err
        case IntegrityError(
            orig=PsycopgUniqueViolation(
                diag=PsycopgDiagnostic(message_detail=str(_msg))
            )
        ):
            raise PyPermissionError(
                f"Permission '{str(permission)}' does already exist!"
            ) from err
        case IntegrityError(
            orig=PsycopgForeignKeyViolation(
                diag=PsycopgDiagnostic(message_detail=str(_msg))
            )
        ):
            raise PyPermissionError(f"Role '{role}' does not exist!") from err
        case _:
            ...
    raise PyPermissionError("Unexpected IntegrityError")
