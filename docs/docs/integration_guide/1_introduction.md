# 1. Integration Guide - Introduction

!!! info

    Before continuing the reference integration guide we recommend going through the documentation in the following order:

    1. [Definitions](../definitions.md)
    2. [Permission design guide](../permission_design_guide.md)


This integration guide demonstrates a reference integration of the **PyPermission** RBAC library in an exemplary backend service layer for a fictive "MeetDown" SaaS application.

The MeetDown application showcases a simplified version of a community event organizing platform where users can join groups and manage events. It illustrates both a theoretical foundation for designing an RBAC system for a SaaS platform like "meetup" and a practical walkthrough of how these concepts are implemented in the accompanying backend Python code.

!!! info

    The complete fictional MeetDown application is included in the **PyPermission** package. The corresponding Python source code can be found in the library repository in the folder [`src/pypermission/example`](https://gitlab.com/DigonIO/pypermission/-/tree/main/src/pypermission/example).

## Features

The MeetDown application structures its features into three core services, each encapsulating a distinct domain of functionality. These services are designed to reflect the underlying data model while also emphasizing the functionality on a feature basis. The following table describes the core service domains:

| Domain  | Description                                                                                        |
| ------- | -------------------------------------------------------------------------------------------------- |
| `User`  | Represents individual `User` accounts within the platform.                                         |
| `Group` | Represents community spaces managed by `User`s. `Group`s act as containers for members and events. |
| `Event` | Represents scheduled activities within a `Group`.                                                  |

## RBAC Roles

The following **Roles** are defined in the RBAC system:

| **Role**    | Description                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------- |
| `guest`     | Represents unauthenticated `User`s (not logged in). Guests can only view public content.           |
| `user`      | Authenticated `User`s who can participate in `Group`s and `Event`s and manage their own account.   |
| `moderator` | Moderators can manage `User`s, `Group`s and `Event`s. They can not participate like normal `User`. |
| `admin`     | Admins can create, modify, and delete any resource.                                                |

## RBAC Policies

The following subsections describe which **Roles** have access to which service functions, including any potential conditions (not to be confused with ABAC), and therefore also indicate which abstract features each **Role** is permitted to access.

### User service

The following table outlines the **Policies** for managing `User` profiles, including email and state updates. Only `admin`s can fully modify or delete a `User` resource, while the **Role** `moderator` and `user` may update only their own profile.

| Actions          | guest | user                | moderator                                                | admin |
| ---------------- | ----- | ------------------- | -------------------------------------------------------- | ----- |
| `create()`       |       |                     | ✓                                                       | ✓    |
| `get()`          |       | ✓                  | ✓                                                       | ✓    |
| `list()`         |       | ✓                  | ✓                                                       | ✓    |
| `set_username()` |       | ✓ (on own profile) | ✓ (except for other `moderator` or `admin` **Members**) | ✓    |
| `set_state()`    |       | ✓ (on own profile) | ✓ (except for other `moderator` or `admin` **Members**) | ✓    |
| `delete()`       |       |                     |                                                          | ✓    |

### Group service

The following table outlines the **Policies** for `Group` resources. Authenticated `User`s are allowed to create and manage their communities. Group owners have full control over `Group` settings, while `moderator`s can assist in managing content and state.

| Actions       | guest | user                | moderator | admin |
| ------------- | ----- | ------------------- | --------- | ----- |
| `create()`    |       | ✓                  |           | ✓    |
| `get()`       | ✓    | ✓                  | ✓        | ✓    |
| `list()`      | ✓    | ✓                  | ✓        | ✓    |
| `set_title()` |       | ✓ (if group owner) |           | ✓    |
| `set_state()` |       | ✓ (if group owner) | ✓        | ✓    |
| `delete()`    |       | ✓ (if group owner) |           | ✓    |

### Event service

The following table outlines the **Policies** for `Event` resources. `Event`s are managed within `Group`s and follow access rules similar to `Group`s. Only owners or `admin`s can make changes to `Event`s, with `moderator`s having additional moderation privileges.

| Actions       | guest | user                | moderator | admin |
| ------------- | ----- | ------------------- | --------- | ----- |
| `create()`    |       | ✓ (if group owner) |           | ✓    |
| `get()`       | ✓    | ✓                  | ✓        | ✓    |
| `list()`      | ✓    | ✓                  | ✓        | ✓    |
| `set_title()` |       | ✓ (if group owner) |           | ✓    |
| `set_state()` |       | ✓ (if group owner) | ✓        | ✓    |
| `delete()`    |       | ✓ (if group owner) |           | ✓    |

This was the first part of the integration guide, which covered which features the fictitious MeetDown application provides and how these are divided into the corresponding service functions, as well as which `User` `Group` has access to which functionality.

In the second part, we continue with how to implement these requirements in an RBAC system and specifically - which **Roles** and **Permissions** are explicitly required. [Continue...](./2_rbac_system_design.md)
