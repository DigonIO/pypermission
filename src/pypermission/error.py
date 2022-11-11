class PyPermissionError(Exception):
    """Basic PyPermission error definition."""


class PathError(PyPermissionError):
    """Raised if no file path is defined while saving to or reading from a file."""


class RoleCycleError(PyPermissionError):
    """Raised to prevent a role cycle."""


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
