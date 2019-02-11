from Jumpscale import j

from ..Errors import UnknownTransansactionVersion

from .Base import TransactionBaseClass, TransactionVersion
from .Standard import TransactionV1
from .Minting import TransactionV128, TransactionV129
from .ThreeBot import BotTransactionBaseClass, TransactionV144, TransactionV145, TransactionV146

class TransactionFactory(j.application.JSBaseClass):
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

    def threebot_registration_new(self):
        """
        Creates and returns an empty 3Bot Registration transaction.
        """
        return TransactionV144()

    def threebot_record_update_new(self):
        """
        Creates and returns an empty 3Bot Record Update transaction.
        """
        return TransactionV145()

    def threebot_name_transfer_new(self):
        """
        Creates and returns an empty 3Bot Name Transfer transaction.
        """
        return TransactionV146()

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
        if tt == TransactionVersion.STANDARD:
            txn = TransactionV1.from_json(obj)
        elif tt == TransactionVersion.THREEBOT_REGISTRATION:
            txn = TransactionV144.from_json(obj)
        elif tt == TransactionVersion.THREEBOT_RECORD_UPDATE:
            txn = TransactionV145.from_json(obj)
        elif tt == TransactionVersion.THREEBOT_NAME_TRANSFER:
            txn = TransactionV146.from_json(obj)
        elif tt == TransactionVersion.MINTER_DEFINITION:
            txn = TransactionV128.from_json(obj)
        elif tt == TransactionVersion.MINTER_COIN_CREATION:
            txn = TransactionV129.from_json(obj)
        elif tt == TransactionVersion.LEGACY:
            txn = TransactionV1.legacy_from_json(obj)

        if isinstance(txn, TransactionBaseClass):
            txn.id = id
            return txn

        raise UnknownTransansactionVersion("transaction version {} is unknown".format(tt))


    def test(self):
        """
        js_shell 'j.clients.tfchain.types.transactions.test()'
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
        v144_txn_json = {"version":144,"data":{"addresses":["91.198.174.192","example.org"],"names":["chatbot.example"],"nrofmonths":1,"txfee":"1000000000","coininputs":[{"parentid":"a3c8f44d64c0636018a929d2caeec09fb9698bfdcbfa3a8225585a51e09ee563","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"909a7df820ec3cee1c99bd2c297b938f830da891439ef7d78452e29efb0c7e593683274c356f72d3b627c2954a24b2bc2276fed47b24cd62816c540c88f13d05"}}}],"refundcoinoutput":{"value":"99999899000000000","condition":{"type":1,"data":{"unlockhash":"01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f"}}},"identification":{"publickey":"ed25519:00bde9571b30e1742c41fcca8c730183402d967df5b17b5f4ced22c677806614","signature":"98e71668dfe7726a357039d7c0e871b6c0ca8fa49dc1fcdccb5f23f5f0a5cab95cfcfd72a9fd2c5045ba899ecb0207ff01125a0151f3e35e3c6e13a7538b340a"}}}
        v144_txn = self.from_json(v144_txn_json)
        assert v144_txn.json() == v144_txn_json
        assert v144_txn.signature_hash_get(BotTransactionBaseClass.SPECIFIER_SENDER).hex() == 'f9204641c6a945af6d262154f3d1dfa82aa291c4fc4000936ee72fc3506cfd2c'
        assert v144_txn.binary_encode().hex() == '90e112115bc6aec02c6578616d706c652e6f72671e63686174626f742e6578616d706c65083b9aca0002a3c8f44d64c0636018a929d2caeec09fb9698bfdcbfa3a8225585a51e09ee56301c401d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d778080909a7df820ec3cee1c99bd2c297b938f830da891439ef7d78452e29efb0c7e593683274c356f72d3b627c2954a24b2bc2276fed47b24cd62816c540c88f13d051001634560d9784e00014201b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960100bde9571b30e1742c41fcca8c730183402d967df5b17b5f4ced22c67780661498e71668dfe7726a357039d7c0e871b6c0ca8fa49dc1fcdccb5f23f5f0a5cab95cfcfd72a9fd2c5045ba899ecb0207ff01125a0151f3e35e3c6e13a7538b340a'

        # v145 Transactions are supported
        v145_txn_json = {"version":145,"data":{"id":3,"addresses":{"add":["example.com","127.0.0.1"],"remove":["example.org"]},"names":{"add":["giveme.yourfeedback","thisis.anexample"],"remove":["chatbot.example"]},"nrofmonths":4,"txfee":"1000000000","coininputs":[{"parentid":"81a0c1f3094b99b0858da8ebc95b52f2c3593ea399d7b72a66a930521aae61bb","fulfillment":{"type":1,"data":{"publickey":"ed25519:880ee50bd7efa4c8b2b5949688a09818a652727fd3c0cb406013be442df68b34","signature":"d612b679377298e6ccb8a877f7a129d34c65b8850cff1806b9f62d392b6ab173020c3698658275c748047642f8012a4ac75ea23e319bcc405c9d7f2b462b6a0b"}}}],"refundcoinoutput":{"value":"99998737000000000","condition":{"type":1,"data":{"unlockhash":"01972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff03e45f1470df82"}}},"signature":"f76e7ed808a9efe405804109d5e3c8695daf8b9bc7abf1e471fef94b3c4d36789b460f9e45cdf27d83d270b0836fef56bd499e1be8e1f279d367e961bbe62f03"}}
        v145_txn = self.from_json(v145_txn_json)
        assert v145_txn.json() == v145_txn_json
        assert v145_txn.signature_hash_get(BotTransactionBaseClass.SPECIFIER_SENDER).hex() == '3d86ed117c97718a9d0d644188e019b4fa55ec22f2c32c187d223d4e73a1ab72'
        assert v145_txn.binary_encode().hex() == '9103000000e4122c6578616d706c652e636f6d117f0000012c6578616d706c652e6f72671226676976656d652e796f7572666565646261636b207468697369732e616e6578616d706c651e63686174626f742e6578616d706c65083b9aca000281a0c1f3094b99b0858da8ebc95b52f2c3593ea399d7b72a66a930521aae61bb01c401880ee50bd7efa4c8b2b5949688a09818a652727fd3c0cb406013be442df68b3480d612b679377298e6ccb8a877f7a129d34c65b8850cff1806b9f62d392b6ab173020c3698658275c748047642f8012a4ac75ea23e319bcc405c9d7f2b462b6a0b10016344524cdf6a00014201972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff0380f76e7ed808a9efe405804109d5e3c8695daf8b9bc7abf1e471fef94b3c4d36789b460f9e45cdf27d83d270b0836fef56bd499e1be8e1f279d367e961bbe62f03'

        # v146 Transactions are supported
        v146_txn_json = {"version":146,"data":{"sender":{"id":1,"signature":"f1c6109c685c7452efaf20cec6b170817f1faeb6f0a4ff49a7a0872343e62810f51dee051d8eb7883fb0ad7a848aa5bf18b8bd30fe109daa04f13e7d76af750a"},"receiver":{"id":2,"signature":"ae9dc9fa308e76de123b5f889fed93d6d9a701dc8d5369787dc25095f3d6eb833f6d47302697d2da22e05854d08f26d723463f328cc6ec445529cff583903308"},"names":["hello.threebot"],"txfee":"1000000000","coininputs":[{"parentid":"572635ceed12c61cd78e97391c75fefb01cc969211aa827de4c44eb66285a37c","fulfillment":{"type":1,"data":{"publickey":"ed25519:3079d97d169f96b996ff87677483bb601150c1bae8b1061ecbb137b9597d7cb9","signature":"88e8c0d168ac60c1c6b47caad1bf660192064f2cd74ea38def15ff91d50e50b9bf2046c70c363d2ba152c51fcdaa017a27ab26a75bca76252df852785dd47007"}}}],"refundcoinoutput":{"value":"99993832000000000","condition":{"type":1,"data":{"unlockhash":"014195d5ada0434d0766bf9e3d9b87d2f63ef7b1820739cff88335d45cbae2dac58ec00841c570"}}}}}
        v146_txn = self.from_json(v146_txn_json)
        assert v146_txn.json() == v146_txn_json
        assert v146_txn.signature_hash_get(BotTransactionBaseClass.SPECIFIER_SENDER).hex() == 'ade263bfbc693e95463f19c201dd672bbd2616412362217c70317dfb42ab73cb'
        assert v146_txn.signature_hash_get(BotTransactionBaseClass.SPECIFIER_RECEIVER).hex() == '36445975184c68e13f8b74e2e87dd72f23cb47ff3bd4f22e80c4654ec63015d9'
        assert v146_txn.binary_encode().hex() == '920100000080f1c6109c685c7452efaf20cec6b170817f1faeb6f0a4ff49a7a0872343e62810f51dee051d8eb7883fb0ad7a848aa5bf18b8bd30fe109daa04f13e7d76af750a0200000080ae9dc9fa308e76de123b5f889fed93d6d9a701dc8d5369787dc25095f3d6eb833f6d47302697d2da22e05854d08f26d723463f328cc6ec445529cff583903308111c68656c6c6f2e7468726565626f74083b9aca0002572635ceed12c61cd78e97391c75fefb01cc969211aa827de4c44eb66285a37c01c4013079d97d169f96b996ff87677483bb601150c1bae8b1061ecbb137b9597d7cb98088e8c0d168ac60c1c6b47caad1bf660192064f2cd74ea38def15ff91d50e50b9bf2046c70c363d2ba152c51fcdaa017a27ab26a75bca76252df852785dd470071001633fdc441710000142014195d5ada0434d0766bf9e3d9b87d2f63ef7b1820739cff88335d45cbae2dac5'

        # 3Bot Transactions also have extra fees,
        # part of these fees are monthly fees
        assert BotTransactionBaseClass.compute_monthly_bot_fees(0) == '0 TFT'
        assert BotTransactionBaseClass.compute_monthly_bot_fees(1) == '10 TFT'
        assert BotTransactionBaseClass.compute_monthly_bot_fees(2) == '20 TFT'
        assert BotTransactionBaseClass.compute_monthly_bot_fees(11) == '110 TFT'
        assert BotTransactionBaseClass.compute_monthly_bot_fees(12) == '84 TFT'
        assert BotTransactionBaseClass.compute_monthly_bot_fees(21) == '147 TFT'
        assert BotTransactionBaseClass.compute_monthly_bot_fees(23) == '161 TFT'
        assert BotTransactionBaseClass.compute_monthly_bot_fees(24) == '120 TFT'

        # ERC20 Transactions

        # v208 Transactions are supported
        # TODO

        # v209 Transactions are supported
        # TODO

        # v210 Transactions are supported
        # TODO
