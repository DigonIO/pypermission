==================
Quick Start (RBAC)
==================

To get started, assume we are writing a RBAC permission system for a chat based online
support service. The permission system provides three group type for accounts, normal `user`, `moderator` and `admin`.

User accounts should be able to:

* Messaging in joined chat rooms
* Join a room by invitation
* Leave chat room

Moderator accounts should have all of the above permissions and additionally:

* Join any chat room
* Invite anyone to chat room
* Ban other `user` (not admin or moderator accounts) from chat room

Admin accounts should additionally be able to:

* Ban anyone from chat

First the given features have to be registered to an Authority. Define the features
to a ``PermissionNode``\ s object and instantiate an ``Authority`` with the given
``Nodes``:

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
        MSG_ = "chat.message.*"
        MSG_X = "chat.message.<x>"

    CNs = ChatNodes

    auth = SerialAuthority(nodes=CNs)

Next the different groups with their respective permissions have to be registered
to the authority. The following file defines the relations mentioned above:

.. literalinclude:: chat_rooms.yaml
   :language: yaml

Additionally the file already defines a couple of accounts:

* `Alice` is a member of the `admin` and `user` groups
* `Bob` is a member of the `moderator` and `user` groups
* `John` is a member of the `user` group only

From the file we can infer, that currently the following chat `rooms`\ s exist:

* `org-moderators`, an organizational chat room where only moderators and admins can message
* Chat rooms for `room`\ s ``12``, ``212`` and ``501`` where user `John` and `moderator`
  `Bob` are together in room ``501``.

The defined relations can directly be assigned to the authority from the file:

.. invisible-code-block: python

    auth.load_file(path="docs/pages/chat_rooms.yaml")

.. skip: next

.. code-block:: pycon

    >>> auth.load_file(path="chat_rooms.yaml")

We can now test, if the permissions from above are available as expected. User `John`
should be able to join a room he was invited to. This can be tested via the
:py:func:`~pypermission.serial.core.SerialAuthority.subject_has_permission`

>>> auth.subject_has_permission(sid="John", node=CNs.JOIN_INV)
True

As a basic `user` 
