# 1. Integration Guide - Introduction

This integration guide demonstrates a reference integration of the **PyPermission** RBAC library in an exemplary backend service layer for a fictive "MeetDown" SaaS application.

!!! warning

    This page is under development.

The MeetDown application showcases a simplified version of a community event organizing platform where users can join groups and manage events. It illustrates both a theoretical foundation for designing an RBAC system for a SaaS platform like "meetup" and a practical walkthrough of how these concepts are implemented in the accompanying backend Python code.

!!! info

    Before continuing the reference integration guide we recommend going through the documentation in the following order:

    1. [Definitions](../definitions.md)
    2. [Permission design guide](../permission_design_guide.md)

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

| Actions       | guest | user | moderator                 | admin |
| ------------- | ----- | ---- | ------------------------- | ----- |
| `create()`    |       |      | yes                       | yes   |
| `get()`       |       | yes  | yes                       | yes   |
| `list()`      |       | yes  | yes                       | yes   |
| `set_email()` |       | self | if not moderator or admin | yes   |
| `set_state()` |       | self | if not moderator or admin | yes   |
| `delete()`    |       |      |                           | yes   |

### Group service

The following table outlines the **Policies** for `Group` resources. Authenticated `User`s are allowed to create and manage their communities. Group owners have full control over `Group` settings, while `moderator`s can assist in managing content and state.

| Actions       | guest | user     | moderator | admin |
| ------------- | ----- | -------- | --------- | ----- |
| `create()`    |       | yes      |           | yes   |
| `get()`       | yes   | yes      | yes       | yes   |
| `list()`      | yes   | yes      | yes       | yes   |
| `set_title()` |       | if owner |           | yes   |
| `set_state()` |       | if owner | yes       | yes   |
| `delete()`    |       | if owner |           | yes   |

### Event service

The following table outlines the **Policies** for `Event` resources. `Event`s are managed within `Group`s and follow access rules similar to `Group`s. Only owners or `admin`s can make changes to `Event`s, with `moderator`s having additional moderation privileges.

| Actions       | guest | user           | moderator | admin |
| ------------- | ----- | -------------- | --------- | ----- |
| `create()`    |       | if group owner |           | yes   |
| `get()`       | yes   | yes            | yes       | yes   |
| `list()`      | yes   | yes            | yes       | yes   |
| `set_title()` |       | if group owner |           | yes   |
| `set_state()` |       | if group owner | yes       | yes   |
| `delete()`    |       | if group owner |           | yes   |
