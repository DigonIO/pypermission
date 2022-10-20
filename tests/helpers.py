import pytest

from pypermission.core import PermissionNode
from pypermission.serial import SerialAuthority

EGG = "egg"
SPAM = "spam"
HAM = "ham"

ORANGE = "orange"
APPLE = "apple"
PEAR = "pear"
BANANA = "banana"

FOOD = "food"
ANIMAL_BASED = "animal_based"
PLANT_BASED = "plant_based"


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


TPN = TownyPermissionNode


@pytest.fixture
def serial_authority() -> SerialAuthority:
    # The authority created here should fulfil the properties of the two save files
    # `./serial/save_file.yaml` and `./serial/save_file.json`
    auth = SerialAuthority(nodes=TPN)

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.add_subject(sid=EGG)
    auth.add_subject(sid=SPAM)
    auth.add_subject(sid=HAM)

    auth.add_subject(sid=ORANGE)
    auth.add_subject(sid=APPLE)
    auth.add_subject(sid=PEAR)
    auth.add_subject(sid=BANANA)

    auth.group_add_member_group(gid=FOOD, member_gid=ANIMAL_BASED)
    auth.group_add_member_group(gid=FOOD, member_gid=PLANT_BASED)

    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=EGG)
    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=SPAM)
    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=HAM)

    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=ORANGE)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=APPLE)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=PEAR)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=BANANA)

    auth.group_add_permission(gid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL)

    auth.group_add_permission(gid=ANIMAL_BASED, node=TPN.TOWNY_CHAT_TOWN)
    auth.group_add_permission(gid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt")
    auth.group_add_permission(gid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="gold")

    auth.group_add_permission(gid=PLANT_BASED, node=TPN.TOWNY_CHAT_NATION)
    auth.group_add_permission(gid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt")
    auth.group_add_permission(gid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold")

    auth.subject_add_permission(sid=HAM, node=TPN.TOWNY_WILD_)

    return auth
