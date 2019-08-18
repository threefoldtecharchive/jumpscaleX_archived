from Jumpscale import j

import pytest

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="atomicswap_verify_receiver")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    # add the blockchain info
    explorer_client.chain_info = '{"blockid":"5c180121d6dbbbc8480ee63d58933a4e0d9eae664c0b8662c3ef81102c3fe82c","difficulty":"23546","estimatedactivebs":"146","height":17384,"maturitytimestamp":1549705634,"target":[0,2,200,131,232,66,109,128,132,97,252,155,147,77,241,96,113,131,22,176,230,53,191,80,170,156,189,0,160,84,41,168],"totalcoins":"0","arbitrarydatatotalsize":4351,"minerpayoutcount":17470,"transactioncount":18011,"coininputcount":637,"coinoutputcount":1231,"blockstakeinputcount":17384,"blockstakeoutputcount":17385,"minerfeecount":626,"arbitrarydatacount":573}'
    explorer_client.hash_add(
        "5c180121d6dbbbc8480ee63d58933a4e0d9eae664c0b8662c3ef81102c3fe82c",
        '{"hashtype":"blockid","block":{"minerpayoutids":["c8f3f82e4c5be07c667f140456e188336dc5c86319260ad9964c1b2a553d7031"],"transactions":[{"id":"9d8823855c59ac903238849e2f31600a9bec2c27d36071402815046dbf8000e7","height":17384,"parent":"5c180121d6dbbbc8480ee63d58933a4e0d9eae664c0b8662c3ef81102c3fe82c","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"7c111a656be26b42215d13df330aa46c30d9f84d8b47ca5f41c4a5a1f89c782d","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"8de764af61c2e404f246482a70e29881929a71e4644a4c6f3a620889b1339a3eb789b0e2b5dad4ba26d1862bbee3a62a6f42be8106867722488aed352b414d00"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["be4408fecfa7fb88831d6ff1ff2d32377c25ac6cdafcdec1a16644ef3540d0ea"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"d329ebc493b75521db55b6595a7bfcbe5c1f94eb0ab1f7646bf39a42a8f7dddf","timestamp":1549705757,"pobsindexes":{"BlockHeight":17383,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"7c111a656be26b42215d13df330aa46c30d9f84d8b47ca5f41c4a5a1f89c782d","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"8de764af61c2e404f246482a70e29881929a71e4644a4c6f3a620889b1339a3eb789b0e2b5dad4ba26d1862bbee3a62a6f42be8106867722488aed352b414d00"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"5c180121d6dbbbc8480ee63d58933a4e0d9eae664c0b8662c3ef81102c3fe82c","difficulty":"23546","estimatedactivebs":"146","height":17384,"maturitytimestamp":1549705634,"target":[0,2,200,131,232,66,109,128,132,97,252,155,147,77,241,96,113,131,22,176,230,53,191,80,170,156,189,0,160,84,41,168],"totalcoins":"0","arbitrarydatatotalsize":4351,"minerpayoutcount":17470,"transactioncount":18011,"coininputcount":637,"coinoutputcount":1231,"blockstakeinputcount":17384,"blockstakeoutputcount":17385,"minerfeecount":626,"arbitrarydatacount":573},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
    )
    # override internal functionality, as to use our stub client
    c._explorer_get = explorer_client.explorer_get
    c._explorer_post = explorer_client.explorer_post

    # a wallet is required to initiate an atomic swap contract
    w = c.wallets.new(
        "mytestwallet",
        seed="remain solar kangaroo welcome clean object friend later bounce strong ship lift hamster afraid you super dolphin warm emotion curve smooth kiss stem diet",
    )

    # one can verify that its transaction is sent as receiver,
    # usually done when someone is the receiver of an intiation contract,
    # such that all details can be verified prior to the creation of the
    # participation contract on the other chain

    # verification will fail if the contract could not be found
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractNotFound):
        w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486")

    # add the coin output info of the submitted atomic swap contract
    explorer_client.hash_add(
        "dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486",
        '{"hashtype":"coinoutputid","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"fd583a124677a3ea7ed7981d008ca79bd9f93cedbee97af2bcfd28b3f31093cc","height":17383,"parent":"d329ebc493b75521db55b6595a7bfcbe5c1f94eb0ab1f7646bf39a42a8f7dddf","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"8c8dbd70c6eb2d5d181aa5ae430f2cc86e038b92e45dd6f6d5a28400efad4511","fulfillment":{"type":1,"data":{"publickey":"ed25519:cf87843f9c9014700eaa2dc28a80e4a54587d8cca0baa717805ce117cecd9bb4","signature":"b9ce44b1e0f9e3fae9f21111ddc08333f6ba32675fc971893f6ab7ca3e5ab664883794fd3a35aef59ba54242d9be92fbcf65cefb5eede3709dd57226203b6601"}}}],"coinoutputs":[{"value":"50000000000","condition":{"type":2,"data":{"sender":"01b88206a3300dea3dd5f6cd73568ac5797b078910c78cbce6a71fcd0837a3ea5a4f2ed9fc70a1","receiver":"01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0","hashedsecret":"e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c1","timelock":1549878527}}},{"value":"99994136000000000","condition":{"type":1,"data":{"unlockhash":"017cb06fa6f44828617b92603e95171044d9dc7c4966ffa0d8f6f97171558735974e7ecc623ff7"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99994187000000000","condition":{"type":1,"data":{"unlockhash":"0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a"}},"unlockhash":"0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a"}],"coinoutputids":["dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486","75bbe54aca26d5a5afbc442c0e033a3ad18efa1e130f0776a9e4b68cdbe24fb7"],"coinoutputunlockhashes":["02f6d25603d232512ade46cdec3160301d8bd4880f2d4e8e20f54aff24f94dac5792ab1b325c3d","017cb06fa6f44828617b92603e95171044d9dc7c4966ffa0d8f6f97171558735974e7ecc623ff7"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}',
    )

    # one can verify it all manually
    contract = w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486")
    assert contract.outputid == "dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486"
    assert contract.amount == "50 TFT"
    assert contract.refund_timestamp == 1549878527
    assert contract.sender == "01b88206a3300dea3dd5f6cd73568ac5797b078910c78cbce6a71fcd0837a3ea5a4f2ed9fc70a1"
    assert contract.receiver == "01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"
    assert contract.secret_hash == "e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c1"

    # the amount can however be verified automatically
    w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486", amount=50)
    # which will fail if the amount is wrong
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486", amount=42)

    # the secret hash can be verified as well, very important
    w.atomicswap.verify(
        "dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486",
        secret_hash="e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c1",
    )
    # which will fail if the secret hash is wrong
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify(
            "dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486",
            secret_hash="e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c2",
        )

    # a minimum duration can also be defined, where the duration defines how long it takes until the
    # contract becomes refundable, 0 if already assumed to be refundable
    w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486", min_refund_time="+1d12h")
    # which will fail if assumed wrong
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486", min_refund_time="+2d")

    # if one is assumed to be the receiver, it can also be verified automatically
    w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486", receiver=True)
    # if one assumed its position wrong, it will however fail
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify("dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486", sender=True)

    # all can be verified at once of course
    contract = w.atomicswap.verify(
        "dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486",
        amount=50,
        secret_hash="e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c1",
        min_refund_time="+1d12h",
        receiver=True,
    )

    # once the expected min duration has been surpassed, validation will fail
    explorer_client.hash_add(
        "5c180121d6dbbbc8480ee63d58933a4e0d9eae664c0b8662c3ef81102c3fe82c",
        '{"hashtype":"blockid","block":{"minerpayoutids":["c8f3f82e4c5be07c667f140456e188336dc5c86319260ad9964c1b2a553d7031"],"transactions":[{"id":"9d8823855c59ac903238849e2f31600a9bec2c27d36071402815046dbf8000e7","height":17384,"parent":"5c180121d6dbbbc8480ee63d58933a4e0d9eae664c0b8662c3ef81102c3fe82c","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"7c111a656be26b42215d13df330aa46c30d9f84d8b47ca5f41c4a5a1f89c782d","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"8de764af61c2e404f246482a70e29881929a71e4644a4c6f3a620889b1339a3eb789b0e2b5dad4ba26d1862bbee3a62a6f42be8106867722488aed352b414d00"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["be4408fecfa7fb88831d6ff1ff2d32377c25ac6cdafcdec1a16644ef3540d0ea"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"d329ebc493b75521db55b6595a7bfcbe5c1f94eb0ab1f7646bf39a42a8f7dddf","timestamp":1549791703,"pobsindexes":{"BlockHeight":17383,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"7c111a656be26b42215d13df330aa46c30d9f84d8b47ca5f41c4a5a1f89c782d","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"8de764af61c2e404f246482a70e29881929a71e4644a4c6f3a620889b1339a3eb789b0e2b5dad4ba26d1862bbee3a62a6f42be8106867722488aed352b414d00"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"5c180121d6dbbbc8480ee63d58933a4e0d9eae664c0b8662c3ef81102c3fe82c","difficulty":"23546","estimatedactivebs":"146","height":17384,"maturitytimestamp":1549705634,"target":[0,2,200,131,232,66,109,128,132,97,252,155,147,77,241,96,113,131,22,176,230,53,191,80,170,156,189,0,160,84,41,168],"totalcoins":"0","arbitrarydatatotalsize":4351,"minerpayoutcount":17470,"transactioncount":18011,"coininputcount":637,"coinoutputcount":1231,"blockstakeinputcount":17384,"blockstakeoutputcount":17385,"minerfeecount":626,"arbitrarydatacount":573},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
        force=True,
    )
    # our initial hope would be wrong now
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify(
            "dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486",
            amount=50,
            secret_hash="e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c1",
            min_refund_time="+1d12h",
            receiver=True,
        )
    # it is still not refundable however,
    # and for multiple checks one can pass the contract that was already fetched
    w.atomicswap.verify(
        "dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486",
        amount=50,
        secret_hash="e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c1",
        min_refund_time="+1d",
        receiver=True,
        contract=contract,
    )
