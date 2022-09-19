class PyPermissionError(Exception):
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
