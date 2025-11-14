---
description: "PyPermission - The python RBAC library. Comparison of PyPermission’s design and features with the ANSI RBAC standard, including noted deviations."
---

# Comparing PyPermission with ANSI RBAC

The RBAC standard published by ANSI/INCITs [^1] [^2] expands on the NIST RBAC model. While not adhering entirely to the standard, the feature set of the PyPermission implementation resembles the General Hierarchical RBAC model (including the suggested advanced review functions).

Note that other authors have identified significant problems with the ANSI standard[^3] [^4] [^5]. In "A formal validation of the RBAC ANSI 2012 standard using B"[^3] the authors suggest a number of corrections to the standard. The following comparison is based on the corrections instead of the original standard and we took the freedom to use `snake_case` notation for all functions defined in the standard.

The standard makes use of z-notation [^6] and defines entities in set notation. The overview below declares the ANSI methods signature using familiar python type annotation syntax. If there is no instance of an entity prior to a function call, we use the placeholder `Name` in the function signature. Further whenever the ANSI standard combines the `Object` and `Operation` in a function signature, we substitute this with the equivalent `Permission` type. Types and methods without correspondence in PyPermission are denoted with "_N/A_"

!!! warning

    PyPermission is not compliant with the Core RBAC ANSI standard, as we decided against implementing the session concept. While the original authors of the RBAC standard insist on the session concept, they nevertheless acknowledge the usefulness of a sessionless approach [^7]. We want to add that it is possible to emulate the session concept by creating temporary subjects and assigning them to subjects while the emulated session is active. The burden of managing such sessions is left to the user of PyPermission.

The ANSI standard additionally defines a Static Separation of Duty (SSD) Relationship as well as Dynamic Separation of Duties (DSD) Relations. These relationships are defined as a constraint to prevent certain roles from being assigned to the same Subject. As PyPermission does not support this feature, the tables below will skip all definitions and sections concerning Separation of Duty Relations.

!!! info

    The section numberings used below map 1:1 to the ANSI standard sections for simple cross-referencing.

## 5 RBAC Reference Model

### 5.1 Core RBAC

#### 5.1.1 Core RBAC specifications

| ANSI Entity set                                | PyPermission                                           |
| ---------------------------------------------- | ------------------------------------------------------ |
| `USERS`                                        | `Subject` as `str`                                     |
| `ROLES`                                        | `Role` as `str`                                        |
| `OBJS` (objects)                               | `Resource` as tuple of `ResourceType` and `ResourceID` |
| `OPS` (operations)                             | `Action` as `str`                                      |
| `PRMS = OPS x OBJS` (`Permission`)             | `rbac.models.Permission`                       |
| `PA ⊆ PERMS x ROLES`  (`PermissionAssignment`) | `rbac.models.Policy`                           |
| `UA ⊆ USERS x ROLES` (`UserAssignment`)        | `rbac.models.MemberORM`                        |
| `SESSIONS`                                     | _N/A_                                                  |
| `USER_SESSIONS ⊆ USERS x SESSIONS`             | _N/A_                                                  |
| `SESSION_ROLES ⊆ SESSION x ROLES`              | _N/A_                                                  |

| ANSI Method                                        | PyPermission            |
| -------------------------------------------------- | ----------------------- |
| `assigned_permissions(r: Role) -> set[Permission]` | `RBAC.role.permissions` |
| `assigned_users(r: Role) -> set[User]`             | `RBAC.role.subjects`    |
| `user_sessions(u: User) -> set[session]`           | _N/A_                   |
| `session_roles(s: Session) -> set[role]`           | _N/A_                   |
| `check_access(s: Session, p: Permission) -> bool`  | _N/A_                   |

!!! tip

    You should not need to use any of the `ORM` models yourself. The `rbac.RBAC` class provides a clean interface to all functionality managing database objects.

### 5.2 Hierarchical RBAC

#### 5.2.1 General Role Hierarchies

| ANSI Entity set                        | PyPermission                       |
| -------------------------------------- | ---------------------------------- |
| `RH ⊆ ROLES x ROLES` (`RoleHierarchy`) | `rbac.models.HierarchyORM` |

| ANSI Method                                          | PyPermission            |
| ---------------------------------------------------- | ----------------------- |
| `authorized_users(r: Role) -> set[User]`             | `RBAC.role.subjects`    |
| `authorized_permissions(r: Role) -> set[Permission]` | `RBAC.role.permissions` |

!!! note

    The ANSI standard "leads the reader to believe that the permissions of a role include the permissions inherited by the role, but this is not the case"[^3]. Instead the standard suggests to check the permissions based on the roles active in a session and the hierarchy determines, which roles a Subject can activate. As our implementation does not have a session concept, the inherited permissions are included by default when requesting the permissions of a role. We provide a `inherited` parameter to the `permissions` method to allow for the explicit exclusion of inherited permissions.

## 7 RBAC System and Administrative Functional Specification

### 7.1 Core RBAC

#### 7.1.1 Administrative core commands

| ANSI                                           | PyPermission                  |
| ---------------------------------------------- | ----------------------------- |
| `add_user(u: Name)`                            | `RBAC.subject.create`         |
| `delete_user(u: User)`                         | `RBAC.subject.delete`         |
| `add_role(r: Name)`                            | `RBAC.role.create`            |
| `delete_role(r: Role)`                         | `RBAC.role.delete`            |
| `assign_user(u: User, role: Role)`             | `RBAC.subject.assign_role`    |
| `deassign_user(u: User, role: Role)`           | `RBAC.subject.deassign_role`  |
| `grant_permission(p: Permission, role: Role)`  | `RBAC.role.grant_permission`  |
| `revoke_permission(p: Permission, role: Role)` | `RBAC.role.revoke_permission` |

#### 7.1.2 Supporting system functions

| ANSI Method                                       | PyPermission                        |
| ------------------------------------------------- | ----------------------------------- |
| `check_access(s: Session, p: Permission) -> bool` | `RBAC.subject.check_permission`🔧  |
|                                                   | `RBAC.subject.assert_permission`🔧 |
|                                                   | `RBAC.role.check_permission`🔧     |
|                                                   | `RBAC.role.assert_permission`🔧    |
| `create_session(u: User, s: Name)`                | _N/A_                               |
| `delete_session(u: User, s: Session)`             | _N/A_                               |
| `add_active_role(u: User, s: Session, r: Role)`   | _N/A_                               |
| `drop_active_role(u: User, s: Session, r: Role)`  | _N/A_                               |

#### 7.1.3 Review functions for Core RBAC

| ANSI Methods                           | PyPermission                      |
| -------------------------------------- | --------------------------------- |
| `assigned_users(r: Role) -> set[User]` | `RBAC.role.subjects` |
| `assigned_roles(r: USER) -> set[Role]` | `RBAC.subject.roles` |

#### 7.1.4 Advanced review functions

| ANSI Methods                                                         | PyPermission                       |
| -------------------------------------------------------------------- | ---------------------------------- |
| `role_permissions(r: Role) -> set[Permission]`⚠️                   | `RBAC.role.permissions`🔧         |
| `user_permissions(u: User) -> set[Permission]`⚠️                   | `RBAC.subject.permissions`🔧      |
| `session_roles(s: Session) -> set[Role]`                             | _N/A_                              |
| `session_permissions(s: Session) -> set[Permission]`                 | _N/A_                              |
| `role_operations_on_object(r: Role, o: Resource) -> set[Action]`⚠️ | `RBAC.role.actions_on_resource`    |
| `user_operations_on_object(u: User, o: Resource) -> set[Action]`⚠️ | `RBAC.subject.actions_on_resource` |

### 7.2 Hierarchical RBAC

#### 7.2.1 General Role Hierarchies

##### 7.2.1.1 Administrative Commands for General Role Hierarchies

| ANSI Methods                                 | NOTE                                      | PyPermission                 |
| -------------------------------------------- | ----------------------------------------- | ---------------------------- |
| `add_inheritance(asc: Role, desc: Role)`⚠️ |                                           | `RBAC.role.add_hierarchy`    |
| `delete_inheritance(asc: Role, desc: Role)`  |                                           | `RBAC.role.remove_hierarchy` |
| `add_ascendant(asc: Name, desc: Role)`       | creates asc Role and its relation to desc |                              |
| `add_descendant(asc: Role, desc: Name)`      | creates desc Role and its relation to asc |                              |

##### 7.2.1.2 Supporting System Functions for General Role Hierarchies

| ANSI Methods                                    | PyPermission |
| ----------------------------------------------- | ------------ |
| `create_session(u: User, s: Name)`              | _N/A_        |
| `add_active_role(u: User, s: Session, r: Role)` | _N/A_        |

##### 7.2.1.3 Review Functions for General Role Hierarchies

| ANSI Methods                             | PyPermission         |
| ---------------------------------------- | -------------------- |
| `authorized_users(r: Role) -> set[User]` | `RBAC.role.subjects` |
| `authorized_roles(u: User) -> set[Role]` | `RBAC.subject.roles` |

##### 7.2.1.4 Advanced Review Functions for General Role Hierarchies

| ANSI Methods                                                         | PyPermission                       |
| -------------------------------------------------------------------- | ---------------------------------- |
| `role_permissions(r: Role) -> set[Permission]`⚠️                   | `RBAC.role.permissions`🔧         |
| `user_permissions(u: User) -> set[Permission]`⚠️                   | `RBAC.subject.permissions`🔧      |
| `role_operations_on_object(r: Role, o: Resource) -> set[Action]`⚠️ | `RBAC.role.actions_on_resource`    |
| `user_operations_on_object(u: User, o: Resource) -> set[Action]`⚠️ | `RBAC.subject.actions_on_resource` |

#### 7.2.2.1 Administrative Commands for Limited Role Hierarchies

| ANSI Methods                                 | PyPermission                 |
| -------------------------------------------- | ---------------------------- |
| `add_inheritance(asc: Role, desc: Role)`⚠️ | `RBAC.role.add_hierarchy`🔧 |

---

* The `⚠️` symbol indicates, that the method is not uniquely defined in the standard
* The `🔧` symbol indicates, that implementation of PyPermission is roughly based on the standard and differs in some aspects.

[^1]: INCITS 359-2004: Information technology - Role Based Access Control - <https://profsandhu.com/journals/tissec/ANSI+INCITS+359-2004.pdf>
[^2]: INCITS 359-2012[R2017]: Information technology - Role Based Access Control - <https://standards.incits.org/apps/group_public/project/details.php?project_id=1906>
[^3]: A formal validation of the RBAC ANSI 2012 standard using B - <https://doi.org/10.1016/j.scico.2016.04.011>
[^4]: B specification of the INCITS 359-2012 standard - <https://info.usherbrooke.ca/mfrappier/RBAC-in-B/>
[^5]: Validating the RBAC ANSI 2012 Standard Using B - <https://doi.org/10.1007/978-3-662-43652-3_22>
[^6]: [Wiki: Z-notation](https://en.wikipedia.org/wiki/Z_notation)
[^7]: [RBAC Standard Rationale: comments on a Critique of the ANSI Standard on Role-Based Access Control](https://doi.org/10.1109%2FMSP.2007.173)