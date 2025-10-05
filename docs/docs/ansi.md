# Comparison to ANSI

## 6.1 Core RBAC

### 6.1.1 Administrative core commands

| ANSI             | This library                 |
| ---------------- | ---------------------------- |
| AddUser          | `RBAC.subject.create`        |
| DeleteUser       | `RBAC.subject.delete`        |
|                  | `RBAC.subject.list`          |
| AddRole          | `RBAC.role.create`           |
| DeleteRole       | `RBAC.role.delete`           |
|                  | `RBAC.role.list`             |
| AssignUser       | `RBAC.subject.assign_role`   |
| DeassignUser     | `RBAC.subject.deassign_role` |
| GrantPermission  | `RBAC.policy.create`         |
| RevokePermission | `RBAC.policy.delete`         |

### 6.1.2 Supporting system functions

| ANSI           | This library |
| -------------- | ------------ |
| CreateSession  |              |
| DeleteSession  |              |
| AddActiveRole  |              |
| DropActiveRole |              |

| ANSI        | This library                     |
| ----------- | -------------------------------- |
| CheckAccess |                                  |
|             | `RBAC.subject.check_permission`  |
|             | `RBAC.subject.assert_permission` |
|             | `RBAC.role.check_permission`     |
|             | `RBAC.role.assert_permission`    |

### 6.1.3 Review functions

| RBAC (ANSI)   | ours                          |
| ------------- | ----------------------------- |
| AssignedUsers | TODO                          |
| AssignedRoles | `RBAC.subject.assigned_roles` |
|               | `RBAC.role.parents`           |
|               | `RBAC.role.children`          |

### 6.1.4 Advanced review functions

| ANSI               | This library |
| ------------------ | ------------ |
| SessionRoles       |              |
| SessionPermissions |              |

| RBAC (ANSI)                 | This library           |
| --------------------------- | ---------------------- |
| RolePermissions             | TODO                   |
| RolePermissions             | TODO                   |
|                             | `RBAC.subject.polices` |
|                             | TODO                   |
| RoleOperationsOnObject (x1) | TODO                   |
| UserOperationsOnObject (x2) | TODO                   |
