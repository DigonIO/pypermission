import pathlib

from pypermission.serial import SerialAuthority

from ..helpers import TownyPermissionNode as TPN

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

path = pathlib.Path(__file__).parent.absolute()


def test_load_file_yaml():
    auth = SerialAuthority(nodes=TPN)

    auth.load_file(path=path / "save_file.yaml")

    assert set(auth._groups.keys()) == {FOOD, ANIMAL_BASED, PLANT_BASED}
    assert set(auth._subjects.keys()) == {
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
    assert auth.group_get_member_subjects(gid=PLANT_BASED) == {ORANGE, APPLE, PEAR, BANANA}

    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_TOWN) == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_NATION) == False

    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_TOWN) == False
    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_NATION) == True

    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt") == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_BUILD_X, payload="gold") == True
    assert (
        auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt") == False
    )
    assert (
        auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold") == False
    )

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

    assert (
        auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt") == True
    )
    assert (
        auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold") == True
    )
