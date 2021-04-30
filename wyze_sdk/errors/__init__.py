class WyzeClientError(Exception):
    """Base class for Client errors"""


class WyzeRequestError(WyzeClientError):
    """Error raised when there's a problem with the request that's being submitted."""


class WyzeFeatureNotSupportedError(WyzeRequestError):
    """Error raised when the requested action on a device isn't supported."""
    def __init__(self, action: str):
        msg = f"{action} is not supported on this device"
        super(WyzeRequestError, self).__init__(msg)


class WyzeApiError(WyzeClientError):
    """Error raised when Wyze does not send the expected response.

    .. note ::
        The message (str) passed into the exception is used when
        a user converts the exception to a str.
        i.e. ``str(WyzeApiError("This text will be sent as a string."))``
    """

    def __init__(self, message, response):
        msg = f"{message}\nThe server responded with: {response}"
        #: The WyzeResponse object containing all of the data sent back from the API
        self.response = response
        super(WyzeApiError, self).__init__(msg)


class WyzeClientNotConnectedError(WyzeClientError):
    """Error raised when attempting to send messages over the websocket when the
    connection is closed."""


class WyzeObjectFormationError(WyzeClientError):
    """Error raised when a constructed object is not valid/malformed"""


class WyzeClientConfigurationError(WyzeClientError):
    """Error raised when attempting to send messages over the websocket when the
    connection is closed."""
