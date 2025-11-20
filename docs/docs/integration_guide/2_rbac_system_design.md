# 2. Integration Guide - RBAC System Design

The second part of the integration guide covers the RBAC system design of the MeetDown application. Its goal is to explain how **Roles** are designed, which **Permissions** are granted per **Role**, and explicitly which features these permissions apply to.

As described in the first part of the integration guide, the **Roles** are: `guest`, `user`, `moderator`, and `admin`.

The first important note is that the `admin` **Role** does not need to be handled inside the RBAC system itself. Instead, a field `is_admin` is added to the **User** table. This field can be used to quickly answer permission checks without actually consulting the RBAC system, since according to our guide, the `admin` **Role** is allowed to perform **any** action.

!!! info

    Some applications introduce a distinction between an `admin` and a `superuser` **Role**.
    In such cases, the `superuser` is stored as a flag on the **User** table, similar to what is described in this guide, and is technically allowed to perform all operations. However, this `superuser` is not intended for normal operational use.

    Additionally, an `admin` **Role** is then added to the RBAC system with fewer privileges than the `superuser`. This allows administrators to perform operational tasks, such as assigning moderators, without having the ability to break the entire application. The **Permissions** of the `admin` **Role** in this setup are checked just like those of any other **Roles**.

    If you are not building an enterprise-grade application, this distinction is usually unnecessary.

## **Policies**

A short refresher (for more detailed information, see the [Permission design guide](../permission_design_guide.md)):

+ "Instance **Permissions**" apply to a single, specific **Resource** instance (e.g. `EventID` `5`).
+ "Container **Permissions**" apply to all **Resources** within a container (e.g. all `Event`s inside a `Group`).

!!! note

    Instance **Permissions** must always be dynamically granted and revoked together with the corresponding Instances. An exception is an instance **Permission** that uses the wildcard `*`, since it directly represents all Instances at once.

### Static **Roles**

Static **Roles** are predefined during application initialization and assigned wildcard **Permissions** to define baseline access. For example, `guest` has `Group[*]:access` and `Event[*]:access` to view all `Group`s and `Event`s, while `user` **Role** adds `User[*]:access` to view all `User`s.

Moderators receive additional **Permissions** like `User[*]:edit` and `Group[*]:deactivate` to manage `User`s and `Group`s across all instances. These can be assigned directly to the **Role**.

#### **Permissions** of **Role** `guest`

| **Permissions**   | Description                             |
| ----------------- | --------------------------------------- |
| `Group[*]:access` | All `Group`s may be viewed.             |
| `Event[*]:access` | All `Event`s may be viewed.             |

#### **Permissions** of **Role** `user`

| **Permissions**   | Description                             |
| ----------------- | --------------------------------------- |
| `User[*]:access`  | All `User`s may be viewed.              |
| `Group[*]:access` | All `Group`s may be viewed.             |
| `Event[*]:access` | All `Event`s may be viewed.             |

#### **Permissions** of **Role** `moderator`

| **Permissions**       | Description                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `User:create`         | New `User`s may be created.                                                                           |
| `User[*]:access`      | All `User`s may be viewed.                                                                            |
| `User[*]:edit`        | All `User` emails may be edited (except for other `moderator` or `admin` **Members**).                |
| `User[*]:deactivate`  | All `User`s may be deactivated (except for other `moderator` or `admin` **Members**).                 |
| `Group[*]:access`     | All `Group`s may be viewed.                                                                           |
| `Group[*]:deactivate` | All `Group`s may be deactivated.                                                                      |
| `Event[*]:access`     | All `Event`s may be viewed.                                                                           |
| `Event[*]:deactivate` | All `Event`s may be deactivated.                                                                      |

### Dynamic **Roles**

#### **Permissions** of **Role** `User[<UserID>]`

When a new `User` is created in the application logic, a new **Role** `User[<UserID>]` must also be created. In the actual implementation of this example, the variable `<UserID>` is replaced by the `username` and links the `User` object to the `User[<UserID>]` **Role**. This **Role** is exclusive to this single `User` and allows them to use classic features such as managing their own profile. If the `User` is deleted, this exclusive **Role** is also deleted.

| **Permissions**       | Description                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `User[<UserID>]:edit`        | The email of the `User` with the `<UserID>` may be edited (except for other `moderator` or `admin` **Members**).                |
| `User[<UserID>]:deactivate`  | The `User` with the `<UserID>` may be deactivated (except for other `moderator` or `admin` **Members**).                 |



!!! tip

    For RBAC **Roles**, the same principle applies as in software design: composition over inheritance!

    Nevertheless, inheritance can still be useful, you just need to carefully consider when **Permissions** should be inherited and when they should not.
