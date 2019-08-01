from Jumpscale import j

import pytest

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="erc20_coins_send")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mydevclient", network_type="DEV")
    # or simply `c = j.tfchain.clients.mydevclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    explorer_client.hash_add(
        "014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a",
        '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"066c03b5cf6db18edd6013591ae6292e8a04f1cc18fc6f0a0f3946d40bb087b3","height":3628,"parent":"761af2728b6f07bbccf4ddaf330c0bb1465246f6fe25fbfb9989129b69fbd899","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"670045cf43421b21577c27613569b65ba0cec613ae5437ee15dc0eea95241cbc","fulfillment":{"type":1,"data":{"publickey":"ed25519:bdea9aff09bcdc66529f6e2ef1bb763a3bab83ce542e8673d97aeaed0581ad97","signature":"e5a47b166eb6724ca7a72b5ddaeff287ebdde09751ed10e8850d320744afc5f45e59aa66e2cc4dc45ff593a0eea696c4e780b81636a1ce748c7149a9ee0ba807"}}},{"parentid":"1d686b8dfe44dfbfea55f327a52d9701a52938cb2c829f709dfb8059bc0e5f87","fulfillment":{"type":1,"data":{"publickey":"ed25519:64ae81a176302ea9ea47ec673f105da7a25e52bdf0cbb5b63d49fc2c69ed2eaa","signature":"5ce7a10373214d269837e9c176ec806469d2b80f200f9ee961c63553b6ee200f88958293a571889f26b2b52664f3c9ff2441eaf8ed61830b51d640003b06fb00"}}}],"coinoutputs":[{"value":"501000000000","condition":{"type":1,"data":{"unlockhash":"0186cea43fa0d303a6379ae76dd79f014698956fb982751549e3ff3844b23fa9551c1725470f55"}}},{"value":"198000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"200000000000","condition":{"type":1,"data":{"unlockhash":"018f5a43327fb865843808ddf549f1b1c06376e07195423778751056be626841f42dcf25a593fd"}},"unlockhash":"018f5a43327fb865843808ddf549f1b1c06376e07195423778751056be626841f42dcf25a593fd"},{"value":"500000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}},"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}],"coinoutputids":["4b43906584620e8a13d98a917d424fb154dd1222a72b886a887c416b2a9120f5","19d4e81d057b4c93a7763f3dfe878f6a37d6111a3808b93afff4b369de0f5376"],"coinoutputunlockhashes":["0186cea43fa0d303a6379ae76dd79f014698956fb982751549e3ff3844b23fa9551c1725470f55","014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"0b5d7509e467b943af12db2d73ddb78a5ec8cfdf64c3c6ecacb2de4af68bdc4d","height":33,"parent":"40e281daee6f113b788d64b8247381c36fe4885233a7475c9be2cce852e1696e","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"a3c8f44d64c0636018a929d2caeec09fb9698bfdcbfa3a8225585a51e09ee563","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"e5b69be3b385f0a33f7978e0d6af30cf37c975bbb99d0f3d06f199cd579d3e6854f6cb398c88082e438c89d11d04de0e7d3b2876e250d4ba8ae457f88547f605"}}}],"coinoutputs":[{"value":"1000000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99998999000000000","condition":{"type":1,"data":{"unlockhash":"01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"100000000000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"coinoutputids":["75f297550acfa48490c21490f82c3c308326c16f950e17ef3a286486065a51b8","6d157a1eb23cadde122192869bc51e2a0fe44a2d8aba898cbdda8b7218a0f8cb"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"1b144b89c4b65cc67416e27286e802c50f78bc7326b4b0e5f6f967f99cc39419","height":200,"parent":"68e3886c9a4c59dea8c7a0eb138ede0e83716b995fd8ebfa5dfc766bfb349565","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"6d157a1eb23cadde122192869bc51e2a0fe44a2d8aba898cbdda8b7218a0f8cb","fulfillment":{"type":1,"data":{"publickey":"ed25519:00bde9571b30e1742c41fcca8c730183402d967df5b17b5f4ced22c677806614","signature":"05c72055d4cca6d8620fd7453c89ac8deaf92c38e366604dc6405cb097321b74e2e5f7ece15b440f4af5721b8aa6ea1f57f4fce44d2a2c6c0fb7a1e068a0480d"}}}],"coinoutputs":[{"value":"500000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99998498000000000","condition":{"type":1,"data":{"unlockhash":"0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99998999000000000","condition":{"type":1,"data":{"unlockhash":"01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"}},"unlockhash":"01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"}],"coinoutputids":["1d686b8dfe44dfbfea55f327a52d9701a52938cb2c829f709dfb8059bc0e5f87","e27ed8bbe45177fafdfd7d21394ff483b8bde24f551dd927a046a0b7c37ec228"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"5ab2604c7d54dd9ea39d829724e46deb8bbf2889d8627a3bb3b57907c6f4dff4","height":1433,"parent":"6b9fdad35096c5a84dcdb6e3e9ec2a8c7562f567e05b1207a7f9330ed51582bb","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"e27ed8bbe45177fafdfd7d21394ff483b8bde24f551dd927a046a0b7c37ec228","fulfillment":{"type":1,"data":{"publickey":"ed25519:41e84f3b0f6a06dd7e45ded4d0e227869725355b73906b82d9e3ffc0b6b01416","signature":"47a4d1a6aeb7403ea5c2cbcc26f84bb1964aadcb8765696db4a623694991f794663b860898db53401dd4324477c43f9fff177b74909201a03e131c2cd885cc0d"}}}],"coinoutputs":[{"value":"500000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99997997000000000","condition":{"type":1,"data":{"unlockhash":"0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99998498000000000","condition":{"type":1,"data":{"unlockhash":"0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"}},"unlockhash":"0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"}],"coinoutputids":["b90422bad2dffde79f0a46bd0a41055cf7974b080e115d76f69891ca31d31f11","f386312779f382f16fa836038b3d25536b928ba88ae1afa1f8c0e8dc25c0ba16"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"81d81b413fc8af3e528478e639d5a6e999e5e96611593cd2458b4d2d7abc3880","height":1433,"parent":"6b9fdad35096c5a84dcdb6e3e9ec2a8c7562f567e05b1207a7f9330ed51582bb","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"f386312779f382f16fa836038b3d25536b928ba88ae1afa1f8c0e8dc25c0ba16","fulfillment":{"type":1,"data":{"publickey":"ed25519:4e42a2fcfc0963d6fa7bb718fd088d9b6544331e8562d2743e730cdfbedeb55a","signature":"4abae694cf6a6408eca6f034ea2ec6930b9a73303c3e70d3444cf36a9966b0c4cc1b65168c23640affb5bdeae539ea583d42da52c58d21f59b71c288b3faef0e"}}}],"coinoutputs":[{"value":"2000000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99995996000000000","condition":{"type":1,"data":{"unlockhash":"0173f82c3ee74286c33fee8d883a7e9e759c6230b9e4e956ef233d7202bde69da45054270eef99"}}}],"minerfees":["1000000000"],"arbitrarydata":"Zm9vYmFy"}},"coininputoutputs":[{"value":"99997997000000000","condition":{"type":1,"data":{"unlockhash":"0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"}},"unlockhash":"0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"}],"coinoutputids":["d1f74e90eba8095e78f08a6284c7b76d4cda86b06ac742062d6e0e02dc4607eb","1edccdb04100ffd05d97431b6798533fa57dc7ed1ea58c75f0f445fb64442d6e"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","0173f82c3ee74286c33fee8d883a7e9e759c6230b9e4e956ef233d7202bde69da45054270eef99"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":["039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a"],"unconfirmed":false}',
    )
    explorer_client.hash_add(
        "018f5a43327fb865843808ddf549f1b1c06376e07195423778751056be626841f42dcf25a593fd",
        '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"066c03b5cf6db18edd6013591ae6292e8a04f1cc18fc6f0a0f3946d40bb087b3","height":3628,"parent":"761af2728b6f07bbccf4ddaf330c0bb1465246f6fe25fbfb9989129b69fbd899","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"670045cf43421b21577c27613569b65ba0cec613ae5437ee15dc0eea95241cbc","fulfillment":{"type":1,"data":{"publickey":"ed25519:bdea9aff09bcdc66529f6e2ef1bb763a3bab83ce542e8673d97aeaed0581ad97","signature":"e5a47b166eb6724ca7a72b5ddaeff287ebdde09751ed10e8850d320744afc5f45e59aa66e2cc4dc45ff593a0eea696c4e780b81636a1ce748c7149a9ee0ba807"}}},{"parentid":"1d686b8dfe44dfbfea55f327a52d9701a52938cb2c829f709dfb8059bc0e5f87","fulfillment":{"type":1,"data":{"publickey":"ed25519:64ae81a176302ea9ea47ec673f105da7a25e52bdf0cbb5b63d49fc2c69ed2eaa","signature":"5ce7a10373214d269837e9c176ec806469d2b80f200f9ee961c63553b6ee200f88958293a571889f26b2b52664f3c9ff2441eaf8ed61830b51d640003b06fb00"}}}],"coinoutputs":[{"value":"501000000000","condition":{"type":1,"data":{"unlockhash":"0186cea43fa0d303a6379ae76dd79f014698956fb982751549e3ff3844b23fa9551c1725470f55"}}},{"value":"198000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"200000000000","condition":{"type":1,"data":{"unlockhash":"018f5a43327fb865843808ddf549f1b1c06376e07195423778751056be626841f42dcf25a593fd"}},"unlockhash":"018f5a43327fb865843808ddf549f1b1c06376e07195423778751056be626841f42dcf25a593fd"},{"value":"500000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}},"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}],"coinoutputids":["4b43906584620e8a13d98a917d424fb154dd1222a72b886a887c416b2a9120f5","19d4e81d057b4c93a7763f3dfe878f6a37d6111a3808b93afff4b369de0f5376"],"coinoutputunlockhashes":["0186cea43fa0d303a6379ae76dd79f014698956fb982751549e3ff3844b23fa9551c1725470f55","014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"d0d290dccddaf086708e4163eacd420bfbaa7acb77deea97c6a8792a139f6e7e","height":3583,"parent":"ca746d80740ff45f6e7f0d6c8b6278b35b1040b4e21baaf41bd03cd3a7a176be","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"1edccdb04100ffd05d97431b6798533fa57dc7ed1ea58c75f0f445fb64442d6e","fulfillment":{"type":1,"data":{"publickey":"ed25519:7469d51063cdb690cc8025db7d28faadc71ff69f7c372779bf3a1e801a923e02","signature":"6f38467bb4ca23900e424d5ac2066a09b61fe9d9ae84a4231755063f591d04711f0a5ab11b60b42c2c32a8e7f73fc1cc1cb0073b036bc417ed504a8ef5f25402"}}}],"coinoutputs":[{"value":"200000000000","condition":{"type":1,"data":{"unlockhash":"018f5a43327fb865843808ddf549f1b1c06376e07195423778751056be626841f42dcf25a593fd"}}},{"value":"99995795000000000","condition":{"type":1,"data":{"unlockhash":"01f706dcbb9f0cb1e97d891ada3a133f68612ebff948c5bbae7851108a65dab7782907eecd86be"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99995996000000000","condition":{"type":1,"data":{"unlockhash":"0173f82c3ee74286c33fee8d883a7e9e759c6230b9e4e956ef233d7202bde69da45054270eef99"}},"unlockhash":"0173f82c3ee74286c33fee8d883a7e9e759c6230b9e4e956ef233d7202bde69da45054270eef99"}],"coinoutputids":["670045cf43421b21577c27613569b65ba0cec613ae5437ee15dc0eea95241cbc","984555e190d58dc752aad81b0a6cf6194fa5bf89b8614efcd9604d138a8953bc"],"coinoutputunlockhashes":["018f5a43327fb865843808ddf549f1b1c06376e07195423778751056be626841f42dcf25a593fd","01f706dcbb9f0cb1e97d891ada3a133f68612ebff948c5bbae7851108a65dab7782907eecd86be"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}',
    )
    explorer_client.chain_info = '{"blockid":"552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e","difficulty":"27801","estimatedactivebs":"59","height":3644,"maturitytimestamp":1549012510,"target":[0,2,91,116,78,165,130,72,116,162,127,4,125,67,108,16,140,247,132,198,107,159,114,177,44,25,18,162,38,157,169,245],"totalcoins":"0","arbitrarydatatotalsize":6,"minerpayoutcount":3650,"transactioncount":3652,"coininputcount":12,"coinoutputcount":15,"blockstakeinputcount":3644,"blockstakeoutputcount":3645,"minerfeecount":7,"arbitrarydatacount":1}'
    explorer_client.hash_add(
        "552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e",
        '{"hashtype":"blockid","block":{"minerpayoutids":["468db689f752414702ef3a5aa06238f03a4539434a61624b3b8a0fb5dc38a211"],"transactions":[{"id":"2396f8e57bbb9b22bd1d749d5de3fd532ea6886e9660a556a13571d701d83e27","height":3644,"parent":"552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"ff5a002ec356b7cb24fbee9f076f239fb8c72d5a8a448cee92ee6d29a87aef52","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"7bec94dfb87640726c6a14de2110599db0f81cf9fa456249e7bf79b0c74b79517edde25c4ee87f181880af44fe6ee054ff20b74eda2144fe07fa5bfb9d884208"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["f683e7319659c61f54e93546bc41b57c5bffe79de26c06ec7371034465804c81"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"47db4274551b0372564f8d1ab89c596428f00e460c0b416327e53983c8765198","timestamp":1549012665,"pobsindexes":{"BlockHeight":3643,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"ff5a002ec356b7cb24fbee9f076f239fb8c72d5a8a448cee92ee6d29a87aef52","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"7bec94dfb87640726c6a14de2110599db0f81cf9fa456249e7bf79b0c74b79517edde25c4ee87f181880af44fe6ee054ff20b74eda2144fe07fa5bfb9d884208"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e","difficulty":"27801","estimatedactivebs":"59","height":3644,"maturitytimestamp":1549012510,"target":[0,2,91,116,78,165,130,72,116,162,127,4,125,67,108,16,140,247,132,198,107,159,114,177,44,25,18,162,38,157,169,245],"totalcoins":"0","arbitrarydatatotalsize":6,"minerpayoutcount":3650,"transactioncount":3652,"coininputcount":12,"coinoutputcount":15,"blockstakeinputcount":3644,"blockstakeoutputcount":3645,"minerfeecount":7,"arbitrarydatacount":1},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
    )
    explorer_client.hash_add(
        "039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a",
        '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"4c70a0406f36cf354edf87642df3f34568fd0a89c052a81d11cc6e4f8fbf685e","height":45,"parent":"f7b78b17d581ff9e58ffbcce1701d4dcadb0781590ca68e839def0dc98b0360a","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"7d4a100fc3bc08b2bdd1284c17260dd2bd6b55fd6c1429dbbd683bf362d92b50","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"c34b8ca1ab08930bc68d61026af504d62d8a8bbda9b79ae01a387560fba22d39b12021e16566732b742ea686f997b3c19c807523797cdc0d74a4d25123691004"}}},{"parentid":"83503f9cea00d562e0460eace93159a4c4dd00df4703c96947e81885b46da04c","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"f6eea681a259baf14433ac55b4293b22ca2056810ee8fed2129039224d14558f54ca58c6d96e9885cb20ecdf7e64ba81d1a83c6e9a42bf9464287fa6359d360c"}}},{"parentid":"578aa43de72b42b4f4547c5ddc7f61736b1cac206e1789bc89fcd9333cf3d1f3","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"a0521d14dfe4a0c9b8b57ed361d738b48b6a8346097246effe0b4ee67b6fecbc3a90e4671ddc0b164f6c2839df249bb5998f10216a4a674ba8d24b8ad6bdf808"}}},{"parentid":"5a1454762e6895431e1b9e4e435e4d0ad60a3881843ac46b88e220771055ca87","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"900e7868780e67bcb68af3ec6976e84289850d0db59210d4689b1c0e2deb3164b9e93eb9ee5a38850f2319463b0845163e1eee443d7b645c59485c2aa0837707"}}},{"parentid":"c04ebebe17a1759457eecaf4d5d33f5ddbe8d154b0be1606f05bc8fd02ab9cd4","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"e992b1cd3347b5362e820166d5929de7c682130c7143fc4c9ff3156f5d44110753687697a0154a2043290b3f022e2537f3e3a6807caf9150f8c255d74e386d0a"}}}],"coinoutputs":[{"value":"42000000000","condition":{"type":4,"data":{"unlockhashes":["01ffd7c884aa869056bfb832d957bb71a0005fee13c19046cebec84b3a5047ee8829eab070374b","014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"],"minimumsignaturecount":1}}},{"value":"7000000000","condition":{"type":1,"data":{"unlockhash":"01972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff03e45f1470df82"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"coinoutputids":["29152fe03a2c8782fcbd670579686088c52be83fa3870f5f0788073d97fb5fb2","0fc9b16bb180cd8f8a7144d65e6c8fca66994a4ccaee42e324289d4039ab2841"],"coinoutputunlockhashes":["039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a","01972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff03e45f1470df82"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}',
    )
    c._explorer_get = explorer_client.explorer_get
    c._explorer_post = explorer_client.explorer_post

    # the devnet genesis seed is the seed of the wallet,
    # which receives all block stakes and coins in the genesis block of the tfchain devnet
    DEVNET_GENESIS_SEED = "image orchard airport business cost work mountain obscure flee alpha alert salmon damage engage trumpet route marble subway immune short tide young cycle attract"

    # create a new devnet wallet
    w = c.wallets.new("mywallet", seed=DEVNET_GENESIS_SEED)
    # we create a new wallet using an existing seed,
    # such that our seed is used and not a new randomly generated seed

    # a tfchain (JS) wallet uses the underlying tfchain client for all its
    # interaction with the tfchain network
    assert w.network_type == "DEV"

    # getting the balance of a wallet is as easy as getting the 'balance' property
    balance = w.balance

    # the available and locked tokens can be easily checked
    assert str(balance.available) == "3698"
    assert str(balance.locked) == "0"

    # sending coins to an ERC20 address (converting TFT to ERC20 Tokens),
    # is as simple as sending regular TFT tokens:
    result = w.coins_send(
        recipient="0x828de486adc50aa52dab52a2ec284bcac75be211",  # the ERC20 address to receive the amount, converted from TFT
        amount="200.5 TFT",  # the amount of TFT to convert to ERC20 Tokens
    )  # no data or lock can be attached
    assert result.submitted  # it is expected the transaction is submitted

    # even though this method is overloaded to also accept TFT to ERC20 transaction,
    # you do need to be aware that it is not allowed to specify a lock or data,
    # as these are not allowed for ERC20 Convert Transactions,
    # a ValueError will be raised if you do try to use one or both of these properties
    with pytest.raises(ValueError):
        result = w.coins_send(recipient="0x828de486adc50aa52dab52a2ec284bcac75be211", amount="200.5 TFT", lock="+5d")
    with pytest.raises(ValueError):
        result = w.coins_send(
            recipient="0x828de486adc50aa52dab52a2ec284bcac75be211", amount="200.5 TFT", data="some data"
        )
    with pytest.raises(ValueError):
        result = w.coins_send(
            recipient="0x828de486adc50aa52dab52a2ec284bcac75be211", amount="200.5 TFT", lock=100, data="some data"
        )

    expected_transaction = {
        "version": 208,
        "data": {
            "address": "0x828de486adc50aa52dab52a2ec284bcac75be211",
            "value": "200500000000",
            "coininputs": [
                {
                    "parentid": "b90422bad2dffde79f0a46bd0a41055cf7974b080e115d76f69891ca31d31f11",
                    "fulfillment": {
                        "type": 1,
                        "data": {
                            "publickey": "ed25519:64ae81a176302ea9ea47ec673f105da7a25e52bdf0cbb5b63d49fc2c69ed2eaa",
                            "signature": "34d8a289741694462d45e01c5f27b351ed42f5b5d5b90e0a410e509c0b6a670d3a2078a3548eb324f62e5f81ffd51ce580596ca5bbeca99419b41a171cd75102",
                        },
                    },
                }
            ],
            "txfee": "1000000000",
            "refundcoinoutput": {
                "value": "298500000000",
                "condition": {
                    "type": 1,
                    "data": {
                        "unlockhash": "014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"
                    },
                },
            },
        },
    }
    # ensure our transaction is as expected
    assert result.transaction.json() == expected_transaction
    # ensure the transaction is posted and as expected there as well
    txn = explorer_client.posted_transaction_get(result.transaction.id)
    assert txn.json() == expected_transaction

    # the refund coin output can be accessed as a regular coin output
    assert len(txn.coin_outputs) == 1
    assert (
        txn.coin_outputs[0].condition.unlockhash
        == "014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"
    )
    assert txn.coin_outputs[0].value == "298.5 TFT"

    # the above command is actually an alias for the following erc20-specific command:
    result = w.erc20.coins_send(
        address="0x828de486adc50aa52dab52a2ec284bcac75be211",  # the ERC20 address to receive the amount, converted from TFT
        amount="200.5 TFT",  # the amount of TFT to convert to ERC20 Tokens
    )  # no data or lock can be attached
    assert result.submitted  # it is expected the transaction is submitted

    expected_transaction = {
        "version": 208,
        "data": {
            "address": "0x828de486adc50aa52dab52a2ec284bcac75be211",
            "value": "200500000000",
            "coininputs": [
                {
                    "parentid": "b90422bad2dffde79f0a46bd0a41055cf7974b080e115d76f69891ca31d31f11",
                    "fulfillment": {
                        "type": 1,
                        "data": {
                            "publickey": "ed25519:64ae81a176302ea9ea47ec673f105da7a25e52bdf0cbb5b63d49fc2c69ed2eaa",
                            "signature": "34d8a289741694462d45e01c5f27b351ed42f5b5d5b90e0a410e509c0b6a670d3a2078a3548eb324f62e5f81ffd51ce580596ca5bbeca99419b41a171cd75102",
                        },
                    },
                }
            ],
            "txfee": "1000000000",
            "refundcoinoutput": {
                "value": "298500000000",
                "condition": {
                    "type": 1,
                    "data": {
                        "unlockhash": "014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"
                    },
                },
            },
        },
    }
    # ensure our transaction is as expected
    assert result.transaction.json() == expected_transaction
    # ensure the transaction is posted and as expected there as well
    txn = explorer_client.posted_transaction_get(result.transaction.id)
    assert txn.json() == expected_transaction
