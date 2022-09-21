# required because yaml has a bigger feature set compared to json
# so the yaml parser behaves different

from pypermission.yaml import Authority

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


def test_affiliation_persistency():
    auth = Authority()

    auth.subject_add(subject_id=EGG)
    auth.subject_add(subject_id=SPAM)
    auth.subject_add(subject_id=HAM)

    auth.subject_add(subject_id=ORANGE)
    auth.subject_add(subject_id=APPLE)
    auth.subject_add(subject_id=PEAR)
    auth.subject_add(subject_id=BANANA)

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


def test_permission_persistency():
    auth = Authority()

    def r(node: str):
        return auth.register_permission(node=node)

    ROOT_ = auth.root_permission
    TOWNY_ = r("towny.*")
    TOWNY_CHAT_ = r("towny.chat.*")
    TOWNY_CHAT_TOWN = r("towny.chat.town")
    TOWNY_CHAT_NATION = r("towny.chat.nation")
    TOWNY_CHAT_GLOBAL = r("towny.chat.global")
    TOWNY_WILD_ = r("towny.wild.*")
    TOWNY_WILD_BUILD_ = r("towny.wild.build.*")
    TOWNY_WILD_BUILD_X = r("towny.wild.build.<x>")
    TOWNY_WILD_DESTROY_ = r("towny.wild.destroy.*")
    TOWNY_WILD_DESTROY_X = r("towny.wild.destroy.<x>")

    auth.subject_add(subject_id=EGG)
    auth.subject_add_permission(subject_id=EGG, permission=TOWNY_CHAT_TOWN)
    auth.subject_add_permission(subject_id=EGG, permission=TOWNY_WILD_BUILD_X, payload="dirt")

    auth.subject_add(subject_id=SPAM)

    auth.group_add(group_id=FOOD)
    auth.group_add_permission(group_id=FOOD, permission=TOWNY_CHAT_NATION)
    auth.group_add_permission(group_id=FOOD, permission=TOWNY_WILD_DESTROY_X, payload="iron")

    serial_data = auth.save_to_str()

    auth2 = Authority()
    auth2.load_from_str(serial_data=serial_data)

    def r(node: str):
        return auth2.register_permission(node=node)

    ROOT_ = auth2.root_permission
    TOWNY_ = r("towny.*")
    TOWNY_CHAT_ = r("towny.chat.*")
    TOWNY_CHAT_TOWN = r("towny.chat.town")
    TOWNY_CHAT_NATION = r("towny.chat.nation")
    TOWNY_CHAT_GLOBAL = r("towny.chat.global")
    TOWNY_WILD_ = r("towny.wild.*")
    TOWNY_WILD_BUILD_ = r("towny.wild.build.*")
    TOWNY_WILD_BUILD_X = r("towny.wild.build.<x>")
    TOWNY_WILD_DESTROY_ = r("towny.wild.destroy.*")
    TOWNY_WILD_DESTROY_X = r("towny.wild.destroy.<x>")

    assert auth2.subject_has_permission(subject_id=EGG, permission=TOWNY_CHAT_TOWN) == True
    assert auth2.subject_has_permission(subject_id=EGG, permission=TOWNY_CHAT_) == False
    assert (
        auth2.subject_add_permission(subject_id=EGG, permission=TOWNY_WILD_BUILD_X, payload="dirt")
        == True
    )
    assert (
        auth2.subject_add_permission(subject_id=EGG, permission=TOWNY_WILD_BUILD_X, payload="stone")
        == False
    )

    assert auth2.group_add_permission(group_id=FOOD, permission=TOWNY_CHAT_NATION) == True
    assert auth2.group_add_permission(group_id=FOOD, permission=TOWNY_CHAT_TOWN) == False
    assert (
        auth2.group_add_permission(group_id=FOOD, permission=TOWNY_WILD_DESTROY_X, payload="iron")
        == True
    )
    assert (
        auth2.group_add_permission(group_id=FOOD, permission=TOWNY_WILD_DESTROY_X, payload="gold")
        == False
    )
