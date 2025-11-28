from collections.abc import Callable
from functools import wraps
from typing import Any, TypeIs, NewType, Literal
from pypermission.exc import PyPermissionError
import inspect
from enum import StrEnum

Subject = NewType("Subject", str)
Role = NewType("Role", str)
ResourceType = NewType("ResourceType", str)
ResourceID = NewType("ResourceID", str)
Action = NewType("Action", str)

type DefinitionalT = Literal["Subject", "Role", "ResourceType", "ResourceID", "Action"]


class DefID(StrEnum):
    SUBJECT = "subject"
    ROLE = "role"
    CHILD_ROLE = "child_role"
    PARENT_ROLE = "parent_role"
    RESOURCE_TYPE = "resource_type"
    RESOURCE_ID = "resource_id"
    ACTION = "action"


def _raise_on_isinstance_str_fail(*, val: Any, def_id: DefID) -> None:
    if not isinstance(val, str):
        raise PyPermissionError(
            f"All `{def_id}` identifiers must be subclass of string. "
            f"Got {type(val).__name__}."
        )


def _raise_on_colon(*, val: Any, def_id: DefID) -> None:
    if ":" in val:
        raise PyPermissionError(f"Invalid character `:` found in `{def_id}`!")


def _raise_on_bracket(*, val: str, def_id: DefID) -> None:
    if "[" in val:
        raise PyPermissionError(f"Invalid character `[` found in `{def_id}`!")
    if "]" in val:
        raise PyPermissionError(f"Invalid character `]` found in `{def_id}`!")


def _raise_on_empty(*, val: str, def_id: DefID) -> None:
    if val == "":
        raise PyPermissionError(f"Argument `{def_id}` cannot be empty!")


def _raise_on_wildcard(*, val: str, def_id: DefID) -> None:
    if val == "*":
        raise PyPermissionError(f"Argument `{def_id}` cannot be the character `*`!")


def _raise_on_lr_whitespaces(*, val: str, def_id: DefID) -> None:
    if val != val.strip():
        raise PyPermissionError(
            f"Argument `{def_id}` cannot have leading or trailing spaces!"
        )


def _raise_on_bracket_imbalance(*, value: str, def_id: DefID) -> None:
    depth = 0
    last = ""
    for ch in value:
        if ch == "[":
            depth += 1
        elif ch == "]":
            if last == "[":
                raise PyPermissionError(
                    f"Invalid `{def_id}`: closing ']' used prematurely."
                )
            depth -= 1
            if depth < 0:
                raise PyPermissionError(
                    f"Invalid `{def_id}`: unmatched closing ']' in {value}."
                )
        last = ch
    if depth != 0:
        raise PyPermissionError(
            f"Invalid `{def_id}`: unmatched opening '[' in {value}."
        )


def assert_subject(subject: Any) -> TypeIs[Subject]:
    _raise_on_isinstance_str_fail(val=subject, def_id=DefID.SUBJECT)
    _raise_on_empty(val=subject, def_id=DefID.SUBJECT)
    _raise_on_lr_whitespaces(val=subject, def_id=DefID.SUBJECT)
    _raise_on_colon(val=subject, def_id=DefID.SUBJECT)
    _raise_on_wildcard(val=subject, def_id=DefID.SUBJECT)
    _raise_on_bracket_imbalance(value=subject, def_id=DefID.SUBJECT)
    return True


def assert_role(role: Any) -> TypeIs[Role]:
    _raise_on_isinstance_str_fail(val=role, def_id=DefID.ROLE)
    _raise_on_empty(val=role, def_id=DefID.ROLE)
    _raise_on_lr_whitespaces(val=role, def_id=DefID.ROLE)
    _raise_on_colon(val=role, def_id=DefID.ROLE)
    _raise_on_wildcard(val=role, def_id=DefID.ROLE)
    _raise_on_bracket_imbalance(value=role, def_id=DefID.ROLE)
    return True


def assert_parent_role(parent_role: Any) -> TypeIs[Role]:
    _raise_on_isinstance_str_fail(val=parent_role, def_id=DefID.PARENT_ROLE)
    _raise_on_empty(val=parent_role, def_id=DefID.PARENT_ROLE)
    _raise_on_lr_whitespaces(val=parent_role, def_id=DefID.PARENT_ROLE)
    _raise_on_colon(val=parent_role, def_id=DefID.PARENT_ROLE)
    _raise_on_wildcard(val=parent_role, def_id=DefID.PARENT_ROLE)
    _raise_on_bracket_imbalance(value=parent_role, def_id=DefID.PARENT_ROLE)
    return True


def assert_child_role(child_role: Any) -> TypeIs[Role]:
    _raise_on_isinstance_str_fail(val=child_role, def_id=DefID.CHILD_ROLE)
    _raise_on_empty(val=child_role, def_id=DefID.CHILD_ROLE)
    _raise_on_lr_whitespaces(val=child_role, def_id=DefID.CHILD_ROLE)
    _raise_on_colon(val=child_role, def_id=DefID.CHILD_ROLE)
    _raise_on_wildcard(val=child_role, def_id=DefID.CHILD_ROLE)
    _raise_on_bracket_imbalance(value=child_role, def_id=DefID.CHILD_ROLE)
    return True


def assert_resource_type(resource_type: Any) -> TypeIs[ResourceType]:
    _raise_on_isinstance_str_fail(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_empty(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_lr_whitespaces(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_colon(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_wildcard(val=resource_type, def_id=DefID.RESOURCE_TYPE)
    _raise_on_bracket(val=resource_type, def_id=DefID.SUBJECT)
    return True


def assert_resource_id(resource_id: Any) -> TypeIs[ResourceID]:
    _raise_on_isinstance_str_fail(val=resource_id, def_id=DefID.RESOURCE_ID)
    _raise_on_lr_whitespaces(val=resource_id, def_id=DefID.RESOURCE_ID)
    _raise_on_colon(val=resource_id, def_id=DefID.RESOURCE_ID)
    _raise_on_bracket_imbalance(value=resource_id, def_id=DefID.RESOURCE_ID)
    return True


def assert_action(action: Any) -> TypeIs[Action]:
    _raise_on_isinstance_str_fail(val=action, def_id=DefID.ACTION)
    _raise_on_empty(val=action, def_id=DefID.ACTION)
    _raise_on_lr_whitespaces(val=action, def_id=DefID.ACTION)
    _raise_on_colon(val=action, def_id=DefID.ACTION)
    _raise_on_wildcard(val=action, def_id=DefID.ACTION)
    _raise_on_bracket_imbalance(value=action, def_id=DefID.ACTION)
    return True


type C[S] = Callable[[Any], TypeIs[S]]


VALIDATION_RULES: dict[
    DefID, C[Subject] | C[Role] | C[ResourceType] | C[ResourceID] | C[Action]
] = {
    DefID.SUBJECT: assert_subject,
    DefID.ROLE: assert_role,
    DefID.CHILD_ROLE: assert_child_role,
    DefID.PARENT_ROLE: assert_parent_role,
    DefID.RESOURCE_TYPE: assert_resource_type,
    DefID.RESOURCE_ID: assert_resource_id,
    DefID.ACTION: assert_action,
}

SKIP_IDENTIFIERS = {
    "child_role",
    "parent_role",
    "db",
    "ancestors",
    "inherited",
    "cls",
    "self",
    "permission",
    "include_descendant_subjects",
    "include_ascendant_roles",
}


def validate_rbac_parameters[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """
    Apply input validation to a method of the RBAC API.

    Provides the following guardrails:

    * The characters `[` and `]` are not allowed anywhere inside ResourceType
    * Strings `"*"` and `""` are only allowed in ResourceID
    * `:` can never be used within any string
    * Leading & trailing spaces are never allowed
    * Decorator will fail to apply, if trying to wrap a function with unexpected signature
    """
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
