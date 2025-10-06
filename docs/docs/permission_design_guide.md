# Permission Design Guide

This guide explains how permissions can be designed in RBAC systems. There are two different approaches to structuring permissions, each with its own trade-offs:

+ **Container permissions**
+ **Instance permissions**

In some cases, a hybrid approach combining both methods can also be applied. The goal of this guide is to provide a clear overview of these approaches and help design flexible, maintainable permission structures.

## Definitions

We define the core concepts of our RBAC model as follows:

+ **ResourceType** - The type or category of a resource (e.g., Group, Event).
+ **ResourceID** - A unique identifier for a specific instance of a resource.
+ **Action** - An operation that can be performed on a resource (e.g., Create, Edit, Delete).
+ **Role** - A collection of permissions assigned to a subject or group of subjects.
+ **Permission** - Grants the ability to perform a specific action on a resource.
+ **Policy** - A set of permissions assigned to a role.

Formally, using set notation:

\[
\begin{aligned}
\text{Resource}   & = \text{ResourceType} \times \text{ResourceID} \\[2mm]
\text{Permission} & = \text{Resource} \times \text{Action} \\
                  & = \text{ResourceType} \times \text{ResourceID} \times \text{Action} \\[2mm]
\text{Policy}     & = \text{Role} \times \text{Permission} \\
                  & = \text{Role} \times \text{ResourceType} \times \text{ResourceID} \times \text{Action}
\end{aligned}
\]

In this model, a resource is any object that can be acted upon, a permission links an action to a resource, and a policy assigns one or more permissions to a role.

## Szenario - MeetDown

We use the fictional platform _MeetDown_ to illustrate the two permission design approaches. In _MeetDown_, users can create Groups and publish Events within them.

For this guide, Group and Event are application-level resources, not RBAC system objects. Each group has at least one owner, and all other users are members.

## Container permissions

When a new Group is created (for example, with ID 1), the required Roles (`group[2]_owner`, `group[2]_member`) and Policies are automatically generated.

| Role            | ResourceType | ResourceID | Action   | Note                                    |
| --------------- | ------------ | ---------- | -------- | --------------------------------------- |
| `group[1]_owner`  | `Group`      | `1`          | `Edit`   | Group 1 owners can edit the group.      |
| `group[1]_owner`  | `Group`      | `1`          | `Delete` | Group 1 owners can delete the group.    |
| `group[1]_owner`  | `Event`      | `Group:1`    | `Create` | Group 1 owners can create new events.   |
| `group[1]_owner`  | `Event`      | `Group:1`    | `Edit`   | Group 1 owners can edit new events.     |
| `group[1]_owner`  | `Event`      | `Group:1`    | `Delete` | Group 1 owners can delete new events.   |
| `group[1]_member` | `Event`      | `Group:1`    | `RSVP`   | Group 1 members can RSVP for events.    |
| `group[1]_member` | `Event`      | `Group:1`    | `Rate`   | Group 1 members can rate a past events. |

!!! note Role hierarchy

    In this example the `group[1]_owner` role would be a child role of `group[1]_member`. So every subject of the owner role will be granted access to the member permissions to.

### Pro

+ Role hierarchy is straightforward, allowing owner Roles to automatically inherit member Permissions.
+ Only a few policies are needed to represent the complete business logic.
+ Checking access to a list of Events is simple: the Group ID can be used as the main argument, making it easy to verify if a user can view the Event list.

### Contra

+ All contained Events inherit the same policies, which can be limiting if exceptions are required for individual Events.
+ Checking access for specific Events is requires getting the Event from DB to get it's Group ID. 

## Instance permissions

When a new Group is created (for example, with ID 2), the required Roles (`group[2]_owner`, `group[2]_member`) and Policies are automatically generated.


| Role           | ResourceType | ResourceID | Action   | Note                                  |
| -------------- | ------------ | ---------- | -------- | ------------------------------------- |
| `group[2]_owner` | `Group`      | `2`          | `Edit`   | Group 2 owners can edit the group.    |
| `group[2]_owner` | `Group`      | `2`          | `Delete` | Group 2 owners can delete the group.  |
| `group[2]_owner` | `Event`      | `Group:2`    | `Create` | Group 2 owners can create new events. |

The policies for Events, except for the `Create` Action, can only be created once the actual Event instance exists. The table below shows the policies that are generated after the Event instance has been created.

| Role            | ResourceType | ResourceID | Action   | Note                                        |
| --------------- | ------------ | ---------- | -------- | ------------------------------------------- |
| `group[2]_owner`  | `Event`      | `5`          | `Edit`   | Group 2 owners can edit event 5.            |
| `group[2]_owner`  | `Event`      | `5`          | `Delete` | Group 2 owners can delete event 5.          |
| `group[2]_member` | `Event`      | `5`          | `RSVP`   | Group 2 members can RSVP for event 5.       |
| `group[2]_member` | `Event`      | `5`          | `Rate`   | Group 2 members can rate the past events 5. |

### Pro

+ Fine-grained control through Event-specific policies, avoiding over-permission.
+ Precise audits and access checks for each Event instance.
+ Checking access for a specific Event is straightforward: the Event ID can be used directly.

### Contra

+ More policies need to be created and maintained.
+ Role hierarchy is less straightforward at the instance level, especially if custom roles are needed for individual Events.
+ Listing all Events of a Group requires a lookup of all accessible Event instances in the RBAC system before pagination and returning results in the application.
 
## When to Use Which Approach

**Container permissions** are generally easier to design and implement. For simpler applications, they are often sufficient. However, it is important to carefully consider the application’s business logic to ensure they meet your requirements.

**Instance permissions** are primarily useful when fine-grained control over individual resources is required, for example, for auditing or compliance purposes.

For very large applications with performance considerations, it is important to analyze the types of requests: if most requests are for Resource lists, **Container permissions** are likely more suitable. If requests are mostly for individual resources, **Instance permissions** may be the better choice. In many cases, it also makes sense to consider a **hybrid** approach, combining both methods to optimize for performance and maintainability.
