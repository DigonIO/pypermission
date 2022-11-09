import os
import pytest
from sqlalchemy import create_engine

from pypermission.serial import SerialAuthority
from pypermission.sqlalchemy import SQLAlchemyAuthority
from pypermission.sqlalchemy.models import DeclarativeMeta
from .helpers import (
    ANIMAL_BASED,
    APPLE,
    BANANA,
    EGG,
    FOOD,
    HAM,
    ORANGE,
    PEAR,
    PLANT_BASED,
    SPAM,
    TPN,
    ID_ALL_STR,
    ID_100_STR,
    ID_100_INT,
    ID_1_STR,
    ID_1_INT,
    ID_TWO_STR,
    ID_2_INT,
    CHILD_GROUP,
    PARENT_GROUP,
    USER,
    IRON,
)

MARIADB_URL = "mariadb" if os.environ.get("MARIADB_ROOT_PASSWORD") else "127.0.0.1"

URL_SQLITE = "sqlite:///pp_test.db"
URL_MARIADB = f"mariadb+mariadbconnector://pp_user:pp_pw@{MARIADB_URL}:3306/pp_db"


@pytest.fixture
def serial_authority() -> SerialAuthority:
    auth = SerialAuthority(nodes=TPN)
    init_auth(auth)
    return auth


@pytest.fixture
def db_engine(request):
    engine = create_engine(request._parent_request.param, echo=False)

    yield engine

    DeclarativeMeta.metadata.drop_all(bind=engine)  # clean the db for the next test


@pytest.fixture
def sqlalchemy_authority(db_engine) -> SQLAlchemyAuthority:
    auth = SQLAlchemyAuthority(nodes=TPN, engine=db_engine)
    init_auth(auth)
    return auth


def init_auth(auth: SerialAuthority | SQLAlchemyAuthority):
    # The authority created here should fulfil the properties of the two save files
    # `./serial/save_file.yaml` and `./serial/save_file.json`

    for group in [FOOD, ANIMAL_BASED, PLANT_BASED]:
        auth.new_group(gid=group)
    for subject in [
        EGG,
        SPAM,
        HAM,
        ORANGE,
        APPLE,
        PEAR,
        BANANA,
    ]:
        auth.new_subject(sid=subject)

    auth.group_add_member_group(gid=FOOD, member_gid=ANIMAL_BASED)
    auth.group_add_member_group(gid=FOOD, member_gid=PLANT_BASED)

    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=EGG)
    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=SPAM)
    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=HAM)

    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=ORANGE)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=APPLE)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=PEAR)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=BANANA)

    auth.group_add_node(gid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL)

    auth.group_add_node(gid=ANIMAL_BASED, node=TPN.TOWNY_CHAT_TOWN)

    auth.group_add_node(gid=PLANT_BASED, node=TPN.TOWNY_CHAT_NATION)

    auth.group_add_node(gid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt")
    auth.group_add_node(gid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="gold")

    auth.group_add_node(gid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt")
    auth.group_add_node(gid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold")

    auth.subject_add_node(sid=HAM, node=TPN.TOWNY_WILD_)  # < diese wars


@pytest.fixture
def serial_authority_typed() -> SerialAuthority:
    auth = SerialAuthority()

    for group in [ID_ALL_STR, ID_100_INT, ID_100_STR]:
        auth.new_group(gid=group)

    for subject in [
        ID_1_STR,
        ID_1_INT,
        ID_TWO_STR,
        ID_2_INT,
    ]:
        auth.new_subject(sid=subject)

    auth.group_add_member_group(gid=ID_ALL_STR, member_gid=ID_100_STR)
    auth.group_add_member_group(gid=ID_ALL_STR, member_gid=ID_100_INT)

    auth.group_add_member_subject(gid=ID_100_INT, member_sid=ID_1_INT)
    auth.group_add_member_subject(gid=ID_100_INT, member_sid=ID_1_STR)

    auth.group_add_member_subject(gid=ID_100_STR, member_sid=ID_2_INT)
    auth.group_add_member_subject(gid=ID_100_STR, member_sid=ID_TWO_STR)

    return auth


def init_auth_for_get_permissions(auth: SerialAuthority | SQLAlchemyAuthority):
    for group in [PARENT_GROUP, CHILD_GROUP]:
        auth.new_group(gid=group)
    auth.new_subject(sid=USER)

    auth.group_add_member_group(gid=PARENT_GROUP, member_gid=CHILD_GROUP)

    auth.group_add_member_subject(gid=CHILD_GROUP, member_sid=USER)

    auth.group_add_node(gid=PARENT_GROUP, node=TPN.TOWNY_CHAT_)
    auth.group_add_node(gid=PARENT_GROUP, node=TPN.TOWNY_WILD_)

    auth.group_add_node(gid=CHILD_GROUP, node=TPN.TOWNY_CHAT_TOWN)
    auth.group_add_node(gid=CHILD_GROUP, node=TPN.TOWNY_WILD_BUILD_X, payload=IRON)
    auth.group_add_node(gid=CHILD_GROUP, node=TPN.TOWNY_WILD_BUILD_IRON)

    auth.subject_add_node(sid=USER, node=TPN.TOWNY_WILD_BUILD_)


@pytest.fixture
def serial_authority_get_permissions() -> SerialAuthority:
    auth = SerialAuthority(nodes=TPN)
    init_auth_for_get_permissions(auth)
    return auth


@pytest.fixture
def sql_authority_get_permissions(db_engine) -> SQLAlchemyAuthority:
    auth = SQLAlchemyAuthority(nodes=TPN, engine=db_engine)
    init_auth_for_get_permissions(auth)
    return auth
