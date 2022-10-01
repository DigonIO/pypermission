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
    auth.add_subject(sid=EGG)
    auth.subject_add_permission(sid=EGG, node=Authority.root_node())

    assert auth.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_CHAT_NATION) == True
    assert (
        auth.subject_has_permission(
            sid=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="dummy"
        )
        == True
    )
    assert (
        auth.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_WILD_DESTROY_) == True
    )

    ### SPAM ### ADD PERMS ##########################################################################
    auth.add_subject(sid=SPAM)
    auth.subject_add_permission(sid=SPAM, node=TownyPermissionNode.TOWNY_CHAT_)
    auth.subject_add_permission(sid=SPAM, node=TownyPermissionNode.TOWNY_WILD_)

    assert auth.subject_has_permission(sid=SPAM, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(sid=SPAM, node=TownyPermissionNode.TOWNY_CHAT_NATION) == True
    assert (
        auth.subject_has_permission(
            sid=SPAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )
    assert (
        auth.subject_has_permission(sid=SPAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_) == True
    )

    ### HAM ### ADD PERMS ##########################################################################
    auth.add_subject(sid=HAM)

    auth.subject_add_permission(sid=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    assert auth.subject_has_permission(sid=HAM, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL) == False
    assert auth.subject_has_permission(sid=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN) == True

    auth.subject_add_permission(sid=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            sid=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )

    auth.subject_add_permission(
        sid=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    auth.subject_add_permission(
        sid=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_2"
    )
    assert (
        auth.subject_has_permission(
            sid=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            sid=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_2"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            sid=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_x"
        )
        == False
    )

    ### HAM ### REM PERMS ##########################################################################
    auth.subject_rem_permission(sid=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    assert auth.subject_has_permission(sid=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN) == False

    auth.subject_rem_permission(sid=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            sid=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == False
    )

    auth.subject_rem_permission(
        sid=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    assert (
        auth.subject_has_permission(
            sid=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
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

    auth.add_subject(sid=EGG)

    auth.group_add_subject(gid=ANIMAL_BASED, sid=EGG)
    auth.group_add_subject(gid=PLANT_BASED, sid=EGG)
    # yeah chickens are some kind of plants too...

    auth.group_add_permission(gid=ANIMAL_BASED, node=TownyPermissionNode.TOWNY_CHAT_)
    auth.group_add_permission(gid=PLANT_BASED, node=TownyPermissionNode.TOWNY_WILD_)

    assert auth.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_) == False
    assert auth.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_CHAT_) == True
    assert auth.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_WILD_) == True


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

    auth.group_add_group(gid=FOOD, cid=ANIMAL_BASED)
    auth.group_add_group(gid=FOOD, cid=PLANT_BASED)

    auth.group_add_group(gid=ANIMAL_BASED, cid=EGG)
    auth.group_add_group(gid=ANIMAL_BASED, cid=SPAM)
    auth.group_add_group(gid=ANIMAL_BASED, cid=HAM)

    auth.group_add_group(gid=PLANT_BASED, cid=ORANGE)
    auth.group_add_group(gid=PLANT_BASED, cid=APPLE)
    auth.group_add_group(gid=PLANT_BASED, cid=PEAR)
    auth.group_add_group(gid=PLANT_BASED, cid=BANANA)

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

    auth.group_add_group(gid=FOOD, cid=ANIMAL_BASED)
    auth.group_add_group(gid=ANIMAL_BASED, cid=PLANT_BASED)

    with pytest.raises(GroupCycleError):
        auth.group_add_group(gid=PLANT_BASED, cid=FOOD)


def test_recursive_permissions():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.group_add_group(gid=FOOD, cid=ANIMAL_BASED)
    auth.group_add_group(gid=ANIMAL_BASED, cid=PLANT_BASED)

    auth.group_add_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_)

    assert auth.group_has_permission(gid=PLANT_BASED, node=TownyPermissionNode.TOWNY_CHAT_) == True
    assert auth.group_has_permission(gid=PLANT_BASED, node=TownyPermissionNode.TOWNY_WILD_) == False

    auth.add_subject(sid=APPLE)
    auth.group_add_subject(gid=PLANT_BASED, sid=APPLE)

    assert auth.subject_has_permission(sid=APPLE, node=TownyPermissionNode.TOWNY_CHAT_) == True
    assert auth.subject_has_permission(sid=APPLE, node=TownyPermissionNode.TOWNY_WILD_) == False


def test_grouped_subjects():
    auth = Authority()

    auth.add_subject(sid=EGG)
    auth.add_subject(sid=SPAM)
    auth.add_subject(sid=HAM)

    auth.add_subject(sid=ORANGE)
    auth.add_subject(sid=APPLE)
    auth.add_subject(sid=PEAR)
    auth.add_subject(sid=BANANA)

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.group_add_subject(gid=FOOD, sid=EGG)
    auth.group_add_subject(gid=FOOD, sid=SPAM)
    auth.group_add_subject(gid=FOOD, sid=HAM)
    auth.group_add_subject(gid=FOOD, sid=ORANGE)
    auth.group_add_subject(gid=FOOD, sid=APPLE)
    auth.group_add_subject(gid=FOOD, sid=PEAR)
    auth.group_add_subject(gid=FOOD, sid=BANANA)

    auth.group_add_subject(gid=ANIMAL_BASED, sid=EGG)
    auth.group_add_subject(gid=ANIMAL_BASED, sid=SPAM)
    auth.group_add_subject(gid=ANIMAL_BASED, sid=HAM)

    auth.group_add_subject(gid=PLANT_BASED, sid=ORANGE)
    auth.group_add_subject(gid=PLANT_BASED, sid=APPLE)
    auth.group_add_subject(gid=PLANT_BASED, sid=PEAR)
    auth.group_add_subject(gid=PLANT_BASED, sid=BANANA)

    assert len(auth._groups[FOOD].sids) == 7
    assert len(auth._groups[ANIMAL_BASED].sids) == 3
    assert len(auth._groups[PLANT_BASED].sids) == 4

    assert len(auth._subjects[EGG].gids) == 2
    assert len(auth._subjects[ORANGE].gids) == 2


def test_unknown_perm_node():
    auth = Authority()

    auth.add_subject(sid=APPLE)

    auth.add_group(gid=FOOD)

    with pytest.raises(UnknownPermissionNodeError):
        auth.subject_add_permission(sid=APPLE, node=TownyPermissionNode.TOWNY_CHAT_)

    with pytest.raises(UnknownPermissionNodeError):
        auth.group_add_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_)
