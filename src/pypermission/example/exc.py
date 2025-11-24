################################################################################
#### Generic Errors
################################################################################


class MeetDownError(Exception):
    """
    MeetDownError is the standard error of the MeetDown Example application.

    Attributes
    ----------
    message : str
        A detailed description of the occurred error.
    """

    message: str

    def __init__(self, message: str = ""):
        self.message = message
