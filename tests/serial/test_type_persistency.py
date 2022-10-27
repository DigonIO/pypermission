import json
import pathlib
import tempfile

import yaml
from deepdiff import DeepDiff

from pypermission.serial import SerialAuthority

ID_ALL_STR = "all"
ID_100_STR = "100"
ID_100_INT = 100
ID_1_STR = "1"
ID_1_INT = 1
ID_TWO_STR = "two"
ID_2_INT = 2

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
