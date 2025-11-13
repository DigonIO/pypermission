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
    foreign_keys_pragma_not_set = (
        "Foreign keys pragma appears to not be set! Please use the 'set_sqlite_pragma' function"
        " on your SQLite engine before interacting with the database!"
    )
    frozen_attributes_cannot_be_modified = "Frozen attributes cannot be modified!"
