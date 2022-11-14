import pytest

from ..helpers import assert_loaded_authority, URL_SQLITE, URL_MARIADB

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


@pytest.mark.parametrize(
    "sqlalchemy_authority",
    (
        URL_SQLITE,
        URL_MARIADB,
    ),
    indirect=["sqlalchemy_authority"],
)
def test_basic_integration(sqlalchemy_authority):
    assert_loaded_authority(sqlalchemy_authority)
