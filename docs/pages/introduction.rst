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

The basic functionality of an RBAC system can be demonstrated for a hypothetical chat
program:

Defining Permissions
--------------------

First we have to define a couple of meaningful permissions for the operations we want to
separate access for by creating a ``PermissionNode`` structure. These have to be registered to
a :py:class:`~pypermission.serial.SerialAuthority` class:

.. code-block:: python

    from pypermission import PermissionNode
    from pypermission.serial import SerialAuthority


    class ChatNodes(PermissionNode):
        INV = "invite"
        BAN = "ban"
        JOIN = "join"
        LEAVE = "leave"
        MSG = "message"


    CNs = ChatNodes

    auth = SerialAuthority(nodes=CNs)

Managing Roles
--------------

Assume we want to manage access to the chat system for the three basic roles `user`,
`moderator` and `admin`. To create the given roles, the
:py:meth:`~pypermission.serial.SerialAuthority.add_role` method can be used (likewise
:py:meth:`~pypermission.serial.SerialAuthority.del_role` removes a given role):

.. code-block:: python

    auth.add_role(rid="user")
    auth.add_role(rid="moderator")
    auth.add_role(rid="admin")

Verify that the authority contains all the expected roles with the
:py:meth:`~pypermission.serial.SerialAuthority.get_roles` method:

>>> auth.get_roles() == {'admin', 'user', 'moderator'}
True

Granting Permissions
--------------------



Managing Subjects
-----------------

Next we want to create the subjects `Alice`, `Bob` and `John`. To create subjects,
use the :py:meth:`~pypermission.serial.SerialAuthority.add_subject` method (similarly
use :py:meth:`~pypermission.serial.SerialAuthority.del_subject` to remove a subject):

.. code-block:: python

    auth.add_subject(sid="Alice")
    auth.add_subject(sid="Bob")
    auth.add_subject(sid="John")

Verify that the authority contains all the expected subjects with the
:py:meth:`~pypermission.serial.SerialAuthority.get_subjects` method:

>>> auth.get_subjects() == {'Alice', 'Bob', 'John'}
True

Subject-Role Assignment
-----------------------

Users can be assigned to multiple roles and likewise the same role can be given to multiple users.

In this example, we want to achieve the following assignment:

* `Alice` as a member of the `admin` role
* `Bob` as a member of the `moderator` and `user` roles
* `John` as a member of the `user` role only

.. code-block:: python

    auth.role_assign_subject(rid="admin", sid="Alice")
    auth.role_assign_subject(rid="moderator", sid="Bob")
    auth.role_assign_subject(rid="user", sid="Bob")
    auth.role_assign_subject(rid="user", sid="John")

Now exemplarily review that the user `Bob` got both - the `user` and the `moderator` role assigned
with the :py:meth:`~pypermission.serial.SerialAuthority.subject_get_roles` method:

>>> auth.subject_get_roles(sid='Bob') == {'moderator', 'user'}
True

Likewise verify that the `user` role has been assigned to both - `Bob` and `John`
with the  :py:meth:`~pypermission.serial.SerialAuthority.role_get_subjects` method:

>>> auth.role_get_subjects(rid='user') == {'Bob', 'John'}
True

.. _NIST_RBAC: The NIST model for role-based access control: towards a unified standard - https://doi.org/10.1145/344287.344301