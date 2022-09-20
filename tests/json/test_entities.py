from pypermission.json import Authority
from pypermission.typing import Permission

# Permission nodes for testing inspired be the towny permission nodes
# https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java

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

    ### EGG ### ADD PERMS ##########################################################################
    auth.subject_add(subject_id=EGG)
    auth.subject_add_permission(subject_id=EGG, permission=ROOT_)

    assert auth.subject_has_permission(subject_id=EGG, permission=TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(subject_id=EGG, permission=TOWNY_CHAT_NATION) == True
    assert (
        auth.subject_has_permission(subject_id=EGG, permission=TOWNY_WILD_BUILD_X, payload="dummy")
        == True
    )
    assert auth.subject_has_permission(subject_id=EGG, permission=TOWNY_WILD_DESTROY_) == True

    ### SPAM ### ADD PERMS ##########################################################################
    auth.subject_add(subject_id=SPAM)
    auth.subject_add_permission(subject_id=SPAM, permission=TOWNY_CHAT_)
    auth.subject_add_permission(subject_id=SPAM, permission=TOWNY_WILD_)

    assert auth.subject_has_permission(subject_id=SPAM, permission=TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(subject_id=SPAM, permission=TOWNY_CHAT_NATION) == True
    assert (
        auth.subject_has_permission(
            subject_id=SPAM, permission=TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )
    assert auth.subject_has_permission(subject_id=SPAM, permission=TOWNY_WILD_DESTROY_) == True

    ### HAM ### ADD PERMS ##########################################################################
    auth.subject_add(subject_id=HAM)

    auth.subject_add_permission(subject_id=HAM, permission=TOWNY_CHAT_TOWN)
    assert auth.subject_has_permission(subject_id=HAM, permission=TOWNY_CHAT_GLOBAL) == False
    assert auth.subject_has_permission(subject_id=HAM, permission=TOWNY_CHAT_TOWN) == True

    auth.subject_add_permission(subject_id=HAM, permission=TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            subject_id=HAM, permission=TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == True
    )

    auth.subject_add_permission(
        subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    auth.subject_add_permission(
        subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_2"
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_2"
        )
        == True
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_x"
        )
        == False
    )

    ### HAM ### REM PERMS ##########################################################################
    auth.subject_rem_permission(subject_id=HAM, permission=TOWNY_CHAT_TOWN)
    assert auth.subject_has_permission(subject_id=HAM, permission=TOWNY_CHAT_TOWN) == False

    auth.subject_rem_permission(subject_id=HAM, permission=TOWNY_WILD_BUILD_)
    assert (
        auth.subject_has_permission(
            subject_id=HAM, permission=TOWNY_WILD_BUILD_X, payload="payload_x"
        )
        == False
    )

    auth.subject_rem_permission(
        subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    assert (
        auth.subject_has_permission(
            subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == False
    )


# Just a short integration test, because groups using the same permission backend like subjects
def test_group_perms():
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

    auth.group_add(ANIMAL_BASED)

    auth.group_add_permission(group_id=ANIMAL_BASED, permission=ROOT_)
    assert auth.group_has_permission(group_id=ANIMAL_BASED, permission=TOWNY_CHAT_TOWN) == True
    assert (
        auth.group_has_permission(
            group_id=ANIMAL_BASED, permission=TOWNY_WILD_DESTROY_X, payload="payload_1"
        )
        == True
    )


def test_subject_perms_with_groups():
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

    auth.group_add(group_id=ANIMAL_BASED)
    auth.group_add(group_id=PLANT_BASED)

    auth.subject_add(subject_id=EGG)

    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=EGG)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=EGG)
    # yeah chickens are some kind of plants too...

    auth.group_add_permission(group_id=ANIMAL_BASED, permission=TOWNY_CHAT_)
    auth.group_add_permission(group_id=PLANT_BASED, permission=TOWNY_WILD_)

    assert auth.subject_has_permission(subject_id=EGG, permission=TOWNY_) == False
    assert auth.subject_has_permission(subject_id=EGG, permission=TOWNY_CHAT_) == True
    assert auth.subject_has_permission(subject_id=EGG, permission=TOWNY_WILD_) == True


def test_grouped_subjects():
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

    assert len(auth._groups[FOOD].subject_ids) == 7
    assert len(auth._groups[ANIMAL_BASED].subject_ids) == 3
    assert len(auth._groups[PLANT_BASED].subject_ids) == 4

    assert len(auth._subjects[EGG].group_ids) == 2
    assert len(auth._subjects[ORANGE].group_ids) == 2
