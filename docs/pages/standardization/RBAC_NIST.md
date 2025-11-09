# RBAC (NIST)

The original NIST RBAC model[^1] defines 4 feature levels and distinguishes level
2, 3 and 4 further depending on the support for either a) arbitrary or b) limited
hierarchies.

.. note::
   * assign implies a matching revoke method
   * convention shows the senior (more powerful) roles on top in diagram
   * unclear, if `user-role` review in flat RBAC and Hierarchical RBAC are 2 functions each or 2 for flat and 4 for hierarchical (probably 4)
   * Our Wildcard Feature is closely related to the customizable permissions in section 7.4
   * What NIST calls Users we call subjects
   * The standard writes:
      | The standard allows for deleting an edge, but states that implied edges will be retained; an operation that deletes an edge and all implied edges can also be defined

     We disagree with this notion - implied edges will be removed

## L.1 Flat RBAC

* assign user to role - `user-role` (many-to-many relation)
* assign permission to role - `permission-role` (many-to-many relation)
* users can simultaneously exercise permissions of multiple roles
* `user-role` review
  * list roles a specific user can take
  * list users that can take a specific role

## L.2 Hierarchical RBAC

* assign seniority relation between roles `role-role` (many-to-many relation)
* senior roles acquire permissions of their juniors
* extends `user-role` review with
  * list roles a specific user inherits by his assigned roles
  * list users a specific role
* possible implementation as
  * inheritance hierarchy - activation of a role implies activation of all junior roles
  * activation hierarchy - roles need to be activated for permissions to take effect,
    activation of several roles at the same time possible

### L.2a General Hierarchical RBAC

* directed acyclic graphs

### L.2b Restricted Hierarchical RBAC

* restricted to tree/inv. tree or similar

## L.3 Constrained RBAC

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

## L.4 Symmetric RBAC

* `permission-role` review
  * list permission assigned to specific role (selectable between direct and indirect relations)
  * list roles assigned to specific permission  (selectable between direct and indirect relations)

---

[^1]: The NIST model for role-based access control: towards a unified standard - <https://doi.org/10.1145/344287.344301>
