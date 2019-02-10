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


class CurrencyPrecisionOverflow(Exception):
    """
    CurrencyPrecisionOverflow error, caused when the value is too precise
    """
    def __init__(self, value):
        super().__init__("value {} is too precise to be a value, can have only 9 numbers after the decimal point".format(str(value)))
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
        self._value = value

    @property
    def value(self):
        """
        The value that caused the overflow.
        """
        return self._value



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

class ExplorerServerPostError(ExplorerError):
    """
    ExplorerServerPostError error
    """
    def __init__(self, message, endpoint, data):
        super().__init__(message, endpoint)
        self._data = data
    
    @property
    def data(self):
        """
        The data that could not be posted.
        """
        return self._data

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


class AtomicSwapInsufficientAmountError(Exception):
    """
    AtomicSwapInsufficientAmountError error,
    triggered when creating a contract with an amount equal or lower than
    minimum fee, which isn't allowed as such a contract cannot be redeemed/refunded.
    """
    def __init__(self, amount, minimum_miner_fee):
        super().__init__(
            "atomic swap contract requires an amount higher than the minimum miner fee ({}): {} is an invalid value".format(
                str(minimum_miner_fee), str(amount)))
        self._amount = amount
        self._minimum_miner_fee = minimum_miner_fee

    @property
    def amount(self):
        """
        The insufficient amount that was used.
        """
        return self._amount

    @property
    def minimum_miner_fee(self):
        """
        The minimum miner fee required on the network used.
        """
        return self._minimum_miner_fee


class AtomicSwapContractError(Exception):
    """
    AtomicSwapError generic Base error,
    containing the contract that went wrong.
    """
    def __init__(self, message, contract):
        super().__init__(message)
        self._contract = contract

    @property
    def contract(self):
        """
        The contract that was verified against.
        """
        return self._contract

class AtomicSwapForbidden(AtomicSwapContractError):
    """
    AtomicSwapForbidden error, caused when a contract was trying
    to be spent by an unautohorized wallet.
    """

class AtomicSwapInvalidSecret(AtomicSwapContractError):
    """
    AtomicSwapInvalidSecret error, caused when a wrong secret was used
    as an attempt to redeem an atomic swap contract. 
    """
    def __init__(self, contract):
        super().__init__(message="defined secret does not match the atomic swap's contract secret hash", contract=contract)

class AtomicSwapContractInvalid(AtomicSwapContractError):
    """
    AtomicSwapContractInvalid error, caused when a contract was deemed
    invalid during verification.
    """

class AtomicSwapContractSpent(AtomicSwapContractError):
    """
    AtomicSwapContractSpent error, caused when
    a callee tried to spend a contract that was already spent.
    """
    def __init__(self, contract, transaction):
        txid = getattr(transaction, 'id', '')
        super().__init__(message="atomic swap contract has already been spent in transaction {}".format(str(txid)), contract=contract)
        self._transaction = transaction

    @property
    def transaction(self):
        """
        The transaction in which the contract was spent.
        """
        return self._transaction

class AtomicSwapContractNotFound(Exception):
    """
    AtomicSwapContractNotFound error, caused when
    a callee tried to get an atomic swap contract that could not be found.
    """
    def __init__(self, outputid):
        super().__init__("atomic swap contract {} could not be found".format(str(outputid)))
        self._outputid = outputid

    @property
    def outputid(self):
        """
        The outputid that was used to look up the contract that could not be found.
        """
        return self._outputid
