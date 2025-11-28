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
#### Testing only:
################################################################################


class ERR_MSG_CONFLICT:
    role_exists = "Conflict: Role with ID '{role}' already exists!"
    subject_exists = "Conflict: Subject with ID '{subject}' already exists!"
    hierarchy_exists = (
        "Conflict: Role Hierarchy '{parent_role}' -> '{child_role}' exists!"
    )
    policy_exists = "Conflict: Policy '{policy_str}' already exists!"
    cycle_detected = "Conflict: Desired Role Hierarchy would create a cycle!"
    role_ids = (
        "Conflict: A Role Hierarchy requires distinct RoleIDs, received '{role}' twice!"
    )
    role_assigned_to_subject = "Conflict: Role with ID '{role}' already assigned to Subject with ID '{subject}'!"


class ERR_STR_EMPTY:
    subject = "`subject` cannot be empty!"
    role = "`role` cannot be empty!"
    parent_role = "`parent_role` cannot be empty!"
    child_role = "`child_role` cannot be empty!"
    resource_type = "`resource_type` cannot be empty!"
    action = "`action` cannot be empty!"


class ERR_STR_WHITESPACE:
    subject = "`subject` cannot have leading or trailing spaces!"
    role = "`role` cannot have leading or trailing spaces!"
    parent_role = "`parent_role` cannot have leading or trailing spaces!"
    child_role = "`child_role` cannot have leading or trailing spaces!"
    resource_type = "`resource_type` cannot have leading or trailing spaces!"
    action = "`action` cannot have leading or trailing spaces!"


class ERR_MSG:
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
    non_existent_policy = "Policy '{policy_str}' does not exist!"

    # permission_not_granted
    permission_not_granted_for_role = (
        "Permission '{permission_str}' is not granted for Role '{role}'!"
    )
    permission_not_granted_for_subject = (
        "Permission '{permission_str}' is not granted for Subject '{subject}'!"
    )

    # other
    unexpected_integrity = "Unexpected IntegrityError!"
    foreign_keys_pragma_not_set = (
        "Foreign keys pragma appears to not be set! Please use the 'set_sqlite_pragma' function"
        " on your SQLite engine before interacting with the database!"
    )
    frozen_attributes_cannot_be_modified = "Frozen attributes cannot be modified!"
