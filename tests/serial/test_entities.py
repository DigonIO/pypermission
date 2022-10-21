import pytest

from pypermission.error import GroupCycleError, UnknownPermissionNodeError
from pypermission.serial import SerialAuthority

from ..helpers import TownyPermissionNode
from ..helpers import TownyPermissionNode as TPN
from .test_persistency import assert_loaded_authority

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


def test_basic_integration(serial_authority: SerialAuthority):
    assert_loaded_authority(auth=serial_authority)


def test_rm_permission(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.group_has_permission(gid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL) == True
    auth.group_rm_permission(gid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL)
    assert auth.group_has_permission(gid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL) == False

    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_) == True
    auth.subject_rm_permission(sid=HAM, node=TPN.TOWNY_WILD_)
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_) == False


def test_subject_get_permissions(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.subject_get_permissions(sid=EGG) == {}
    assert auth.subject_get_permissions(sid=HAM) == {TPN.TOWNY_WILD_: set()}


def test_group_get_permissions(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.group_get_permissions(gid=FOOD) == {TPN.TOWNY_CHAT_GLOBAL: set()}
    assert auth.group_get_permissions(gid=ANIMAL_BASED) == {
        TPN.TOWNY_CHAT_TOWN: set(),
        TPN.TOWNY_WILD_BUILD_X: {"dirt", "gold"},
    }


def test_rm_subject(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.get_subjects() == {
        EGG,
        SPAM,
        HAM,
        ORANGE,
        APPLE,
        PEAR,
        BANANA,
    }
    assert auth.group_get_member_subjects(gid=PLANT_BASED) == {
        ORANGE,
        APPLE,
        PEAR,
        BANANA,
    }

    auth.rm_subject(sid=ORANGE)

    assert auth.get_subjects() == {
        EGG,
        SPAM,
        HAM,
        APPLE,
        PEAR,
        BANANA,
    }
    assert auth.group_get_member_subjects(gid=PLANT_BASED) == {
        APPLE,
        PEAR,
        BANANA,
    }


def test_rm_parent_group(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.get_groups() == {FOOD, ANIMAL_BASED, PLANT_BASED}
    assert auth.group_get_parent_groups(gid=ANIMAL_BASED) == {FOOD}

    auth.rm_group(gid=FOOD)

    assert auth.get_groups() == {ANIMAL_BASED, PLANT_BASED}
    assert auth.group_get_parent_groups(gid=ANIMAL_BASED) == set()


def test_rm_child_group(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.get_groups() == {FOOD, ANIMAL_BASED, PLANT_BASED}
    assert auth.group_get_member_groups(gid=FOOD) == {ANIMAL_BASED, PLANT_BASED}
    assert auth.subject_get_groups(sid=EGG) == {ANIMAL_BASED}

    auth.rm_group(gid=ANIMAL_BASED)

    assert auth.get_groups() == {FOOD, PLANT_BASED}
    assert auth.group_get_member_groups(gid=FOOD) == {PLANT_BASED}
    assert auth.subject_get_groups(sid=EGG) == set()


def test_rm_member_group(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.group_get_member_groups(gid=FOOD) == {ANIMAL_BASED, PLANT_BASED}
    assert auth.group_get_parent_groups(gid=ANIMAL_BASED) == {FOOD}

    auth.group_rm_member_group(gid=FOOD, member_gid=ANIMAL_BASED)

    assert auth.group_get_member_groups(gid=FOOD) == {PLANT_BASED}
    assert auth.group_get_parent_groups(gid=ANIMAL_BASED) == set()


def test_rm_member_subject(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.group_get_member_subjects(gid=ANIMAL_BASED) == {EGG, SPAM, HAM}
    assert auth.subject_get_groups(sid=EGG) == {ANIMAL_BASED}

    auth.group_rm_member_subject(gid=ANIMAL_BASED, member_sid=EGG)

    assert auth.group_get_member_subjects(gid=ANIMAL_BASED) == {SPAM, HAM}
    assert auth.subject_get_groups(sid=EGG) == set()


def test_unknown_perm_node():
    auth = SerialAuthority()

    auth.add_subject(sid=APPLE)

    auth.add_group(gid=FOOD)

    with pytest.raises(UnknownPermissionNodeError):
        auth.subject_add_permission(sid=APPLE, node=TownyPermissionNode.TOWNY_CHAT_)

    with pytest.raises(UnknownPermissionNodeError):
        auth.group_add_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_)
