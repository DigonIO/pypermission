import json
import pathlib
import tempfile

import yaml
from deepdiff import DeepDiff

from pypermission.serial import SerialAuthority

from ..helpers import (
    ID_ALL_STR,
    ID_100_STR,
    ID_100_INT,
    ID_1_STR,
    ID_1_INT,
    ID_TWO_STR,
    ID_2_INT,
)

PATH = pathlib.Path(__file__).parent.absolute()


def test_load_typed_file_yaml():
    auth = SerialAuthority()

    auth.load_file(path=PATH / "save_file_types.yaml")

    assert_loaded_authority(auth)


def test_load_typed_file_json():
    auth = SerialAuthority()

    auth.load_file(path=PATH / "save_file_types.json")

    assert_loaded_authority(auth)


def assert_loaded_authority(auth: SerialAuthority):

    assert auth.get_groups() == {ID_ALL_STR, ID_100_STR, ID_100_INT}

    assert auth.get_subjects() == {
        ID_1_STR,
        ID_1_INT,
        ID_TWO_STR,
        ID_2_INT,
    }

    assert auth.group_get_member_groups(gid=ID_ALL_STR) == {ID_100_STR, ID_100_INT}

    assert auth.group_get_member_subjects(gid=ID_100_INT) == {ID_1_INT, ID_1_STR}
    assert auth.group_get_member_subjects(gid=ID_100_STR) == {ID_2_INT, ID_TWO_STR}


def test_write_file_yaml_typed(serial_authority_typed):
    auth: SerialAuthority = serial_authority_typed

    with tempfile.NamedTemporaryFile(suffix=".yaml") as handle:
        auth.save_file(path=handle.name)

        content = handle.read()
        save_data = yaml.safe_load(content)

    assert DeepDiff(save_data, SAVE_DATA_YAML, ignore_order=True) == {}


def test_write_file_json_typed(serial_authority_typed):
    auth: SerialAuthority = serial_authority_typed

    with tempfile.NamedTemporaryFile(suffix=".json") as handle:
        auth.save_file(path=handle.name)

        content = handle.read()
        save_data = json.loads(content)

    assert DeepDiff(save_data, SAVE_DATA_JSON, ignore_order=True) == {}


SAVE_DATA_YAML = {
    "groups": {
        "all": {
            "member_groups": [
                100,
                "100",
            ],
            "member_subjects": [],
            "permission_nodes": [],
        },
        100: {
            "member_groups": [],
            "member_subjects": [
                1,
                "1",
            ],
            "permission_nodes": [],
        },
        "100": {
            "member_groups": [],
            "member_subjects": [
                2,
                "two",
            ],
            "permission_nodes": [],
        },
    },
    "subjects": {
        1: {"permission_nodes": []},
        "1": {"permission_nodes": []},
        2: {"permission_nodes": []},
        "two": {"permission_nodes": []},
    },
}

SAVE_DATA_JSON = {
    "groups": {
        "str:all": {
            "member_groups": [
                "int:100",
                "str:100",
            ],
            "member_subjects": [],
            "permission_nodes": [],
        },
        "int:100": {
            "member_groups": [],
            "member_subjects": [
                "int:1",
                "str:1",
            ],
            "permission_nodes": [],
        },
        "str:100": {
            "member_groups": [],
            "member_subjects": [
                "int:2",
                "str:two",
            ],
            "permission_nodes": [],
        },
    },
    "subjects": {
        "int:1": {"permission_nodes": []},
        "str:1": {"permission_nodes": []},
        "int:2": {"permission_nodes": []},
        "str:two": {"permission_nodes": []},
    },
}
