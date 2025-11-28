from collections.abc import Callable
from functools import wraps
import re
from re import Pattern
from typing import Any, TypeIs, NewType, Literal
from pypermission.exc import PyPermissionError
import inspect
from enum import StrEnum

Subject = NewType("Subject", str)
Role = NewType("Role", str)
ResourceType = NewType("ResourceType", str)
ResourceID = NewType("ResourceID", str)
Action = NewType("Action", str)


_RE_ALLOWED = r"^\*|^[a-zA-Z0-9_\[\] \.\,\-]+$"
_RE_FORBIDDEN = r"[^a-zA-Z0-9_\[\] \.\,\-\*]"
# TODO: this needs work
_SUBJECT_CHAR_RE = _RE_ALLOWED
_ROLE_CHAR_RE = _RE_ALLOWED
_RESOURCE_TYPE_CHAR_RE = _RE_ALLOWED
_RESOURCE_ID_CHAR_RE = _RE_ALLOWED
_ACTION_CHAR_RE = _RE_ALLOWED

type DefinitionalT = Literal["Subject", "Role", "ResourceType", "ResourceID", "Action"]


class DefID(StrEnum):
    SUBJECT = "subject"
    ROLE = "role"
    CHILD_ROLE = "child_role"
    PARENT_ROLE = "parent_role"
    RESOURCE_TYPE = "resource_type"
    RESOURCE_ID = "resource_id"
    ACTION = "action"


_DEFINITIONAL_T_MAP: dict[DefID, DefinitionalT] = {
    DefID.SUBJECT: "Subject",
    DefID.ROLE: "Role",
    DefID.CHILD_ROLE: "Role",
    DefID.PARENT_ROLE: "Role",
    DefID.RESOURCE_TYPE: "ResourceType",
    DefID.RESOURCE_ID: "ResourceID",
    DefID.ACTION: "Action",
}

_RE_MAP: dict[DefID, str] = {
    DefID.SUBJECT: _SUBJECT_CHAR_RE,
    DefID.ROLE: _ROLE_CHAR_RE,
    DefID.CHILD_ROLE: _ROLE_CHAR_RE,
    DefID.PARENT_ROLE: _ROLE_CHAR_RE,
    DefID.RESOURCE_TYPE: _RESOURCE_TYPE_CHAR_RE,
    DefID.RESOURCE_ID: _RESOURCE_ID_CHAR_RE,
    DefID.ACTION: _ACTION_CHAR_RE,
}

_RE_PAT: dict[DefID, Pattern[str]] = {k: re.compile(v) for k, v in _RE_MAP.items()}


def _raise_on_isinstance_str_fail(*, val: Any, def_id: DefID) -> None:
    if not isinstance(val, str):
        breakpoint()
        raise PyPermissionError(
            f"{def_id} must be a string, got {type(val).__name__}. "
            f"Note: All {def_id} identifiers must be subclass of string."
        )


def _raise_on_empty_and_lr_whitespaces(*, val: str, def_id: DefID) -> None:
    if val == "":
        raise PyPermissionError(f"`{def_id}` cannot be empty!")
    if val != val.strip():
        raise PyPermissionError(f"`{def_id}` cannot have leading or trailing spaces!")


def _raise_on_regex_violation(*, val: str, def_id: DefID) -> None:
    disallowed_chars = re.search(_RE_FORBIDDEN, val)
    if disallowed_chars:
        pos = disallowed_chars.start()
        char = disallowed_chars.group(0)
        raise PyPermissionError(
            f"{def_id} name contains invalid characters. "
            f"Disallowed character '{char}' found at position {pos}."
        )
    if not _RE_PAT[def_id].match(val):
        raise PyPermissionError(f"Invalid {def_id}: {val!r}")


def _raise_on_bracket_imbalance(*, value: str, def_id: DefID) -> None:
    depth = 0
    for ch in value:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth < 0:
                raise PyPermissionError(
                    f"Invalid {def_id}: unmatched closing ']' in {value}."
                )
    if depth != 0:
        raise PyPermissionError(f"Invalid {def_id}: unmatched opening '[' in {value}.")


def assert_subject(subject: Any) -> TypeIs[Subject]:
    _raise_on_isinstance_str_fail(val=subject, def_id=DefID.SUBJECT)
    _raise_on_empty_and_lr_whitespaces(val=subject, def_id=DefID.SUBJECT)
    _raise_on_regex_violation(val=subject, def_id=DefID.SUBJECT)
    _raise_on_bracket_imbalance(value=subject, def_id=DefID.SUBJECT)
    return True


def assert_role(role: Any) -> TypeIs[Role]:
    _raise_on_isinstance_str_fail(val=role, def_id=DefID.ROLE)
    _raise_on_empty_and_lr_whitespaces(val=role, def_id=DefID.ROLE)
    _raise_on_regex_violation(val=role, def_id=DefID.ROLE)
    _raise_on_bracket_imbalance(value=role, def_id=DefID.ROLE)
    return True


def assert_resource_type(resource_type: Any) -> TypeIs[ResourceType]:
    _raise_on_isinstance_str_fail(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_empty_and_lr_whitespaces(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_regex_violation(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_bracket_imbalance(value=resource_type, def_id=DefID.RESOURCE_TYPE)
    return True


def assert_resource_id(resource_id: Any) -> TypeIs[ResourceID]:
    _raise_on_isinstance_str_fail(val=resource_id, def_id=DefID.RESOURCE_ID)
    _raise_on_empty_and_lr_whitespaces(val=resource_id, def_id=DefID.RESOURCE_ID)
    _raise_on_regex_violation(val=resource_id, def_id=DefID.RESOURCE_ID)
    _raise_on_bracket_imbalance(value=resource_id, def_id=DefID.RESOURCE_ID)
    return True


def assert_action(action: Any) -> TypeIs[Action]:
    _raise_on_isinstance_str_fail(val=action, def_id=DefID.ACTION)
    _raise_on_empty_and_lr_whitespaces(val=action, def_id=DefID.ACTION)
    _raise_on_regex_violation(val=action, def_id=DefID.ACTION)
    _raise_on_bracket_imbalance(value=action, def_id=DefID.ACTION)
    return True


type C[S] = Callable[[Any], TypeIs[S]]


VALIDATION_RULES: dict[
    DefID, C[Subject] | C[Role] | C[ResourceType] | C[ResourceID] | C[Action]
] = {
    DefID.SUBJECT: assert_subject,
    DefID.ROLE: assert_role,
    DefID.RESOURCE_TYPE: assert_resource_type,
    DefID.RESOURCE_ID: assert_resource_id,
    DefID.ACTION: assert_action,
}

SKIP_IDENTIFIERS = {"child_role", "parent_role", "db", "ancestors", "inherited", "cls"}


def validate_rbac_parameters[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    sig = inspect.signature(func)

    param_names = set(sig.parameters)
    validateable_names = set(VALIDATION_RULES)
    names_to_validate = param_names & validateable_names
    if unexpected_args := param_names - (SKIP_IDENTIFIERS | validateable_names):
        raise PyPermissionError(
            f"Found unexpected args when applying the decorator: {unexpected_args}"
        )

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        # Bind arguments to parameter names (see if really necessary)
        bound = sig.bind(*args, **kwargs)  # <- here
        bound.apply_defaults()  # <- here

        for name in names_to_validate:
            VALIDATION_RULES[DefID(name)](bound.arguments[name])

        return func(*args, **kwargs)

    return wrapper
