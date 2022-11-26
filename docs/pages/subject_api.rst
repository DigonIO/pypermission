===========
Subject API
===========

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

Subject management API
======================

Create some subject IDs.

.. code-block:: pycon

    >>> EGG = "egg"
    >>> SPAM = "spam"
    >>> HAM = "ham"

Add subjects to the authority.

.. code-block:: pycon

    >>> auth.add_subject(sid=EGG)
    >>> auth.add_subject(sid=SPAM)
    >>> auth.add_subject(sid=HAM)

.. code-block:: pycon

    >>> sids: set[EntityID] = auth.get_subjects()

    >>> EGG in sids
    True

    >>> SPAM in sids
    True

    >>> HAM in sids
    True

    >>> len(sids)
    3

.. code-block:: pycon

    >>> auth.rem_subject(sid=HAM)

.. code-block:: pycon

    >>> sids: set[EntityID] = auth.get_subjects()

    >>> EGG in sids
    True

    >>> SPAM in sids
    True

    >>> HAM in sids
    False

    >>> len(sids)
    2

Subject permission API
======================

.. code-block:: pycon

    >>> auth.subject_add_permission(sid=EGG, node=BuildinPN.COMMAND_STATS)

.. code-block:: pycon

    >>> auth.subject_has_permission(sid=EGG, node=BuildinPN.COMMAND_STATS)
    True

    >>> auth.subject_has_permission(sid=EGG, node=BuildinPN.COMMAND_RESPAWN)
    False

.. code-block:: pycon

    >>> auth.subject_rem_permission(sid=EGG, node=BuildinPN.COMMAND_STATS)

.. code-block:: pycon

    >>> auth.subject_has_permission(sid=EGG, node=BuildinPN.COMMAND_STATS)
    False
