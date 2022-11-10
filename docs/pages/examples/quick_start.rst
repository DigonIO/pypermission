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

First the given features have to be registered to an Authority. Define the features
to a ``PermissionNode``\ s object and instantiate an ``Authority`` with the given
``Nodes``:

.. code-block:: python

    from pypermission import PermissionNode
    from pypermission.serial import SerialAuthority

    class Nodes(PermissionNode):
        CHAT_ = "chat.*"
        CHAT_CREATE_ = "chat.create.*"
        CHAT_CREATE_OWN = "chat.create.own"
        CHAT_CREATE_ANY = "chat.create.any"
        CHAT_CLOSE_ = "chat.close.*"
        CHAT_CLOSE_OWN = "chat.close.own"
        CHAT_CLOSE_ANY = "chat.close.any"
        CHAT_INVITE = "chat.invite"
        CHAT_KICK_ = "chat.kick.*"
        CHAT_KICK_USER = "chat.kick.user"
        CHAT_KICK_OTHER = "chat.kick.other"
        CHAT_KICK_ANY = "chat.kick.any"
        CHAT_JOIN_ = "chat.join.*"
        CHAT_JOIN_INVITED = "chat.join.invited"
        CHAT_JOIN_ANY = "chat.join.any"
        CHAT_LEAVE = "chat.leave"
        CHAT_MESSAGE_ = "chat.message.*"
        CHAT_MESSAGE_JOINED = "chat.message.joined"
        CHAT_MESSAGE_ANY = "chat.message.any"

    auth = SerialAuthority(nodes=Nodes)

Next the different groups with their respective permissions have to be registered
to the authority. The following file defines the relations mentioned above:

.. literalinclude:: chat_rooms.yaml
   :language: yaml

Additionally the file already defines a couple of accounts:

* Alice is a member of the `admin` and `user` groups
* Bob is a member of the `moderator` and `user` groups
* John is a member of the `user` group only

The defined relations can directly be assigned to the authority from the file:

.. invisible-code-block: python

    auth.load_file(path="docs/pages/examples/chat_rooms.yaml")

.. skip: next

.. code-block:: pycon

    >>> auth.load_file(path="chat_rooms.yaml")

We can now test, if the permissions are available as expected...