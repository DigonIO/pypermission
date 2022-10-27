from pypermission.serial import SerialAuthority
from pypermission.sqlalchemy import SQLAlchemyAuthority
from pypermission.core import PermissionNode

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

ID_ALL_STR = "all"
ID_100_STR = "100"
ID_100_INT = 100
ID_1_STR = "1"
ID_1_INT = 1
ID_TWO_STR = "two"
ID_2_INT = 2


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


def assert_loaded_authority(auth: SerialAuthority | SQLAlchemyAuthority):
    # The authority tested here should fulfil the properties of the two save files
    # `./serial/save_file.yaml` and `./serial/save_file.json`

    assert auth.get_groups() == {FOOD, ANIMAL_BASED, PLANT_BASED}

    assert auth.get_subjects() == {
        EGG,
        SPAM,
        HAM,
        ORANGE,
        APPLE,
        PEAR,
        BANANA,
    }

    assert auth.group_get_member_groups(gid=FOOD) == {ANIMAL_BASED, PLANT_BASED}
    assert auth.group_get_parent_groups(gid=ANIMAL_BASED) == {FOOD}
    assert auth.group_get_parent_groups(gid=PLANT_BASED) == {FOOD}

    assert auth.group_get_member_subjects(gid=ANIMAL_BASED) == {EGG, SPAM, HAM}
    assert auth.subject_get_groups(sid=EGG) == {ANIMAL_BASED}

    assert auth.group_get_member_subjects(gid=PLANT_BASED) == {ORANGE, APPLE, PEAR, BANANA}
    assert auth.subject_get_groups(sid=ORANGE) == {PLANT_BASED}

    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_GLOBAL) == True

    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_TOWN) == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_NATION) == False

    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_TOWN) == False
    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_NATION) == True

    # test EGG
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt") == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_BUILD_X, payload="gold") == True
    assert (
        auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt") == False
    )
    assert (
        auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold") == False
    )

    # test PEAR
    assert (
        auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt") == False
    )
    assert (
        auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_WILD_BUILD_X, payload="gold") == False
    )
    assert (
        auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt") == True
    )
    assert (
        auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold") == True
    )

    # test HAM
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt") == True
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="gold") == True
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="iron") == True
    assert (
        auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt") == True
    )
    assert (
        auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold") == True
    )
