import os

from pypermission.core import PermissionNode
from pypermission.serial import SerialAuthority
from pypermission.sqlalchemy import SQLAlchemyAuthority

# The gitlab-ci provides access to the db under the `mariadb` hostname for the `pytest_3_10_7` job
# as specified under https://docs.gitlab.com/ee/ci/services/#accessing-the-services
# Set the `MARIADB_ROOT_PASSWORD` variable in the gitlab ci for this to be used.
MARIADB_URL = "mariadb" if os.environ.get("MARIADB_ROOT_PASSWORD") else "127.0.0.1"

URL_SQLITE = "sqlite:///pp_test.db"
URL_MARIADB = f"mariadb+mariadbconnector://pp_user:pp_pw@{MARIADB_URL}:3306/pp_db"

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

ID_ALL_STR = "all"
ID_100_STR = "100"
ID_100_INT = 100
ID_1_STR = "1"
ID_1_INT = 1
ID_TWO_STR = "two"
ID_2_INT = 2


class TownyPermissionNode(PermissionNode):
    # Permission nodes for testing inspired be the towny permission nodes
    # https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java
    TOWNY_ = "towny.*"
    TOWNY_CHAT_ = "towny.chat.*"
    TOWNY_CHAT_TOWN = "towny.chat.town"
    TOWNY_CHAT_NATION = "towny.chat.nation"
    TOWNY_CHAT_GLOBAL = "towny.chat.global"
    TOWNY_WILD_ = "towny.wild.*"
    TOWNY_WILD_BUILD_ = "towny.wild.build.*"
    TOWNY_WILD_BUILD_X = "towny.wild.build.<x>"
    TOWNY_WILD_BUILD_IRON = "towny.wild.build.iron"
    TOWNY_WILD_DESTROY_ = "towny.wild.destroy.*"
    TOWNY_WILD_DESTROY_X = "towny.wild.destroy.<x>"


TPN = TownyPermissionNode


def assert_loaded_authority(auth: SerialAuthority | SQLAlchemyAuthority):
    # The authority tested here should fulfil the properties of the two save files
    # `./serial/save_file.yaml` and `./serial/save_file.json`

    assert auth.get_roles() == {FOOD, ANIMAL_BASED, PLANT_BASED}

    assert auth.get_subjects() == {
        EGG,
        SPAM,
        HAM,
        ORANGE,
        APPLE,
        PEAR,
        BANANA,
    }

    assert auth.role_get_child_roles(rid=FOOD) == {ANIMAL_BASED, PLANT_BASED}
    assert auth.role_get_parent_roles(rid=ANIMAL_BASED) == {FOOD}
    assert auth.role_get_parent_roles(rid=PLANT_BASED) == {FOOD}

    assert auth.role_get_subjects(rid=ANIMAL_BASED) == {EGG, SPAM, HAM}
    assert auth.subject_get_roles(sid=EGG) == {ANIMAL_BASED}

    assert auth.role_get_subjects(rid=PLANT_BASED) == {ORANGE, APPLE, PEAR, BANANA}
    assert auth.subject_get_roles(sid=ORANGE) == {PLANT_BASED}

    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_GLOBAL) == True
    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_GLOBAL) == True

    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_TOWN) == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_NATION) == False

    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_TOWN) == False
    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_NATION) == True

    # test EGG
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt") == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_BUILD_X, payload="gold") == True
    assert (
        auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt") == False
    )
    assert (
        auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold") == False
    )

    # test PEAR
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

    # test HAM
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt") == True
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="gold") == True
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="iron") == True
    assert (
        auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt") == True
    )
    assert (
        auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold") == True
    )


CHILD_GROUP = "child_role"
PARENT_GROUP = "parent_role"
USER_GROUP = "user_role"
USER = "user"
IRON = "iron"

SUBJECT_INFO_NODES_EID = {
    "roles": {
        CHILD_GROUP: {
            "parents": [PARENT_GROUP],
            "permission_nodes": {
                TPN.TOWNY_CHAT_TOWN: None,
                TPN.TOWNY_WILD_BUILD_X: [IRON],
                TPN.TOWNY_WILD_BUILD_IRON: None,
            },
        },
        PARENT_GROUP: {
            "parents": [],
            "permission_nodes": {TPN.TOWNY_CHAT_: None, TPN.TOWNY_WILD_: None},
        },
    },
    "subject": {
        "entity_id": USER,
        "permission_nodes": {TPN.TOWNY_WILD_BUILD_: None},
        "roles": [CHILD_GROUP],
    },
    "permission_tree": {
        TPN.TOWNY_CHAT_: {
            TPN.TOWNY_CHAT_GLOBAL: None,
            TPN.TOWNY_CHAT_NATION: None,
            TPN.TOWNY_CHAT_TOWN: None,
        },
        TPN.TOWNY_CHAT_TOWN: None,
        TPN.TOWNY_WILD_: {
            TPN.TOWNY_WILD_BUILD_: {TPN.TOWNY_WILD_BUILD_X: [], TPN.TOWNY_WILD_BUILD_IRON: None},
            TPN.TOWNY_WILD_DESTROY_: {TPN.TOWNY_WILD_DESTROY_X: []},
        },
        TPN.TOWNY_WILD_BUILD_X: [IRON],
        TPN.TOWNY_WILD_BUILD_IRON: None,
        TPN.TOWNY_WILD_BUILD_: {TPN.TOWNY_WILD_BUILD_X: [], TPN.TOWNY_WILD_BUILD_IRON: None},
    },
}


SUBJECT_INFO_STR_STR = {
    "roles": {
        "str:child_role": {
            "parents": ["str:parent_role"],
            "permission_nodes": {
                "towny.chat.town": None,
                "towny.wild.build.<x>": [IRON],
                "towny.wild.build.iron": None,
            },
        },
        "str:parent_role": {
            "parents": [],
            "permission_nodes": {"towny.chat.*": None, "towny.wild.*": None},
        },
    },
    "subject": {
        "entity_id": "str:user",
        "permission_nodes": {"towny.wild.build.*": None},
        "roles": ["str:child_role"],
    },
    "permission_tree": {
        "towny.chat.*": {
            "towny.chat.global": None,
            "towny.chat.nation": None,
            "towny.chat.town": None,
        },
        "towny.chat.town": None,
        "towny.wild.*": {
            "towny.wild.build.*": {"towny.wild.build.<x>": [], "towny.wild.build.iron": None},
            "towny.wild.destroy.*": {"towny.wild.destroy.<x>": []},
        },
        "towny.wild.build.<x>": [IRON],
        "towny.wild.build.iron": None,
        "towny.wild.build.*": {"towny.wild.build.<x>": [], "towny.wild.build.iron": None},
    },
}

GROUP_INFO_NODES_EID = {
    "roles": {
        CHILD_GROUP: {
            "parents": [PARENT_GROUP],
            "permission_nodes": {
                TPN.TOWNY_CHAT_TOWN: None,
                TPN.TOWNY_WILD_BUILD_X: [IRON],
                TPN.TOWNY_WILD_BUILD_IRON: None,
            },
        },
        PARENT_GROUP: {
            "parents": [],
            "permission_nodes": {TPN.TOWNY_CHAT_: None, TPN.TOWNY_WILD_: None},
        },
    },
    "role": {
        "entity_id": USER_GROUP,
        "permission_nodes": {TPN.TOWNY_WILD_BUILD_: None},
        "roles": [CHILD_GROUP],
    },
    "permission_tree": {
        TPN.TOWNY_CHAT_: {
            TPN.TOWNY_CHAT_GLOBAL: None,
            TPN.TOWNY_CHAT_NATION: None,
            TPN.TOWNY_CHAT_TOWN: None,
        },
        TPN.TOWNY_CHAT_TOWN: None,
        TPN.TOWNY_WILD_: {
            TPN.TOWNY_WILD_BUILD_: {TPN.TOWNY_WILD_BUILD_X: [], TPN.TOWNY_WILD_BUILD_IRON: None},
            TPN.TOWNY_WILD_DESTROY_: {TPN.TOWNY_WILD_DESTROY_X: []},
        },
        TPN.TOWNY_WILD_BUILD_X: [IRON],
        TPN.TOWNY_WILD_BUILD_IRON: None,
        TPN.TOWNY_WILD_BUILD_: {TPN.TOWNY_WILD_BUILD_X: [], TPN.TOWNY_WILD_BUILD_IRON: None},
    },
}

GROUP_INFO_STR_STR = {
    "roles": {
        "str:child_role": {
            "parents": ["str:parent_role"],
            "permission_nodes": {
                "towny.chat.town": None,
                "towny.wild.build.<x>": [IRON],
                "towny.wild.build.iron": None,
            },
        },
        "str:parent_role": {
            "parents": [],
            "permission_nodes": {"towny.chat.*": None, "towny.wild.*": None},
        },
    },
    "role": {
        "entity_id": "str:user_role",
        "permission_nodes": {"towny.wild.build.*": None},
        "roles": ["str:child_role"],
    },
    "permission_tree": {
        "towny.chat.*": {
            "towny.chat.global": None,
            "towny.chat.nation": None,
            "towny.chat.town": None,
        },
        "towny.chat.town": None,
        "towny.wild.*": {
            "towny.wild.build.*": {"towny.wild.build.<x>": [], "towny.wild.build.iron": None},
            "towny.wild.destroy.*": {"towny.wild.destroy.<x>": []},
        },
        "towny.wild.build.<x>": [IRON],
        "towny.wild.build.iron": None,
        "towny.wild.build.*": {"towny.wild.build.<x>": [], "towny.wild.build.iron": None},
    },
}
