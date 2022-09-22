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
    auth.add_subject(subject_id=EGG)
    auth.subject_add_permission(subject_id=EGG, node=Authority.root_node())

    assert (
        auth.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL)
        == True
    )
    assert (
        auth.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_NATION)
        == True
    )
    assert (
        auth.subject_has_permission(
            subject_id=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="dummy"
        )
        == True
    )
    assert (
        auth.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_WILD_DESTROY_)
        == True
    )

    ### SPAM ### ADD PERMS ##########################################################################
    auth.add_subject(subject_id=SPAM)
    auth.subject_add_permission(subject_id=SPAM, node=TownyPermissionNode.TOWNY_CHAT_)
    auth.subject_add_permission(subject_id=SPAM, node=TownyPermissionNode.TOWNY_WILD_)

    assert (
        auth.subject_has_permission(subject_id=SPAM, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL)
        == True
    )
    assert (
        auth.subject_has_permission(subject_id=SPAM, node=TownyPermissionNode.TOWNY_CHAT_NATION)
        == True
    )
    assert (
        auth.subject_has_permission(
            subject_id=SPAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )
    assert (
        auth.subject_has_permission(subject_id=SPAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_)
        == True
    )

    ### HAM ### ADD PERMS ##########################################################################
    auth.add_subject(subject_id=HAM)

    auth.subject_add_permission(subject_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    assert (
        auth.subject_has_permission(subject_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_GLOBAL)
        == False
    )
    assert (
        auth.subject_has_permission(subject_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
        == True
    )

    auth.subject_add_permission(subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )

    auth.subject_add_permission(
        subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    auth.subject_add_permission(
        subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_2"
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_2"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_x"
        )
        == False
    )

    ### HAM ### REM PERMS ##########################################################################
    auth.subject_rem_permission(subject_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    assert (
        auth.subject_has_permission(subject_id=HAM, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
        == False
    )

    auth.subject_rem_permission(subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == False
    )

    auth.subject_rem_permission(
        subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == False
    )


# Just a short integration test, because groups using the same permission backend like subjects
def test_group_perms():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_group(ANIMAL_BASED)

    auth.group_add_permission(group_id=ANIMAL_BASED, node=Authority.root_node())
    assert (
        auth.group_has_permission(group_id=ANIMAL_BASED, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
        == True
    )
    assert (
        auth.group_has_permission(
            group_id=ANIMAL_BASED,
            node=TownyPermissionNode.TOWNY_WILD_DESTROY_X,
            payload="payload_1",
        )
        == True
    )


def test_subject_perms_with_groups():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_group(group_id=ANIMAL_BASED)
    auth.add_group(group_id=PLANT_BASED)

    auth.add_subject(subject_id=EGG)

    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=EGG)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=EGG)
    # yeah chickens are some kind of plants too...

    auth.group_add_permission(group_id=ANIMAL_BASED, node=TownyPermissionNode.TOWNY_CHAT_)
    auth.group_add_permission(group_id=PLANT_BASED, node=TownyPermissionNode.TOWNY_WILD_)

    assert auth.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_) == False
    assert auth.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_) == True
    assert auth.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_WILD_) == True


def test_grouped_subjects():
    auth = Authority()

    auth.add_subject(subject_id=EGG)
    auth.add_subject(subject_id=SPAM)
    auth.add_subject(subject_id=HAM)

    auth.add_subject(subject_id=ORANGE)
    auth.add_subject(subject_id=APPLE)
    auth.add_subject(subject_id=PEAR)
    auth.add_subject(subject_id=BANANA)

    auth.add_group(group_id=FOOD)
    auth.add_group(group_id=ANIMAL_BASED)
    auth.add_group(group_id=PLANT_BASED)

    auth.group_add_subject(group_id=FOOD, subject_id=EGG)
    auth.group_add_subject(group_id=FOOD, subject_id=SPAM)
    auth.group_add_subject(group_id=FOOD, subject_id=HAM)
    auth.group_add_subject(group_id=FOOD, subject_id=ORANGE)
    auth.group_add_subject(group_id=FOOD, subject_id=APPLE)
    auth.group_add_subject(group_id=FOOD, subject_id=PEAR)
    auth.group_add_subject(group_id=FOOD, subject_id=BANANA)

    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=EGG)
    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=SPAM)
    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=HAM)

    auth.group_add_subject(group_id=PLANT_BASED, subject_id=ORANGE)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=APPLE)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=PEAR)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=BANANA)

    assert len(auth._groups[FOOD].subject_ids) == 7
    assert len(auth._groups[ANIMAL_BASED].subject_ids) == 3
    assert len(auth._groups[PLANT_BASED].subject_ids) == 4

    assert len(auth._subjects[EGG].group_ids) == 2
    assert len(auth._subjects[ORANGE].group_ids) == 2
