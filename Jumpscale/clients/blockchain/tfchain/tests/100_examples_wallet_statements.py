from Jumpscale import j

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="examples_wallet_statements")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mydevclient", network_type="DEV")
    # or simply `c = j.tfchain.clients.mydevclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    explorer_client.hash_add(
        "0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb",
        '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"208d9f524e937176e50a7399fd3886f584290948983bbd0ed781f59cefc343a8","height":39994,"parent":"c5fb21d8921b8974950b69bdabd2fdccb5b328e4f1cb42a657a4b71ecbdfd3ed","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"a249d627c5a5f8e23c751e7f4a3fef9dd9ddbfeea9d07f5bbf242bd339b287f0","fulfillment":{"type":1,"data":{"publickey":"ed25519:8b371733c8648a50f959efea292f5e1e38063dac3f9bfc0d260829ea74a17fff","signature":"a1c5c349637976ad18e07a206cb23cfdaf831ebb9d4cda3cf768a0b5e723c1ae6e643338c73cff1feb43f946e75788ebdb1b4200f39653efdb127e8e10e6ec02"}}}],"coinoutputs":[{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"01cb0aedd4098efd926195c2f7bba9323d919f99ecd95cf3626f0508f6be33f49bcae3dd62cca6"}}},{"value":"89000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"100000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}},"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}],"coinoutputids":["3f90223a71e6e474a0b6c073efec5ff2ce0656e932e55f10b8c3cdbf24ec8ede","b3e3787dc5c83fb8d174752721976341f02d4b3a58914984882520fea99b4eb7"],"coinoutputunlockhashes":["01cb0aedd4098efd926195c2f7bba9323d919f99ecd95cf3626f0508f6be33f49bcae3dd62cca6","0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"544a204f0211e7642f508a7918c5d29334bd7d6892b2612e8acfb6dc36d39bd9","height":39990,"parent":"d37c592e45407b70ea8000e8f4bb46fe0577d1740ff6c7ccf912b9765cb90c2e","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"1d2f5471fce574fb488615d42f8ed0cda3432fd9fde7b8c8914db5b05814e93d","fulfillment":{"type":1,"data":{"publickey":"ed25519:49106a6f57ef3a7c2f1d75acb1911c26b9c70e050b319ae4d00d07b38a328251","signature":"4a877bf9a46b31ff52e37469228516184611274a7b24fbc2d3b699d2a5f87eb81caf6a44fdb95d3b4568ce335447c9408b9f9a6c4aedda6f12ad9624b293f801"}}}],"coinoutputs":[{"value":"400000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}}},{"value":"99991626000000000","condition":{"type":1,"data":{"unlockhash":"01456d748fc44c753f63671cb384b8cb8a2aebb1d48b4e0be82c302d71c10f2448b2d8e3d164f6"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99992027000000000","condition":{"type":1,"data":{"unlockhash":"01773a1dd123347e1030f0822cb8d22082fe3f9b0ea8563d4ac8e7abc377eba920c47efb2fd736"}},"unlockhash":"01773a1dd123347e1030f0822cb8d22082fe3f9b0ea8563d4ac8e7abc377eba920c47efb2fd736"}],"coinoutputids":["07bd125a69db7d7aad56d1cebbdf3d6d8e830b8b1034a15c0482c778d0ca9f91","73b19c28a3995f8d255a772ffba2d8a19d10d3c74970f8de7373611964c97240"],"coinoutputunlockhashes":["0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb","01456d748fc44c753f63671cb384b8cb8a2aebb1d48b4e0be82c302d71c10f2448b2d8e3d164f6"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"779cf13ecee7f45f032af92429056cd5976cb75ce968bab98e3e2fdf9a9b1034","height":39997,"parent":"9e1127983d851593fdaee90979a0d68446c3f0088278b270f48c41ea14178f7f","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"b3e3787dc5c83fb8d174752721976341f02d4b3a58914984882520fea99b4eb7","fulfillment":{"type":1,"data":{"publickey":"ed25519:8b371733c8648a50f959efea292f5e1e38063dac3f9bfc0d260829ea74a17fff","signature":"0985318dcf8a484218d80430880e9668c1569b400bc0b96cdb4834dc9df7745e97e1764a98ad82c65b9aca269200349b500aec7a85ccbfe9e18b804687c0470e"}}}],"coinoutputs":[{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}}},{"value":"78000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"89000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}},"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}],"coinoutputids":["759d47d4d21f0bb95182fa12790e7f35a5299ed6cd49d7ca2f845baa31281485","80814afea75b03cee855b9a7359f60001e3cf1c9e413054bfa2d63b5cf4a99b7"],"coinoutputunlockhashes":["0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb","0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"b104308e683d4353a5a6b6cdfd4f6dfce39e241ff1218d6d6189bae89945034f","height":39995,"parent":"6dac39c66532c5704d212ce2d88540baa6c3d3567dc01b156531266b3cd244b1","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"231065ee55dc100ea7b4d19143a6daf3b7c29750366329143d842b87eae30a1e","fulfillment":{"type":1,"data":{"publickey":"ed25519:01adfffb60f4a5b84bc29b2c2a3e48a8be892399fe2544d71e1213e2e746fb79","signature":"2acb5319353ebb6bc260bcc81c8085399f973c133056142e1305db3048ade34916c0415fb419337f53e804a69de2cbaf55988cbd1cb7b89ad1eaca65f1722a0e"}}}],"coinoutputs":[{"value":"200000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}}},{"value":"50000000000","condition":{"type":1,"data":{"unlockhash":"01cb0aedd4098efd926195c2f7bba9323d919f99ecd95cf3626f0508f6be33f49bcae3dd62cca6"}}},{"value":"99991274000000000","condition":{"type":1,"data":{"unlockhash":"01f0f397fd6b7b51b46ddd2ffda1e2240e639b19b47d27a4adc2bed78da0fc3d97c1fe7b972d1e"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99991525000000000","condition":{"type":1,"data":{"unlockhash":"015827a0cabfb4be5531ecd2b42470a25cf9910a868b857029c2bdabdc05cad51e66d5dd899064"}},"unlockhash":"015827a0cabfb4be5531ecd2b42470a25cf9910a868b857029c2bdabdc05cad51e66d5dd899064"}],"coinoutputids":["6d39719a217be42db384d947db08dc4224718ed9e357b990cbfc39586d764da8","ed9cf75bffbeb91e756059422874bad956b0aedfbfae337d41dabe9be2a111c3","78282a245a381c7aa700a16fabfa3924e95d6329913e9d916a49a22ad1e4f177"],"coinoutputunlockhashes":["0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb","01cb0aedd4098efd926195c2f7bba9323d919f99ecd95cf3626f0508f6be33f49bcae3dd62cca6","01f0f397fd6b7b51b46ddd2ffda1e2240e639b19b47d27a4adc2bed78da0fc3d97c1fe7b972d1e"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"e7785bacd0d12f93ab435cf3e29301f15b84be82ae8abbdaed1cfd034f4ed652","height":39991,"parent":"3a3b2fee4728f347e26b74ace8ebfdb2b3e042e1be92cbc6ee2711eb42fd43e7","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"73b19c28a3995f8d255a772ffba2d8a19d10d3c74970f8de7373611964c97240","fulfillment":{"type":1,"data":{"publickey":"ed25519:d92be6ab3ddbed0f31d7ee2fd1a61e4e8ba746c4265567f4a9f00c59aa25f470","signature":"a2c990f636a8a1020d9bb937f5b65d7fa76078467b73429444192b2f95fe5b4b2cdfe393a3b00769fb8a3cc706c7dfa26b27454705fdd2df7287c49f618ec502"}}}],"coinoutputs":[{"value":"100000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}}},{"value":"99991525000000000","condition":{"type":1,"data":{"unlockhash":"015827a0cabfb4be5531ecd2b42470a25cf9910a868b857029c2bdabdc05cad51e66d5dd899064"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99991626000000000","condition":{"type":1,"data":{"unlockhash":"01456d748fc44c753f63671cb384b8cb8a2aebb1d48b4e0be82c302d71c10f2448b2d8e3d164f6"}},"unlockhash":"01456d748fc44c753f63671cb384b8cb8a2aebb1d48b4e0be82c302d71c10f2448b2d8e3d164f6"}],"coinoutputids":["a249d627c5a5f8e23c751e7f4a3fef9dd9ddbfeea9d07f5bbf242bd339b287f0","231065ee55dc100ea7b4d19143a6daf3b7c29750366329143d842b87eae30a1e"],"coinoutputunlockhashes":["0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb","015827a0cabfb4be5531ecd2b42470a25cf9910a868b857029c2bdabdc05cad51e66d5dd899064"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"573290763024ae0a5e981412598a3d41bc02f8da628fa1e1adfe07d98818c689","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"78282a245a381c7aa700a16fabfa3924e95d6329913e9d916a49a22ad1e4f177","fulfillment":{"type":1,"data":{"publickey":"ed25519:83ca81ff674dd835801a0aa3e5e5b05758033bffb425524d1be51da06a5a2341","signature":"638caa49226fb31ed1c3f51e5ad13e45f36246fdf6ea249563b0018595623624b01bf028953a3db31e4082d6dd3a9544d5de65a1a8c4b89a55366d004747390d"}}}],"coinoutputs":[{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb"}}},{"value":"99991263000000000","condition":{"type":1,"data":{"unlockhash":"016d2dea96293304aaff85f61fbfa882dd1f5ee2401c3f0dd6d1f20f53047e720c73fc0ddff6e9"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99991274000000000","condition":{"type":1,"data":{"unlockhash":"01f0f397fd6b7b51b46ddd2ffda1e2240e639b19b47d27a4adc2bed78da0fc3d97c1fe7b972d1e"}},"unlockhash":"01f0f397fd6b7b51b46ddd2ffda1e2240e639b19b47d27a4adc2bed78da0fc3d97c1fe7b972d1e"}],"coinoutputids":["3221846ff477b42583278fa4e4704f7f2267542fa1ac2b3ca8a19e4721b20dcb","18b436899914bc3b2f5aa2f3d6dad5f248a4c1a26078eb7e94855cc166d44bfb"],"coinoutputunlockhashes":["0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb","016d2dea96293304aaff85f61fbfa882dd1f5ee2401c3f0dd6d1f20f53047e720c73fc0ddff6e9"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":true}],"multisigaddresses":null,"unconfirmed":false}',
    )
    c._explorer_get = explorer_client.explorer_get

    # the devnet genesis seed is the seed of the wallet,
    # which receives all block stakes and coins in the genesis block of the tfchain devnet
    DEVNET_GENESIS_SEED = "smooth team admit virus weapon tiny jazz ecology check jump unit thought ankle rice please victory fringe logic patient eager rescue trial hawk veteran"

    # create a new devnet wallet
    w = c.wallets.new("mywallet", seed=DEVNET_GENESIS_SEED)
    # we create a new wallet using an existing seed,
    # such that our seed is used and not a new randomly generated seed

    # an example that shows how one can write logic around the TFChain client,
    # to do something with the transactions linked to a wallet

    addresses = set(w.addresses)
    text = ""
    for txn in w.transactions:
        # collect to addresses, and incoming/outgoing balance,
        # focussing only on the addresses of this wallet
        to_addresses = set()
        incoming_balance = 0
        for co in txn.coin_outputs:
            addr = str(co.condition.unlockhash)
            to_addresses.add(addr)
            if addr not in addresses:
                continue
            incoming_balance = incoming_balance + co.value

        # collect all from addresses, that are not ours,
        # as well as update the incoming balance
        from_addresses = set()
        outgoing_balance = 0
        for ci in txn.coin_inputs:
            pco = ci.parent_output
            addr = str(pco.condition.unlockhash)
            from_addresses.add(addr)
            if addr not in addresses:
                continue
            if incoming_balance > 0:
                if pco.value > incoming_balance:
                    outgoing_balance = outgoing_balance + (pco.value - incoming_balance)
                    incoming_balance = 0
                else:
                    incoming_balance -= pco.value
            else:
                outgoing_balance = outgoing_balance + pco.value

        if incoming_balance == 0 and outgoing_balance == 0:
            # nothing to print here
            continue

        if outgoing_balance > 0:
            # remove our addresses from address sets, as these are most likely refunds
            to_addresses -= addresses
            from_addresses -= addresses
        else:
            # only care about subset of addresses in to set
            to_addresses &= addresses

        # balance out the incoming and outgoing balance
        if incoming_balance > outgoing_balance:
            incoming_balance -= outgoing_balance
            outgoing_balance = 0
        else:
            outgoing_balance -= incoming_balance
            incoming_balance = 0

        text += j.core.text.strip(
            """
            {:<12} Tx: {} | {:^24} | {:^24} |
            \t> to: {}
            \t> from: {}

            """.format(
                ("unconfirmed" if txn.unconfirmed else txn.height),
                str(txn.id),
                "- " + outgoing_balance.str(with_unit=True) if outgoing_balance > 0 else "",
                "+ " + incoming_balance.str(with_unit=True) if incoming_balance > 0 else "",
                ", ".join(to_addresses) if len(to_addresses) > 0 else "this wallet",
                ", ".join(from_addresses) if len(from_addresses) > 0 else "this wallet",
            )
        )

    # print text
    print(text)

    # assert text is as expected
    expected_text = """unconfirmed  Tx: 573290763024ae0a5e981412598a3d41bc02f8da628fa1e1adfe07d98818c689 |                          |         + 10 TFT         |
\t> to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
\t> from: 01f0f397fd6b7b51b46ddd2ffda1e2240e639b19b47d27a4adc2bed78da0fc3d97c1fe7b972d1e

39997        Tx: 779cf13ecee7f45f032af92429056cd5976cb75ce968bab98e3e2fdf9a9b1034 |         - 1 TFT          |                          |
\t> to: this wallet
\t> from: this wallet

39995        Tx: b104308e683d4353a5a6b6cdfd4f6dfce39e241ff1218d6d6189bae89945034f |                          |        + 200 TFT         |
\t> to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
\t> from: 015827a0cabfb4be5531ecd2b42470a25cf9910a868b857029c2bdabdc05cad51e66d5dd899064

39994        Tx: 208d9f524e937176e50a7399fd3886f584290948983bbd0ed781f59cefc343a8 |         - 11 TFT         |                          |
\t> to: 01cb0aedd4098efd926195c2f7bba9323d919f99ecd95cf3626f0508f6be33f49bcae3dd62cca6
\t> from: this wallet

39991        Tx: e7785bacd0d12f93ab435cf3e29301f15b84be82ae8abbdaed1cfd034f4ed652 |                          |        + 100 TFT         |
\t> to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
\t> from: 01456d748fc44c753f63671cb384b8cb8a2aebb1d48b4e0be82c302d71c10f2448b2d8e3d164f6

39990        Tx: 544a204f0211e7642f508a7918c5d29334bd7d6892b2612e8acfb6dc36d39bd9 |                          |        + 400 TFT         |
\t> to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
\t> from: 01773a1dd123347e1030f0822cb8d22082fe3f9b0ea8563d4ac8e7abc377eba920c47efb2fd736

"""
    assert expected_text == text
