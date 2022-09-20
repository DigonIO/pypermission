import pytest

from pypermission.json import Authority
from pypermission.typing import Permission

# Permission nodes for testing inspired be the towny permission nodes
# https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java

test_data = (
    # (node, is_leave, has_payload)
    ("towny.*", False, False),
    ("towny.chat.*", False, False),
    ("towny.chat.town", True, False),
    ("towny.chat.nation", True, False),
    ("towny.chat.global", True, False),
    ("towny.wild.*", False, False),
    ("towny.wild.build.*", False, False),
    ("towny.wild.build.<x>", True, True),
    ("towny.wild.destroy.*", False, False),
    ("towny.wild.destroy.<x>", True, True),
)


EGG = "egg"
SPAM = "spam"
HAM = "ham"

ORANGE = "orange"
APPLE = "apple"
PEAR = "pear"
BANANA = "banana"

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

    auth.subject_add(subject_id=EGG)
    auth.subject_add(subject_id=SPAM)
    auth.subject_add(subject_id=HAM)

    auth.subject_add_permission(subject_id=EGG, permission=ROOT_)

    auth.subject_add_permission(subject_id=SPAM, permission=TOWNY_CHAT_)
    auth.subject_add_permission(subject_id=SPAM, permission=TOWNY_WILD_)

    auth.subject_add_permission(subject_id=HAM, permission=TOWNY_CHAT_TOWN)
    auth.subject_add_permission(subject_id=HAM, permission=TOWNY_WILD_BUILD_)
    auth.subject_add_permission(
        subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_1"
    )
    auth.subject_add_permission(
        subject_id=HAM, permission=TOWNY_WILD_DESTROY_X, payload="payload_2"
    )


#    auth.subject_add(ORANGE)
#    auth.subject_add(APPLE)
#    auth.subject_add(PEAR)
#    auth.subject_add(BANANA)
#
#    auth.group_add(ANIMAL_BASED)
#    auth.group_add(PLANT_BASED)
#
#    auth.group_add_subject(ANIMAL_BASED,EGG)
#    auth.group_add_subject(ANIMAL_BASED,SPAM)
#    auth.group_add_subject(ANIMAL_BASED,HAM)
#
#    auth.group_add_subject(PLANT_BASED,)
#    auth.group_add_subject(PLANT_BASED,)
#    auth.group_add_subject(PLANT_BASED,)
#    auth.group_add_subject(PLANT_BASED,)
