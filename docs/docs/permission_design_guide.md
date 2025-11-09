# PyPermission - Permission Design Guide

This guide explores how to design permissions in Role-Based Access Control (RBAC) systems, focusing on two primary approaches: Container Permissions and Instance Permissions. Each approach defines how permissions are assigned to resources, and each has distinct trade-offs.

The key distinction lies in how the Resource is scoped in the RBAC policy:

+ **Container permissions** - Permissions are tied to a _container_ (e.g., a Group), and apply to all resources within that container (e.g., all Events in a Group).
+ **Instance permissions** - Permissions are tied to _individual instances_ (e.g., Event ID 5), allowing fine-grained control over each resource.

In some cases, a hybrid approach combining both methods can offer the best of both worlds. This guide will help you evaluate these options and choose the most appropriate design for your use case.

## Szenario: MeetDown

We use the fictional platform _MeetDown_ to illustrate the two permission design approaches. In _MeetDown_, users can create Groups and publish Events within them.

+ **Group** and **Event** are application-level resources, not RBAC system objects.
+ Each Group has at least one owner, and all other users are members.
+ Owners have full control over the Group and its Events; members can RSVP and rate Events.

## Container permissions

In this approach, permissions are defined at the **container level** (e.g., Group). When a new Group is created (e.g., ID 1), Roles like `group[1]_owner` and `group[1]_member` are automatically generated. Policies are then assigned to these Roles, with ResourceIDs referencing the container (e.g., `Group:1`), meaning the permissions apply to all resources _within_ that container.

### Example Policies for Group 1

| Role              | ResourceType | ResourceID | Action   | Note                                                          |
| ----------------- | ------------ | ---------- | -------- | ------------------------------------------------------------- |
| `group[1]_owner`  | `Group`      | `1`        | `Edit`   | Owners of Group 1 can edit the Group.                         |
| `group[1]_owner`  | `Group`      | `1`        | `Delete` | Owners of Group 1 can delete the Group.                       |
| `group[1]_owner`  | `Event`      | `Group:1`  | `Create` | Owners of Group 1 can create new Events for the Group.        |
| `group[1]_owner`  | `Event`      | `Group:1`  | `Edit`   | Owners of Group 1 can edit Events for the Group.              |
| `group[1]_owner`  | `Event`      | `Group:1`  | `Delete` | Owners of Group 1 can delete create new Events for the Group. |
| `group[1]_member` | `Event`      | `Group:1`  | `RSVP`   | Members of Group 1 can RSVP for Events of the Group.          |
| `group[1]_member` | `Event`      | `Group:1`  | `Rate`   | Members of Group 1 can rate past Events of the Group.         |

!!! note Role hierarchy

    The `group[1]_owner` Role inherits permissions from `group[1]_member`. This allows owners to perform all member actions automatically.

### ✅ Pros of Container Permissions

+ **Simple role hierarchy**: Owner roles naturally inherit member permissions.
+ **Fewer policies**: One set of policies applies to all instances within a container.
+ **Efficient list access**: To check access to a list of Events, only the GroupID is needed. Individual Event IDs don't need to be resolved.

### ❌ Cons of Container Permissions

+ **Lack of granularity**: All Events in a Group inherit the same permissions. No exceptions can be made for individual Events.
+ **Indirect access checks**: To verify access to a specific Event, you must first retrieve the Event from the database to get its GroupID.

## Instance permissions

In this approach, permissions are defined at the **instance level** (e.g., Event ID 5). When a Group is created (e.g., ID 2), Roles like `group[2]_owner` and `group[2]_member` are generated. However, policies for Events are only created **after** the Event instance exists, and each policy references the specific Event ID.

### Example Policies for Group 2 (Before Event Creation)

| Role             | ResourceType | ResourceID | Action   | Note                                              |
|------------------|--------------|------------|----------|---------------------------------------------------|
| `group[2]_owner` | `Group`      | `2`        | `Edit`   | Owners can edit Group 2.                          |
| `group[2]_owner` | `Group`      | `2`        | `Delete` | Owners can delete Group 2.                        |
| `group[2]_owner` | `Event`      | `Group:2`  | `Create` | Owners can create Events in Group 2.              |

!!! note

    Policies for `Edit`, `Delete`, `RSVP`, and `Rate` on Events are **not created until the Event instance is created**.

### Example Policies After Creating Event 5

| Role             | ResourceType | ResourceID | Action   | Note                                              |
|------------------|--------------|------------|----------|---------------------------------------------------|
| `group[2]_owner` | `Event`      | `5`        | `Edit`   | Owners can edit Event 5.                          |
| `group[2]_owner` | `Event`      | `5`        | `Delete` | Owners can delete Event 5.                        |
| `group[2]_member`| `Event`      | `5`        | `RSVP`   | Members can RSVP to Event 5.                      |
| `group[2]_member`| `Event`      | `5`        | `Rate`   | Members can rate Event 5.                         |

### ✅ Pros of Instance Permissions

+ **Fine-grained control**: Permissions can be customized per Event (e.g., restrict RSVP for a specific Event).
+ **Precise audits**: Access logs and checks are tied to specific resource instances.
+ **Direct access checks**: To verify access to Event 5, use EventID directly, no need to resolve GroupID.

### ❌ Cons of Instance Permissions

+ **More policies**: Each Event requires its own set of policies, increasing maintenance overhead.
+ **Complex role hierarchy**: Custom roles per Event may break simple inheritance patterns.
+ **Inefficient list access**: To list all Events a user can access, you must query the RBAC system for all accessible Event instances, potentially impacting performance.

!!! tip

    You can prevent inefficient permission checks on individual list items by querying all Permissions assigned to a Subject/Resource at once using the `RBAC.subject.permissions(subject: str, db: Session)` and `RBAC.role.permissions(subject: str, db: Session)` methods.

## When to Use Which Approach

**Container permissions** are ideal for simpler applications or when most operations involve listing or accessing resources within a container (e.g., all Events in a Group). They are easier to design, require fewer policies, and are more efficient for list-based access.

**Instance permissions** are better suited when you need fine-grained control over individual resources - such as for auditing, compliance, or when exceptions are common. They offer precision but come with higher maintenance and performance overhead.

In many cases, a **hybrid approach** - using container permissions as the default and adding instance policies only where needed provides a good balance.
