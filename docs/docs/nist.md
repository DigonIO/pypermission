---
description: "PyPermission - The python RBAC library. Technical mapping of PyPermission to NIST RBAC levels, explaining hierarchy handling and design differences."
---


# Comparing PyPermission with the NIST RBAC model

The **PyPermission** library implements a feature set that closely resembles the **General Hierarchical RBAC** model (Level 2a) described in the **NIST RBAC** model[^1]. Additionally, it implements specific review functions defined in **Symmetric RBAC** (Level 4).

The following comparison maps the functionality of `pypermission` against the four levels of the NIST reference model. The section numberings used below map 1:1 to the NIST standard sections for simple cross-referencing.

## 3 Flat RBAC (Level 1)

Flat RBAC requires the fundamental ability to assign **Subjects** (Users) to **Roles**, and **Permissions** to **Roles** in a many-to-many relationship. It also mandates specific review capabilities.

| NIST Requirement                             | PyPermission Implementation                                  |
| :------------------------------------------- | :----------------------------------------------------------- |
| **User - Role Assignment**                   | `pypermission.RBAC.subject.assign_role`                      |
| **User - Role Revokation**                   | `pypermission.RBAC.subject.deassign_role`                    |
| **Permission to Role Assignment**            | `pypermission.RBAC.role.grant_permission`                    |
| **Permission Revokation**                    | `pypermission.RBAC.role.revoke_permission`                   |
| **Simultaneous Role Activation**             | Supported (Session-less design implies all roles are active) |
| **User-Role Review** (List roles for a user) | `pypermission.RBAC.subject.roles`                            |
| **Role-User Review** (List users for a role) | `pypermission.RBAC.role.subjects`                            |

In this context, **PyPermission** maps NIST entities as follows:

+ `User` $\rightarrow$ **Subject**
+ `Operation` $\rightarrow$ **Action**
+ `Object` $\rightarrow$ **Resource**
+ `Operation` + `Object` $\rightarrow$ **Permission**
+ `Role` + `Operation` + `Object` $\rightarrow$ **Policy**

## 4 Hierarchical RBAC (Level 2)

Level 2 introduces **Role** hierarchies, where senior **Roles** inherit **Permissions** from junior **Roles**. The standard distinguishes between **General** (arbitrary partial order, where diamonds are possible) and **Limited** (tree/inverted tree) hierarchies. **PyPermission** supports **General Hierarchical RBAC (Level 2a)**, allowing for arbitrary Directed Acyclic Graphs (DAGs).

The standard further offers two interpretations of the role hierarchy, of which **PyPermission** subscribes to the _permission-inheritance_ interpretation, where the **Role** hierarchy is called an _inheritance hierarchy_. Here a senior **Role** automatically has all **Permissions** of its junior **Roles** available for use. The _activation interpretation_ is the alternative interpretation, requires a **Session** concept and is demanded by the ANSI RBAC standard. Here junior roles have to be explicitly activated for a **Session** in order to gain inherited **Permissions** during a **Session**. This behaviour can be emulated when using **PyPermission**, but we leave the burden of **Session** management to the user of this library.

!!! warning

    Hierarchical RBAC comes with a semantic for the inferred **Permissions** that is not inherently obvious when compared to everyday language. In NIST, a **Role** inherits **Permissions** of the **Roles** it is senior of, while in **PyPermission** a child **Role** has access to at least all the **Permissions** it inherits from its parent **Roles**. This is why we suggest designing **RBAC** systems using a **Roles** composition first approach. If you choose to utilize hierarchical **RBAC** make sure to check out the available auditing and review functions we support.

In this context, **PyPermission** maps NIST entities as follows:

+ `Senior` $\rightarrow$ **Child** (a direct descendant, more powerful **Role** than the corresponding **Parent**)
+ `Junior` $\rightarrow$ **Parent** (a direct ascendant)

| NIST Requirement                           | PyPermission Implementation                                           |
| :----------------------------------------- | :-------------------------------------------------------------------- |
| **Add Hierarchy** (Senior/Junior relation) | `pypermission.RBAC.role.add_hierarchy`                                |
| **Delete Hierarchy**                       | `pypermission.RBAC.role.remove_hierarchy`                             |
| **Inheritance Calculation**                | Handled automatically in `pypermission.RBAC.subject.check_permission` |

A visual comparison between the **NIST RBAC** model and our database tables shows the close architectural resemblance:

![NIST Hierarchical RBAC model](./assets/NIST_hierarchical_RBAC.png)
_NIST Hierarchical RBAC model[^1]_

![PyPermission database model](./assets/RBAC_python.png)
_PyPermission database model_

## 5 Constrained RBAC (Level 3)

Level 3 requires the enforcement of Separation of Duties (SOD), either statically (SSD) or dynamically (DSD). These relationships are defined as a constraint to prevent conflicting **Roles** from being assigned to the same **Subject**.

| NIST Requirement | PyPermission Implementation |
| :--- | :--- |
| **Static Separation of Duty** | _N/A_ |
| **Dynamic Separation of Duty** | _N/A_ |

!!! info

    **PyPermission** does not currently implement Separation of Duty constraints.

## 6 Symmetric RBAC (Level 4)

Symmetric RBAC adds requirements for **Permission**-**Role** review, ensuring administrators can determine which **Permissions** belong to a specific **Role**.

| NIST Requirement           | PyPermission Implementation                                           |
| :------------------------- | :-------------------------------------------------------------------- |
| **Permission-Role Review** | `pypermission.RBAC.role.permissions` (only role to permission lookup) |

## 7 Other RBAC Attributes

The NIST standard discusses several attributes that are not part of the core model but are relevant for implementation.

### 7.4 Nature of Permissions

The NIST standard leaves the definition of **Permissions** open. **PyPermission** defines a **Permission** as a structured tuple of `resource_type`, `resource_id`, and `action`. We decided for splitting up the **Resource** in particular into its constituent `resource_type` and `resource_id`, because it makes container **Permissions** (as described in the [Permission Design Guide](./permission_design_guide.md)) simple to implement. The `resource_id` further accepts `resource_id="*"` as a simple wildcard argument, matching all resources of the given `resource_type`. The **Permission** `event[*]:view` then represents access to all resources of type `event`.

### 7.9 **Role** Revocation

The standard discusses the immediacy of revocation. In **PyPermission**, revocation via `pypermission.RBAC.role.revoke_permission` or `pypermission.RBAC.subject.deassign_role` is immediate. Since there are no long-lived sessions caching **Permissions** in the library itself, the next `check_permission` call reflects the updated state immediately.

[^1]: The NIST model for role-based access control: towards a unified standard - <https://doi.org/10.1145/344287.344301>
