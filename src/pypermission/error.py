class PyPermissionError(Exception):
    """Basic PyPermission error definition."""


class MissingPathError(PyPermissionError):
    """Raised if no file path is defined while saving to or reading from a file."""


class GroupCycleError(PyPermissionError):
    """Raised to prevent a group cycle."""


class PermissionParsingError(PyPermissionError):
    ...


class EntityIDCollisionError(PyPermissionError):
    ...


class UnknownPermissionNodeError(PermissionError):
    ...


class UnknownSubjectIDError(PyPermissionError):
    ...


class UnknownGroupIDError(PyPermissionError):
    ...


class MissingPayloadError(PyPermissionError):
    ...


class UnusedPayloadError(PyPermissionError):
    ...
