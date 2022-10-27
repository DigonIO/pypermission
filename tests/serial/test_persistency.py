import json
import pathlib
import tempfile

import yaml
from deepdiff import DeepDiff

from pypermission.serial import SerialAuthority

from ..helpers import TownyPermissionNode as TPN
from ..helpers import assert_loaded_authority

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

    assert DeepDiff(save_data, SAVE_DATA_YAML, ignore_order=True) == {}


def test_write_file_json(serial_authority):
    auth: SerialAuthority = serial_authority

    with tempfile.NamedTemporaryFile(suffix=".json") as handle:
        auth.save_file(path=handle.name)

        content = handle.read()
        save_data = json.loads(content)

    assert DeepDiff(save_data, SAVE_DATA_JSON, ignore_order=True) == {}


# Fulfil the properties of the fixture `serial_authority`
SAVE_DATA_YAML = {
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

SAVE_DATA_JSON = {
    "groups": {
        "str:animal_based": {
            "member_groups": [],
            "member_subjects": ["str:spam", "str:ham", "str:egg"],
            "permission_nodes": [
                "towny.chat.town",
                "towny.wild.build.<dirt>",
                "towny.wild.build.<gold>",
            ],
        },
        "str:food": {
            "member_groups": ["str:plant_based", "str:animal_based"],
            "member_subjects": [],
            "permission_nodes": ["towny.chat.global"],
        },
        "str:plant_based": {
            "member_groups": [],
            "member_subjects": ["str:apple", "str:orange", "str:banana", "str:pear"],
            "permission_nodes": [
                "towny.chat.nation",
                "towny.wild.destroy.<dirt>",
                "towny.wild.destroy.<gold>",
            ],
        },
    },
    "subjects": {
        "str:apple": {"permission_nodes": []},
        "str:banana": {"permission_nodes": []},
        "str:egg": {"permission_nodes": []},
        "str:ham": {"permission_nodes": ["towny.wild.*"]},
        "str:orange": {"permission_nodes": []},
        "str:pear": {"permission_nodes": []},
        "str:spam": {"permission_nodes": []},
    },
}
