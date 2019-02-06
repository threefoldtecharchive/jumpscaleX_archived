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

from decimal import Decimal

class CurrencyPrecisionOverflow(Exception):
    """
    CurrencyPrecisionOverflow error, caused when the value is too precise
    """
    def __init__(self, value):
        super().__init__("value {} is too precise to be a value, can have only 9 numbers after the decimal point".format(str(value)))
        if not isinstance(value, Decimal):
            raise TypeError("invalid value, expected it to be of type Decimal not {}".format(type(value)))
        self._value = value

    @property
    def precision(self):
        """
        The precision of the value that caused the overflow.
        """
        _, _, exp = self.value
        return abs(exp)

    @property
    def value(self):
        """
        The value that caused the overflow.
        """
        return self._value

class CurrencyNegativeValue(Exception):
    """
    CurrencyNegativeValue error, caused when the value is negative
    """
    def __init__(self, value):
        super().__init__("currency has to be at least 0, while value {} is negative".format(str(value)))
        if not isinstance(value, Decimal):
            raise TypeError("invalid value, expected it to be of type Decimal not {}".format(type(value)))
        self._value = value

    @property
    def value(self):
        """
        The value that caused the overflow.
        """
        return self._value
