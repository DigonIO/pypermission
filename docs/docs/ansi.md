# Comparison to ANSI

The RBAC standard published by ANSI/INCITs[^1][^2] expands on the NIST RBAC model.
Note that Other authors have identified numerous problems with the ANSI standard[^3][^4][^5],
some of the noted problems have been mitigated below according to the problem descriptions.
The PyPermission library does not conform to the ANSI standard, as conformance to the
standard requires at least the core feature set (6.1) and this library does not implement the ANSI session concept.

Below follows an overview of the _RBAC INCITS 359-2012_ standard, where we modified parts of the notation for consistency as well as correctness[^3] reasons (the original notation can be referenced quickly via the section references). Where applicable we provide the equivalent implementation resource of the PyPermission library.

## 5 RBAC Reference Model

### 5.1 Definitions Core RBAC

| ANSI Types                                       | This library                     |
| ------------------------------------------------ | -------------------------------- |
| `USERS`                                          | `Subject` as `str`               |
| `ROLES`                                          | `Role` as `str`                  |
| `OBJS`                                           | `Resource` as `str`              |
| `OPS`                                            | `Action` as `str`                |
| `PRMS: OPS x OBJS` aka. `Permissions`            | `pypermission.models.Permission` |
| `UA: USERS x ROLES` aka. `UserAssignment`        | `pypermission.models.MemberORM`  |
| `PA: PERMS x ROLES`  aka. `PermissionAssignment` | `pypermission.models.Policy`     |
| `SESSIONS`                                       | _N/A_                            |
| `USER_SESSIONS: USERS x SESSIONS`                | _N/A_                            |
| `SESSION_ROLES: SESSION x ROLES`                 | _N/A_                            |

!!! note

    As this library currently does not implement the RBAC session concept, the types `SESSIONS`, `USER_SESSIONS` and `SESSION_ROLES` from the ANSI standard have no equivalent!

| ANSI Methods                                 | This library                         |
| -------------------------------------------- | ------------------------------------ |
| `user_sessions(user: USERS) -> 2^SESSIONS`   | _N/A_                                |
| `assigned_permissions(r: ROLES) -> 2^PRMS`   | `pypermission.RBAC.role.permissions` |
| `session_roles(s: SESSIONS) -> 2^ROLES`      | _N/A_                                |
| `assigned_users(r: ROLES) -> 2^USERS`        | `pypermission.RBAC.role.subjects`    |
| `check_access(s: SESSIONS, p: PRMS) -> bool` | _N/A_                                |

### 5.2 Hierarchical RBAC

| ANSI Types                               | This library                       |
| ---------------------------------------- | ---------------------------------- |
| `RH: ROLES x ROLES` aka. `RoleHierarchy` | `pypermission.models.HierarchyORM` |

| ANSI Methods                                 | This library                         |
| -------------------------------------------- | ------------------------------------ |
| `authorized_users(r: ROLES) -> 2^USERS`      | `TODO`                               |
| `authorized_permissions(r: ROLES) -> 2^PRMS` | `pypermission.RBAC.role.permissions` |


## 6 RBAC System and Administrative Functional Specification

### 6.1 Core RBAC

#### 6.1.1 Administrative core commands

| ANSI               | This library                               |
| ------------------ | ------------------------------------------ |
| `AddUser()`        | `pypermission.RBAC.subject.create`         |
| `DeleteUser()`     | `pypermission.RBAC.subject.delete`         |
|                    | `pypermission.RBAC.subject.list`           |
| `AddRole`          | `pypermission.RBAC.role.create`            |
| `DeleteRole`       | `pypermission.RBAC.role.delete`            |
|                    | `pypermission.RBAC.role.list`              |
| `AssignUser`       | `pypermission.RBAC.subject.assign_role`    |
| `DeassignUser`     | `pypermission.RBAC.subject.deassign_role`  |
| `GrantPermission`  | `pypermission.RBAC.role.grant_permission`  |
| `RevokePermission` | `pypermission.RBAC.role.revoke_permission` |

#### 6.1.2 Supporting system functions

| ANSI                                        | This library                     |
| ------------------------------------------- | -------------------------------- |
| `CheckAccess(s: SESSIONS, p: PRMS) -> bool` |                                  |
|                                             | `RBAC.subject.check_permission`  |
|                                             | `RBAC.subject.assert_permission` |
|                                             | `RBAC.role.check_permission`     |
|                                             | `RBAC.role.assert_permission`    |

!!! note

    As this library currently does not implement the RBAC session concept, the functions `CheckAccess`, `CreateSession`, `DeleteSession`, `AddActiveRole` and `DropActiveRole` from the ANSI standard have no equivalent!

#### 6.1.3 Review functions

| ANSI Methods                         | ours                              |
| ------------------------------------ | --------------------------------- |
| `AssignedUsers`                      | `pypermission.RBAC.role.subjects` |
| `assigned_roles(r: USER) -> 2^ROLES` | `pypermission.RBAC.subject.roles` |
|                                      | `pypermission.RBAC.role.parents`  |
|                                      | `pypermission.RBAC.role.children` |
|                                      | `pypermission.RBAC.role.children` |

#### 6.1.4 Advanced review functions

| RBAC (ANSI)                 | This library               |
| --------------------------- | -------------------------- |
| RolePermissions             | `RBAC.role.permissions`    |
| UserPermissions             | `RBAC.subject.permissions` |
|                             | `RBAC.role.polices`        |
|                             | `RBAC.subject.polices`     |
|                             | TODO                       |
| RoleOperationsOnObject (x1) | TODO                       |
| UserOperationsOnObject (x2) | TODO                       |

!!! note

    As this library currently does not implement the RBAC session concept, the functions `SessionRoles` and `SessionPermissions` from the ANSI standard have no equivalent!

---

[^1]: INCITS 359-2004: Information technology - Role Based Access Control - <https://profsandhu.com/journals/tissec/ANSI+INCITS+359-2004.pdf>
[^2]: INCITS 359-2012[R2017]: Information technology - Role Based Access Control - <https://standards.incits.org/apps/group_public/project/details.php?project_id=1906>
[^3]: A formal validation of the RBAC ANSI 2012 standard using B - <https://doi.org/10.1016/j.scico.2016.04.011>
[^4]: B specification of the INCITS 359-2012 standard - <https://info.usherbrooke.ca/mfrappier/RBAC-in-B/>
[^5]: Validating the RBAC ANSI 2012 Standard Using B - <https://doi.org/10.1007/978-3-662-43652-3_22>
