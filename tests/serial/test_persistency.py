import pathlib
import tempfile
import json

import yaml
from deepdiff import DeepDiff

from pypermission.serial import SerialAuthority

from ..helpers import TownyPermissionNode as TPN
from ..helpers import serial_authority

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

    assert_loaded_authority(auth=auth)


def test_load_file_json():
    auth = SerialAuthority(nodes=TPN)

    auth.load_file(path=path / "save_file.json")

    assert_loaded_authority(auth=auth)


def test_write_file_yaml(serial_authority):
    auth: SerialAuthority = serial_authority

    with tempfile.NamedTemporaryFile(suffix=".yaml") as handle:
        auth.save_file(path=handle.name)

        content = handle.read()
        save_data = yaml.safe_load(content)

    assert DeepDiff(save_data, SAVE_DATA, ignore_order=True) == {}


def test_write_file_json(serial_authority):
    auth: SerialAuthority = serial_authority

    with tempfile.NamedTemporaryFile(suffix=".json") as handle:
        auth.save_file(path=handle.name)

        content = handle.read()
        save_data = json.loads(content)

    assert DeepDiff(save_data, SAVE_DATA, ignore_order=True) == {}


def assert_loaded_authority(auth: SerialAuthority):

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
    assert auth.subject_has_permission(sid=PEAR, node=TPN.TOWNY_CHAT_GLOBAL) == True

    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_TOWN) == True
    assert auth.subject_has_permission(sid=EGG, node=TPN.TOWNY_CHAT_NATION) == False

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

    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt") == True
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="gold") == True
    assert auth.subject_has_permission(sid=HAM, node=TPN.TOWNY_WILD_BUILD_X, payload="iron") == True


# Fulfil the properties of the fixture `serial_authority`
SAVE_DATA = {
    "groups": {
        "animal_based": {
            "member_groups": [],
            "member_subjects": ["spam", "ham", "egg"],
            "permission_nodes": [
                "towny.chat.town",
                "towny.wild.build.<dirt>",
                "towny.wild.build.<gold>",
            ],
        },
        "food": {
            "member_groups": ["plant_based", "animal_based"],
            "member_subjects": [],
            "permission_nodes": ["towny.chat.global"],
        },
        "plant_based": {
            "member_groups": [],
            "member_subjects": ["apple", "orange", "banana", "pear"],
            "permission_nodes": [
                "towny.chat.nation",
                "towny.wild.destroy.<dirt>",
                "towny.wild.destroy.<gold>",
            ],
        },
    },
    "subjects": {
        "apple": {"permission_nodes": []},
        "banana": {"permission_nodes": []},
        "egg": {"permission_nodes": []},
        "ham": {"permission_nodes": ["towny.wild.*"]},
        "orange": {"permission_nodes": []},
        "pear": {"permission_nodes": []},
        "spam": {"permission_nodes": []},
    },
}
