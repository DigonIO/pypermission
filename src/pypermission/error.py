class PyPermissionError(Exception):
    """Basic PyPermission error definition."""


class PathError(PyPermissionError):
    """Raised if no file path is defined while saving to or reading from a file."""


class GroupCycleError(PyPermissionError):
    """Raised to prevent a group cycle."""


class ParsingError(PyPermissionError):
    ...


class UnknownPermissionNodeError(PyPermissionError):
    ...


class EntityIDError(PyPermissionError):
    ...


class MissingPayloadError(PyPermissionError):
    ...


class UnusedPayloadError(PyPermissionError):
    ...
