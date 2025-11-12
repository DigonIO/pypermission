from typing import Never
from sqlalchemy.exc import IntegrityError
from sqlite3 import IntegrityError as Sqlite3IntegrityError
from pypermission.models import Permission

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


class PermissionNotGrantedError(PyPermissionError):
    """
    PermissionNotGrantedError will be thrown if an `assert_permission()` fails!

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
        case IntegrityError(orig=orig) if (
            str(orig.__class__) == "<class 'psycopg.errors.ForeignKeyViolation'>"
        ):
            if f"Key (role_id)=({role}) is not present in table" in str(orig):
                raise PyPermissionError(f"Role '{role}' does not exist!")
            if f"Key (subject_id)=({subject}) is not present in table" in str(orig):
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
            )
        case IntegrityError(
            orig=Sqlite3IntegrityError(sqlite_errorname="SQLITE_CONSTRAINT_FOREIGNKEY")
        ):
            raise PyPermissionError(f"Role '{role}' does not exist!")
        case IntegrityError(orig=orig) if (
            str(orig.__class__) == "<class 'psycopg.errors.UniqueViolation'>"
        ):
            raise PyPermissionError(
                f"Permission '{str(permission)}' does already exist!"
            )
        case IntegrityError(orig=orig) if (
            str(orig.__class__) == "<class 'psycopg.errors.ForeignKeyViolation'>"
        ):
            raise PyPermissionError(f"Role '{role}' does not exist!")
        case _:
            ...
    raise PyPermissionError("Unexpected IntegrityError")


################################################################################
#### Testing only:
################################################################################


class ERR_MSG:
    # conflict
    conflict_role_exists = "Role '{role}' already exists!"
    conflict_subject_exists = "Subject '{subject}' already exists!"
    conflict_hierarchy_exists = "Hierarchy '{parent_role}' -> '{child_role}' exists!"
    conflict_permission_exists = "Permission '{permission_str}' does already exist!"
    conflict_cycle_detected = "Desired hierarchy would create a cycle!"
    conflicting_role_ids = "RoleIDs must not be equal: '{role}'!"

    # empty string not allowed
    empty_subject = "Subject name cannot be empty!"
    empty_role = "Role name cannot be empty!"
    empty_parent_role = "Role name cannot be empty, but `parent_role` is empty!"
    empty_child_role = "Role name cannot be empty, but `child_role` is empty!"
    empty_resource_type = "Resource type cannot be empty!"
    empty_action = "Action cannot be empty!"

    # non_existent
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
    non_existent_permission = "Permission '{permission_str}' does not exist!"

    # permission_not_granted
    permission_not_granted_for_role = (
        "Permission '{permission_str}' is not granted for Role '{role}'!"
    )
    permission_not_granted_for_subject = (
        "Permission '{permission_str}' is not granted for Subject '{subject}'!"
    )

    # other
    unexpected_integrity = "Unexpected IntegrityError!"
