import pytest

from pypermission.error import GroupCycleError, UnknownPermissionNodeError
from pypermission.serial import SerialAuthority

from ..helpers import TownyPermissionNode
from ..helpers import TownyPermissionNode as TPN
from ..helpers import serial_authority

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


def test_cyclic_groups():
    auth = SerialAuthority()

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.group_add_member_group(gid=FOOD, member_gid=ANIMAL_BASED)
    auth.group_add_member_group(gid=ANIMAL_BASED, member_gid=PLANT_BASED)

    with pytest.raises(GroupCycleError):
        auth.group_add_member_group(gid=PLANT_BASED, member_gid=FOOD)


def test_unknown_perm_node():
    auth = SerialAuthority()

    auth.add_subject(sid=APPLE)

    auth.add_group(gid=FOOD)

    with pytest.raises(UnknownPermissionNodeError):
        auth.subject_add_permission(sid=APPLE, node=TownyPermissionNode.TOWNY_CHAT_)

    with pytest.raises(UnknownPermissionNodeError):
        auth.group_add_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_)
