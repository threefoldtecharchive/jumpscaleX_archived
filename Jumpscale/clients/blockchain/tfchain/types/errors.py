"""
Public TFChain Errors
"""

class InvalidPublicKeySpecifier(Exception):
    """
    InvalidPublicKeySpecifier error
    """


class UnknownTransansactionVersion(Exception):
    """
    UnknownTransansactionVersion error
    """


class InsufficientFunds(Exception):
    """
    InsufficientFunds error
    """


class ExplorerError(Exception):
    """
    Generic Explorer error
    """
    def __init__(self, message, endpoint):
        super().__init__("{}: {}".format(endpoint, message))
        if not isinstance(endpoint, str):
            raise TypeError("invalid endpoint, expected it to be of type str not {}".format(type(endpoint)))
        self._endpoint = endpoint
    
    @property
    def endpoint(self):
        """
        The endpoint that was called.
        """
        return self._endpoint


class ExplorerNoContent(ExplorerError):
    """
    ExplorerNoContent error
    """

class ExplorerServerError(ExplorerError):
    """
    ExplorerServerError error
    """

class ExplorerNotAvailable(ExplorerError):
    """
    ExplorerNotAvailable error
    """
    def __init__(self, message, endpoint, addresses):
        super().__init__(message, endpoint)
        if not isinstance(addresses, list):
            raise TypeError("invalid addresses, expected it to be of type list not {}".format(type(addresses)))
        self._addresses = addresses

    @property
    def addresses(self):
        """
        The addresses that were used to try to reach an explorer.
        """
        return self._addresses

class ExplorerInvalidResponse(ExplorerError):
    """
    ExplorerInvalidResponse error
    """
    def __init__(self, message, endpoint, response):
        super().__init__(message, endpoint)
        if not isinstance(response, dict):
            raise TypeError("invalid response, expected it to be of type dict not {}".format(type(response)))
        self._response = response

    @property
    def response(self):
        """
        The invalid response
        """
        return self._response


class DoubleSignError(Exception):
    """
    DoubleSignError error
    """
