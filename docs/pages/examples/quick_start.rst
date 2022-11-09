===========
Quick Start
===========

To get started, assume we are writing a permission system for a chat based online
support service.

Users should be able to:

* Join a room by invitation
* Leave chat room
* Messaging in joined chat rooms

Moderators should have all of the above permissions and additionally:

* Join any chat room
* Create own chat rooms
* Close own chat rooms
* Invite anyone to own chat room
* Kick other non-admins from own chat room

Admins should additionally (and everything else):

* Create/close any chat room
* Kick anyone from chat

First the given features have to be mapped to ``PermissionNode``\ s:

.. code-block:: pycon

    >>> from pypermission import PermissionNode

    >>> class Nodes(PermissionNode):
    ...     CHAT_ = "chat.*"
    ...     CHAT_CREATE_ = "chat.create.*"
    ...     CHAT_CREATE_OWN = "chat.create.own"
    ...     CHAT_CREATE_ANY = "chat.create.any"
    ...     CHAT_CLOSE = "chat.close"
    ...     CHAT_CLOSE_OWN = "chat.close.own"
    ...     CHAT_CLOSE_ANY = "chat.close.any"
    ...     CHAT_INVITE = "chat.invite"
    ...     CHAT_KICKUSER_ = "chat.kickuser"
    ...     CHAT_KICK_OTHER = "chat.kick.other"
    ...     CHAT_KICK_ANY = "chat.kick.any"
    ...     CHAT_JOIN_ = "chat.join.*"
    ...     CHAT_JOIN_INVITED = "chat.join.invited"
    ...     CHAT_JOIN_ANY = "chat.join.any"
    ...     CHAT_LEAVE = "chat.leave"
    ...     CHAT_MESSAGE_ = "chat.message.*"
    ...     CHAT_MESSAGE_JOINED = "chat.message.joined"
    ...     CHAT_MESSAGE_ANY = "chat.message.any"



Next the different groups with their respective permissions have to be registered
to an Authority. This can be defined with the following file:

literalinclude:: chat_rooms.yaml


.. code-block:: pycon

    >>> from pypermission.serial import SerialAuthority
    >>> auth = SerialAuthority(nodes=Nodes)
    >>> import os
    >>> tmp = getfixture('serial_authority_typed')
    >>> tmp

Next...