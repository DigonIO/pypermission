import pytest

from pypermission.exc import PyPermissionError
from pypermission.util.input_validation import (
    assert_action,
    assert_child_role,
    assert_parent_role,
    assert_resource_id,
    assert_resource_type,
    assert_role,
    assert_subject,
)

ALWAYS_ALLOWED = [
    ("admin", ""),
    ("abc_123", ""),
    ("List(Item)", ""),
    ("List{Item}", ""),
    ("A B C D", ""),
    ("version_1.2.3", ""),
    ("file-name-01", ""),
    ("notes, draft version", ""),
    ("hello!", ""),
    ("email@example.com", ""),
    ("price$", ""),
    ("C#Code", ""),
    ("100% sure", ""),
    ("value+1", ""),
    ("path/to/file", ""),
    ('quote "text"', ""),
    ("88ecfc8f-7f07-4e83-9b39-67cd2e0d9814", ""),
    ("new<T>", ""),
    ("tabs\tnope", ""),
    ("it's fine", ""),
    ("German - ÄäÖöÜüß", ""),
    ("French - bêcédéè", ""),
    ("Greek - ἀγκών εγγραφή εγγεγραμμένος", ""),
    ("Many Languages - ⴰⵎⴰⵣⵉⵖ中文ÆØÅæㄏㄢøå字漢", ""),
    ("ℹ️ W🤩W R🔒🫷ES 🤟🏼 ✔️", ""),
    ("📈 To the moon 🚀", ""),
    ("ax* cs", ""),
    ("value*multiplier", ""),
]

ALWAYS_FORBIDDEN = [
    (":", ""),
    ("xx :s", ""),
    ("xx: cs", ""),
    (" admin", ""),
    ("admin ", ""),
    (" ", ""),
    ("Item[123", ""),
    ("]Item", ""),
    ("a:b", ""),
    ("[]", ""),
]


CONTAINS_BRACKET = [
    ("List[Item]", ""),
    ("DATASET[2024].csv", ""),
    ("User[Anna]_88ecfc8f-7f07-4e83-9b39-67cd2e0d9814", ""),
]

SINGLE_WILDCARD = [
    ("*", ""),
]

# ============================ subject, role, action ===========================


@pytest.mark.parametrize(
    "value, note",
    ALWAYS_ALLOWED + CONTAINS_BRACKET,
)
def test_values__passable(*, value: str, note: str) -> None:
    assert_subject(subject=value)
    assert_role(role=value)
    assert_child_role(child_role=value)
    assert_parent_role(parent_role=value)
    assert_action(action=value)


@pytest.mark.parametrize(
    "value, note",
    ALWAYS_FORBIDDEN + SINGLE_WILDCARD,
)
def test_raise_on_invalid_subject_role_action(*, value: str, note: str) -> None:
    with pytest.raises(PyPermissionError) as err:
        assert_subject(subject=value)
        assert_role(role=value)
        assert_child_role(child_role=value)
        assert_parent_role(parent_role=value)
        assert_action(action=value)


# =============================== resource_type ================================


@pytest.mark.parametrize(
    "value, note",
    ALWAYS_ALLOWED,
)
def test_resource_type__passable(*, value: str, note: str) -> None:
    assert_resource_type(resource_type=value)


@pytest.mark.parametrize(
    "value, note",
    ALWAYS_FORBIDDEN + CONTAINS_BRACKET + SINGLE_WILDCARD,
)
def test_raise_on_invalid_resource_type(*, value: str, note: str) -> None:
    with pytest.raises(PyPermissionError) as err:
        assert_resource_type(resource_type=value)


# =============================== resource_id ================================


@pytest.mark.parametrize(
    "value, note",
    ALWAYS_ALLOWED + CONTAINS_BRACKET + SINGLE_WILDCARD,
)
def test_resource_id__passable(*, value: str, note: str) -> None:
    assert_resource_id(resource_id=value)


@pytest.mark.parametrize(
    "value, note",
    ALWAYS_FORBIDDEN,
)
def test_raise_on_invalid_resource_id(*, value: str, note: str) -> None:
    with pytest.raises(PyPermissionError) as err:
        assert_resource_id(resource_id=value)
