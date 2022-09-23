class PyPermissionError(Exception):
    ...


class MissingPathError(PyPermissionError):
    ...


class GroupCycleError(PyPermissionError):
    ...


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
