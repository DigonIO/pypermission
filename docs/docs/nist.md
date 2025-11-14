---
description: "PyPermission - The python RBAC library. Technical mapping of PyPermission to NIST RBAC levels, explaining hierarchy handling and design differences."
---


# Comparing PyPermission with NIST

The original NIST RBAC model[^1] defines 4 feature levels and distinguishes level
2, 3 and 4 further depending on the support for either a) arbitrary or b) limited
hierarchies. Level L.2a is closest to our implementation.

!!! warning

    PyPermission is not compliant with the RBAC NIST standard, as we decided against implementing the session concept.

The section numberings used below map 1:1 to the NIST standard sections for simple cross-referencing.

!!! warning

    This page is currently incomplete.

The NIST standard additionally defines a Static Separation of Duty (SSD) Relationship as well as Dynamic Separation of Duties (DSD) Relations. These relationships are defined as a constraint to prevent certain roles from being assigned to the same Subject.

## RBAC NIST Reference Model

!!! note "Conventions in the NIST Standard"

    * assign implies a matching revoke method
    * The senior (more powerful) roles are placed on top in diagrams

!!! note "Work in progress"

    * Our Wildcard Feature is closely related to the customizable permissions in section 7.4
    * TODO: check if `user-role` review in flat RBAC and Hierarchical RBAC are 2 functions each or 2 for flat and 4 for hierarchical (probably 4)

### L.1 Flat RBAC

* assign user to role - `user-role` (many-to-many relation)
* assign permission to role - `permission-role` (many-to-many relation)
* users can simultaneously exercise permissions of multiple roles
* `user-role` review
    * list roles a specific user can take
    * list users that can take a specific role

### L.2 Hierarchical RBAC

* assign seniority relation between roles `role-role` (many-to-many relation)
* senior roles acquire permissions of their juniors
* extends `user-role` review with
    * list roles a specific user inherits by his assigned roles
    * list users a specific role
* possible implementation as
    * inheritance hierarchy - activation of a role implies activation of all junior roles
    * activation hierarchy - roles need to be activated for permissions to take effect,
    activation of several roles at the same time possible

#### L.2a General Hierarchical RBAC

General Hierarchical RBAC as defined in the NIST Standard permits role hierarchies, as long as the defining graph is directed and acyclic.

A visual comparison between the NIST RBAC model and our database tables shows a close resemblance:

![NIST Hierarchical RBAC model](./assets/NIST_hierarchical_RBAC.png)

NIST Hierarchical RBAC model[^1]

![PyPermission database model](./assets/RBAC_python.png)

PyPermission database model

#### L.2b Restricted Hierarchical RBAC

* restricted to tree/inv. tree or similar

### L.3 Constrained RBAC

* Separation of duties (SOD)
* possible implementation as
    * static SOD (based on user-role assignment)
    * dynamic SOD (based on role activation)

#### Static SOD (SSD)

* `role-role` (constrained many-to-many relation)
    * roles within a linear ordering cannot at the same time have a containment relationship
* Constrain conflicting roles
    * When trying to assign users to conflicting roles
    * When trying to add a constrain, that would currently be violated by either existing
    users or by an existing role ordering
    * Dynamically adding containment relationships might make management difficult on an existing structure. Possible Mitigations:
        * Warn when attempted assignment/addition introduces a conflict (ignore with `-f` flag),
      therefore allowing a structure to have active conflicts (with constraints unenforced)
        * If a structure with active conflicts is a valid state, conflict-review must be possible

### L.4 Symmetric RBAC

* `permission-role` review
    * list permission assigned to specific role (selectable between direct and indirect relations)
    * list roles assigned to specific permission  (selectable between direct and indirect relations)
        * What NIST calls Users we call Subjects

---

[^1]: The NIST model for role-based access control: towards a unified standard - <https://doi.org/10.1145/344287.344301>
