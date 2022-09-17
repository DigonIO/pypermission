class PyPermissionError(Exception):
    ...


class UnknownSubjectIDError(PyPermissionError):
    ...


class UnknownGroupIDError(PyPermissionError):
    ...


class MissingPayloadError(PyPermissionError):
    ...

class UnusedPayloadError(PyPermissionError):
    ...
