---
description: "PyPermission - The python RBAC library. Compare container vs. instance Permissions and learn how to structure authorization the right way."
---

# PyPermission - **Permission** Design Guide

This guide explores how to design **Permissions** in Role-Based Access Control (RBAC) systems, focusing on two primary approaches: Container **Permissions** and Instance **Permissions**. Each approach defines how **Permissions** are assigned to resources, and each has distinct trade-offs.

The key distinction lies in how the Resource is scoped in the RBAC **Policy**:

+ **Container Permissions** - **Permissions** are tied to a _container_ (e.g., a `Group`), and apply to all resources within that container (e.g., all `Event`s).
+ **Instance Permissions** - **Permissions** are tied to _individual instances_ (e.g., `EventID` 5), allowing fine-grained control over each resource.

In some cases, a hybrid approach combining both methods can offer the best of both worlds. This guide will help you evaluate these options and choose the most appropriate design for your use case.

## Szenario: MeetDown

We use the fictional platform _MeetDown_ to illustrate the two permission design approaches. In _MeetDown_, users can create `Groups` and publish Events within them.

+ **Group** and **Event** are application-level resources, not RBAC system objects.
+ Each Group has at least one owner, and all other users are members.
+ Owners have full control over the Group and its Events; members can RSVP and rate Events.

## Container **Permissions**

In this approach, **Permissions** are defined at the **container level** (e.g., Group). When a new Group is created (e.g., ID 1), **Roles** like `Group[1]_Owner` and `Group[1]_Member` are automatically generated. **Policies** are then assigned to these **Roles**, with ResourceIDs referencing the container (e.g., `Group[1]`), meaning the **Permissions** apply to all resources _within_ that container.

### Example **Policies** for `Group` 1

| **Role**          | **ResourceType** | **ResourceID** | Action   | Note                                                          |
| ----------------- | ---------------- | -------------- | -------- | ------------------------------------------------------------- |
| `Group[1]_Owner`  | `Group`          | `1`            | `edit`   | Owners of Group 1 can edit the Group.                         |
| `Group[1]_Owner`  | `Group`          | `1`            | `delete` | Owners of Group 1 can delete the Group.                       |
| `Group[1]_Owner`  | `Event`          | `Group[1]`     | `create` | Owners of Group 1 can create new Events for the Group.        |
| `Group[1]_Owner`  | `Event`          | `Group[1]`     | `edit`   | Owners of Group 1 can edit Events for the Group.              |
| `Group[1]_Owner`  | `Event`          | `Group[1]`     | `delete` | Owners of Group 1 can delete create new Events for the Group. |
| `Group[1]_Member` | `Event`          | `Group[1]`     | `RSVP`   | Members of Group 1 can RSVP for Events of the Group.          |
| `Group[1]_Member` | `Event`          | `Group[1]`     | `rate`   | Members of Group 1 can rate past Events of the Group.         |

!!! note **Role** hierarchy
    The `Group[1]_Owner` **Role** inherits **Permissions** from `Group[1]_Member`. This allows owners to perform all member **Actions** automatically.

### ✅ Pros of Container **Permissions**

+ **Simple Hierarchies**: Owner **Roles** naturally inherit member **Permissions**.
+ **Fewer Policies**: One set of **Policies** applies to all instances within a container.
+ **Efficient list access**: To check access to a list of Events, only the GroupID is needed. Individual Event IDs don't need to be resolved.

### ❌ Cons of Container **Permissions**

+ **Lack of granularity**: All Events in a Group inherit the same **Permissions**. No exceptions can be made for individual Events.
+ **Indirect access checks**: To verify access to a specific Event, you must first retrieve the Event from the database to get its GroupID.

## Instance **Permissions**

In this approach, **Permissions** are defined at the **instance level** (e.g., Event ID 5). When a Group is created (e.g., ID 2), **Roles** like `Group[2]_Owner` and `Group[2]_Member` are generated. However, **Policies** for Events are only created **after** the Event instance exists, and each policy references the specific Event ID.

### Example Policies for Group 2 (Before Event Creation)

| **Role**         | **ResourceType** | **ResourceID** | Action   | Note                                 |
| ---------------- | ---------------- | -------------- | -------- | ------------------------------------ |
| `Group[2]_Owner` | `Group`          | `2`            | `edit`   | Owners can edit Group 2.             |
| `Group[2]_Owner` | `Group`          | `2`            | `delete` | Owners can delete Group 2.           |
| `Group[2]_Owner` | `Event`          | `Group[2]`     | `create` | Owners can create Events in Group 2. |

!!! note

    Policies for `Edit`, `Delete`, `RSVP`, and `Rate` on Events are **not created until the Event instance is created**.

### Example Policies After Creating Event 5

| **Role**          | **ResourceType** | **ResourceID** | Action   | Note                         |
| ----------------- | ---------------- | -------------- | -------- | ---------------------------- |
| `Group[2]_Owner`  | `Event`          | `5`            | `Edit`   | Owners can edit Event 5.     |
| `Group[2]_Owner`  | `Event`          | `5`            | `Delete` | Owners can delete Event 5.   |
| `Group[2]_Member` | `Event`          | `5`            | `RSVP`   | Members can RSVP to Event 5. |
| `Group[2]_Member` | `Event`          | `5`            | `Rate`   | Members can rate Event 5.    |

### ✅ Pros of Instance Permissions

+ **Fine-grained control**: **Permissions** can be customized per Event (e.g., restrict RSVP for a specific Event).
+ **Precise audits**: Access logs and checks are tied to specific resource instances.
+ **Direct access checks**: To verify access to Event 5, use EventID directly, no need to resolve GroupID.

### ❌ Cons of Instance Permissions

+ **More Policies**: Each Event requires its own set of **Policies**, increasing maintenance overhead.
+ **Complex Hierarchies**: Custom **Roles** per Event may break simple inheritance patterns.
+ **Inefficient list access**: To list all Events a user can access, you must query the RBAC system for all accessible Event instances, potentially impacting performance.

!!! tip
    You can prevent inefficient permission checks on individual list items by querying all **Permissions** assigned to a **Subject**/**Resource** at once using the `pypermission.RBAC.subject.permissions(subject: str, db: Session)` and `pypermission.RBAC.role.permissions(subject: str, db: Session)` methods.

## When to Use Which Approach

**Container permissions** are ideal for simpler applications or when most operations involve listing or accessing resources within a container (e.g., all `Event`s in a `Group`). They are easier to design, require fewer **Policies**, and are more efficient for list-based access.

**Instance permissions** are better suited when you need fine-grained control over individual resources - such as for auditing, compliance, or when exceptions are common. They offer precision but come with higher maintenance and performance overhead.

In many cases, a **hybrid approach** - using container **Permissions** as the default and adding instance **Policies** only where needed provides a good balance.
