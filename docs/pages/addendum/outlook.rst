Outlook
=======

The following is open for future discussion:

* add flag to `subject_get_permissions` and `role_get_permissions` to switch
  between directly granted and inherited permissions (default to inherited)
* The ANSI/INCITS standard defines certain datasets and structures needed for the
  implementation, but not a lot of query functions for review (etc. get a list of
  existing users). We define a number of these and it would be nice to include them already
  in the introductory RBAC guide.
* The beginner guides should not show how permission nodes are assigned directly to
  a subject (complicates things and is not part of either NIST or INCITS standard).
* The beginner guides should not show our extension of the permission structure to trees,
  flat permission nodes should be enough for an introduction
* lattice-based access control (LBAC) emulation - possible when introducing new Permission type?
  e.g. a `SuperPermission` defined by a number of required permissions
  `[BAN_USER, JOIN_INV, MSG_X]`
* can we maybe remove the session argument from the functions in SQLAlchemyAuthority and just
  run self._session_maker() to get a session? Or (if possible somehow) have a session in
  SQLAlchemyAuthority exist within context manager
* wikipedia describes the `operation-permission` relation as a many-to-many relation,
  this library does not manage the operation to permission relation.
  Currently our intention is to use the permission check at the place where the operation is defined in the user's code. Users are free to implement their own abstraction. Pull requests are welcome