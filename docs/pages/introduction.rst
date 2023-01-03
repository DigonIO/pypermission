====================
Introduction to RBAC
====================

The original *NIST Model for RBAC*\ [#NIST_RBAC]_ isolates the following functional
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

* assign subject to role - `subject-role` (`many-to-many` relationship)
* assign permission to role - `permission-role` (`many-to-many` relationship)
* subjects can simultaneously exercise permissions of multiple roles
* `subject-role` review

  * list roles assigned to specific subject
  * list subjects assigned to specific role

A **Hierarchical Role Structure** additionally supports:

* senior roles acquire permissions of their juniors
* assign seniority relation between roles - `role-role`
* **General Hierarchy** - `role-role` (`many-to-many` relationship)
* `subject-role` review extended by

  * list all roles a specific subject can take
  * list all subjects that can take a specific role

The **Role Symmetry** adds support for:

* `permission-role` review

  * list permission assigned to specific role (selectable between direct and indirect relations)
  * list roles assigned to specific permission (selectable between direct and indirect relations)


Starting RBAC with PyPermission
===============================

The basic functionality of an RBAC system can be demonstrated for a hypothetical chat
program. The library provides different backends for persistency - for simplicity reasons
the following example uses the :py:mod:`pypermission.serial` module which stores and loads
the state to either a single ``json`` or ``yaml`` file. Alternatively the
:py:mod:`pypermission.sqlalchemy` module can be used to write and read the state to a
database supported by ``sqlalchemy``\ [#sqlalchemy]_. Most of the functions presented
below are available in both backends, the :py:mod:`pypermission.sqlalchemy` module however
requires a database session.

Defining Permissions
--------------------

First we have to define a couple of meaningful permissions for the operations we want to
separate access for by creating a :py:class:`~pypermission.core.PermissionNode` structure.
These have to be registered to a :py:class:`~pypermission.serial.core.SerialAuthority` class:

.. code-block:: python

    from pypermission import PermissionNode
    from pypermission.serial import SerialAuthority


    class ChatNodes(PermissionNode):
        JOIN = "join"
        LEAVE = "leave"
        MSG = "message"
        INV = "invite"
        BAN_USER = "ban_user"
        CHANGE_ROLE = "change_role"


    CNs = ChatNodes

    auth = SerialAuthority(nodes=CNs)

Managing Subjects
-----------------

Next we want to create the subjects `Alice`, `Bob` and `John`. To create subjects,
use the :py:meth:`~pypermission.serial.core.SerialAuthority.add_subject` method (similarly
use :py:meth:`~pypermission.serial.core.SerialAuthority.del_subject` to remove a subject):

.. code-block:: python

    auth.add_subject(sid="Alice")
    auth.add_subject(sid="Bob")
    auth.add_subject(sid="John")

Managing Roles
--------------

Assume we want to manage access to the chat system for the three basic roles `user`,
`moderator` and `admin`. To create the given roles, the
:py:meth:`~pypermission.serial.core.SerialAuthority.add_role` method can be used (likewise
:py:meth:`~pypermission.serial.core.SerialAuthority.del_role` removes a given role):

.. code-block:: python

    auth.add_role(rid="user")
    auth.add_role(rid="moderator")
    auth.add_role(rid="admin")

Subject-Role Assignment
-----------------------

A subject can be assigned to multiple roles and likewise the same role can be given
to multiple subjects.

For management of the `subject-role` assignment, use the
:py:meth:`~pypermission.serial.core.SerialAuthority.role_assign_subject` method
to add a relation (use
:py:meth:`~pypermission.serial.core.SerialAuthority.role_deassign_subject`
to remove a relation).

In this example, we want to achieve the following assignment:

* `Alice` as a member of the `admin` role
* `Bob` as a member of the `moderator` and `user` roles
* `John` as a member of the `user` role only

.. code-block:: python

    auth.role_assign_subject(rid="admin", sid="Alice")
    auth.role_assign_subject(rid="moderator", sid="Bob")
    auth.role_assign_subject(rid="user", sid="Bob")
    auth.role_assign_subject(rid="user", sid="John")

Granting Permissions
--------------------

We can grant a permission to multiple roles, while at the same time a single role can
be granted multiple permissions. Here we are going to perform the following permission assignment:

* The `user` role should be able to `join`, `leave` and `message` a chat room.
* A `moderator` should be granted the `invite` and `ban_user` permission.
* All permissions should be granted to the `admin` role. Note the call to the
  :py:meth:`~pypermission.serial.core.SerialAuthority.root_node` method granting
  all permissions within the authority using a single statement.

To grant a permission to a role, the
:py:meth:`~pypermission.serial.core.SerialAuthority.role_grant_permission` method is provided
(a permission can be revoked with the
:py:meth:`~pypermission.serial.core.SerialAuthority.role_revoke_permission` method).

.. note::
   There are multiple ways to grant subjects the same permissions as shown here.
   Concerning *separation of duties*\ [#WIKI_SOD]_\ , the setup shown here is certainly not ideal.

.. code-block:: python

    auth.role_grant_permission(rid="user", node=CNs.JOIN)
    auth.role_grant_permission(rid="user", node=CNs.LEAVE)
    auth.role_grant_permission(rid="user", node=CNs.MSG)

    auth.role_grant_permission(rid="moderator", node=CNs.INV)
    auth.role_grant_permission(rid="moderator", node=CNs.BAN_USER)

    auth.role_grant_permission(rid="admin", node=auth.root_node())

Review the RBAC configuration
-----------------------------

At this point we should have a flat permission setup for multiple subjects, permissions and roles
as shown in the following diagram:

.. mermaid:: ../diagrams/introduction_graph.mmd

Using more elaborated setups necessitates a variety of review functions.

Subject Review
^^^^^^^^^^^^^^

Verify that the authority contains all the expected subjects with the
:py:meth:`~pypermission.serial.core.SerialAuthority.get_subjects` method:

>>> auth.get_subjects() == {'Alice', 'Bob', 'John'}
True

Role Review
^^^^^^^^^^^

Verify that the authority contains all the expected roles with the
:py:meth:`~pypermission.serial.core.SerialAuthority.get_roles` method:

>>> auth.get_roles() == {'admin', 'user', 'moderator'}
True

Subject-Role Review
^^^^^^^^^^^^^^^^^^^

To exemplarily review that the subject `Bob` got both - the `user` and the `moderator` role
assigned with the :py:meth:`~pypermission.serial.core.SerialAuthority.subject_get_roles` method:

>>> auth.subject_get_roles(sid='Bob') == {'moderator', 'user'}
True

Likewise verify that the `user` role has been assigned to both - `Bob` and `John`
with the  :py:meth:`~pypermission.serial.core.SerialAuthority.role_get_subjects` method:

>>> auth.role_get_subjects(rid='user') == {'Bob', 'John'}
True

Permission-Role Review
^^^^^^^^^^^^^^^^^^^^^^

To verify that the permissions have been granted as desired to the given roles,
we use the :py:meth:`~pypermission.serial.core.SerialAuthority.role_get_permissions` method:

.. warning::
   Checking the output of :py:meth:`~pypermission.serial.core.SerialAuthority.role_get_permissions`
   is not sufficient to identify all permissions of a given role, as permissions can be
   granted through either the role hierarchy (TODO Guide) or the permission hierarchy (TODO Guide).
   This method only returns the :py:class:`~pypermission.core.PermissionNode` instances
   that are directly assigned to a role.

>>> {CNs.JOIN, CNs.LEAVE, CNs.MSG} == set(auth.role_get_permissions(rid='user'))
True

>>> {CNs.INV, CNs.BAN_USER} == set(auth.role_get_permissions(rid='moderator'))
True

Note, how the
:py:meth:`~pypermission.serial.core.SerialAuthority.role_get_permissions` method
only returns a single :py:class:`~pypermission.core.PermissionNode` for the
`admin` role. In section :ref:`introduction.access_checking` we will show that
the `admin` role has indeed access to all
:py:class:`~pypermission.core.PermissionNode`\ s of the ``auth`` object.

>>> set(auth.role_get_permissions(rid='admin'))
{<RootPermissionNode.ROOT_: '*'>}

.. _introduction.access_checking:

Access Checking
---------------

To check, if a subject can obtain a permission, use the
:py:meth:`~pypermission.serial.core.SerialAuthority.subject_obtains_permission`
method (similarly to check if a role can obtain a given permission, use the
:py:meth:`~pypermission.serial.core.SerialAuthority.role_obtains_permission` method).

.. warning::
   In contrast to the similar ``CheckAccess`` function defined in the RBAC standard
   published by ANSI/INCITs\ [#INCITS2004]_\ [#INCITS2017]_, our methods will
   check for possible hierarchical ordering of roles. This means the method can
   still return ``True``, even if the permission has not directly been assigned to
   a given role but is inferred through inheritance. For more on this topic see TODO: example link,
   as this introduction is mainly focussed on flat RBAC.

As a `user`, `John` should be allowed to `join` a chat, however he should not be able
to obtain the permission to `invite`.

>>> auth.subject_obtains_permission(sid='John', node=CNs.JOIN)
True

>>> auth.subject_obtains_permission(sid='John', node=CNs.INV)
False

As both a `user` and a `moderator`, `Bob` should be able to `join` and `invite` a chat. The
`change_role` permission however should be denied to him:

>>> auth.subject_obtains_permission(sid='Bob', node=CNs.JOIN)
True

>>> auth.subject_obtains_permission(sid='Bob', node=CNs.INV)
True

>>> auth.subject_obtains_permission(sid='Bob', node=CNs.CHANGE_ROLE)
False

Finally, for our `admin` `Alice`, we expect access to all of the functions above:

>>> auth.subject_obtains_permission(sid='Alice', node=CNs.JOIN)
True

>>> auth.subject_obtains_permission(sid='Alice', node=CNs.INV)
True

>>> auth.subject_obtains_permission(sid='Alice', node=CNs.CHANGE_ROLE)
True

Storing And Loading State
-------------------------

To store the state of the authority to a file, use the
:py:meth:`~pypermission.serial.core.SerialAuthority.save_file` method. The file
format will be determined by the file extension given. Recognized extensions are
``.json``, ``.yml`` and ``.yaml`` for either JSON or YAML formatting. Note that
YAML formatting requires the ``PyYAML`` library to be available to the python
runtime.

.. invisible-code-block: python

    from pathlib import Path
    import os
    cwd = Path.cwd()
    os.chdir(cwd / "docs/pages/")


>>> from pathlib import Path
>>> auth.save_file(path=Path("introduction.yaml"), sort_keys=True)

.. invisible-code-block: python

    os.chdir(cwd)

.. literalinclude:: introduction.yaml
   :language: yaml

TODO
----

* Document ``del_subject``, ``del_role``, ``role_deassign_subject``,
  ``role_revoke_permission``, ``role_add_inheritance``
* Do we have a "list permissions" function (Permission review subsubsection)?

.. rubric:: Footnotes

.. [#NIST_RBAC] The NIST model for role-based access control: towards a unified standard - https://doi.org/10.1145/344287.344301
.. [#WIKI_SOD] Wikipedia - Separation of duties (SOD) - https://en.wikipedia.org/wiki/Separation_of_duties
.. [#sqlalchemy] SQLAlchemy - The Python SQL Toolkit and Object Relational Mapper - https://www.sqlalchemy.org/
.. [#INCITS2004] INCITS 359-2004: Information technology - Role Based Access Control - <https://profsandhu.com/journals/tissec/ANSI+INCITS+359-2004.pdf>
.. [#INCITS2017] INCITS 359-2012[R2017]: Information technology - Role Based Access Control - <https://standards.incits.org/apps/group_public/project/details.php?project_id=1906>