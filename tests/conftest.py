import pytest

from pypermission.serial import SerialAuthority

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
)


@pytest.fixture
def serial_authority() -> SerialAuthority:
    # The authority created here should fulfil the properties of the two save files
    # `./serial/save_file.yaml` and `./serial/save_file.json`
    auth = SerialAuthority(nodes=TPN)

    for group in [FOOD, ANIMAL_BASED, PLANT_BASED]:
        auth.add_group(gid=group)
    for subject in [
        EGG,
        SPAM,
        HAM,
        ORANGE,
        APPLE,
        PEAR,
        BANANA,
    ]:
        auth.add_subject(sid=subject)

    auth.group_add_member_group(gid=FOOD, member_gid=ANIMAL_BASED)
    auth.group_add_member_group(gid=FOOD, member_gid=PLANT_BASED)

    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=EGG)
    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=SPAM)
    auth.group_add_member_subject(gid=ANIMAL_BASED, member_sid=HAM)

    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=ORANGE)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=APPLE)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=PEAR)
    auth.group_add_member_subject(gid=PLANT_BASED, member_sid=BANANA)

    auth.group_add_permission(gid=FOOD, node=TPN.TOWNY_CHAT_GLOBAL)

    auth.group_add_permission(gid=ANIMAL_BASED, node=TPN.TOWNY_CHAT_TOWN)

    auth.group_add_permission(gid=PLANT_BASED, node=TPN.TOWNY_CHAT_NATION)

    auth.group_add_permission(gid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="dirt")
    auth.group_add_permission(gid=ANIMAL_BASED, node=TPN.TOWNY_WILD_BUILD_X, payload="gold")

    auth.group_add_permission(gid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="dirt")
    auth.group_add_permission(gid=PLANT_BASED, node=TPN.TOWNY_WILD_DESTROY_X, payload="gold")

    auth.subject_add_permission(sid=HAM, node=TPN.TOWNY_WILD_)

    return auth
