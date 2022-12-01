# RBAC Features (NIST)

## Flat RBAC

* assign user to role - `user-role` (many-to-many relation)
* assign permission to role - `permission-role` (many-to-many relation)
* users can simultaniously exercise permissions of multiple roles
* `user-role` review
  * list roles a specific user can take
  * list users that can take a specific role

## Hierarchical RBAC

* assign seniority relation between roles `role-role` (many-to-many relation)
* senior roles acquire permissions of their juniors
* extends `user-role` review with
  * list roles a specific user inherits by his assigned roles
  * list users a specific role
* possible implementation as
  * inheritance hierarchy - activation of a role implies activation of all junior roles
  * activation hierarchy - roles need to be activated for permissions to take effect,
    activation of several roles at the same time possible

### General Hierarchical RBAC

* directed acyclic graphs

### Restricted Hierarchical RBAC

* restricted to tree/inv. tree or similar

## Constrained RBAC

* Separation of duties (SOD)
* possible implementation as
  * static SOD (based on user-role assignment)
  * dynamic SOD (based on role activation)

### Static SOD (SSD)

* `role-role` (constrained many-to-many relation)
  * roles within a linear ordering cannot at the same time have a containment relationship
* Constrain conflicting roles
  * When trying to assign users to conflicting roles
  * When trying to add a contrain, that would currently be violated by either existing
    users or by an existing role ordering
  * Dynamically adding containment relationships might make management difficult on an existing structure. Possible Mitigations:
    * Warn when attempted assignment/addition introduces a conflict (ignore with `-f` flag),
      therefore allowing a structure to have active conflicts (with constraints unenforced)
    * If a structure with active conflicts is a valid state, conflict-review must be possible

## Symmetric RBAC

* `permission-role` review
  * list permission assigned to specific role (selectable between direct and indirect relations)
  * list roles assigned to specific permission  (selectable between direct and indirect relations)

## TODO

* remove permission_nodes directly assigned to users (not part of NIST RBAC)
* Flat permission nodes in RBAC example
* correct external link

## NOTE

* assign implies a matching revoke method
* convention shows the senior (more powerful) roles on top in diagram
* lattice-based access control (LBAC) - possible when introducing new Permission type?
  e.g. SuperPermission: requires `[BAN_USER, JOIN_INV, MSG_X]`
* unclear, if `user-role` review in flat RBAC and Hierarchical RBAC are 2 functions each
  or 2 for flat and 4 for hierarchical (probably 4)
* The Wildcard Feature is closely related to the customizable permissions in section 7.4
* SOD defined on permission base in NIST or only role based?
* can we maybe rm the session argument from the functions in SQLAlchemyAuthority and just
  run self._session_maker() to get a session? Or (if possible somehow) have a session in
  SQLAlchemyAuthority exist within context manager
* What NIST calls Users we call subjects
* wikipedia describes the `operation-permission` relation as a many-to-many relation

> The standard allows for deleting an edge, but states that implied edges will be retained; an operation that deletes an edge and all implied edges can also be defined
