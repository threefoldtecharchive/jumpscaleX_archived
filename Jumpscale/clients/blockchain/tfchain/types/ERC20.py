"""
ERC20 Types.
"""

from Jumpscale import j

from .PrimitiveTypes import BinaryData, Hash


class ERC20Address(BinaryData):
    SIZE = 20

    """
    ERC20 Contract/Wallet Address, used in TFChain-ERC20 code.
    """

    def __init__(self, value=None):
        super().__init__(value, fixed_size=ERC20Address.SIZE, strencoding="hexprefix")

    @staticmethod
    def is_valid_value(value):
        """
        Returns True if the given value is a valid ERC20Address value, False otherwise.
        """
        if isinstance(value, str):
            if value.startswith("0x") or value.startswith("0X"):
                value = value[2:]
            if len(value) != ERC20Address.SIZE * 2:
                return False
            try:
                int(value, 16)
                return True
            except ValueError:
                return False
        elif isinstance(value, (bytes, bytearray)):
            return len(value) == ERC20Address.SIZE
        elif isinstance(value, ERC20Address):
            return ERC20Address.is_valid_value(value.value)
        else:
            return False

    @classmethod
    def from_unlockhash(cls, unlockhash):
        """
        Create an ERC20 Address from a TFT Address (type: UnlockHash).
        """
        e = j.data.rivine.encoder_sia_get()
        unlockhash.sia_binary_encode(e)
        hash = bytes.fromhex(j.data.hash.blake2_string(e.data))
        return cls(value=hash[Hash.SIZE - ERC20Address.SIZE :])

    @classmethod
    def from_json(cls, obj):
        if obj is not None and not isinstance(obj, str):
            raise j.exceptions.Value(
                "ERC20 address is expected to be an encoded string when part of a JSON object, not {}".format(type(obj))
            )
        if obj == "":
            obj = None
        return cls(value=obj)


class ERC20Hash(BinaryData):
    SIZE = 32

    """
    ERC20 Hash, used in TFChain-ERC20 code.
    """

    def __init__(self, value=None):
        super().__init__(value, fixed_size=ERC20Hash.SIZE, strencoding="hexprefix")

    @classmethod
    def from_json(cls, obj):
        if obj is not None and not isinstance(obj, str):
            raise j.exceptions.Value(
                "ERC20 hash is expected to be an encoded string when part of a JSON object, not {}".format(type(obj))
            )
        if obj == "":
            obj = None
        return cls(value=obj)
