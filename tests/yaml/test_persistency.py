# required because yaml has a bigger feature set compared to json
# so the yaml parser behaves different

from pypermission.yaml import Authority

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


def test_affiliation_persistency_yaml():
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

    serial_data = auth.save_to_str()

    auth2 = Authority()
    auth2.load_from_str(serial_data=serial_data)

    assert set(auth._subjects.keys()) == set(auth2._subjects.keys())
    assert set(auth._groups.keys()) == set(auth2._groups.keys())

    assert auth._groups[FOOD]._sids == auth2._groups[FOOD]._sids
    assert auth._groups[ANIMAL_BASED]._sids == auth2._groups[ANIMAL_BASED]._sids
    assert auth._groups[PLANT_BASED]._sids == auth2._groups[PLANT_BASED]._sids


def test_permission_persistency_yaml():
    auth = Authority(nodes=TownyPermissionNode)

    auth.add_subject(sid=EGG)
    auth.subject_add_permission(sid=EGG, node=TownyPermissionNode.TOWNY_CHAT_TOWN)
    auth.subject_add_permission(
        sid=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="dirt"
    )

    auth.add_subject(sid=SPAM)

    auth.add_group(gid=FOOD)
    auth.group_add_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_NATION)
    auth.group_add_permission(
        gid=FOOD, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="iron"
    )

    serial_data = auth.save_to_str()

    auth2 = Authority(nodes=TownyPermissionNode)
    auth2.load_from_str(serial_data=serial_data)

    assert auth2.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_CHAT_TOWN) == True
    assert auth2.subject_has_permission(sid=EGG, node=TownyPermissionNode.TOWNY_CHAT_) == False
    assert (
        auth2.subject_has_permission(
            sid=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="dirt"
        )
        == True
    )
    assert (
        auth2.subject_has_permission(
            sid=EGG, node=TownyPermissionNode.TOWNY_WILD_BUILD_X, payload="stone"
        )
        == False
    )

    assert auth2.group_has_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_NATION) == True
    assert auth2.group_has_permission(gid=FOOD, node=TownyPermissionNode.TOWNY_CHAT_TOWN) == False
    assert (
        auth2.group_has_permission(
            gid=FOOD, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="iron"
        )
        == True
    )
    assert (
        auth2.group_has_permission(
            gid=FOOD, node=TownyPermissionNode.TOWNY_WILD_DESTROY_X, payload="gold"
        )
        == False
    )


def test_grouped_groups_yaml():
    auth = Authority()

    auth.add_group(gid=FOOD)
    auth.add_group(gid=ANIMAL_BASED)
    auth.add_group(gid=PLANT_BASED)

    auth.group_add_group(gid=ANIMAL_BASED, pid=FOOD)
    auth.group_add_group(gid=PLANT_BASED, pid=FOOD)

    serial_data = auth.save_to_str()

    auth2 = Authority()

    auth2.load_from_str(serial_data=serial_data)

    assert ANIMAL_BASED in auth2._groups[FOOD].child_ids
    assert PLANT_BASED in auth2._groups[FOOD].child_ids

    assert FOOD in auth2._groups[ANIMAL_BASED].parent_ids
    assert FOOD in auth2._groups[PLANT_BASED].parent_ids
