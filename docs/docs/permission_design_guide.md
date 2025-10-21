# RBAC for Python - Permission Design Guide

In this Guide, we will discuss the following two approaches how you can choose the right Resource Identification for your Permission Model.

+ **Container permissions** - Groups all contained resources under one identifier
+ **Instance permissions** - Treats each resource instance individually

Each of these come with their own trade-offs and a hybrid approach might just be the choice for you. In the following Szenario about the fictional platform _MeetDown_ we'll illustrate the two approaches.

## Szenario - MeetDown

In _MeetDown_, users can create Groups and publish Events within them.

In this guide, Group and Event are application-level resources, not RBAC system objects. Each Group has at least one owner, and all other users are members.

## Container permissions

When a new Group is created (for example, with ID 1), the required Roles (`group[1]_owner`, `group[1]_member`) are automatically generated, leading to the following exemplary Policies:

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

    In this example the `group[1]_owner` Role would be a child Role of `group[1]_member`. So every subject of the owner Role will be granted access to the member permissions as well.

### ✅ Pro Container permissions

+ Role hierarchy is straightforward, allowing owner Roles to automatically inherit member Permissions.
+ Only a few Policies are needed to represent the complete business logic.
+ To verify if a user can view the Event list, the GroupID can be used in the ResourceID.

### ❌ Contra Container permissions

+ All contained Events inherit the same Policies, which can be limiting if exceptions are required for individual Events.
+ Checking access for specific Events requires getting the Event from DB to get it's GroupID.

## Instance permissions

When a new Group is created (for example, with ID 2), the required Roles (`group[2]_owner`, `group[2]_member`) are automatically generated, leading to the following exemplary Policies:

| Role             | ResourceType | ResourceID | Action   | Note                                                   |
| ---------------- | ------------ | ---------- | -------- | ------------------------------------------------------ |
| `group[2]_owner` | `Group`      | `2`        | `Edit`   | Owners of Group 2 can edit the Group.                  |
| `group[2]_owner` | `Group`      | `2`        | `Delete` | Owners of Group 2 can delete the Group.                |
| `group[2]_owner` | `Event`      | `Group:2`  | `Create` | Owners of Group 2 can create new Events for the Group. |

The Policies that apply to Events, except for the `Create` Action, can only be created once the actual Event instance exists. The table below shows the Policies that are generated after the Event 5 instance has been created.

| Role              | ResourceType | ResourceID | Action   | Note                                          |
| ----------------- | ------------ | ---------- | -------- | --------------------------------------------- |
| `group[2]_owner`  | `Event`      | `5`        | `Edit`   | Owners of Group 2 can edit Event 5.           |
| `group[2]_owner`  | `Event`      | `5`        | `Delete` | Owners of Group 2 can delete Event 5.         |
| `group[2]_member` | `Event`      | `5`        | `RSVP`   | Members of Group 2 can RSVP for Event 5.      |
| `group[2]_member` | `Event`      | `5`        | `Rate`   | Members of Group 2 can rate the past Event 5. |

### ✅ Pro Instance permissions

+ Fine-grained control through event-specific policies, avoiding over-permission.
+ Precise audits and access checks for each Event instance.
+ Checking access for a specific Event is straightforward: the EventID can be used directly.

### ❌ Contra Instance permissions

+ More policies need to be created and maintained.
+ Role hierarchy is less straightforward at the instance level, especially if custom roles are needed for individual Events.
+ Listing all Events of a Group requires a lookup of all accessible Event instances in the RBAC system before pagination and returning results in the application.

## When to Use Which Approach

**Container permissions** are generally easier to design and implement. For simpler applications, they are often sufficient. However, it is important to carefully consider the application’s business logic to ensure they meet your requirements.

**Instance permissions** are primarily useful when fine-grained control over individual resources is required, for example, for auditing or compliance purposes.

For very large applications with performance considerations, it is important to analyze the types of requests: if most requests are for Resource lists, **Container permissions** are likely more suitable. If requests are mostly for individual resources, **Instance permissions** may be the better choice. In many cases, it also makes sense to consider a **hybrid** approach, combining both methods to optimize for performance and maintainability.
