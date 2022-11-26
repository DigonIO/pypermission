import pytest
from sqlalchemy import create_engine

from pypermission.serial import SerialAuthority
from pypermission.sqlalchemy import SQLAlchemyAuthority
from pypermission.sqlalchemy.models import DeclarativeMeta
from tests.helpers import (
    ANIMAL_BASED,
    APPLE,
    BANANA,
    CHILD_GROUP,
    EGG,
    FOOD,
    HAM,
    ID_1_INT,
    ID_1_STR,
    ID_2_INT,
    ID_100_INT,
    ID_100_STR,
    ID_ALL_STR,
    ID_TWO_STR,
    IRON,
    ORANGE,
    PARENT_GROUP,
    PEAR,
    PLANT_BASED,
    SPAM,
    TPN,
    USER,
    USER_GROUP,
)


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

    for role in [FOOD, ANIMAL_BASED, PLANT_BASED]:
        auth.new_role(rid=role)
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

    auth.role_add_member_role(rid=FOOD, member_rid=ANIMAL_BASED)
    auth.role_add_member_role(rid=FOOD, member_rid=PLANT_BASED)

    auth.role_add_member_subject(rid=ANIMAL_BASED, member_sid=EGG)
    auth.role_add_member_subject(rid=ANIMAL_BASED, member_sid=SPAM)
    auth.role_add_member_subject(rid=ANIMAL_BASED, member_sid=HAM)

    auth.role_add_member_subject(rid=PLANT_BASED, member_sid=ORANGE)
    auth.role_add_member_subject(rid=PLANT_BASED, member_sid=APPLE)
    auth.role_add_member_subject(rid=PLANT_BASED, member_sid=PEAR)
    auth.role_add_member_subject(rid=PLANT_BASED, member_sid=BANANA)

    auth.role_add_node(rid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL)

    auth.role_add_node(rid=ANIMAL_BASED, node=TPN.TOWNY_CHAT_TOWN)

    auth.role_add_node(rid=PLANT_BASED, node=TPN.TOWNY_CHAT_NATION)

    auth.role_add_node(rid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt")
    auth.role_add_node(rid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="gold")

    auth.role_add_node(rid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt")
    auth.role_add_node(rid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold")

    auth.subject_add_node(sid=HAM, node=TPN.TOWNY_WILD_)  # < diese wars


@pytest.fixture
def serial_authority_typed() -> SerialAuthority:
    auth = SerialAuthority()

    for role in [ID_ALL_STR, ID_100_INT, ID_100_STR]:
        auth.new_role(rid=role)

    for subject in [
        ID_1_STR,
        ID_1_INT,
        ID_TWO_STR,
        ID_2_INT,
    ]:
        auth.new_subject(sid=subject)

    auth.role_add_member_role(rid=ID_ALL_STR, member_rid=ID_100_STR)
    auth.role_add_member_role(rid=ID_ALL_STR, member_rid=ID_100_INT)

    auth.role_add_member_subject(rid=ID_100_INT, member_sid=ID_1_INT)
    auth.role_add_member_subject(rid=ID_100_INT, member_sid=ID_1_STR)

    auth.role_add_member_subject(rid=ID_100_STR, member_sid=ID_2_INT)
    auth.role_add_member_subject(rid=ID_100_STR, member_sid=ID_TWO_STR)

    return auth


def init_auth_for_get_info_subject(auth: SerialAuthority | SQLAlchemyAuthority):
    for role in [PARENT_GROUP, CHILD_GROUP]:
        auth.new_role(rid=role)
    auth.new_subject(sid=USER)

    auth.role_add_member_role(rid=PARENT_GROUP, member_rid=CHILD_GROUP)

    auth.role_add_member_subject(rid=CHILD_GROUP, member_sid=USER)

    auth.role_add_node(rid=PARENT_GROUP, node=TPN.TOWNY_CHAT_)
    auth.role_add_node(rid=PARENT_GROUP, node=TPN.TOWNY_WILD_)

    auth.role_add_node(rid=CHILD_GROUP, node=TPN.TOWNY_CHAT_TOWN)
    auth.role_add_node(rid=CHILD_GROUP, node=TPN.TOWNY_WILD_BUILD_X, payload=IRON)
    auth.role_add_node(rid=CHILD_GROUP, node=TPN.TOWNY_WILD_BUILD_IRON)

    auth.subject_add_node(sid=USER, node=TPN.TOWNY_WILD_BUILD_)


def init_auth_for_get_info_role(auth: SerialAuthority | SQLAlchemyAuthority):
    for role in [PARENT_GROUP, CHILD_GROUP, USER_GROUP]:
        auth.new_role(rid=role)

    auth.role_add_member_role(rid=PARENT_GROUP, member_rid=CHILD_GROUP)

    auth.role_add_member_role(rid=CHILD_GROUP, member_rid=USER_GROUP)

    auth.role_add_node(rid=PARENT_GROUP, node=TPN.TOWNY_CHAT_)
    auth.role_add_node(rid=PARENT_GROUP, node=TPN.TOWNY_WILD_)

    auth.role_add_node(rid=CHILD_GROUP, node=TPN.TOWNY_CHAT_TOWN)
    auth.role_add_node(rid=CHILD_GROUP, node=TPN.TOWNY_WILD_BUILD_X, payload=IRON)
    auth.role_add_node(rid=CHILD_GROUP, node=TPN.TOWNY_WILD_BUILD_IRON)

    auth.role_add_node(rid=USER_GROUP, node=TPN.TOWNY_WILD_BUILD_)


@pytest.fixture
def serial_authority_get_info_subject() -> SerialAuthority:
    auth = SerialAuthority(nodes=TPN)
    init_auth_for_get_info_subject(auth)
    return auth


@pytest.fixture
def sql_authority_get_info_subject(db_engine) -> SQLAlchemyAuthority:
    auth = SQLAlchemyAuthority(nodes=TPN, engine=db_engine)
    init_auth_for_get_info_subject(auth)
    return auth


@pytest.fixture
def serial_authority_get_info_role() -> SerialAuthority:
    auth = SerialAuthority(nodes=TPN)
    init_auth_for_get_info_role(auth)
    return auth


@pytest.fixture
def sql_authority_get_info_role(db_engine) -> SQLAlchemyAuthority:
    auth = SQLAlchemyAuthority(nodes=TPN, engine=db_engine)
    init_auth_for_get_info_role(auth)
    return auth
