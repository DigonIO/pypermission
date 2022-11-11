=========
Group API
=========

Prepare a authority with example permissions.

.. code-block:: pycon

    >>> from pypermission.json import Authority, PermissionNode, EntityID

    >>> class BuildinPN(PermissionNode):
    ...     ADMIN = "admin"  # leaf
    ...     COMMAND_ = "command.*"  # parent
    ...     COMMAND_STATS = "command.stats"  # leaf
    ...     COMMAND_RESPAWN = "command.respawn"  # leaf

    >>> auth = Authority(nodes=BuildinPN)  # register buildin nodes

Graph based group structure
===========================

Create some dummy group IDs.

.. code-block:: pycon

    >>> # EntityID = str | int
    >>> GID_FOOD = "food"
    >>> GID_ANIMAL_BASED = "animal_based"
    >>> GID_PLANT_BASED = "plant_based"

Register the groups at the authority.

.. code-block:: pycon

    >>> auth.add_group(gid=GID_FOOD)
    >>> auth.add_group(gid=GID_ANIMAL_BASED)
    >>> auth.add_group(gid=GID_PLANT_BASED)

Create a graph based group structure. Child groups inherit all permissions from their parents.

.. code-block:: pycon

    >>> auth.group_add_child_group(gid=GID_FOOD, cid=GID_ANIMAL_BASED)
    >>> auth.group_add_child_group(gid=GID_FOOD, cid=GID_PLANT_BASED)

Check from the child perspective.

.. code-block:: pycon

    >>> pids_animal = auth.group_get_parent_groups(gid=GID_ANIMAL_BASED)
    >>> pids_plant = auth.group_get_parent_groups(gid=GID_PLANT_BASED)
    >>> pids_animal == pids_plant == {GID_FOOD}
    True

Check from the parent perspective.

.. code-block:: pycon

    >>> cids = auth.group_get_child_groups(gid=GID_FOOD)
    >>> cids == {GID_ANIMAL_BASED, GID_PLANT_BASED}
    True

Subjects as part of a group
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

Add subjects to a groups.

.. code-block:: pycon

    >>> auth.group_add_subject(gid=GID_ANIMAL_BASED, sid=SID_EGG)
    >>> auth.group_add_subject(gid=GID_ANIMAL_BASED, sid=SID_SPAM)

    >>> auth.group_add_subject(gid=GID_PLANT_BASED, sid=SID_ORANGE)
    >>> auth.group_add_subject(gid=GID_PLANT_BASED, sid=SID_APPLE)

Check the member subject IDs.

.. code-block:: pycon

    >>> sids = auth.group_get_subjects(gid=GID_ANIMAL_BASED)
    >>> sids == {SID_EGG, SID_SPAM}
    True

Check the group IDs a subject is member of.

.. code-block:: pycon

    >>> gids = auth.subject_get_groups(sid=SID_EGG)
    >>> gids == {GID_ANIMAL_BASED}
    True

Permission inheritance between groups and subjects
==================================================

.. code-block:: pycon

    >>> auth.group_add_permission(gid=GID_FOOD, node=BuildinPN.ADMIN)

Child groups inherit the permissions of the parent group.

.. code-block:: pycon

    >>> auth.group_has_permission(gid=GID_ANIMAL_BASED, node=BuildinPN.ADMIN)
    True

    >>> auth.group_has_permission(gid=GID_PLANT_BASED, node=BuildinPN.ADMIN)
    True

Subjects inherit the permissions of the groups their are member of.

.. code-block:: pycon

    >>> auth.subject_has_permission(sid=SID_EGG, node=BuildinPN.ADMIN)
    True

    >>> auth.subject_has_permission(sid=SID_ORANGE, node=BuildinPN.ADMIN)
    True