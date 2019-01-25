from Jumpscale import j

_LEGACY_TRANSACTION_V0 = 0
_TRANSACTION_V1 = 1
_TRANSACTION_V128_MINTER_DEFINITION = 128
_TRANSACTION_V129_COIN_CREATION = 129

from .types.errors import UnknownTransansactionVersion

class TFChainTransactionFactory(j.application.JSBaseClass):
    """
    TFChain Transaction Factory class
    """

    def new(self):
        """
        Creates and return a default transaction.
        """
        return TransactionV1()

    def from_json(self, obj, id=None):
        """
        Create a TFChain transaction from a JSON string or dictionary.

        @param obj: JSON-encoded str, bytes, bytearray or JSON-decoded dict that contains a raw JSON Tx.
        """
        if isinstance(obj, (str, bytes, bytearray)):
            obj = j.data.serializers.json.loads(obj)
        if not isinstance(obj, dict):
            raise TypeError("only a dictionary or JSON-encoded dictionary is supported as input: type {} is not supported", type(obj))
        tt = obj.get('version', -1)
        
        txn = None
        if tt == _TRANSACTION_V1:
            txn = TransactionV1.from_json(obj)
        elif tt == _TRANSACTION_V128_MINTER_DEFINITION:
            txn = TransactionV128.from_json(obj)
        elif tt == _TRANSACTION_V129_COIN_CREATION:
            txn = TransactionV129.from_json(obj)
        elif tt == _LEGACY_TRANSACTION_V0:
            txn = TransactionV1.legacy_from_json(obj)

        if isinstance(txn, TransactionBaseClass):
            txn.id = id
            return txn

        raise UnknownTransansactionVersion("transaction version {} is unknown".format(tt))


    def test(self):
        """
        js_shell 'j.clients.tfchain.transactions.test()'
        """
        # v1 Transactions are supported
        v1_txn_json = {"version":1,"data":{"coininputs":[{"parentid":"abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd","fulfillment":{"type":1,"data":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}}},{"parentid":"012345defabc012345defabc012345defabc012345defabc012345defabc0123","fulfillment":{"type":2,"data":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab","secret":"def789def789def789def789def789dedef789def789def789def789def789de"}}},{"parentid":"045645defabc012345defabc012345defabc012345defabc012345defabc0123","fulfillment":{"type":2,"data":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab","secret":"def789def789def789def789def789dedef789def789def789def789def789de"}}}],"coinoutputs":[{"value":"3","condition":{"type":1,"data":{"unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"}}},{"value":"5","condition":{"type":1,"data":{"unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}}},{"value":"13","condition":{"type":2,"data":{"sender":"01654f96b317efe5fd6cd8ba1a394dce7b6ebe8c9621d6c44cbe3c8f1b58ce632a3216de71b23b","receiver":"01e89843e4b8231a01ba18b254d530110364432aafab8206bea72e5a20eaa55f70b1ccc65e2105","hashedsecret":"abc543defabc543defabc543defabc543defabc543defabc543defabc543defa","timelock":1522068743}}}],"minerfees":["1","2","3"],"arbitrarydata":"ZGF0YQ=="}}
        v1_txn = self.from_json(v1_txn_json)
        assert v1_txn.json() == v1_txn_json
        assert v1_txn.signature_hash_get(0).hex() == '4175b7bc6c376493949df657ae7966b6bf01efabacdfc51da01fd8624a55b17b'

        # v0 Transactions are supported
        v0_txn_json = {"version":0,"data":{"coininputs":[{"parentid":"abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd","unlocker":{"type":1,"condition":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"},"fulfillment":{"signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}}}],"coinoutputs":[{"value":"3","unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"},{"value":"5","unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}],"minerfees":["1","2","3"],"arbitrarydata":"ZGF0YQ=="}}
        v0_txn = self.from_json(v0_txn_json)
        expected_v0_txn_json_as_v1 = {"version":1,"data":{"coininputs":[{"parentid":"abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd","fulfillment":{"type":1,"data":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}}}],"coinoutputs":[{"value":"3","condition":{"type":1,"data":{"unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"}}},{"value":"5","condition":{"type":1,"data":{"unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}}}],"minerfees":["1","2","3"],"arbitrarydata":"ZGF0YQ=="}}
        assert v0_txn.json() == expected_v0_txn_json_as_v1
        assert v0_txn.signature_hash_get(0).hex() == 'e913e88d7c698ccc27ba130cf702cdb153e3088f403f8448cd16d121661942e5'

        # Coin Creation Transactions

        # v128 Transactions are supported
        v128_txn_json = {"version":128,"data":{"nonce":"FoAiO8vN2eU=","mintfulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"bdf023fbe7e0efec584d254b111655e1c2f81b9488943c3a712b91d9ad3a140cb0949a8868c5f72e08ccded337b79479114bdb4ed05f94dfddb359e1a6124602"}},"mintcondition":{"type":1,"data":{"unlockhash":"01e78fd5af261e49643dba489b29566db53fa6e195fa0e6aad4430d4f06ce88b73e047fe6a0703"}},"minerfees":["1000000000"],"arbitrarydata":"YSBtaW50ZXIgZGVmaW5pdGlvbiB0ZXN0"}}
        v128_txn = self.from_json(v128_txn_json)
        assert v128_txn.json() == v128_txn_json
        assert v128_txn.signature_hash_get(0).hex() == 'c0b865dd6980f377c9bc6fb195bca3cf169ea06e6bc658b29639bdb6fc387f8d'

        # v129 Transactions are supported
        v129_txn_json = {"version":129,"data":{"nonce":"1oQFzIwsLs8=","mintfulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"ad59389329ed01c5ee14ce25ae38634c2b3ef694a2bdfa714f73b175f979ba6613025f9123d68c0f11e8f0a7114833c0aab4c8596d4c31671ec8a73923f02305"}},"coinoutputs":[{"value":"500000000000000","condition":{"type":1,"data":{"unlockhash":"01e3cbc41bd3cdfec9e01a6be46a35099ba0e1e1b793904fce6aa5a444496c6d815f5e3e981ccf"}}}],"minerfees":["1000000000"],"arbitrarydata":"dGVzdC4uLiAxLCAyLi4uIDM="}}
        v129_txn = self.from_json(v129_txn_json)
        assert v129_txn.json() == v129_txn_json
        assert v129_txn.signature_hash_get(0).hex() == '984ccc3da2107e86f67ef618886f9144040d84d9f65f617c64fa34de68c0018b'

        # 3Bot Transactions

        # v144 Transactions are supported
        # TODO

        # v145 Transactions are supported
        # TODO

        # v146 Transactions are supported
        # TODO


from abc import ABC, abstractmethod, abstractclassmethod

class TransactionBaseClass(ABC, j.application.JSBaseClass):
    def __init__(self):
        self._id = None

    @classmethod
    def from_json(cls, obj):
        """
        Create this transaction from a raw JSON Tx
        """
        txn = cls()
        assert txn.version == obj.get('version', -1)
        txn._from_json_data_object(obj.get('data', {}))
        return txn

    @property
    @abstractmethod
    def version(self):
        """
        Version of this Transaction.
        """
        pass
    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        if type(id) is type(self._id):
            self._id = id
        else:
            self._id = j.clients.tfchain.types.hash_new(value=id)

    @property
    def coin_inputs(self):
        """
        Coin inputs of this Transaction,
        used as funding for coin outputs, fees and any other kind of coin output.
        """
        return []

    @property
    def coin_outputs(self):
        """
        Coin outputs of this Transaction,
        funded by the Transaction's coin inputs.
        """
        return []

    @property
    def miner_fees(self):
        """
        Miner fees, paid to the block creator of this Transaction,
        funded by this Transaction's coin inputs.
        """
        return []
    
    @property
    def data(self):
        """
        Optional binary data attached to this Transaction,
        with a max length of 83 bytes.
        """
        return bytearray()
    
    @abstractmethod
    def _signature_hash_input_get(self, *extra_objects):
        """
        signature_hash_get is used to get the input
        """
        pass

    def signature_hash_get(self, *extra_objects):
        """
        signature_hash_get is used to get the signature hash for this Transaction,
        which are used to proof the authenticity of the transaction.
        """
        input = self._signature_hash_input_get(*extra_objects)
        return bytearray.fromhex(j.data.hash.blake2_string(input))

    @abstractmethod
    def _from_json_data_object(self, data):
        pass

    @abstractmethod
    def _json_data_object(self):
        pass
    
    def json(self):
        obj = {'version': self.version}
        data = self._json_data_object()
        if data:
            obj['data'] = data
        return obj

    # TODO: check if we need a better string representation or if this is fine
    def __str__(self):
        return j.data.serializers.json.dumps(self.json())
    __repr__ = __str__


from .types.CompositionTypes import CoinInput, CoinOutput
from .types.PrimitiveTypes import Currency, RawData


class TransactionV1(TransactionBaseClass):
    def __init__(self):
        self._coin_inputs = []
        self._coin_outputs = []
        self._miner_fees = []
        self._data = RawData()

        # hidden flag, that indicates if this Txn was a Legacy v0 Txn or not,
        # False by default as we do not wish to produce new legacy Txns, only decode existing ones
        self._legacy = False

        super().__init__()
    
    @classmethod
    def legacy_from_json(cls, obj):
        """
        Class method to decode v1 Tx from a legacy v0 Tx.
        """

        assert _LEGACY_TRANSACTION_V0 == obj.get('version', -1)
        txn = cls()

        if 'data' not in obj:
            raise ValueError("no data object found in Legacy Transaction (v{})".format(_LEGACY_TRANSACTION_V0))
        txn_data = obj['data']
        if 'coininputs' in txn_data:
            for legacy_ci_info in (txn_data['coininputs'] or []):
                unlocker = legacy_ci_info.get('unlocker', {})
                ci_info = {
                    'parentid': legacy_ci_info.get('parentid', ''),
                    'fulfillment': {
                        'type': 1,
                        'data': {
                            'publickey': unlocker.get('condition', {}).get('publickey'),
                            'signature': unlocker.get('fulfillment', {}).get('signature'),
                        }
                    }
                }
                ci = CoinInput.from_json(ci_info)
                txn._coin_inputs.append(ci)
        if 'coinoutputs' in txn_data:
            for legacy_co_info in (txn_data['coinoutputs'] or []):
                co_info = {
                    'value': legacy_co_info.get('value', '0'),
                    'condition': {
                        'type': 1,
                        'data': {
                            'unlockhash': legacy_co_info.get('unlockhash', ''),
                        }
                    }
                }
                co = CoinOutput.from_json(co_info)
                txn._coin_outputs.append(co)

        if 'minerfees' in txn_data:
            for minerfee in (txn_data['minerfees'] or []) :
                txn._miner_fees.append(Currency.from_json(minerfee))
        if 'arbitrarydata' in txn_data:
            txn._data = RawData.from_json(txn_data.get('arbitrarydata', None) or '')

        txn._legacy = True
        return txn


    @property
    def version(self):
        return _TRANSACTION_V1
    
    @property
    def coin_inputs(self):
        """
        Coin inputs of this Transaction,
        used as funding for coin outputs, fees and any other kind of coin output.
        """
        return self._coin_inputs

    def coin_input_add(self, parent_id, fulfillment):
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))

    def coin_output_add(self, value, condition):
        self._coin_outputs.append(CoinOutput(value=value, condition=condition))


    @property
    def coin_outputs(self):
        """
        Coin outputs of this Transaction,
        funded by the Transaction's coin inputs.
        """
        return self._coin_outputs

    @property
    def miner_fees(self):
        """
        Miner fees, paid to the block creator of this Transaction,
        funded by this Transaction's coin inputs.
        """
        return self._miner_fees
    
    @property
    def data(self):
        """
        Optional binary data attached to this Transaction,
        with a max length of 83 bytes.
        """
        return self._data
    @data.setter
    def data(self, value):
        if not value:
            self._data = RawData()
            return
        if isinstance(value, RawData):
            value = value.value
        self._data.value = value
    
    def _signature_hash_input_get(self, *extra_objects):
        if self._legacy:
            return self._legacy_signature_hash_input_get(*extra_objects)

        e = j.data.rivine.encoder_sia_get()

        # encode the transaction version
        e.add_byte(self.version)

        # encode extra objects if exists
        if extra_objects:
            e.add_all(*extra_objects)

        # encode the number of coins inputs
        e.add(len(self.coin_inputs))
        # encode coin inputs parent_ids
        for ci in self.coin_inputs:
            e.add(ci.parent_id)

        # encode coin outputs
        e.add_slice(self.coin_outputs)

        # encode the number of blockstakes (input/output)
        # NOTE: this is hardcoded at 0, as our client does not support block stakes for now,
        #       should we ever need block stakes we can easily enough support those
        e.add_all(0, 0)

        # encode miner fees
        e.add_slice(self.miner_fees)

        # encode custom data
        e.add(self.data)

        # return the encoded data
        return e.data
    
    def _legacy_signature_hash_input_get(self, *extra_objects):
        e = j.data.rivine.encoder_sia_get()

        # encode extra objects if exists
        if extra_objects:
            e.add_all(*extra_objects)

        # encode coin inputs
        for ci in self.coin_inputs:
            e.add_all(ci.parent_id, ci.fulfillment.public_key.unlock_hash())

        # encode coin outputs
        e.add(len(self.coin_outputs))
        for co in self.coin_outputs:
            e.add_all(co.value, co.condition.unlockhash)

        # encode the number of blockstakes outputs (number of inputs is not encoded in legacy format)
        # NOTE: this is hardcoded at 0, as our client does not support block stakes for now,
        #       should we ever need block stakes we can easily enough support those
        e.add(0)

        # encode miner fees
        e.add_slice(self.miner_fees)

        # encode custom data
        e.add(self.data)

        # return the encoded data
        return e.data
        

    def _from_json_data_object(self, data):
        self._coin_inputs = [CoinInput.from_json(ci) for ci in data.get('coininputs', []) or []]
        self._coin_outputs = [CoinOutput.from_json(co) for co in data.get('coinoutputs', []) or []]
        self._miner_fees = [Currency.from_json(fee) for fee in data.get('minerfees', []) or []]
        self._data = RawData.from_json(data.get('arbitrarydata', None) or '')

    def _json_data_object(self):
        return {
            'coininputs': [ci.json() for ci in self._coin_inputs],
            'coinoutputs': [co.json() for co in self._coin_outputs],
            'minerfees': [fee.json() for fee in self._miner_fees],
            'arbitrarydata': self._data.json(),
        }


from .types.FulfillmentTypes import FulfillmentBaseClass, FulfillmentSingleSignature 
from .types.ConditionTypes import ConditionBaseClass, ConditionNil 

from .types.PrimitiveTypes import BinaryData

class TransactionV128(TransactionBaseClass):
    def __init__(self):
        self._mint_fulfillment = FulfillmentSingleSignature()
        self._mint_condition = ConditionNil()
        self._miner_fees = []
        self._data = RawData()
        self._nonce = RawData(j.data.idgenerator.generateXByteID(8))

        super().__init__()


    @property
    def version(self):
        return _TRANSACTION_V128_MINTER_DEFINITION
    
    @property
    def miner_fees(self):
        """
        Miner fees, paid to the block creator of this Transaction,
        funded by this Transaction's coin inputs.
        """
        return self._miner_fees
    
    @property
    def data(self):
        """
        Optional binary data attached to this Transaction,
        with a max length of 83 bytes.
        """
        return self._data
    @data.setter
    def data(self, value):
        if not value:
            self._data = RawData()
            return
        if isinstance(value, RawData):
            value = value.value
        self._data.value = value

    @property
    def mint_condition(self):
        """
        Retrieve the new mint condition which will be set
        """
        return self._mint_condition
    @mint_condition.setter
    def mint_condition(self, value):
        if not value:
            self._mint_condition = ConditionNil()
            return
        assert isinstance(value, ConditionBaseClass)
        self._mint_condition = value

    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        return self._mint_fulfillment
    @mint_fulfillment.setter
    def mint_fulfillment(self, value):
        if not value:
            self._mint_fulfillment = FulfillmentSingleSignature()
            return
        assert isinstance(value, FulfillmentBaseClass)
        self._mint_fulfillment = value

    def _signature_hash_input_get(self, *extra_objects):
        e = j.data.rivine.encoder_sia_get()

        # encode the transaction version
        e.add_byte(self.version)

        # encode the specifier
        e.add_array(b'minter defin tx\0')

        # encode nonce
        e.add_array(self._nonce.value)

        # extra objects if any
        if extra_objects:
            e.add_all(*extra_objects)

        # encode new mint condition
        e.add(self.mint_condition)

        # encode miner fees
        e.add_slice(self.miner_fees)

        # encode custom data
        e.add(self.data)

        # return the encoded data
        return e.data

    def _from_json_data_object(self, data):
        self._nonce = RawData.from_json(data.get('nonce', ''))
        self._mint_condition = j.clients.tfchain.types.conditions.from_json(data.get('mintcondition', {}))
        self._mint_fulfillment = j.clients.tfchain.types.fulfillments.from_json(data.get('mintfulfillment', {}))
        self._miner_fees = [Currency.from_json(fee) for fee in data.get('minerfees', []) or []]
        self._data = RawData.from_json(data.get('arbitrarydata', None) or '')

    def _json_data_object(self):
        return {
            'nonce': self._nonce.json(),
            'mintfulfillment': self._mint_fulfillment.json(),
            'mintcondition': self._mint_condition.json(),
            'minerfees': [fee.json() for fee in self._miner_fees],
            'arbitrarydata': self._data.json(),
        }

class TransactionV129(TransactionBaseClass):
    def __init__(self):
        self._mint_fulfillment = FulfillmentSingleSignature()
        self._coin_outputs = []
        self._miner_fees = []
        self._data = RawData()
        self._nonce = RawData(j.data.idgenerator.generateXByteID(8))

        super().__init__()


    @property
    def version(self):
        return _TRANSACTION_V129_COIN_CREATION
    
    @property
    def miner_fees(self):
        """
        Miner fees, paid to the block creator of this Transaction,
        funded by this Transaction's coin inputs.
        """
        return self._miner_fees
    
    @property
    def data(self):
        """
        Optional binary data attached to this Transaction,
        with a max length of 83 bytes.
        """
        return self._data
    @data.setter
    def data(self, value):
        if not value:
            self._data = RawData()
            return
        if isinstance(value, RawData):
            value = value.value
        self._data.value = value

    @property
    def coin_outputs(self):
        """
        Coin outputs of this Transaction,
        funded by the Transaction's coin inputs.
        """
        return self._coin_outputs

    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        return self._mint_fulfillment
    @mint_fulfillment.setter
    def mint_fulfillment(self, value):
        if not value:
            self._mint_fulfillment = FulfillmentSingleSignature()
            return
        assert isinstance(value, FulfillmentBaseClass)
        self._mint_fulfillment = value
    
    def coin_output_add(self, value, condition):
        self._coin_outputs.append(CoinOutput(value=value, condition=condition))

    def _signature_hash_input_get(self, *extra_objects):
        e = j.data.rivine.encoder_sia_get()

        # encode the transaction version
        e.add_byte(self.version)

        # encode the specifier
        e.add_array(b'coin mint tx\0\0\0\0')

        # encode nonce
        e.add_array(self._nonce.value)

        # extra objects if any
        if extra_objects:
            e.add_all(*extra_objects)

        # encode coin outputs
        e.add_slice(self.coin_outputs)

        # encode miner fees
        e.add_slice(self.miner_fees)

        # encode custom data
        e.add(self.data)

        # return the encoded data
        return e.data


    def _from_json_data_object(self, data):
        self._nonce = RawData.from_json(data.get('nonce', ''))
        self._mint_fulfillment = j.clients.tfchain.types.fulfillments.from_json(data.get('mintfulfillment', {}))
        self._coin_outputs = [CoinOutput.from_json(co) for co in data.get('coinoutputs', []) or []]
        self._miner_fees = [Currency.from_json(fee) for fee in data.get('minerfees', []) or []]
        self._data = RawData.from_json(data.get('arbitrarydata', None) or '')

    def _json_data_object(self):
        return {
            'nonce': self._nonce.json(),
            'mintfulfillment': self._mint_fulfillment.json(),
            'coinoutputs': [co.json() for co in self._coin_outputs],
            'minerfees': [fee.json() for fee in self._miner_fees],
            'arbitrarydata': self._data.json(),
        }
