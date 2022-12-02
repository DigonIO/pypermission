# RBAC (ANSI)

The RBAC standard published by ANSI/INCITs[^1][^2] expands on the NIST RBAC model.
Note that Other authors have identified numerous problems with the ANSI standard[^3][^4][^5],
some of the noted problems have been mitigated below according to the problem descriptions.
The PyPermission library does not conform to the ANSI standard, as conformance to the
standard requires at least the core feature set (6.1).

Below follows an overview of the RBAC INCITS 359-2012 standard as well as the differences in naming
and behaviour compared to the PyPermission library.

.. warning::

   * `role_get_permissions` and `subject_get_permissions` don't return a set of permissions, like the `RolePermissions` and `UserPermissions` functions, but a NodeMap (`dict[PermissionNode, set[str]]`)
   * `RoleOperationsOnObject` and `UserOperationsOnObject` are left open in the standard concerning their behaviour (direct relation/inherited relation/active role).
   * `authorized_users` depends on the role-hierarchy, whereas `role_get_subjects` does not

Definitions Core RBAC:

* `USERS`
* `ROLES`
* `SESSIONS`
* `OPS` (operations, aka. `Actions`)
* `OBJS` (objects, aka. `Ressources`)
* `PRMS`          (OPS * OBJS)       many-to-many relation
* `UA`            (USERS * ROLES)    many-to-many relation
* `PA`            (USERS * ROLES)    many-to-many relation
* `USER_SESSIONS` (USERS * SESSIONS) one-to-many relation
* `SESSION_ROLES` (SESSION * ROLES)  many-to-many relation
* `user_sessions(user: USERS) -> 2^SESSIONS`
* `assigned_permissions(r: ROLES) -> 2^PRMS`
* `session_roles(s: SESSIONS) -> 2^ROLES`
* `assigned_users(r: ROLES) -> 2^USERS`
* `CheckAccess(s: SESSIONS, p: PRMS) -> bool`

Definitions Hierarchical RBAC:

* `RH` (ROLES X ROLES) many-to-many relation
* `authorized_users(r: ROLES) -> 2^USERS`
* `authorized_permissions(r: ROLES) -> 2^PRMS`

## 6.1 Core RBAC

### 6.1.1 administrative core commands

| RBAC (ANSI)      | ours                   |
| ---------------- | ---------------------- |
| AddUser          | add_subject            |
| DeleteUser       | del_subject            |
| AddRole          | add_role               |
| DeleteRole       | del_role               |
| AssignUser       | role_assign_subject    |
| DeassignUser     | role_deassign_subject  |
| GrantPermission  | role_grant_permission  |
| RevokePermission | role_revoke_permission |

### 6.1.2 supporting system functions

| RBAC (ANSI)      | ours                                       |
| ---------------- | ------------------------------------------ |
| CreateSession    | N/A                                        |
| DeleteSession    | N/A                                        |
| AddActiveRole    | N/A                                        |
| DropActiveRole   | N/A                                        |

We do not have a 1:1 analog of `CheckAccess`, as `CheckAccess` does not look at the hierarchy.

| RBAC (ANSI)                  | ours                             |
| ---------------------------- | -------------------------------- |
| CheckAccess                  | role/subject_inherits_permission |
| ^ does not check hierarchy ^ | ^ checks hierarchy             ^ |

NOTE:

`CheckAccess` does not check the role hierarchy, it only returns true if one of the active roles has direct access to a given permission. This behaviour is less useful without a session concept. Our implementation checks the hierarchy.

### 6.1.3 review functions

| RBAC (ANSI)      | ours              |
| ---------------- | ----------------- |
| AssignedUsers    | role_get_subjects |
| AssignedRoles    | subject_get_roles |

### 6.1.4 advanced review functions

| RBAC (ANSI)                 | ours                         |
| --------------------------- | ---------------------------- |
| RolePermissions             | role_get_permissions (x2)    |
| UserPermissions             | subject_get_permissions (x2) |
| SessionRoles                | N/A                          |
| SessionPermissions          | N/A                          |
| RoleOperationsOnObject (x1) | N/A                          |
| UserOperationsOnObject (x2) | N/A                          |

* `(xN)` identifies the number `N` of possible implementations the standard allows

## 6.2 Hierarchical RBAC

### 6.2.1 General Role Hierarchies

#### 6.2.1.1 Administrative Commands for General Role Hierarchies

| RBAC (ANSI)            | ours                 |
| ---------------------- | -------------------- |
| AddInheritance         | role_add_inheritance |
| DeleteInheritance      | role_del_inheritance |
| AddAscentant           | N/A                  |
| AddDescendant          | N/A                  |

AddInheritance(r_asc, r_desc) asc_rid, desc_rid

#### 6.2.1.2 Supporting System Functions for General Role Hierarchies

| RBAC (ANSI)            | ours             |
| ---------------------- | ---------------- |
| CreateSession          | N/A              |
| AddActiveRole          | N/A              |

#### 6.2.1.3 Review Functions for General Role Hierarchies

| RBAC (ANSI)               | ours              |
| ------------------------- | ----------------- |
| AuthorizedUsers           | N/A               |
| AuthorizedRoles           | N/A               |
| ^ these check hierarchy ^ | \                 |

`AuthorizedPermissions` is not defined here, but implied in section 5.2 (should probably be skipped in guide, as it is confusing with the behaviour of `CheckAccess`, which does not check with respect to hierarchy):

| RBAC (ANSI)               | ours                      |
| ------------------------- | ------------------------- |
| AuthorizedPermissions     | role_inherits_permission  |
| ^ these check hierarchy ^ | ^ these check hierarchy ^ |

#### 6.2.1.4 Advanced Review Functions for General Role Hierarchies

| RBAC (ANSI)                 | ours                         |
| --------------------------- | ---------------------------- |
| RolePermissions             | role_get_permissions (x2)    |
| UserPermissions             | subject_get_permissions (x2) |
| RoleOperationsOnObject (x2) | N/A                          |
| UserOperationsOnObject (x3) | N/A                          |

* `(xN)` identifies the number `N` of possible implementations the standard allows
* `role_get_permissions` and `subject_get_permissions` currently ignore inherited permissions,
  implementation needs to be changed

### 6.2.2 Limited Role Hierarchies

Same as in *General Role Hierarchies* (6.2.1) except for redefinition of `AddInheritance`

## 6.3 Static Separation of Duty (SSD) Relations

### 6.3.1 Core RBAC

#### 6.3.1.1 Administrative commands for SSD Relations

Redefines `AssignUser`

| RBAC (ANSI)            | ours             |
| ---------------------- | ---------------- |
| CreateSsdSet           | N/A              |
| AddSsdRoleMember       | N/A              |
| DeleteSsdRoleMember    | N/A              |
| DeleteSsdSet           | N/A              |
| SetSsdSetCardinality   | N/A              |

#### 6.3.1.2 Supporting System Functions for SSD

Same as in 6.1.2

#### 6.3.1.3 Review Functions for SSD

Same as in 6.1.3 with the following additions:

| RBAC (ANSI)            | ours             |
| ---------------------- | ---------------- |
| SsdRoleSets            | N/A              |
| SsdRoleSetRoles        | N/A              |
| SsdRoleSetCardinality  | N/A              |

#### 6.3.1.4 Advanced Review Functions for SSD

Same as in 6.1.4

### 6.3.2 SSD with General Role Hierarchies

Same as in 6.2.1 and 6.3.1, except for some redefinitions of functions in 6.2.1.1 and 6.3.1.1

#### 6.3.2.1 Administrative Commands for SSD with General Role Hierarchies

Redefines `AssignUser`, `AddInheritance`, `CreateSsdSet`, `AddSsdRoleMember`, `SetSsdSetCardinality`

### 6.3.3 SSD Relations with Limited Role Hierarchies

Same as in 6.3.2, except for redefinition of `AddInheritance`

## 6.4 Dynamic Separation of Duties (DSD) Relations

### 6.4.1 Core RBAC

#### 6.4.1.1 Administrative Commands for DSD Relations

Same as in 6.1.1 with the following additions:

| RBAC (ANSI)            | ours             |
| ---------------------- | ---------------- |
| CreateDsdSet           | N/A              |
| AddDsdRoleMember       | N/A              |
| DeleteDsdRoleMember    | N/A              |
| DeleteDsdSet           | N/A              |
| SetDsdSetCardinality   | N/A              |

#### 6.4.1.2 Supporting System Functions for DSD Relations

Same as in 6.1.2, except for redefinitions of `CreateSession` and `AddActiveRole`

#### 6.4.1.3 Review Functions for DSD Releations

Same as in 6.1.3 with the following additions:

| RBAC (ANSI)            | ours             |
| ---------------------- | ---------------- |
| DsdRoleSets            | N/A              |
| DsdRoleSetRoles        | N/A              |
| DsdRoleSetCardinality  | N/A              |

#### 6.4.1.4 Advanced Review Functions for DSD Releations

Same as in 6.1.4

### 6.4.2 DSD Relations with General Role Hierarchies

Same as in 6.2.1 and 6.4.1, except for redefinitions of `CreateSession` and `AddActiveRole`

### 6.4.3 DSD Relations with Limited Role Hierarchies

Same as 6.2.2 (Limited Role Hierarchies), 6.4.1.1 (Administrative Commands for DSD Relations), 6.4.2 (DSD Relations with General Role Hierarchies), 6.2.1.4 (Advanced Review Functions for General Role Hierarchies)

---

[^1]: INCITS 359-2004: Information technology - Role Based Access Control - <https://profsandhu.com/journals/tissec/ANSI+INCITS+359-2004.pdf>
[^2]: INCITS 359-2012[R2017]: Information technology - Role Based Access Control - <https://standards.incits.org/apps/group_public/project/details.php?project_id=1906>
[^3]: A formal validation of the RBAC ANSI 2012 standard using B - <https://doi.org/10.1016/j.scico.2016.04.011>
[^4]: B specification of the INCITS 359-2012 standard - <https://info.usherbrooke.ca/mfrappier/RBAC-in-B/>
[^5]: Validating the RBAC ANSI 2012 Standard Using B - <https://doi.org/10.1007/978-3-662-43652-3_22>