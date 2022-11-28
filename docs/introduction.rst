====================
Introduction to RBAC
====================

The original `NIST Model for RBAC <NIST_RBAC_>`_ isolates the following functional
capabilities. Features implemented in this library are highlighted below:

+-------------+----------------------------+------------------+---------------+
|             | Role Structure             | Role Constraints | Role Symmetry |
+=============+============================+==================+===============+
|             | Flat |br|                  | No |br|          | No |br|       |
|             | Limited Hierarchy |br|     | Yes              | Yes           |
|             | General Hierarchy          |                  |               |
+-------------+----------------------------+------------------+---------------+
| implemented | :green:`General Hierarchy` | :red:`No` |br|   | :green:`Yes`  |
+-------------+----------------------------+------------------+---------------+

Within a **Role Structure** the following features are supported:

* assign user to role - *user-role* (many-to-many relationship)
* assign permission to role - *permission-role* (many-to-many relationship)
* users can simultaneously exercise permissions of multiple roles
* *user-role* review

  * list roles assigned to specific user
  * list users assigned to specific role

A **Hierarchical Role Structure** additionally supports:

* senior roles acquire permissions of their juniors
* assign seniority relation between roles - *role-role*
* **General Hierarchy** - *role-role* (many-to-many relationship)
* *user-role* review extended by

  * list all roles a specific user can take
  * list all users that can take a specific role

The **Role Symmetry** adds support for:

* *permission-role* review

  * list permission assigned to specific role (selectable between direct and indirect relations)
  * list roles assigned to specific permission (selectable between direct and indirect relations)


Starting RBAC with PyPermission
===============================

Lets define a simple online chat system. The features managed by the permission system
first have to be defined within a ``PermissionNode`` structure:

.. code-block:: python

    from pypermission import PermissionNode
    from pypermission.serial import SerialAuthority


    class ChatNodes(PermissionNode):
        _ = "chat.*"
        INV = "chat.invite"
        BAN_ = "chat.ban.*"
        BAN_USER = "chat.ban.user"
        BAN_ANY = "chat.ban.any"
        JOIN_ = "chat.join.*"
        JOIN_INV = "chat.join.invited"
        JOIN_ANY = "chat.join.any"
        LEAVE = "chat.leave"
        MSG = "chat.message"


    CNs = ChatNodes

    auth = SerialAuthority(nodes=CNs)

Assume we want to manage access to the chat system for the three basic roles `user`,
`moderator` and `admin`. To create the given roles, the
:py:meth:`~pypermission.serial.SerialAuthority.new_role` method can be used:

.. code-block:: python

    auth.new_role(rid="user")
    auth.new_role(rid="moderator")
    auth.new_role(rid="admin")

Verify that the authority contains all the expected roles with the
:py:meth:`~pypermission.serial.SerialAuthority.get_roles` method:

>>> auth.get_roles() == {'admin', 'user', 'moderator'}
True

Next we want to create the subjects `Alice`, `Bob` and `John`.

.. code-block:: python

    auth.new_subject(sid="Alice")
    auth.new_subject(sid="Bob")
    auth.new_subject(sid="John")

Verify that the authority contains all the expected subjects with the
:py:meth:`~pypermission.serial.SerialAuthority.get_subjects` method:

>>> auth.get_subjects() == {'Alice', 'Bob', 'John'}
True

Assign the subjects as follows:

* `Alice` as a member of the `admin` role
* `Bob` as a member of the `moderator` and `user` roles
* `John` as a member of the `user` role only

.. code-block:: python

    auth.role_add_subject(rid="admin", sid="Alice")
    auth.role_add_subject(rid="moderator", sid="Bob")
    auth.role_add_subject(rid="user", sid="Bob")
    auth.role_add_subject(rid="user", sid="John")

Now exemplarily review that the user `Bob` got both - the `user` and the `moderator` role assigned
with the :py:meth:`~pypermission.serial.SerialAuthority.subject_get_roles` method:

>>> auth.subject_get_roles(sid='Bob') == {'moderator', 'user'}
True

Likewise verify that the `user` role has been assigned to both - `Bob` and `John`
with the  :py:meth:`~pypermission.serial.SerialAuthority.role_get_subjects` method:

>>> auth.role_get_subjects(rid='user') == {'Bob', 'John'}
True

.. _NIST_RBAC: https://doi.org/10.1145/344287.344301