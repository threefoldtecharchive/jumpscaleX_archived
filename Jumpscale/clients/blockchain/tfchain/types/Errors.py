"""
Public TFChain Errors
"""

from Jumpscale import j


class ErrorTypes:
    """
    All TFChain Error types,
    collected as public properties of one class.
    """

    # Primitive Type Errors

    @property
    def InvalidPublicKeySpecifier(self):
        """
        InvalidPublicKeySpecifier error
        """
        return InvalidPublicKeySpecifier

    @property
    def CurrencyPrecisionOverflow(self):
        """
        CurrencyPrecisionOverflow error, caused when the currency value is too precise.

        The `value` property exposes the value that caused the overflow,
        and the `precision` property exposes the precision of that value.
        """
        return CurrencyPrecisionOverflow

    @property
    def CurrencyNegativeValue(self):
        """
        CurrencyNegativeValue error, caused when the value is negative.

        THe `value` property exposes the negative value that caused this error.
        """
        return CurrencyNegativeValue

    # Explorer Errors

    @property
    def ExplorerNoContent(self):
        """
        ExplorerNoContent error, returned when the explorer found
        no content for the given GET Request.

        The `endpoint` property exposes the full endpoint that was involved.
        """
        return ExplorerNoContent

    @property
    def ExplorerServerError(self):
        """
        ExplorerServerError error, returned when the explorer returned an Error,
        for example when an internal error occured or the given query was invalid.

        The `endpoint` property exposes the full endpoint that was involved.
        """
        return ExplorerServerError

    @property
    def ExplorerServerPostError(self):
        """
        ExplorerServerPostError error, returned when the explorer returned an Error,
        for example when a posted transaction was not accepted for some reason.

        The `endpoint` property exposes the full endpoint that was involved.
        And the `data` property exposes the JSON-encoded data that was posted.
        """
        return ExplorerServerPostError

    @property
    def ExplorerNotAvailable(self):
        """
        ExplorerServerPostError error,
        returned when none of the known explorers were available for the desired request.

        The `endpoint` property exposes the full endpoint that was involved.
        And the `addresses` property exposes all (explorer) addresses that were tried to reach.
        """
        return ExplorerNotAvailable

    @property
    def ExplorerInvalidResponse(self):
        """
        ExplorerInvalidResponse error, returned in case the response given by
        the Explorer for a GET/POST request is not as expected.

        The `endpoint` property exposes the full endpoint that was involved.
        And the `response` property exposes the dict (JSON-dececoded) response that was invalid (unexpexted).

        Please report an issue at https://github.com/threefoldfoundation/tfchain/issues
        with all details should this happen. Also include in the issue the values of the properties
        of this response.
        """
        return ExplorerInvalidResponse

    # wallet errors

    @property
    def AddressNotInWallet(self):
        """
        AddressNotInWallet error, triggered
        when trying to use an address on a wallet that does not own it.

        The `address` property exposes the address that was attempted to be used.
        """
        return AddressNotInWallet

    # Generic Transaction Errors

    @property
    def UnknownTransansactionVersion(self):
        """
        UnknownTransansactionVersion error
        """
        return UnknownTransansactionVersion

    @property
    def InsufficientFunds(self):
        """
        InsufficientFunds error
        """
        return InsufficientFunds

    @property
    def DoubleSignError(self):
        """
        DoubleSignError error, in case an input or extension is signed twice.

        Unless you do something weird and manual,
        this most likely indicates a bug that should be reported at
        https://github.com/threefoldfoundation/tfchain/issues
        """
        return DoubleSignError

    # Atomic Swap (Transaction) Errors

    @property
    def AtomicSwapInsufficientAmountError(self):
        """
        AtomicSwapInsufficientAmountError error,
        triggered when creating a contract with an amount equal or lower than
        minimum fee, which isn't allowed as such a contract cannot be redeemed/refunded.

        The `amount` property exposes the amount that was tried,
        and the `minimum_miner_fee` exposes the minimum miner fee used and required by the network.
        """
        return AtomicSwapInsufficientAmountError

    @property
    def AtomicSwapForbidden(self):
        """
        AtomicSwapForbidden error, caused when a contract was trying
        to be spent by an unautohorized wallet.

        The `contract` property exposes the contract that was involved in this error.
        """
        return AtomicSwapForbidden

    @property
    def AtomicSwapInvalidSecret(self):
        """
        AtomicSwapInvalidSecret error, caused when a wrong secret was used
        as an attempt to redeem an atomic swap contract. 

        The `contract` property exposes the contract that was involved in this error.
        """
        return AtomicSwapInvalidSecret

    @property
    def AtomicSwapContractInvalid(self):
        """
        AtomicSwapContractInvalid error, caused when a contract was deemed
        invalid during verification.

        The `contract` property exposes the contract that was involved in this error.
        """
        return AtomicSwapContractInvalid

    @property
    def AtomicSwapContractSpent(self):
        """
        AtomicSwapContractSpent error, caused when
        a callee tried to spend a contract that was already spent.

        The `contract` property exposes the contract that was involved in this error.
        And the `transaction` property exposes the transaction in which the contract was already spent.
        """
        return AtomicSwapContractSpent

    @property
    def AtomicSwapContractNotFound(self):
        """
        AtomicSwapContractNotFound error, caused when
        a callee tried to get an atomic swap contract that could not be found.

        The `outputid` property exposes the identifier that was used
        to try to find the atomic swap contract.
        """
        return AtomicSwapContractNotFound

    # 3Bot (Transaction) Errors

    @property
    def ThreeBotNotFound(self):
        """
        ThreeBotNotFound error, triggered when a 3Bot was not found.

        The `identifier` property exposes the identifier that was used
        to try to find the 3Bot.
        """
        return ThreeBotNotFound

    @property
    def ThreeBotInactive(self):
        """
        ThreeBotInactive error, triggered when a 3Bot is an active,
        and the operation to be applied to the 3Bot would not change that fact.

        The `identifier` property exposes the identifier of the inactive 3Bot
        and the `expiration` property exposes the timestamp (int, Epoch UNIX seconds)
        since when the 3Bot is inactive.
        """
        return ThreeBotInactive

    # ERC20 (Transaction) Errors

    @property
    def ERC20RegistrationForbidden(self):
        """
        ERC20RegistrationForbidden error, triggered
        when trying to register an ERC20 address not owned by the used wallet.

        The `address` property exposes the address that was attempted to be registered.
        """
        return ERC20RegistrationForbidden


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
        super().__init__(
            "value {} is too precise to be a value, can have only 9 numbers after the decimal point".format(str(value))
        )
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
            raise j.exceptions.Value("invalid endpoint, expected it to be of type str not {}".format(type(endpoint)))
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
            raise j.exceptions.Value("invalid addresses, expected it to be of type list not {}".format(type(addresses)))
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
            raise j.exceptions.Value("invalid response, expected it to be of type dict not {}".format(type(response)))
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
                str(minimum_miner_fee), str(amount)
            )
        )
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
        super().__init__(
            message="defined secret does not match the atomic swap's contract secret hash", contract=contract
        )


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
        txid = getattr(transaction, "id", "")
        super().__init__(
            message="atomic swap contract has already been spent in transaction {}".format(str(txid)), contract=contract
        )
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


class ThreeBotNotFound(Exception):
    """
    ThreeBotNotFound error, triggered when a 3Bot was not found.
    """

    def __init__(self, identifier):
        super().__init__("3Bot {} could not be found".format(identifier))
        self._identifier = identifier

    @property
    def identifier(self):
        """
        The (unique) identifier of the 3Bot that could not be found.
        """
        return self._identifier


class ThreeBotInactive(Exception):
    """
    ThreeBotInactive error, triggered when a 3Bot is an active,
    and the operation to be applied to the 3Bot would not change that fact.
    """

    def __init__(self, identifier, expiration):
        super().__init__(
            "3Bot {} is inactive since {}".format(str(identifier), j.data.time.epoch2HRDateTime(expiration))
        )
        self._identifier = identifier
        self._expiration = expiration

    @property
    def identifier(self):
        """
        The (unique) identifier of the 3Bot that could not be found.
        """
        return self._identifier

    @property
    def expiration(self):
        """
        The timestamp on which the 3Bot became inactive.
        """
        return self._expiration


class AddressNotInWallet(Exception):
    """
    AddressNotInWallet error, triggered
    when trying to use an address on a wallet that does not own it
    """

    def __init__(self, address):
        super().__init__("address {} is not owned by the used wallet".format(str(address)))
        self._address = address

    @property
    def address(self):
        """
        The address attempted to be used.
        """
        return self._address


class ERC20RegistrationForbidden(Exception):
    """
    ERC20RegistrationForbidden error, triggered
    when trying to register an ERC20 address not owned by the used wallet.
    """

    def __init__(self, address):
        super().__init__("address {} is not owned by the used wallet".format(str(address)))
        self._address = address

    @property
    def address(self):
        """
        The address attempted to be registered.
        """
        return self._address
