from Jumpscale import j

from functools import reduce

from .Errors import UnknownTransansactionVersion

_LEGACY_TRANSACTION_V0 = 0
_TRANSACTION_V1 = 1
_TRANSACTION_V128_MINTER_DEFINITION = 128
_TRANSACTION_V129_COIN_CREATION = 129

class TFChainTransactionFactory(j.application.JSBaseClass):
    """
    TFChain Transaction Factory class
    """

    def new(self):
        """
        Creates and returns a default transaction.
        """
        return TransactionV1()

    def mint_definition_new(self):
        """
        Creates and returns an empty Mint Definition transaction.
        """
        return TransactionV128()

    def mint_coin_creation_new(self):
        """
        Creates and returns an empty Mint CoinCreation transaction.
        """
        return TransactionV129()

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
        v1_txn_json = {"version":1,"data":{"coininputs":[{"parentid":"5b907d6e4d34cdd825484d2f9f14445377fb8b4f8cab356a390a7fe4833a3085","fulfillment":{"type":1,"data":{"publickey":"ed25519:bd5e0e345d5939f5f9eb330084c7f0ffb8fc7fc5bdb07a94c304620eb4e2d99a","signature":"55dace7ccbc9cdd23220a8ef3ec09e84ce5c5acc202c5f270ea0948743ebf52135f3936ef7477170b4f9e0fe141a61d8312ab31afbf926a162982247e5d2720a"}}}],"coinoutputs":[{"value":"1000000000","condition":{"type":1,"data":{"unlockhash":"010009a2b6a482da73204ccc586f6fab5504a1a69c0d316cdf828a476ae7c91c9137fd6f1b62bb"}}},{"value":"8900000000","condition":{"type":1,"data":{"unlockhash":"01b81f9e02d6be3a7de8440365a7c799e07dedf2ccba26fd5476c304e036b87c1ab716558ce816"}}}],"blockstakeinputs":[{"parentid":"782e4819d6e199856ba1bff3def5d7cc37ae2a0dabecb05359d6072156190d68","fulfillment":{"type":1,"data":{"publickey":"ed25519:95990ca3774de81309932302f74dfe9e540d6c29ca5cb9ee06e999ad46586737","signature":"70be2115b82a54170c94bf4788e2a6dd154a081f61e97999c2d9fcc64c41e7df2e8a8d4f82a57a04a1247b9badcb6bffbd238e9a6761dd59e5fef7ff6df0fc01"}}}],"blockstakeoutputs":[{"value":"99","condition":{"type":1,"data":{"unlockhash":"01fdf10836c119186f1d21666ae2f7dc62d6ecc46b5f41449c3ee68aea62337dad917808e46799"}}}],"minerfees":["100000000"],"arbitrarydata":"ZGF0YQ=="}}
        v1_txn = self.from_json(v1_txn_json)
        assert v1_txn.json() == v1_txn_json
        assert v1_txn.signature_hash_get(0).hex() == '8a4f0c8e4c01940f0dcc14cc8d96487fcdc1a07e6abf000a156c11fc6fd3a8d2'
        assert v1_txn.binary_encode().hex() == '01320200000000000001000000000000005b907d6e4d34cdd825484d2f9f14445377fb8b4f8cab356a390a7fe4833a3085018000000000000000656432353531390000000000000000002000000000000000bd5e0e345d5939f5f9eb330084c7f0ffb8fc7fc5bdb07a94c304620eb4e2d99a400000000000000055dace7ccbc9cdd23220a8ef3ec09e84ce5c5acc202c5f270ea0948743ebf52135f3936ef7477170b4f9e0fe141a61d8312ab31afbf926a162982247e5d2720a020000000000000004000000000000003b9aca00012100000000000000010009a2b6a482da73204ccc586f6fab5504a1a69c0d316cdf828a476ae7c91c91050000000000000002127b390001210000000000000001b81f9e02d6be3a7de8440365a7c799e07dedf2ccba26fd5476c304e036b87c1a0100000000000000782e4819d6e199856ba1bff3def5d7cc37ae2a0dabecb05359d6072156190d6801800000000000000065643235353139000000000000000000200000000000000095990ca3774de81309932302f74dfe9e540d6c29ca5cb9ee06e999ad46586737400000000000000070be2115b82a54170c94bf4788e2a6dd154a081f61e97999c2d9fcc64c41e7df2e8a8d4f82a57a04a1247b9badcb6bffbd238e9a6761dd59e5fef7ff6df0fc01010000000000000001000000000000006301210000000000000001fdf10836c119186f1d21666ae2f7dc62d6ecc46b5f41449c3ee68aea62337dad0100000000000000040000000000000005f5e100040000000000000064617461'
        assert str(v1_txn.coin_outputid_new(0)) == '865594096bbaa36753b9ee8ca404d75bbe9563855c684e8bba827ce5eef246c4'
        assert str(v1_txn.blockstake_outputid_new(0)) == 'd471d525ce9a063e1c15998a1ab877e9682e0c822eccaf1dbd61b95d592e4a29'

        # v1 transactions do not have block stakes when used just for coins
        v1_txn_json = {"version":1,"data":{"coininputs":[{"parentid":"5b907d6e4d34cdd825484d2f9f14445377fb8b4f8cab356a390a7fe4833a3085","fulfillment":{"type":1,"data":{"publickey":"ed25519:bd5e0e345d5939f5f9eb330084c7f0ffb8fc7fc5bdb07a94c304620eb4e2d99a","signature":"55dace7ccbc9cdd23220a8ef3ec09e84ce5c5acc202c5f270ea0948743ebf52135f3936ef7477170b4f9e0fe141a61d8312ab31afbf926a162982247e5d2720a"}}}],"coinoutputs":[{"value":"1000000000","condition":{"type":1,"data":{"unlockhash":"010009a2b6a482da73204ccc586f6fab5504a1a69c0d316cdf828a476ae7c91c9137fd6f1b62bb"}}},{"value":"8900000000","condition":{"type":1,"data":{"unlockhash":"01b81f9e02d6be3a7de8440365a7c799e07dedf2ccba26fd5476c304e036b87c1ab716558ce816"}}}],"minerfees":["100000000"],"arbitrarydata":"ZGF0YQ=="}}
        v1_txn = self.from_json(v1_txn_json)
        assert v1_txn.json() == v1_txn_json
        assert v1_txn.signature_hash_get(0).hex() == 'ff0daecf468e009bebb87fd1eb8e9bf00573e5f20c97572d080a1b0e5b09939b'
        assert v1_txn.binary_encode().hex() == '01560100000000000001000000000000005b907d6e4d34cdd825484d2f9f14445377fb8b4f8cab356a390a7fe4833a3085018000000000000000656432353531390000000000000000002000000000000000bd5e0e345d5939f5f9eb330084c7f0ffb8fc7fc5bdb07a94c304620eb4e2d99a400000000000000055dace7ccbc9cdd23220a8ef3ec09e84ce5c5acc202c5f270ea0948743ebf52135f3936ef7477170b4f9e0fe141a61d8312ab31afbf926a162982247e5d2720a020000000000000004000000000000003b9aca00012100000000000000010009a2b6a482da73204ccc586f6fab5504a1a69c0d316cdf828a476ae7c91c91050000000000000002127b390001210000000000000001b81f9e02d6be3a7de8440365a7c799e07dedf2ccba26fd5476c304e036b87c1a000000000000000000000000000000000100000000000000040000000000000005f5e100040000000000000064617461'
        assert str(v1_txn.coin_outputid_new(0)) == 'c60952beb5d6213f29e4af96bceed28197d00b9dcaebbd185a498ad407b489c3'

        # v0 Transactions are supported, but are not recommend or created by this client
        v0_txn_json = {"version":0,"data":{"coininputs":[{"parentid":"abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd","unlocker":{"type":1,"condition":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"},"fulfillment":{"signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}}}],"coinoutputs":[{"value":"3","unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"},{"value":"5","unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}],"blockstakeinputs":[{"parentid":"dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfde","unlocker":{"type":1,"condition":{"publickey":"ed25519:ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef12"},"fulfillment":{"signature":"01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def"}}}],"blockstakeoutputs":[{"value":"4","unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"},{"value":"2","unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}],"minerfees":["1","2","3"],"arbitrarydata":"ZGF0YQ=="}}
        v0_txn = self.from_json(v0_txn_json)
        expected_v0_txn_json_as_v1 = {"version":1,"data":{"coininputs":[{"parentid":"abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd","fulfillment":{"type":1,"data":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}}}],"coinoutputs":[{"value":"3","condition":{"type":1,"data":{"unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"}}},{"value":"5","condition":{"type":1,"data":{"unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}}}],"blockstakeinputs":[{"parentid":"dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfde","fulfillment":{"type":1,"data":{"publickey":"ed25519:ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef12","signature":"01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def"}}}],"blockstakeoutputs":[{"value":"4","condition":{"type":1,"data":{"unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"}}},{"value":"2","condition":{"type":1,"data":{"unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}}}],"minerfees":["1","2","3"],"arbitrarydata":"ZGF0YQ=="}}
        assert v0_txn.json() == expected_v0_txn_json_as_v1
        assert v0_txn.signature_hash_get(0).hex() == 'a9115e430d3d0bbec178091abc5db00a146fe0a4e18c9c10f3f4f4e9e415be4d'
        assert v0_txn.binary_encode().hex() == '000100000000000000abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd013800000000000000656432353531390000000000000000002000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff4000000000000000abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab02000000000000000100000000000000030142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce001000000000000000501a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc350100000000000000dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfd23dfde013800000000000000656432353531390000000000000000002000000000000000ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef1234ef12400000000000000001234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def01234def02000000000000000100000000000000040142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce001000000000000000201a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc350300000000000000010000000000000001010000000000000002010000000000000003040000000000000064617461'
        assert str(v0_txn.coin_outputid_new(0)) == 'c527714a30000defabad230e81109ec1826aca3868092cc49164f31f0c7baf12'
        assert str(v0_txn.blockstake_outputid_new(0)) == 'b4c7dbb77034cfd91c3ec9bbc9b38c8ff4f31d72aee93118496a66e910e54358'

        # v0 Transactions do not have block stakes when used just for coins
        v0_txn_json = {"version":0,"data":{"coininputs":[{"parentid":"abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd","unlocker":{"type":1,"condition":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"},"fulfillment":{"signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}}}],"coinoutputs":[{"value":"3","unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"},{"value":"5","unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}],"minerfees":["1","2","3"],"arbitrarydata":"ZGF0YQ=="}}
        v0_txn = self.from_json(v0_txn_json)
        expected_v0_txn_json_as_v1 = {"version":1,"data":{"coininputs":[{"parentid":"abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd","fulfillment":{"type":1,"data":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}}}],"coinoutputs":[{"value":"3","condition":{"type":1,"data":{"unlockhash":"0142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce0df815fd7570e"}}},{"value":"5","condition":{"type":1,"data":{"unlockhash":"01a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc353bdcf54be7d8"}}}],"minerfees":["1","2","3"],"arbitrarydata":"ZGF0YQ=="}}
        assert v0_txn.json() == expected_v0_txn_json_as_v1
        assert v0_txn.signature_hash_get(0).hex() == 'e913e88d7c698ccc27ba130cf702cdb153e3088f403f8448cd16d121661942e5'
        assert v0_txn.binary_encode().hex() == '000100000000000000abcdef012345abcdef012345abcdef012345abcdef012345abcdef012345abcd013800000000000000656432353531390000000000000000002000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff4000000000000000abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab02000000000000000100000000000000030142e9458e348598111b0bc19bda18e45835605db9f4620616d752220ae8605ce001000000000000000501a6a6c5584b2bfbd08738996cd7930831f958b9a5ed1595525236e861c1a0dc35000000000000000000000000000000000300000000000000010000000000000001010000000000000002010000000000000003040000000000000064617461'
        assert str(v0_txn.coin_outputid_new(0)) == 'bf7706e06fcbace4d2c2b69015619094009aa2bf722e7db3cb3187e499f0f951'

        # Coin Creation Transactions

        # v128 Transactions are supported
        v128_txn_json = {"version":128,"data":{"nonce":"FoAiO8vN2eU=","mintfulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"bdf023fbe7e0efec584d254b111655e1c2f81b9488943c3a712b91d9ad3a140cb0949a8868c5f72e08ccded337b79479114bdb4ed05f94dfddb359e1a6124602"}},"mintcondition":{"type":1,"data":{"unlockhash":"01e78fd5af261e49643dba489b29566db53fa6e195fa0e6aad4430d4f06ce88b73e047fe6a0703"}},"minerfees":["1000000000"],"arbitrarydata":"YSBtaW50ZXIgZGVmaW5pdGlvbiB0ZXN0"}}
        v128_txn = self.from_json(v128_txn_json)
        assert v128_txn.json() == v128_txn_json
        assert v128_txn.signature_hash_get(0).hex() == 'c0b865dd6980f377c9bc6fb195bca3cf169ea06e6bc658b29639bdb6fc387f8d'
        assert v128_txn.binary_encode().hex() == '801680223bcbcdd9e5018000000000000000656432353531390000000000000000002000000000000000d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d77804000000000000000bdf023fbe7e0efec584d254b111655e1c2f81b9488943c3a712b91d9ad3a140cb0949a8868c5f72e08ccded337b79479114bdb4ed05f94dfddb359e1a612460201210000000000000001e78fd5af261e49643dba489b29566db53fa6e195fa0e6aad4430d4f06ce88b73010000000000000004000000000000003b9aca00180000000000000061206d696e74657220646566696e6974696f6e2074657374'

        # v129 Transactions are supported
        v129_txn_json = {"version":129,"data":{"nonce":"1oQFzIwsLs8=","mintfulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"ad59389329ed01c5ee14ce25ae38634c2b3ef694a2bdfa714f73b175f979ba6613025f9123d68c0f11e8f0a7114833c0aab4c8596d4c31671ec8a73923f02305"}},"coinoutputs":[{"value":"500000000000000","condition":{"type":1,"data":{"unlockhash":"01e3cbc41bd3cdfec9e01a6be46a35099ba0e1e1b793904fce6aa5a444496c6d815f5e3e981ccf"}}}],"minerfees":["1000000000"],"arbitrarydata":"dGVzdC4uLiAxLCAyLi4uIDM="}}
        v129_txn = self.from_json(v129_txn_json)
        assert v129_txn.json() == v129_txn_json
        assert v129_txn.signature_hash_get(0).hex() == '984ccc3da2107e86f67ef618886f9144040d84d9f65f617c64fa34de68c0018b'
        assert v129_txn.binary_encode().hex() == '81d68405cc8c2c2ecf018000000000000000656432353531390000000000000000002000000000000000d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d77804000000000000000ad59389329ed01c5ee14ce25ae38634c2b3ef694a2bdfa714f73b175f979ba6613025f9123d68c0f11e8f0a7114833c0aab4c8596d4c31671ec8a73923f023050100000000000000070000000000000001c6bf5263400001210000000000000001e3cbc41bd3cdfec9e01a6be46a35099ba0e1e1b793904fce6aa5a444496c6d81010000000000000004000000000000003b9aca001100000000000000746573742e2e2e20312c20322e2e2e2033'
        assert str(v129_txn.coin_outputid_new(0)) == 'f4b8569f430a29af187a8b97e78167b63895c51339255ea5198a35f4b162b4c6'

        # 3Bot Transactions

        # v144 Transactions are supported
        # TODO

        # v145 Transactions are supported
        # TODO

        # v146 Transactions are supported
        # TODO

        # ERC20 Transactions

        # v208 Transactions are supported
        # TODO

        # v209 Transactions are supported
        # TODO

        # v210 Transactions are supported
        # TODO

from abc import ABC, abstractmethod, abstractclassmethod

from .PrimitiveTypes import Hash

class TransactionBaseClass(ABC):
    def __init__(self):
        self._id = None
        self._unconfirmed = False

    @classmethod
    def from_json(cls, obj):
        """
        Create this transaction from a raw JSON Tx
        """
        txn = cls()
        tv = obj.get('version', -1)
        if txn.version != tv:
            raise ValueError("transaction is expected to be of version {}, not version {}".format(txn.version, tv))
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
    def unconfirmed(self):
        return self._unconfirmed
    @unconfirmed.setter
    def unconfirmed(self, value):
        if not isinstance(value, bool):
            raise TypeError("unconfirmed status of a Transaction is expected to be of type bool, not {}".format(type(bool)))
        self._unconfirmed = bool(value)
    
    @property
    def id(self):
        return str(self._id)
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
    def blockstake_inputs(self):
        """
        Blockstake inputs of this Transaction,
        used mainly as funding for block creations.
        """
        return []

    @property
    def blockstake_outputs(self):
        """
        BLockstake outputs of this Transaction,
        funded by the Transaction's blockstake inputs.
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
        return bytes()
    
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
        return bytes.fromhex(j.data.hash.blake2_string(input))

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

    def __str__(self):
        s = "transaction v{}".format(self.version)
        if self.id:
            s += " {}".format(self.id)
        return s
    __repr__ = __str__

    @property
    def _coin_outputid_specifier(self):
        return b'coin output\0\0\0\0\0'

    @property
    def _blockstake_outputid_specifier(self):
        return b'blstake output\0\0'

    def coin_outputid_new(self, index):
        """
        Compute the ID of a Coin Output within this transaction.
        """
        if index < 0 or index >= len(self.coin_outputs):
            raise ValueError("coin output index is out of range")
        return self._outputid_new(specifier=self._coin_outputid_specifier, index=index)

    def blockstake_outputid_new(self, index):
        """
        Compute the ID of a Coin Output within this transaction.
        """
        if index < 0 or index >= len(self.coin_outputs):
            raise ValueError("coin output index is out of range")
        return self._outputid_new(specifier=self._blockstake_outputid_specifier, index=index)

    def _outputid_new(self, specifier, index):
        encoder = j.data.rivine.encoder_sia_get()
        encoder.add_array(specifier)
        encoder.add_array(self._id_input_compute())
        encoder.add_int(index)
        hash = bytearray.fromhex(j.data.hash.blake2_string(encoder.data))
        return Hash(value=hash)

    def _id_input_compute(self):
        """
        Compute the core input data used for any ID computation.
        The default can be overriden by Transaction Classes should it be required.
        """
        return self.binary_encode()

    def binary_encode(self):
        """
        Binary encoding of a Transaction,
        the transaction type defines if it is done using Sia or Rivine encoding.
        """
        return bytearray([self.version]) + self._binary_encode_data()

    def _binary_encode_data(self):
        """
        Default Binary encoding of a Transaction Data,
        can be overriden if required.
        """
        encoder = j.data.rivine.encoder_sia_get()
        encoder.add_all(
            self.coin_inputs,
            self.coin_outputs,
            self.blockstake_inputs,
            self.blockstake_outputs,
            self.miner_fees,
            self.data,
        )
        return encoder.data

    def signature_requests_new(self):
        """
        Returns all signature requests still open for this Transaction.
        """
        requests = []
        for (index, ci) in enumerate(self.coin_inputs):
            f = InputSignatureHashFactory(self, index).signature_hash_new
            requests += ci.signature_requests_new(input_hash_func=f)
        for (index, bsi) in enumerate(self.blockstake_inputs):
            f = InputSignatureHashFactory(self, index).signature_hash_new
            requests += bsi.signature_requests_new(input_hash_func=f)
        return requests + self._extra_signature_requests_new()

    def _extra_signature_requests_new(self):
        """
        Optional signature requests that can be defined by the transaction,
        outside of the ordinary, returns an empty list by default.
        """
        return []

    def is_fulfilled(self):
        """
        Returns if the entire transaction is fulfilled,
        meaning it has all the required signatures in all the required places.
        """
        return reduce(
            (lambda r, ci: r and ci.is_fulfilled()),
            self.coin_inputs, self._extra_is_fulfilled())

    def _extra_is_fulfilled(self):
        """
        Optional check that can be defined by specific transactions,
        in case there are signatures required in other scenarios.

        Returns True by default.
        """
        return True


class InputSignatureHashFactory():
    """
    Class that can be used by Transaction consumers,
    to generate a factory that can provide the signature_hash_func callback
    used during the creation of signature requests,
    only useful if some extra objects needs to be included that are outside the Txn scope.
    """
    def __init__(self, txn, *extra_objects):
        if not isinstance(txn, TransactionBaseClass):
            raise TypeError("txn has an invalid type {}".format(type(txn)))
        self._txn = txn
        self._extra_objects = extra_objects

    def signature_hash_new(self, *extra_objects):
        objects = list(self._extra_objects)
        objects += extra_objects
        return self._txn.signature_hash_get(*objects)


from .CompositionTypes import CoinInput, CoinOutput, BlockstakeInput, BlockstakeOutput
from .PrimitiveTypes import Currency, RawData

class TransactionV1(TransactionBaseClass):
    def __init__(self):
        self._coin_inputs = []
        self._coin_outputs = []
        self._blockstake_inputs = []
        self._blockstake_outputs = []
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

        tv = obj.get('version', -1)
        if _LEGACY_TRANSACTION_V0 != tv:
            raise ValueError("legacy v0 transaction is expected to be of version {}, not version {}".format(_LEGACY_TRANSACTION_V0, tv))
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
        if 'blockstakeinputs' in txn_data:
            for legacy_bsi_info in (txn_data['blockstakeinputs'] or []):
                unlocker = legacy_bsi_info.get('unlocker', {})
                bsi_info = {
                    'parentid': legacy_bsi_info.get('parentid', ''),
                    'fulfillment': {
                        'type': 1,
                        'data': {
                            'publickey': unlocker.get('condition', {}).get('publickey'),
                            'signature': unlocker.get('fulfillment', {}).get('signature'),
                        }
                    }
                }
                bsi = BlockstakeInput.from_json(bsi_info)
                txn._blockstake_inputs.append(bsi)
        if 'blockstakeoutputs' in txn_data:
            for legacy_bso_info in (txn_data['blockstakeoutputs'] or []):
                bso_info = {
                    'value': legacy_bso_info.get('value', '0'),
                    'condition': {
                        'type': 1,
                        'data': {
                            'unlockhash': legacy_bso_info.get('unlockhash', ''),
                        }
                    }
                }
                bso = BlockstakeOutput.from_json(bso_info)
                txn._blockstake_outputs.append(bso)

        if 'minerfees' in txn_data:
            for miner_fee in (txn_data['minerfees'] or []) :
                txn._miner_fees.append(Currency.from_json(miner_fee))
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
    @coin_inputs.setter
    def coin_inputs(self, value):
        self._coin_inputs = []
        if not value:
            return
        for ci in value:
            self.coin_input_add(ci.parentid, ci.fulfillment, parent_output=ci.parent_output)

    @property
    def coin_outputs(self):
        """
        Coin outputs of this Transaction,
        funded by the Transaction's coin inputs.
        """
        return self._coin_outputs
    @coin_outputs.setter
    def coin_outputs(self, value):
        self._coin_outputs = []
        if not value:
            return
        for co in value:
            self.coin_output_add(co.value, co.condition, id=co.id)

    def coin_input_add(self, parentid, fulfillment, parent_output=None):
        ci = CoinInput(parentid=parentid, fulfillment=fulfillment)
        ci.parent_output = parent_output
        self._coin_inputs.append(ci)

    def coin_output_add(self, value, condition, id=None):
        co = CoinOutput(value=value, condition=condition)
        co.id = id
        self._coin_outputs.append(co)

    @property
    def blockstake_inputs(self):
        """
        Blockstake inputs of this Transaction.
        """
        return self._blockstake_inputs
    @blockstake_inputs.setter
    def blockstake_inputs(self, value):
        self._blockstake_inputs = []
        if not value:
            return
        for bsi in value:
            self.blockstake_input_add(bsi.parentid, bsi.fulfillment, parent_output=bsi.parent_output)

    @property
    def blockstake_outputs(self):
        """
        Blockstake outputs of this Transaction.
        """
        return self._blockstake_outputs
    @blockstake_outputs.setter
    def blockstake_outputs(self, value):
        self._blockstake_outputs = []
        if not value:
            return
        for bso in value:
            self.blockstake_output_add(bso.value, bso.condition, id=bso.id)

    def blockstake_input_add(self, parentid, fulfillment, parent_output=None):
        bsi = BlockstakeInput(parentid=parentid, fulfillment=fulfillment)
        bsi.parent_output = parent_output
        self._blockstake_inputs.append(bsi)

    def blockstake_output_add(self, value, condition, id=None):
        bso = BlockstakeOutput(value=value, condition=condition)
        bso.id = id
        self._blockstake_outputs.append(bso)

    def miner_fee_add(self, value):
        self._miner_fees.append(Currency(value=value))

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
        if self._data is None:
            return RawData()
        return self._data
    @data.setter
    def data(self, value):
        if value is None:
            self._data = None
            return
        if isinstance(value, RawData):
            value = value.value
        elif isinstance(value, str):
            value = value.encode('utf-8')
        if len(value) > 83:
            raise ValueError("arbitrary data can have a maximum bytes length of 83, {} exceeds this limit".format(len(value)))
        self._data = RawData(value=value)
    
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
            e.add(ci.parentid)

        # encode coin outputs
        e.add_slice(self.coin_outputs)

        # encode the number of blockstake inputs
        e.add(len(self.blockstake_inputs))
        # encode blockstake inputs parent_ids
        for bsi in self.blockstake_inputs:
            e.add(bsi.parentid)

        # encode blockstake outputs
        e.add_slice(self.blockstake_outputs)

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
            e.add_all(ci.parentid, ci.fulfillment.public_key.unlockhash())

        # encode coin outputs
        e.add(len(self.coin_outputs))
        for co in self.coin_outputs:
            e.add_all(co.value, co.condition.unlockhash)

        # encode blockstake inputs
        for bsi in self.blockstake_inputs:
            e.add_all(bsi.parentid, bsi.fulfillment.public_key.unlockhash())

        # encode blockstake outputs
        e.add(len(self.blockstake_outputs))
        for bso in self.blockstake_outputs:
            e.add_all(bso.value, bso.condition.unlockhash)

        # encode miner fees
        e.add_slice(self.miner_fees)

        # encode custom data
        e.add(self.data)

        # return the encoded data
        return e.data
        

    def _from_json_data_object(self, data):
        self._coin_inputs = [CoinInput.from_json(ci) for ci in data.get('coininputs', []) or []]
        self._coin_outputs = [CoinOutput.from_json(co) for co in data.get('coinoutputs', []) or []]
        self._blockstake_inputs = [BlockstakeInput.from_json(bsi) for bsi in data.get('blockstakeinputs', []) or []]
        self._blockstake_outputs = [BlockstakeOutput.from_json(bso) for bso in data.get('blockstakeoutputs', []) or []]
        self._miner_fees = [Currency.from_json(fee) for fee in data.get('minerfees', []) or []]
        self._data = RawData.from_json(data.get('arbitrarydata', None) or '')

    def _json_data_object(self):
        obj = {
            'coininputs': [ci.json() for ci in self._coin_inputs],
            'coinoutputs': [co.json() for co in self._coin_outputs],
            'blockstakeinputs': [bsi.json() for bsi in self._blockstake_inputs],
            'blockstakeoutputs': [bso.json() for bso in self._blockstake_outputs],
            'minerfees': [fee.json() for fee in self._miner_fees],
            'arbitrarydata': self.data.json(),
        }
        keys = list(obj.keys())
        for key in keys:
            if not obj[key]:
                del obj[key]
        return obj

    @property
    def _coin_outputid_specifier(self):
        if self._legacy:
            return b'coin output\0\0\0\0'
        return super()._coin_outputid_specifier

    @property
    def _blockstake_outputid_specifier(self):
        if self._legacy:
            return b'blstake output\0'
        return super()._blockstake_outputid_specifier

    def binary_encode(self):
        """
        Binary encoding of a Transaction,
        overriden to specify the version correctly
        """
        if self._legacy:
            return bytearray([_LEGACY_TRANSACTION_V0]) + self._binary_encode_data()
        encoder = j.data.rivine.encoder_sia_get()
        encoder.add_array(bytearray([_TRANSACTION_V1]))
        encoder.add_slice(self._binary_encode_data())
        return encoder.data

    def _binary_encode_data(self):
        if not self._legacy:
            return super()._binary_encode_data()
        # encoding was slightly different in legacy transactions (v0)
        # (NOTE: we only support the subset of v0 transactions that are actually active on the tfchain network)
        encoder = j.data.rivine.encoder_sia_get()
        # > encode coin inputs
        encoder.add_int(len(self.coin_inputs))
        for ci in self.coin_inputs:
            encoder.add(ci.parentid)
            encoder.add_array(bytearray([1])) # FulfillmentTypeSingleSignature
            sub_encoder = j.data.rivine.encoder_sia_get()
            sub_encoder.add(ci.fulfillment.public_key)
            encoder.add_slice(sub_encoder.data)
            encoder.add(ci.fulfillment.signature)
        # > encode coin outputs
        encoder.add_int(len(self.coin_outputs))
        for co in self.coin_outputs:
            encoder.add_all(co.value, co.condition.unlockhash)
        # > encode block stake inputs
        encoder.add_int(len(self._blockstake_inputs))
        for bsi in self._blockstake_inputs:
            encoder.add(bsi.parentid)
            encoder.add_array(bytearray([1])) # FulfillmentTypeSingleSignature
            sub_encoder = j.data.rivine.encoder_sia_get()
            sub_encoder.add(bsi.fulfillment.public_key)
            encoder.add_slice(sub_encoder.data)
            encoder.add(bsi.fulfillment.signature)
        # > encode block stake outputs
        encoder.add_int(len(self._blockstake_outputs))
        for bso in self.blockstake_outputs:
            encoder.add_all(bso.value, bso.condition.unlockhash)
        # > encode miner fees and arbitrary data
        encoder.add_all(self.miner_fees, self.data)
        return encoder.data


from .FulfillmentTypes import FulfillmentBaseClass, FulfillmentSingleSignature 
from .ConditionTypes import ConditionBaseClass, ConditionNil 

from .PrimitiveTypes import BinaryData

class TransactionV128(TransactionBaseClass):
    _SPECIFIER = b'minter defin tx\0'

    def __init__(self):
        self._mint_fulfillment = None
        self._mint_condition = None
        self._miner_fees = []
        self._data = None
        self._nonce = RawData(j.data.idgenerator.generateXByteID(8))

        # current mint condition
        self._parent_mint_condition = None

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
        if self._data is None:
            return RawData()
        return self._data
    @data.setter
    def data(self, value):
        if value is None:
            self._data = None
            return
        if isinstance(value, RawData):
            value = value.value
        elif isinstance(value, str):
            value = value.encode('utf-8')
        if len(value) > 83:
            raise ValueError("arbitrary data can have a maximum bytes length of 83, {} exceeds this limit".format(len(value)))
        self._data = RawData(value=value)

    @property
    def mint_condition(self):
        """
        Retrieve the new mint condition which will be set
        """
        if self._mint_condition is None:
            return ConditionNil()
        return self._mint_condition
    @mint_condition.setter
    def mint_condition(self, value):
        if value is None:
            self._mint_condition = None
            return
        if not isinstance(value, ConditionBaseClass):
            raise TypeError("MintDefinition (v128) Transaction's mint condition has to be a subtype of ConditionBaseClass, not {}".format(type(value)))
        self._mint_condition = value

    @property
    def parent_mint_condition(self):
        """
        Retrieve the parent mint condition which will be set
        """
        if self._parent_mint_condition is None:
            return ConditionNil()
        return self._parent_mint_condition
    @parent_mint_condition.setter
    def parent_mint_condition(self, value):
        if value is None:
            self._parent_mint_condition = None
            return
        if not isinstance(value, ConditionBaseClass):
            raise TypeError("MintDefinition (v128) Transaction's parent mint condition has to be a subtype of ConditionBaseClass, not {}".format(type(value)))
        self._parent_mint_condition = value

    def mint_fulfillment_defined(self):
        return self._mint_fulfillment is not None

    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        if self._mint_fulfillment is None:
            return FulfillmentSingleSignature()
        return self._mint_fulfillment
    @mint_fulfillment.setter
    def mint_fulfillment(self, value):
        if value is None:
            self._mint_fulfillment = None
            return
        if not isinstance(value, FulfillmentBaseClass):
            raise TypeError("MintDefinition (v128) Transaction's mint fulfillment has to be a subtype of FulfillmentBaseClass, not {}".format(type(value)))
        self._mint_fulfillment = value

    def miner_fee_add(self, value):
        self._miner_fees.append(Currency(value=value))

    def _signature_hash_input_get(self, *extra_objects):
        e = j.data.rivine.encoder_sia_get()

        # encode the transaction version
        e.add_byte(self.version)

        # encode the specifier
        e.add_array(TransactionV128._SPECIFIER)

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

    def _id_input_compute(self):
        return bytearray(TransactionV128._SPECIFIER) + self._binary_encode_data()

    def _binary_encode_data(self):
        encoder = j.data.rivine.encoder_sia_get()
        encoder.add_array(self._nonce.value)
        encoder.add_all(
            self.mint_fulfillment,
            self.mint_condition,
            self.miner_fees,
            self.data,
        )
        return encoder.data

    def _from_json_data_object(self, data):
        self._nonce = RawData.from_json(data.get('nonce', ''))
        self._mint_condition = j.clients.tfchain.types.conditions.from_json(data.get('mintcondition', {}))
        self._mint_fulfillment = j.clients.tfchain.types.fulfillments.from_json(data.get('mintfulfillment', {}))
        self._miner_fees = [Currency.from_json(fee) for fee in data.get('minerfees', []) or []]
        self._data = RawData.from_json(data.get('arbitrarydata', None) or '')

    def _json_data_object(self):
        return {
            'nonce': self._nonce.json(),
            'mintfulfillment': self.mint_fulfillment.json(),
            'mintcondition': self.mint_condition.json(),
            'minerfees': [fee.json() for fee in self._miner_fees],
            'arbitrarydata': self.data.json(),
        }
    
    def _extra_signature_requests_new(self):
        if self._parent_mint_condition is None:
            return [] # nothing to be signed
        return self._mint_fulfillment.signature_requests_new(
            input_hash_func=self.signature_hash_get, # no extra objects are to be included within txn scope
            parent_condition=self._parent_mint_condition,
        )

    def _extra_is_fulfilled(self):
        if self._parent_mint_condition is None:
            return False
        return self.mint_fulfillment.is_fulfilled(parent_condition=self._parent_mint_condition)

class TransactionV129(TransactionBaseClass):
    _SPECIFIER = b'coin mint tx\0\0\0\0'

    def __init__(self):
        self._mint_fulfillment = None
        self._coin_outputs = []
        self._miner_fees = []
        self._data = None
        self._nonce = RawData(j.data.idgenerator.generateXByteID(8))

        # current mint condition
        self._parent_mint_condition = None

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
        if self._data is None:
            return RawData()
        return self._data
    @data.setter
    def data(self, value):
        if value is None:
            self._data = None
            return
        if isinstance(value, RawData):
            value = value.value
        elif isinstance(value, str):
            value = value.encode('utf-8')
        if len(value) > 83:
            raise ValueError("arbitrary data can have a maximum bytes length of 83, {} exceeds this limit".format(len(value)))
        self._data = RawData(value=value)

    @property
    def coin_outputs(self):
        """
        Coin outputs of this Transaction,
        funded by the Transaction's coin inputs.
        """
        return self._coin_outputs
    @coin_outputs.setter
    def coin_outputs(self, value):
        self._coin_outputs = []
        if not value:
            return
        for co in value:
            self.coin_output_add(co.value, co.condition, id=co.id)

    def coin_output_add(self, value, condition, id=None):
        co = CoinOutput(value=value, condition=condition)
        co.id = id
        self._coin_outputs.append(co)

    def miner_fee_add(self, value):
        self._miner_fees.append(Currency(value=value))

    def mint_fulfillment_defined(self):
        return self._mint_fulfillment is not None

    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        if self._mint_fulfillment is None:
            return FulfillmentSingleSignature()
        return self._mint_fulfillment
    @mint_fulfillment.setter
    def mint_fulfillment(self, value):
        if value is None:
            self._mint_fulfillment = None
            return
        if not isinstance(value, FulfillmentBaseClass):
            raise TypeError("CoinCreation (v129) Transaction's mint fulfillment has to be a subtype of FulfillmentBaseClass, not {}".format(type(value)))
        self._mint_fulfillment = value

    @property
    def parent_mint_condition(self):
        """
        Retrieve the parent mint condition which will be set
        """
        if self._parent_mint_condition is None:
            return ConditionNil()
        return self._parent_mint_condition
    @parent_mint_condition.setter
    def parent_mint_condition(self, value):
        if value is None:
            self._parent_mint_condition = None
            return
        if not isinstance(value, ConditionBaseClass):
            raise TypeError("CoinCreation (v129) Transaction's parent mint condition has to be a subtype of ConditionBaseClass, not {}".format(type(value)))
        self._parent_mint_condition = value

    def _signature_hash_input_get(self, *extra_objects):
        e = j.data.rivine.encoder_sia_get()

        # encode the transaction version
        e.add_byte(self.version)

        # encode the specifier
        e.add_array(TransactionV129._SPECIFIER)

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

    def _id_input_compute(self):
        return bytearray(TransactionV129._SPECIFIER) + self._binary_encode_data()

    def _binary_encode_data(self):
        encoder = j.data.rivine.encoder_sia_get()
        encoder.add_array(self._nonce.value)
        encoder.add_all(
            self.mint_fulfillment,
            self.coin_outputs,
            self.miner_fees,
            self.data,
        )
        return encoder.data

    def _from_json_data_object(self, data):
        self._nonce = RawData.from_json(data.get('nonce', ''))
        self._mint_fulfillment = j.clients.tfchain.types.fulfillments.from_json(data.get('mintfulfillment', {}))
        self._coin_outputs = [CoinOutput.from_json(co) for co in data.get('coinoutputs', []) or []]
        self._miner_fees = [Currency.from_json(fee) for fee in data.get('minerfees', []) or []]
        self._data = RawData.from_json(data.get('arbitrarydata', None) or '')

    def _json_data_object(self):
        return {
            'nonce': self._nonce.json(),
            'mintfulfillment': self.mint_fulfillment.json(),
            'coinoutputs': [co.json() for co in self.coin_outputs],
            'minerfees': [fee.json() for fee in self.miner_fees],
            'arbitrarydata': self.data.json(),
        }
    
    def _extra_signature_requests_new(self):
        if self._parent_mint_condition is None:
            return [] # nothing to be signed
        return self._mint_fulfillment.signature_requests_new(
            input_hash_func=self.signature_hash_get, # no extra objects are to be included within txn scope
            parent_condition=self._parent_mint_condition,
        )

    def _extra_is_fulfilled(self):
        if self._parent_mint_condition is None:
            return False
        return self.mint_fulfillment.is_fulfilled(parent_condition=self._parent_mint_condition)
