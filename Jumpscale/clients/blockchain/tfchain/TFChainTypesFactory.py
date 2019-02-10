from Jumpscale import j

from .types.PrimitiveTypes import BinaryData, Hash, Currency, Blockstake
from .types.FulfillmentTypes import FulfillmentFactory
from .types.ConditionTypes import ConditionFactory
from .types.CryptoTypes import PublicKey, PublicKeySpecifier

from .crypto.MerkleTree import Tree

class TFChainTypesFactory(j.application.JSBaseClass):
    """
    TFChain Types Factory class
    """

    @property
    def fulfillments(self):
        """
        Fulfillment types.
        """
        return FulfillmentFactory()

    @property
    def conditions(self):
        """
        Condition types.
        """
        return ConditionFactory()
    
    def currency_new(self, value=0):
        """
        Create a new currency value.
        
        @param value: str or int that defines the value to be set, 0 by default
        """
        return Currency(value=value)

    def blockstake_new(self, value=0):
        """
        Create a new block stake value.

        @param value: str or int that defines the value to be set, 0 by default
        """
        return Blockstake(value=value)

    def hash_new(self, value=None):
        """
        Create a new hash value.
        
        @param value: bytearray, bytes or str that defines the hash value to be set, nil hash by default
        """
        return Hash(value=value)

    def binary_data_new(self, value=None, fixed_size=None, strencoding=None):
        """
        Create a new binary data value.
        
        @param value: bytearray, bytes or str that defines the hash value to be set, nil hash by default
        """
        return BinaryData(value=value, fixed_size=fixed_size, strencoding=strencoding)

    def public_key_new(self, hash=None):
        """
        Create a new NIL or ED25519 public key.
        
        @param hash: bytearray, bytes or str that defines the hash value to be set, nil hash by default
        """
        if not hash:
            return PublicKey()
        return PublicKey(specifier=PublicKeySpecifier.ED25519, hash=hash)

    def public_key_from_json(self, obj):
        """
        Create a new public key from a json string.
        
        @param obj: str that contains a nil str or a json string
        """
        return PublicKey.from_json(obj)

    def merkle_tree_new(self):
        """
        Create a new MerkleTree
        """
        return Tree(hash_func=lambda o: bytes.fromhex(j.data.hash.blake2_string(o)))

    def test(self):
        """
        js_shell 'j.clients.tfchain.types.test()'
        """
        
        # currency values can be created from both
        # int and str values, but are never allowed to be negative
        assert str(self.currency_new()) == '0'
        assert str(self.currency_new(value=123)) == '123'
        assert str(self.currency_new(value='1')) == '1'
        # in the string versions you can also add the TFT currency notation,
        # or use decimal notation to express the currency in the TFT Currency Unit,
        # rather than the primitive unit
        assert str(self.currency_new(value='1 TFT')) == '1'
        assert str(self.currency_new(value='0.123456789')) == '0.123456789'
        assert str(self.currency_new(value='9.123456789')) == '9.123456789'
        assert str(self.currency_new(value='1234.34')) == '1234.34'
        assert str(self.currency_new(value='1.00000')) == '1'
        assert str(self.currency_new(value='1.0 tft')) == '1'
        assert str(self.currency_new(value=1)) == '1'
        assert str(self.currency_new(value=12344)) == '12344'

        # hash values can be created directly from binary data,
        # or from a hex-encoded string, by default the nil hash will be created
        assert str(self.hash_new()) == '0'*64
        assert self.hash_new(b'12345678901234567890123456789001').value == b'12345678901234567890123456789001'

        # binary data is very similar to a hash,
        # except that it doesn't have a fixed length and it is binary serialized
        # as a slice, not an array
        assert str(self.binary_data_new()) == ''
        assert str(self.binary_data_new(b'1')) == '31'

        # raw data is pretty much binary data, except that it is
        # base64 encoded/decoded for str/json purposes
        assert str(self.binary_data_new(b'data', strencoding='base64')) == 'ZGF0YQ=='

        # block stake values can be created from both
        # int and str values, but are never allowed to be negative
        assert str(self.blockstake_new()) == '0'
        assert str(self.blockstake_new(value=123)) == '123'
        assert str(self.blockstake_new(value='1')) == '1'
