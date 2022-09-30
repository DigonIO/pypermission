import pytest

from pypermission.error import GroupCycleError, UnknownPermissionNodeError
from pypermission.json import Authority

from ..helpers import TownyPermissionNode

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


def test_subject_perms_without_groups():
    auth = Authority(nodes=TownyPermissionNode)

    ### EGG ### ADD PERMS ##########################################################################
    auth.add_subject(s_id=EGG)
    auth.subject_add_permission(s_id=EGG, node=Authority.root_node())

    assert auth.subject_has_permission(s_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(s_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_NATION) == True
    assert (
        auth.subject_has_permission(
            s_id=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="dummy"
        )
        == True
    )
    assert (
        auth.subject_has_permission(s_id=EGG, node=TownyPermissionNode.TOWNY_WILD_DESTROY_) == True
    )

    ### SPAM ### ADD PERMS ##########################################################################
    auth.add_subject(s_id=SPAM)
    auth.subject_add_permission(s_id=SPAM, node=TownyPermissionNode.TOWNY_CHAT_)
    auth.subject_add_permission(s_id=SPAM, node=TownyPermissionNode.TOWNY_WILD_)

    assert (
        auth.subject_has_permission(s_id=SPAM, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL) == True
    )
    assert (
        auth.subject_has_permission(s_id=SPAM, node=TownyPermissionNode.TOWNY_CHAT_NATION) == True
    )
    assert (
        auth.subject_has_permission(
            s_id=SPAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )
    assert (
        auth.subject_has_permission(s_id=SPAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_) == True
    )

    ### HAM ### ADD PERMS ##########################################################################
    auth.add_subject(s_id=HAM)

    auth.subject_add_permission(s_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    assert (
        auth.subject_has_permission(s_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL) == False
    )
    assert auth.subject_has_permission(s_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN) == True

    auth.subject_add_permission(s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )

    auth.subject_add_permission(
        s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    auth.subject_add_permission(
        s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_2"
    )
    assert (
        auth.subject_has_permission(
            s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_2"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_x"
        )
        == False
    )

    ### HAM ### REM PERMS ##########################################################################
    auth.subject_rem_permission(s_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    assert auth.subject_has_permission(s_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN) == False

    auth.subject_rem_permission(s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == False
    )

    auth.subject_rem_permission(
        s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    assert (
        auth.subject_has_permission(
            s_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == False
    )


# Just a short integration test, because groups using the same permission backend like subjects
def test_group_perms():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_group(ANIMAL_BASED)

    auth.group_add_permission(gid=ANIMAL_BASED, node=Authority.root_node())
    assert (
        auth.group_has_permission(gid=ANIMAL_BASED, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
        == True
    )
    assert (
        auth.group_has_permission(
            gid=ANIMAL_BASED,
            node=TownyPermissionNode.TOWNY_WILD_DESTROY_X,
            payload="payload_1",
        )
        == True
    )


def test_subject_perms_with_groups():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.add_subject(s_id=EGG)

    auth.group_add_subject(gid=ANIMAL_BASED, s_id=EGG)
    auth.group_add_subject(gid=PLANT_BASED, s_id=EGG)
    # yeah chickens are some kind of plants too...

    auth.group_add_permission(gid=ANIMAL_BASED, node=TownyPermissionNode.TOWNY_CHAT_)
    auth.group_add_permission(gid=PLANT_BASED, node=TownyPermissionNode.TOWNY_WILD_)

    assert auth.subject_has_permission(s_id=EGG, node=TownyPermissionNode.TOWNY_) == False
    assert auth.subject_has_permission(s_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_) == True
    assert auth.subject_has_permission(s_id=EGG, node=TownyPermissionNode.TOWNY_WILD_) == True


def test_grouped_groups():
    auth = Authority()

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.add_group(gid=EGG)
    auth.add_group(gid=SPAM)
    auth.add_group(gid=HAM)

    auth.add_group(gid=ORANGE)
    auth.add_group(gid=APPLE)
    auth.add_group(gid=PEAR)
    auth.add_group(gid=BANANA)

    auth.group_add_group(parent_id=FOOD, gid=ANIMAL_BASED)
    auth.group_add_group(parent_id=FOOD, gid=PLANT_BASED)

    auth.group_add_group(parent_id=ANIMAL_BASED, gid=EGG)
    auth.group_add_group(parent_id=ANIMAL_BASED, gid=SPAM)
    auth.group_add_group(parent_id=ANIMAL_BASED, gid=HAM)

    auth.group_add_group(parent_id=PLANT_BASED, gid=ORANGE)
    auth.group_add_group(parent_id=PLANT_BASED, gid=APPLE)
    auth.group_add_group(parent_id=PLANT_BASED, gid=PEAR)
    auth.group_add_group(parent_id=PLANT_BASED, gid=BANANA)

    assert len(auth._groups[FOOD].child_ids) == 2
    assert len(auth._groups[PLANT_BASED].child_ids) == 4
    assert len(auth._groups[ANIMAL_BASED].parent_ids) == 1
    assert len(auth._groups[PLANT_BASED].parent_ids) == 1

    assert len(auth._groups[ANIMAL_BASED].child_ids) == 3
    assert len(auth._groups[PLANT_BASED].child_ids) == 4


def test_cyclic_groups():
    auth = Authority()

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.group_add_group(parent_id=FOOD, gid=ANIMAL_BASED)
    auth.group_add_group(parent_id=ANIMAL_BASED, gid=PLANT_BASED)

    with pytest.raises(GroupCycleError):
        auth.group_add_group(parent_id=PLANT_BASED, gid=FOOD)


def test_recursive_permissions():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.group_add_group(parent_id=FOOD, gid=ANIMAL_BASED)
    auth.group_add_group(parent_id=ANIMAL_BASED, gid=PLANT_BASED)

    auth.group_add_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_)

    assert auth.group_has_permission(gid=PLANT_BASED, node=TownyPermissionNode.TOWNY_CHAT_) == True
    assert auth.group_has_permission(gid=PLANT_BASED, node=TownyPermissionNode.TOWNY_WILD_) == False

    auth.add_subject(s_id=APPLE)
    auth.group_add_subject(gid=PLANT_BASED, s_id=APPLE)

    assert auth.subject_has_permission(s_id=APPLE, node=TownyPermissionNode.TOWNY_CHAT_) == True
    assert auth.subject_has_permission(s_id=APPLE, node=TownyPermissionNode.TOWNY_WILD_) == False


def test_grouped_subjects():
    auth = Authority()

    auth.add_subject(s_id=EGG)
    auth.add_subject(s_id=SPAM)
    auth.add_subject(s_id=HAM)

    auth.add_subject(s_id=ORANGE)
    auth.add_subject(s_id=APPLE)
    auth.add_subject(s_id=PEAR)
    auth.add_subject(s_id=BANANA)

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.group_add_subject(gid=FOOD, s_id=EGG)
    auth.group_add_subject(gid=FOOD, s_id=SPAM)
    auth.group_add_subject(gid=FOOD, s_id=HAM)
    auth.group_add_subject(gid=FOOD, s_id=ORANGE)
    auth.group_add_subject(gid=FOOD, s_id=APPLE)
    auth.group_add_subject(gid=FOOD, s_id=PEAR)
    auth.group_add_subject(gid=FOOD, s_id=BANANA)

    auth.group_add_subject(gid=ANIMAL_BASED, s_id=EGG)
    auth.group_add_subject(gid=ANIMAL_BASED, s_id=SPAM)
    auth.group_add_subject(gid=ANIMAL_BASED, s_id=HAM)

    auth.group_add_subject(gid=PLANT_BASED, s_id=ORANGE)
    auth.group_add_subject(gid=PLANT_BASED, s_id=APPLE)
    auth.group_add_subject(gid=PLANT_BASED, s_id=PEAR)
    auth.group_add_subject(gid=PLANT_BASED, s_id=BANANA)

    assert len(auth._groups[FOOD].s_ids) == 7
    assert len(auth._groups[ANIMAL_BASED].s_ids) == 3
    assert len(auth._groups[PLANT_BASED].s_ids) == 4

    assert len(auth._subjects[EGG].gids) == 2
    assert len(auth._subjects[ORANGE].gids) == 2


def test_unknown_perm_node():
    auth = Authority()

    auth.add_subject(s_id=APPLE)

    auth.add_group(gid=FOOD)

    with pytest.raises(UnknownPermissionNodeError):
        auth.subject_add_permission(s_id=APPLE, node=TownyPermissionNode.TOWNY_CHAT_)

    with pytest.raises(UnknownPermissionNodeError):
        auth.group_add_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_)
