from pypermission.json import Authority, PermissionNode, EntityID


class BuildinPN(PermissionNode):
    ADMIN = "admin"  # leaf
    COMMAND_ = "command.*"  # parent
    COMMAND_STATS = "command.stats"  # leaf
    COMMAND_RESPAWN = "command.respawn"  # leaf


class PluginPN(PermissionNode):
    # Permission nodes for testing inspired be the towny permission nodes
    # https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java
    TOWNY_ = "towny.*"  # parent
    TOWNY_CHAT_ = "towny.chat.*"  # parent
    TOWNY_CHAT_TOWN = "towny.chat.town"  # leaf
    TOWNY_CHAT_NATION = "towny.chat.nation"  # leaf
    TOWNY_CHAT_GLOBAL = "towny.chat.global"  # leaf
    TOWNY_WILD_ = "towny.wild.*"  # parent
    TOWNY_WILD_BUILD_ = "towny.wild.build.*"  # parent
    TOWNY_WILD_BUILD_X = "towny.wild.build.<x>"  # leaf w/ payload
    TOWNY_WILD_DESTROY_ = "towny.wild.destroy.*"  # parent
    TOWNY_WILD_DESTROY_X = "towny.wild.destroy.<x>"  # leaf w/ payload


auth = Authority(nodes=BuildinPN)  # register buildin nodes
auth.register_permission_nodes(nodes=PluginPN)  # method for plugin based node registration

GROUP_ID: EntityID = "group_foo"  # the group ID can be str or int
auth.add_group(gid=GROUP_ID)

auth.group_add_permission(gid=GROUP_ID, node=PluginPN.TOWNY_CHAT_)
auth.group_add_permission(gid=GROUP_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="iron")
auth.group_add_permission(gid=GROUP_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="gold")

SUBJECT_ID: EntityID = "user_bar"  # the subject ID can be str or int
auth.add_subject(sid=SUBJECT_ID)
auth.group_add_subject(gid=GROUP_ID, sid=SUBJECT_ID)

auth.subject_add_permission(sid=SUBJECT_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="diamond")

if auth.subject_has_permission(sid=SUBJECT_ID, node=PluginPN.TOWNY_CHAT_TOWN):
    print("Parent permission provided by the group.")

if auth.subject_has_permission(sid=SUBJECT_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="iron"):
    print("Leaf w/ payload permission provided by the group")

if auth.subject_has_permission(
    sid=SUBJECT_ID, node=PluginPN.TOWNY_WILD_DESTROY_X, payload="diamond"
):
    print("Leaf w/ payload permission provided by the subject itself")
