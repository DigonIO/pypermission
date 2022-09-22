from pypermission.typing import PermissionNode


class TownyPermissionNode(PermissionNode):
    # Permission nodes for testing inspired be the towny permission nodes
    # https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java
    TOWNY_ = "towny.*"
    TOWNY_CHAT_ = "towny.chat.*"
    TOWNY_CHAT_TOWN = "towny.chat.town"
    TOWNY_CHAT_NATION = "towny.chat.nation"
    TOWNY_CHAT_GLOBAL = "towny.chat.global"
    TOWNY_WILD_ = "towny.wild.*"
    TOWNY_WILD_BUILD_ = "towny.wild.build.*"
    TOWNY_WILD_BUILD_X = "towny.wild.build.<x>"
    TOWNY_WILD_DESTROY_ = "towny.wild.destroy.*"
    TOWNY_WILD_DESTROY_X = "towny.wild.destroy.<x>"
