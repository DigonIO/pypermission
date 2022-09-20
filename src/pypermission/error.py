class PyPermissionError(Exception):
    ...


class MissingPathError(Exception):
    ...


class PermissionParsingError(PyPermissionError):
    ...


class EntityIDCollisionError(PyPermissionError):
    ...


class UnknownSubjectIDError(PyPermissionError):
    ...


class UnknownGroupIDError(PyPermissionError):
    ...


class MissingPayloadError(PyPermissionError):
    ...


class UnusedPayloadError(PyPermissionError):
    ...
