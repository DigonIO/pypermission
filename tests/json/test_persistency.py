from pypermission.json import Authority

EGG = "egg"
SPAM = "spam"
HAM = "ham"

ORANGE = 1
APPLE = 2
PEAR = 3
BANANA = 4

FOOD = 1234
ANIMAL_BASED = "animal_based"
PLANT_BASED = "plant_based"


def test_affiliation_persistency():
    auth = Authority()

    auth.subject_add(subject_id=EGG)
    auth.subject_add(subject_id=SPAM)
    auth.subject_add(subject_id=HAM)

    auth.subject_add(subject_id=ORANGE)
    auth.subject_add(subject_id=APPLE)
    auth.subject_add(subject_id=PEAR)
    auth.subject_add(subject_id=BANANA)

    auth.group_add(group_id=FOOD)
    auth.group_add(group_id=ANIMAL_BASED)
    auth.group_add(group_id=PLANT_BASED)

    auth.group_add_subject(group_id=FOOD, subject_id=EGG)
    auth.group_add_subject(group_id=FOOD, subject_id=SPAM)
    auth.group_add_subject(group_id=FOOD, subject_id=HAM)
    auth.group_add_subject(group_id=FOOD, subject_id=ORANGE)
    auth.group_add_subject(group_id=FOOD, subject_id=APPLE)
    auth.group_add_subject(group_id=FOOD, subject_id=PEAR)
    auth.group_add_subject(group_id=FOOD, subject_id=BANANA)

    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=EGG)
    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=SPAM)
    auth.group_add_subject(group_id=ANIMAL_BASED, subject_id=HAM)

    auth.group_add_subject(group_id=PLANT_BASED, subject_id=ORANGE)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=APPLE)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=PEAR)
    auth.group_add_subject(group_id=PLANT_BASED, subject_id=BANANA)

    serial_data = auth.save_to_str()

    auth2 = Authority()
    auth2.load_from_str(serial_data=serial_data)

    assert set(auth._subjects.keys()) == set(auth2._subjects.keys())
    assert set(auth._groups.keys()) == set(auth2._groups.keys())

    assert auth._groups[FOOD]._subject_ids == auth2._groups[FOOD]._subject_ids
    assert auth._groups[ANIMAL_BASED]._subject_ids == auth2._groups[ANIMAL_BASED]._subject_ids
    assert auth._groups[PLANT_BASED]._subject_ids == auth2._groups[PLANT_BASED]._subject_ids
