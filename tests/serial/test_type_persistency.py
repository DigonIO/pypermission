import json
import pathlib
import tempfile

import yaml
from deepdiff import DeepDiff

from pypermission.serial import SerialAuthority

from ..helpers import (
    ID_1_INT,
    ID_1_STR,
    ID_2_INT,
    ID_100_INT,
    ID_100_STR,
    ID_ALL_STR,
    ID_TWO_STR,
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

    assert auth.get_roles() == {ID_ALL_STR, ID_100_STR, ID_100_INT}

    assert auth.get_subjects() == {
        ID_1_STR,
        ID_1_INT,
        ID_TWO_STR,
        ID_2_INT,
    }

    assert auth.role_get_child_roles(rid=ID_ALL_STR) == {ID_100_STR, ID_100_INT}

    assert auth.role_get_subjects(rid=ID_100_INT) == {ID_1_INT, ID_1_STR}
    assert auth.role_get_subjects(rid=ID_100_STR) == {ID_2_INT, ID_TWO_STR}


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
    "roles": {
        "all": {
            "member_roles": [
                100,
                "100",
            ],
            "member_subjects": [],
            "permission_nodes": [],
        },
        100: {
            "member_roles": [],
            "member_subjects": [
                1,
                "1",
            ],
            "permission_nodes": [],
        },
        "100": {
            "member_roles": [],
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
    "roles": {
        "str:all": {
            "member_roles": [
                "int:100",
                "str:100",
            ],
            "member_subjects": [],
            "permission_nodes": [],
        },
        "int:100": {
            "member_roles": [],
            "member_subjects": [
                "int:1",
                "str:1",
            ],
            "permission_nodes": [],
        },
        "str:100": {
            "member_roles": [],
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
