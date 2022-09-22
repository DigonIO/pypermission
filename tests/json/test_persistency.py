from pypermission.json import Authority

from ..helpers import TownyPermissionNode

EGG = "egg"
SPAM = "spam"
HAM = "ham"

ORANGE = 1
APPLE = 2
PEAR = 3
BANANA = 4

FOOD = 1234
ANIMAL_BASED = "animal_based"
PLANT_BASED = "plant_based"


def test_affiliation_persistency_json():
    auth = Authority()

    auth.add_subject(subject_id=EGG)
    auth.add_subject(subject_id=SPAM)
    auth.add_subject(subject_id=HAM)

    auth.add_subject(subject_id=ORANGE)
    auth.add_subject(subject_id=APPLE)
    auth.add_subject(subject_id=PEAR)
    auth.add_subject(subject_id=BANANA)

    auth.group_add(group_id=FOOD)
    auth.group_add(group_id=ANIMAL_BASED)
    auth.group_add(group_id=PLANT_BASED)

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

    serial_data = auth.save_to_str()

    auth2 = Authority()
    auth2.load_from_str(serial_data=serial_data)

    assert set(auth._subjects.keys()) == set(auth2._subjects.keys())
    assert set(auth._groups.keys()) == set(auth2._groups.keys())

    assert auth._groups[FOOD]._subject_ids == auth2._groups[FOOD]._subject_ids
    assert auth._groups[ANIMAL_BASED]._subject_ids == auth2._groups[ANIMAL_BASED]._subject_ids
    assert auth._groups[PLANT_BASED]._subject_ids == auth2._groups[PLANT_BASED]._subject_ids


def test_permission_persistency_json():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_subject(subject_id=EGG)
    auth.subject_add_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    auth.subject_add_permission(
        subject_id=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="dirt"
    )

    auth.add_subject(subject_id=SPAM)

    auth.group_add(group_id=FOOD)
    auth.group_add_permission(group_id=FOOD, node=TownyPermissionNode.TOWNY_CHAT_NATION)
    auth.group_add_permission(
        group_id=FOOD, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="iron"
    )

    serial_data = auth.save_to_str()

    auth2 = Authority(nodes=TownyPermissionNode)
    auth2.load_from_str(serial_data=serial_data)

    assert (
        auth2.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
        == True
    )
    assert (
        auth2.subject_has_permission(subject_id=EGG, node=TownyPermissionNode.TOWNY_CHAT_) == False
    )
    assert (
        auth2.subject_has_permission(
            subject_id=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="dirt"
        )
        == True
    )
    assert (
        auth2.subject_has_permission(
            subject_id=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="stone"
        )
        == False
    )

    assert (
        auth2.group_has_permission(group_id=FOOD, node=TownyPermissionNode.TOWNY_CHAT_NATION)
        == True
    )
    assert (
        auth2.group_has_permission(group_id=FOOD, node=TownyPermissionNode.TOWNY_CHAT_TOWN) == False
    )
    assert (
        auth2.group_has_permission(
            group_id=FOOD, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="iron"
        )
        == True
    )
    assert (
        auth2.group_has_permission(
            group_id=FOOD, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="gold"
        )
        == False
    )
