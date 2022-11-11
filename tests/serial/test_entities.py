import pytest

from pypermission.error import RoleCycleError, UnknownPermissionNodeError
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

    assert auth.role_has_permission(rid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL) == True
    auth.role_rm_node(rid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL)
    assert auth.role_has_permission(rid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL) == False

    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_) == True
    auth.subject_rm_node(sid=HAM, node=TPN.TOWNY_WILD_)
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_) == False


def test_subject_get_permissions(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.subject_get_nodes(sid=EGG) == {}
    assert auth.subject_get_nodes(sid=HAM) == {TPN.TOWNY_WILD_: set()}


def test_role_get_permissions(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.role_get_nodes(rid=FOOD) == {TPN.TOWNY_CHAT_GLOBAL: set()}
    assert auth.role_get_nodes(rid=ANIMAL_BASED) == {
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
    assert auth.role_get_member_subjects(rid=PLANT_BASED) == {
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
    assert auth.role_get_member_subjects(rid=PLANT_BASED) == {
        APPLE,
        PEAR,
        BANANA,
    }


def test_rm_parent_role(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.get_roles() == {FOOD, ANIMAL_BASED, PLANT_BASED}
    assert auth.role_get_parent_roles(rid=ANIMAL_BASED) == {FOOD}

    auth.rm_role(rid=FOOD)

    assert auth.get_roles() == {ANIMAL_BASED, PLANT_BASED}
    assert auth.role_get_parent_roles(rid=ANIMAL_BASED) == set()


def test_rm_child_role(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.get_roles() == {FOOD, ANIMAL_BASED, PLANT_BASED}
    assert auth.role_get_member_roles(rid=FOOD) == {ANIMAL_BASED, PLANT_BASED}
    assert auth.subject_get_roles(sid=EGG) == {ANIMAL_BASED}

    auth.rm_role(rid=ANIMAL_BASED)

    assert auth.get_roles() == {FOOD, PLANT_BASED}
    assert auth.role_get_member_roles(rid=FOOD) == {PLANT_BASED}
    assert auth.subject_get_roles(sid=EGG) == set()


def test_rm_member_role(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.role_get_member_roles(rid=FOOD) == {ANIMAL_BASED, PLANT_BASED}
    assert auth.role_get_parent_roles(rid=ANIMAL_BASED) == {FOOD}

    auth.role_rm_member_role(rid=FOOD, member_rid=ANIMAL_BASED)

    assert auth.role_get_member_roles(rid=FOOD) == {PLANT_BASED}
    assert auth.role_get_parent_roles(rid=ANIMAL_BASED) == set()


def test_rm_member_subject(serial_authority: SerialAuthority):
    auth = serial_authority

    assert auth.role_get_member_subjects(rid=ANIMAL_BASED) == {EGG, SPAM, HAM}
    assert auth.subject_get_roles(sid=EGG) == {ANIMAL_BASED}

    auth.role_rm_member_subject(rid=ANIMAL_BASED, member_sid=EGG)

    assert auth.role_get_member_subjects(rid=ANIMAL_BASED) == {SPAM, HAM}
    assert auth.subject_get_roles(sid=EGG) == set()


def test_unknown_perm_node():
    auth = SerialAuthority()

    auth.new_subject(sid=APPLE)

    auth.new_role(rid=FOOD)

    with pytest.raises(UnknownPermissionNodeError):
        auth.subject_add_node(sid=APPLE, node=TownyPermissionNode.TOWNY_CHAT_)

    with pytest.raises(UnknownPermissionNodeError):
        auth.role_add_node(rid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_)
