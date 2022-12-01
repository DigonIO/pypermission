=========
Role API
=========

Prepare a authority with example permissions.

.. code-block:: pycon

    >>> from pypermission.json import Authority, PermissionNode, EntityID

    >>> class BuildinPN(PermissionNode):
    ...     ADMIN = "admin"  # leaf
    ...     COMMAND_ = "command.*"  # parent
    ...     COMMAND_STATS = "command.stats"  # leaf
    ...     COMMAND_RESPAWN = "command.respawn"  # leaf
    ...

    >>> auth = Authority(nodes=BuildinPN)  # register buildin nodes

Graph based role structure
===========================

Create some dummy role IDs.

.. code-block:: pycon

    >>> # EntityID = str | int
    >>> GID_FOOD = "food"
    >>> GID_ANIMAL_BASED = "animal_based"
    >>> GID_PLANT_BASED = "plant_based"

Register the roles at the authority.

.. code-block:: pycon

    >>> auth.add_role(rid=GID_FOOD)
    >>> auth.add_role(rid=GID_ANIMAL_BASED)
    >>> auth.add_role(rid=GID_PLANT_BASED)

Create a graph based role structure. Child roles inherit all permissions from their parents.

.. code-block:: pycon

    >>> auth.role_add_inheritance(rid=GID_FOOD, cid=GID_ANIMAL_BASED)
    >>> auth.role_add_inheritance(rid=GID_FOOD, cid=GID_PLANT_BASED)

Check from the child perspective.

.. code-block:: pycon

    >>> pids_animal = auth.role_get_parent_roles(rid=GID_ANIMAL_BASED)
    >>> pids_plant = auth.role_get_parent_roles(rid=GID_PLANT_BASED)
    >>> pids_animal == pids_plant == {GID_FOOD}
    True

Check from the parent perspective.

.. code-block:: pycon

    >>> cids = auth.role_get_child_roles(rid=GID_FOOD)
    >>> cids == {GID_ANIMAL_BASED, GID_PLANT_BASED}
    True

Subjects as part of a role
===========================

Create some dummy subject IDs

.. code-block:: pycon

    >>> # EntityID = str | int
    >>> SID_EGG = "egg"
    >>> SID_SPAM = "spam"

    >>> SID_ORANGE = "orange"
    >>> SID_APPLE = "apple"

Register the subjects add the authority.

.. code-block:: pycon

    >>> auth.add_subject(sid=SID_EGG)
    >>> auth.add_subject(sid=SID_SPAM)

    >>> auth.add_subject(sid=SID_ORANGE)
    >>> auth.add_subject(sid=SID_APPLE)

Add subjects to a roles.

.. code-block:: pycon

    >>> auth.role_assign_subject(rid=GID_ANIMAL_BASED, sid=SID_EGG)
    >>> auth.role_assign_subject(rid=GID_ANIMAL_BASED, sid=SID_SPAM)

    >>> auth.role_assign_subject(rid=GID_PLANT_BASED, sid=SID_ORANGE)
    >>> auth.role_assign_subject(rid=GID_PLANT_BASED, sid=SID_APPLE)

Check the member subject IDs.

.. code-block:: pycon

    >>> sids = auth.role_get_subjects(rid=GID_ANIMAL_BASED)
    >>> sids == {SID_EGG, SID_SPAM}
    True

Check the role IDs a subject is member of.

.. code-block:: pycon

    >>> rids = auth.subject_get_roles(sid=SID_EGG)
    >>> rids == {GID_ANIMAL_BASED}
    True

Permission inheritance between roles and subjects
==================================================

.. code-block:: pycon

    >>> auth.role_add_permission(rid=GID_FOOD, node=BuildinPN.ADMIN)

Child roles inherit the permissions of the parent role.

.. code-block:: pycon

    >>> auth.role_inherits_permission(rid=GID_ANIMAL_BASED, node=BuildinPN.ADMIN)
    True

    >>> auth.role_inherits_permission(rid=GID_PLANT_BASED, node=BuildinPN.ADMIN)
    True

Subjects inherit the permissions of the roles their are member of.

.. code-block:: pycon

    >>> auth.subject_inherits_permission(sid=SID_EGG, node=BuildinPN.ADMIN)
    True

    >>> auth.subject_inherits_permission(sid=SID_ORANGE, node=BuildinPN.ADMIN)
    True
