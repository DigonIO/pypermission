from typing import Never
from sqlalchemy.exc import IntegrityError
from sqlite3 import IntegrityError as Sqlite3IntegrityError
from psycopg.errors import (
    ForeignKeyViolation as PsycopgForeignKeyViolation,
    Diagnostic as PsycopgDiagnostic,
)

################################################################################
#### Generic Errors
################################################################################


class PyPermissionError(Exception):
    """
    PyPermissionError is the standard error of PyPermission.

    Attributes
    ----------
    message : str
        A detailed description of the occurred error.
    """

    message: str

    def __init__(self, message: str = ""):
        self.message = message


class PyPermissionNotGrantedError(PyPermissionError):
    """
    PyPermissionNotGrantedError will be thrown if an `assert_permission()` fails!

    Attributes
    ----------
    message : str
        A constant error description.
    """

    message = "RBAC: Permission not granted!"


################################################################################
#### Error Utilities
################################################################################


def process_subject_role_integrity_error(
    *, err: IntegrityError, subject: str = "", role: str = ""
) -> Never:
    match err:
        case IntegrityError(
            orig=PsycopgForeignKeyViolation(
                diag=PsycopgDiagnostic(message_detail=str(message_detail))
            )
        ):
            if f"Key (role_id)=({role}) is not present in table" in message_detail:
                raise PyPermissionError(f"Role '{role}' does not exist!")
            if (
                f"Key (subject_id)=({subject}) is not present in table"
                in message_detail
            ):
                raise PyPermissionError(f"Subject '{subject}' does not exist!")
        case IntegrityError(orig=Sqlite3IntegrityError()):
            if subject and role:
                raise PyPermissionError(
                    f"Subject '{subject}' or Role '{role}' does not exist!"
                )
            if subject:
                raise PyPermissionError(f"Subject '{subject}' does not exist!")
            if role:
                raise PyPermissionError(f"Role '{role}' does not exist!")
        case _:
            ...
    raise PyPermissionError("Unexpected IntegrityError")

    ################################################################################
    #### Testing only:
    ################################################################################


class ERR_MSG:
    role_exists = "Role '{role}' already exists!"
    subject_exists = "Subject '{subject}' already exists!"
    hierarchy_exists = "Hierarchy '{parent_role}' -> '{child_role}' exists!"
    permission_exists = "Permission '{permission_str}' does already exist!"

    non_existent_subject_role = "Subject '{subject}' or Role '{role}' does not exist!"
    non_existent_subject = "Subject '{subject}' does not exist!"
    non_existent_role = "Role '{role}' does not exist!"
    non_existent_hierarchy = (
        "Hierarchy '{parent_role}' -> '{child_role}' does not exist!"
    )
    non_existent_parent_child_roles = (
        "Roles '{parent_role}' and '{child_role}' do not exist!"
    )
    non_existent_role_assignment = (
        "Role '{role}' is not assigned to Subject '{subject}'!"
    )

    permission_not_granted_for_role = (
        "Permission '{permission_str}' is not granted for Role '{role}'!"
    )
    permission_not_granted_for_subject = (
        "Permission '{permission_str}' is not granted for Subject '{subject}'!"
    )

    conflicting_role_ids = "RoleIDs must not be equal: '{role}'!"
    cycle_detected = "Desired hierarchy would create a cycle!"
    unexpected_integrity = "Unexpected IntegrityError!"
