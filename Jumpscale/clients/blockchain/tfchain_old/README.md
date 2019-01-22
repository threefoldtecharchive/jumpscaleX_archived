# TfChain client for JumpScale

This is a thin client for the [Threefold Chain blockchain](https://github.com/threefoldfoundation/tfchain).
It works by communicating with the public explorer nodes. This client is leveraging the rivine
library, using the tfchain specific constants and supporting all tfchain features.

## Provided functionality

This is a thin client/wallet for tfchain blockchains.
This means that it communicates with (a) full node(s) but does not store the blockchain locally
and does not participate in the P2P protocol.

Please see [the Usage chapter](#chapter) for all functionalities.
Here is a summary of what this client provides:

- You can get transactions, coin outputs and wallet balances from the blockchain;
- You can create and recover TFChain (thin) wallets as to be able to manage funds and sign (multi-sig) transactions;
- Initiate/Participate in atomic swaps;
- Get, create and update 3Bots;
- Manage the mint definition and create coins;

## Dependencies

The client depends on the following python libraries to be able to function properly:
- ed25519
- pyblake2

If you installed jumpscale on your system in dev mode and without setting the full installation flag (JSFULL=1) then you will need to install these libs manually if you want to continue using the client, to do that simply execute the following commands:
```python
pip3 install ed25519
pip3 install pyblake2
```


## Usage

Start by creating a wallet:
```python3
wallet1  = j.clients.tfchain.create_wallet('wallet1')
```
Should you want to create a testnet/devnet walk you have to define the network value:
```python3
wallet1  = j.clients.tfchain.create_wallet('wallet1', network=j.clients.tfchain.network.TESTNET)
```
In case you already created a wallet, you can open it:
```python3
 wallet1 = j.clients.tfchain.open_wallet('wallet1')
 ```
Now that we have our wallet, we can get the addresses we already generated

```python3
wallet1.addresses
Out[10]: ['01ffffbd36a9d6c995a82c8e34d53cf9cbb13b2c55bed3fcc0020d9c0ff682cd8d45d2f41acbeb']
```

 Check the balance:

```python3
wallet1.current_balance
Out[11]:
Unlocked:

	0.0
```

And once we received some funds on one of the addresses: 

```python
wallet1.current_balance
Out[17]:
Unlocked:

	1000.0
```

### Sending funds

```python
# First create a new wallet and get the address we will send funds to
wallet2 = j.clients.tfchain.create_wallet('wallet2', network=j.clients.tfchain.network.TESTNET)
address = wallet2.addresses[0] # Take the first address from the list of addresses
# Send 20 tft which can be spend immediatly. The transaction is commited automatically
amount = 20
wallet1.send_money(amount, address)
# It probably takes some time before the transaction is added in a block.
# In the meantime, it can already be seen in the balance of wallet2 as "unconfirmed":
wallet2.current_balance
Out[5]:
Unlocked:

	0.0

Unconfirmed Balance:

	20.0

# Now send 20 tft which are timelocked until the 30th of october, 1 PM GMT
locktime = 1540904400 # unix timestamp
wallet1.send_money(amount, address, locktime=locktime)

# After the transactions have been confirmed, the wallet2 balance will show:
wallet2.current_balance
Out[9]: 
Unlocked:

	20.0

Locked:

	20.0 locked until 2018-10-30 13:00:00
```

Funds can also be sent to a multisig wallet. To do so, the `send_to_multisig` function
should be used. It is also possible to add optional data or a locking period here.


```python
# Create another wallet
wallet3 = j.clients.tfchain.create_wallet('wallet3', network=j.clients.tfchain.network.TESTNET)
# now create the list of addresses which can spend the funds
addresses = [wallet2.addresses[0], wallet3.addresses[0]]
# both addresses will need to sign
required_sigs = 2
# First send 10 tft, which can be spent immediately
amount = 10
wallet1.send_to_multisig(amount, addresses, required_sigs)
# Now send 5 more tft which are timelocked until the 30th of october, 1PM GMT
locktime = 1540904400
wallet1.send_to_multisig(amount, addresses, required_sigs, locktime=locktime)

# After the transactions have been confirmed, wallet2 and wallet3 will report the
# multisig outputs as part of their balance
wallet2.current_balance
Out[19]:
Unlocked:

	20.0

Locked:

	20.0 locked until 2018-10-30 13:00:00

Unlocked multisig outputs:

	Output id: 3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0

Locked multisig outputs:

	Output id: d5290bae4c86dc85d42dfa030cfcb2c8d17c88a3a4d43b4fb4e88da3c7e4895f
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0 locked until 2018-10-30 13:00:00
```

### Listing all incoming transactions of a wallet

Get all incoming transactions for a wallet from standard net:
```python
# parameter is a list of addresses to look up incoming transactions for
In [1]: wallet.list_incoming_transactions()
Out[1]:
[8566 - 24b7b608a16ecfbd54d95151e4b906d5d9d2e4a44e55e735fcc828f43109ec90 :
        01abf9030007f43ec5eaf75a63ef2e048bf6ee2b418e2c18695d0c0284d6ff40655251593da7b1 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 1000000000000,
 8051 - 68729244ac851233d9852abd1479b1f2b1b0870e0da45f4a1c03e0081a21d608 :
        019a87e477a68e0c4186873fe55c42334712b21ed399a15fb3598111fe1497a63ebbc2e79df718 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 42000000000
        data: Hello JumpScale, here is some money,
 8030 - c988654c81b4f35aa5be52315b9dda0fb79262625074b39db92ae3e20aa7367d :
        0106d1d7938e2f06a38dc4127a727548c3c312006f973145b9e891762a1883b9932780b1f0ce31 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 42000000000,
 8008 - 40f12e44ee07971ecb5256fd0a21fbc93c73b41a23cc59d5bbec3c48a4dcabf8 :
        01fb747135ce38b8fbd5c3019119dccd7645cc8c7e540399df1cef170a0dd55b832d22ab8b02eb -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 500000000000,
 5798 - 91ad9468f5a01e2033df3eb33e8e0ab4d08bdb051b506bb41cea38eb93022d45 :
        01f414c817c376064b1d34422bb4c434297a14a1970368fba67fcb25ab8e952799e2f9826640ea -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 1000000000000
        data: hello old arbitrary data,
 2861 - a88fd6ae555630ec18912e1a6f88ffa483792a8cc8c15aaef69d3f73e6543b7b :
        017cb06fa6f44828617b92603e95171044d9dc7c4966ffa0d8f6f97171558735974e7ecc623ff7 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 1000000000000,
 2829 - d873e0dd655952731567b821a829e1600839921c9a8a5b64f0cf4b17cb6e580e :
        01b88206a3300dea3dd5f6cd73568ac5797b078910c78cbce6a71fcd0837a3ea5a4f2ed9fc70a1 -> 01223b2a4e39a477ca57883b8a13820759728d6c83731223bbb65df8b508ab93f111f538224ccb : 200000000000
        data: is this still locked?,
 2827 - 74ccbe28cf008b38619c9779002105eadbe74f6b6b04eac069037509be6da8cf :
        0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a -> 01223b2a4e39a477ca57883b8a13820759728d6c83731223bbb65df8b508ab93f111f538224ccb : 200000000000
        data: another gift,
 2792 - cf7ffb6a3d6600212fa123cffd0707ec592a04b2333024a23c67f154bda7c2ea :
        019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c -> 01223b2a4e39a477ca57883b8a13820759728d6c83731223bbb65df8b508ab93f111f538224ccb : 200000000000
        data: a x-mas gift,
 179 - 7d72232a9f99174073ab8313d8a34b54b44c21bca8dcde36169a86f725ab8177 :
        0186cea43fa0d303a6379ae76dd79f014698956fb982751549e3ff3844b23fa9551c1725470f55 -> 01223b2a4e39a477ca57883b8a13820759728d6c83731223bbb65df8b508ab93f111f538224ccb : 1000000000000]
# you can also use the tx list (a list of simplified tx objects) directly as a python list of object:

In [2]: txs = _
# get the ID
In [3]: txs[0].id
Out[3]: '24b7b608a16ecfbd54d95151e4b906d5d9d2e4a44e55e735fcc828f43109ec90'
# get the senders
In [4]: txs[0].from_addresses
Out[4]: ['01abf9030007f43ec5eaf75a63ef2e048bf6ee2b418e2c18695d0c0284d6ff40655251593da7b1']
# get the address of your wallet the money was sent to
In [5]: txs[0].to_address
Out[5]: '012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282'
# get the amount of money that was sent to the address above
In [6]: txs[0].amount
Out[6]: 1000000000000 # == 1000 TFT
# get the data (decoded from the arbitrary data of the tx)
In [7]: txs[1].data
Out[7]: 'Hello JumpScale, here is some money'
# get the confirmation state of the transaction
In [8]: txs[1].confirmed
Out[8]: True
# get the identifier, senders and amount of all confirmed transactions, and which have the word 'gift' in tx
In [9]: [(tx.id, tx.from_addresses, tx.amount) for tx in txs if tx.confirmed and 'gift' in tx.data]
Out[9]:
[('74ccbe28cf008b38619c9779002105eadbe74f6b6b04eac069037509be6da8cf',
  ['0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a'],
  200000000000),
 ('cf7ffb6a3d6600212fa123cffd0707ec592a04b2333024a23c67f154bda7c2ea',
  ['019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c'],
  200000000000)]
# look up the transaction details of all confirmed 'gift' transactions
In [10]: [j.clients.tfchain.get_transaction(tx.id) for tx in txs if tx.confirmed and 'gift' in tx.data]
Out[10]:
[Transaction 74ccbe28cf008b38619c9779002105eadbe74f6b6b04eac069037509be6da8cf at block height 2827:
        - Coin Inputs:
                - (a96e259b4a2fceb51bae992c02ea5ad3ccc2f590c79231a4337cdc3eafc66200) 0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a : 99994995000000000
        - Coin Outputs:
                - 01223b2a4e39a477ca57883b8a13820759728d6c83731223bbb65df8b508ab93f111f538224ccb : 200000000000
                - 01b88206a3300dea3dd5f6cd73568ac5797b078910c78cbce6a71fcd0837a3ea5a4f2ed9fc70a1 : 99994794000000000
        - Data: another gift,
 Transaction cf7ffb6a3d6600212fa123cffd0707ec592a04b2333024a23c67f154bda7c2ea at block height 2792:
        - Coin Inputs:
                - (6652b1db7d9f38dadd07d1482441cc57f0315a24864a335aa5ca5b8fc93473ad) 019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c : 99995196000000000
        - Coin Outputs:
                - 01223b2a4e39a477ca57883b8a13820759728d6c83731223bbb65df8b508ab93f111f538224ccb : 200000000000
                - 0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a : 99994995000000000
        - Data: a x-mas gift]
```

### Using a multisig wallet

```python
# check the available inputs
wallet2.check_balance
Out[31]
Unlocked:

	20.0

Locked:

	20.0 locked until 2018-10-30 13:00:00

Unlocked multisig outputs:

	Output id: 3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0

Locked multisig outputs:

	Output id: d5290bae4c86dc85d42dfa030cfcb2c8d17c88a3a4d43b4fb4e88da3c7e4895f
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0 locked until 2018-10-30 13:00:00

# send funds to our original wallet, 1 tft 
address = wallet1.addresses[0]
amount = 1
# select the inputids we want to spend, multiple can be given
tx = wallet2.create_multisig_spending_transaction('3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c',
						  recipient=address, amount=amount)
wallet2.sign_transaction(tx, multisig=True)
# Print the tx json so it can be passed to the other signer
tx.json
Out[36]:
{'version': 1,
 'data': {'coininputs': [{'parentid': '3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c',
    'fulfillment': {'type': 3,
     'data': {'pairs': [{'publickey': 'ed25519:894d0138e5eef44dcea71ff5990ec3941cb1f9c10fda6935474b2054db8d45a3',
        'signature': '90ebde0eef55f18c8c7d6c48181a8f4dc727464a68fac425763acb77cefca401bb9eed93d5c21c9020c94e1d4a721814bcd33783caaf4a6b5fae1c4d427b9b0b'}]}}}],
  'coinoutputs': [{'value': '1000000000',
    'condition': {'type': 1,
     'data': {'unlockhash': '01eacabf383ece86d601f755a283f853c74d09c7a1e48d73af541e6267181c25a6a8fe98157a0e'}}},
   {'value': '3900000000',
    'condition': {'type': 4,
     'data': {'unlockhashes': ['017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921',
       '019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43'],
      'minimumsignaturecount': 2}}}],
  'minerfees': ['100000000']}}

# Other person loads the transaction so his wallet can sign
tx = j.clients.tfchain.create_transaction_from_json(...) # copy transaction json
# Sign and commit transaction
wallet3.sign_transaction(tx, multisig=True, commit=True)

# after the transaction is confirmed, the output is added to the balance of the wallet.
# likewise, timelocked tokens can be send like this
wallet2.current_balance
Out[45]: omitted for brevity

# lock until 30th october 1 PM GMT
locktime = 1540904400
tx = wallet2.create_multisig_spending_transaction('6c68623bdb50e3127606f845f7fa23f3849ff9752c8ec35517a8ccd677493368',
						  amount=amount, recipient=recipient, locktime=locktime)
wallet2.sign_transaction(tx, multisig=True)
# get transaction json and load it so the other person can sign
Out[48]: omitted for brevity

# sign and commit transaction
wallet3.sign_transaction(tx, multisig=True, commit=True)
```

## How to use AtomicSwap
The light wallet client supports the different atomicswap operations. It allows the user to:
- Initiate a new atomicswap contract
- Participate in an exsisting atomicswap contract
- Validate the information of an atomicswap contract
- Withdraw funds from atomicswap contract
- Refund funds from atomicswap contract

For more details about the atomicswap process, it is recommended to check the documentation at the Rivine offical repository here: https://github.com/rivine/rivine/blob/master/doc/atomicswap/atomicswap.md

Detailed documentation on how to use the atomicswap api of the JumpScale client can
be found in [the atomicswap documentation](../../../../docs/clients/blockchain/atomicswapwalkthrough.md).
### recovering a wallet 

A wallet is essentially a seed. Using this seed, (and only
this seed), the wallet can be fully recovered at a later date, including by someone else.
The seed must never be shared with anyone.
```python
seed = wallet.seed
newwallet =  j.clients.tfchain.create_wallet('default', seed=seed)
```

Instead of reusing the seed of an existing wallet, you can also generate a seed yourself and create wallets from that one.

```python
seed = j.clients.tfchain.generate_seed()
```

This will produce a 24 word mnemonic. A mnemonic is a human readable representation
of the seed, which is just a bunch of bytes. Some shorter mnemonics could be used,
however we always generate 32 byte seeds, which results in a 24 word mnemonics when encoded.

## Creating coins

Coin creation is handled by a "coin creation transaction" (transaction version 129).
In order to create coins, the `mint condition` needs to be fulfilled. The current
mint condition can be viewed using the `get_current_mint_condition` method on a wallet.

### Quick start

This section describes how to create a coin creation transaction as quickly as possible.
From start to finish, we perform the following steps:

- Create a condition, which will define how the output can be spent
- Create a new transaction, using this condition and a value
- Sign the transaction.

After this is done, the transaction likely needs to be signed by other people.

Our condition can be created by using the `create_singlesig_condition` or
`create_multisig_condition` methods on the tfchain client factory. The required
arguments are the unlockhash, and the list of unlockhashes + the minimum amount of
signatures required respectively. Both conditions can optionally be timelocked
by providing the `timelock` parameter.

Now that we have a condition, a transaction can be created using the
`create_coincreation_transaction` method. The previously created condition can be
given as an optional parameter (named `condition`). If the `value` parameter is also
set, an output will be created and added on the transaction. If wanted, a `description`
string can be given, which is set in the arbitrary data field.

Lastly, the transaction needs to be signed. If the wallet which does the signing does
not have any key capable of signing, nothing happens. Signing is done with the
wallet's `sign_transaction` method.

If the transaction then needs to be signed by others, it can be shared in its json
form. A json transaction can also be loaded.

Full example:

```python3
# Create the condition, we just want to send to an address here:
condition = j.clients.tfchain.create_singlesig_condition('01b4668a4b9a438f9143af8500f6566b6ca4cb3e3a3d98711deee3dee371765f58626809117a33')

# Create the transaction, sending 1 TFT ( = 1000000000 units)
# Also set an example description
tx = j.clients.tfchain.create_coincreation_transaction(condition=condition, value=1000000000, description='optional description')

# Try to add signatures
# Assume cl is a previously loaded client, see above
cl.wallet.sign_transaction(tx)

# Convert the transaction to json, so it can be shared to other signers
jsontx = tx.json

#Sign it through the a cosigner wallet 
tx = j.clients.tfchain.create_transaction_from_json(jsontx)
secondsignerwallet.sign_transaction(tx)

# the last signer commits it to the network as well
thirdsignerwallet.sign_transaction(tx, commit=True) 
```


### Full description

To get started, we first need to obtain such a transaction. A new one can be created,
after which we can add the coin outputs, or an existing one can be loaded from json.
To create a new (empty) coin creation transaction, the `create_coincreation_transaction()`
method on the tfchain client factory can be used:

```python
tx = j.clients.tfchain.create_coincreation_transaction()
```

Alternatively, to load one from json, the `create_transaction_from_json()` method
can be used:

```python
tx = j.clients.tfchain.create_transaction_from_json(_transaction json_)
```

Now that we have a transaction, we can add outputs. This functions just like regular
transactions: we can create either a single signature output, or a multisig output.
Both outputs can be timelocked as well. To send coins to a single sig address, the
`add_coin_output` method of the transaction can be used, with the amount to send
(expressed in base units), followed by the string representation of the destination address
as parameters, for instance:

```python
tx.add_coin_output(1000000000,
	'013a787bf6248c518aee3a040a14b0dd3a029bc8e9b19a1823faf5bcdde397f4201ad01aace4c9')
```

In the above snippet, a new output is added in which 1 TFT is send to the specified address.
Should this be required, the `locktime` parameter can be added, with a given block height
or unix timestamp untill which the output will be timelocked.

Likewise, a multisig output can be added by using the `add_multisig_output` method.
As with singe sig outputs, the first parameter is the amount to send, followed by the
addresses which can spend said multisig output, and then the mininimum amount of
signatures required to spend (similar to adding a multisig output to a regular
transaction). If required, the `locktime` parameter can once again be specified to
time lock the output.

It is important to note that outputs can only be added before any signature is added,
as with regular transaction.

Arbitrary data can be set on the transaction. This can be done with the `add_data` method.
Note that the maximum length of the arbitrary data can be at most 83 bytes, if there
is more data then the transaction will be rejected.

Likewise additional minerfees can be specified with the `add_minerfee` method. Since
we are creating coins, we are also creating the minerfee, so there is no need to add
any input for this.

Signing this transaction can be done using a tfchain wallet. Using the wallet's
`sign_transaction` method will greedily add a signature for any applicable key
loaded in said wallet, based on the current mint condition. Once your signature
is added, the transaction json can be distributed to the other coin creators, or if enough
signatures are added, the transaction can be published to the chain. If you want to
try and commit the transaction after signing it, the `commit` parameter can be set to
`True` when calling the signing method.

Example of signing a transaction:

```python
cl.wallet.sign_transaction(tx, commit=True)
```

## Stand-alone commands

### Get a Transaction

Get a transaction from standard net:
```python
# parameter is the id of the trnasaction
In [1]: j.clients.tfchain.get_transaction('c13091f07af3da1b85ffa94736aef9505ee0a718c592aad2175d2b93e54e2228')
Out[1]:
Transaction c13091f07af3da1b85ffa94736aef9505ee0a718c592aad2175d2b93e54e2228 at block height 2038:
        - Coin Inputs:
                - (fafede06beb869023e1962afc948d6c592bed1f4bb072fae8c5c228bbd76eab3) 01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c : 99995297000000000
        - Coin Outputs:
                - 0191dee035d25bf008817309d14e972651cc515b09dadde3155357682da120886f96133186a9f3 : 100000000000
                - 019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c : 99995196000000000
        - Data: test data

# you can also use the tx (a simplified object) directly as a python object:

In [2]: tx = _
# get the ID
In [3]: tx.id
Out[3]: 'c13091f07af3da1b85ffa94736aef9505ee0a718c592aad2175d2b93e54e2228'
# get the coin inputs
In [4]: tx.coin_inputs
Out[4]: [(fafede06beb869023e1962afc948d6c592bed1f4bb072fae8c5c228bbd76eab3) 01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c : 99995297000000000]
# get the coin output (don't index if no coin outputs exist in this tx)
In [5]: tx.coin_outputs[0]
Out[5]: 0191dee035d25bf008817309d14e972651cc515b09dadde3155357682da120886f96133186a9f3 : 10000000000
# get the data (decoded from the arbitrary data of the tx)
In [6]: tx.data
Out[6]: 'test data'
```

Getting a transaction from testnet can be done as follows:
```python
In [1]: j.clients.tfchain.get_transaction('f6acb26269e1426b7c729128ebf5c0afb1698f0b678588dcabc7644efbf7dae6', network=j.clients.tfchain.network.TESTNET)
Out[1]: Transaction f6acb26269e1426b7c729128ebf5c0afb1698f0b678588dcabc7644efbf7dae6 at block height 162791

# in this output we see no coin outputs or inputs, which is a possibility,
# either because the tx type doesn't support coin transfers, or because such transfers are optional.
```

You can also get a transaction from any devnet, by using the `explorers` optional parameter.

### Get all transactions for one or multiple wallet addresses

Get all transactions for a wallet address from standard net:
```python
# parameter is a list of addresses to look up transactions for
In [1]: j.clients.tfchain.list_incoming_transactions_for(['012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282'])
Out[1]:
[8566 - 24b7b608a16ecfbd54d95151e4b906d5d9d2e4a44e55e735fcc828f43109ec90 :
        01abf9030007f43ec5eaf75a63ef2e048bf6ee2b418e2c18695d0c0284d6ff40655251593da7b1 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 1000000000000,
 8051 - 68729244ac851233d9852abd1479b1f2b1b0870e0da45f4a1c03e0081a21d608 :
        019a87e477a68e0c4186873fe55c42334712b21ed399a15fb3598111fe1497a63ebbc2e79df718 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 42000000000
        data: Hello JumpScale, here is some money,
 8030 - c988654c81b4f35aa5be52315b9dda0fb79262625074b39db92ae3e20aa7367d :
        0106d1d7938e2f06a38dc4127a727548c3c312006f973145b9e891762a1883b9932780b1f0ce31 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 42000000000,
 8008 - 40f12e44ee07971ecb5256fd0a21fbc93c73b41a23cc59d5bbec3c48a4dcabf8 :
        01fb747135ce38b8fbd5c3019119dccd7645cc8c7e540399df1cef170a0dd55b832d22ab8b02eb -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 500000000000,
 5798 - 91ad9468f5a01e2033df3eb33e8e0ab4d08bdb051b506bb41cea38eb93022d45 :
        01f414c817c376064b1d34422bb4c434297a14a1970368fba67fcb25ab8e952799e2f9826640ea -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 1000000000000
        data: hello old arbitrary data,
 2861 - a88fd6ae555630ec18912e1a6f88ffa483792a8cc8c15aaef69d3f73e6543b7b :
        017cb06fa6f44828617b92603e95171044d9dc7c4966ffa0d8f6f97171558735974e7ecc623ff7 -> 012a564c6d9cac3c348a87d3b49a7e1612caa78e92702ea46d54b830cc27f6d0d855c08be0d282 : 1000000000000]

# again, each tx in that returned list can be used directly as a python object
```

Get all transactions for a wallet address from testnet can be done as follows:
```python
In [1]: j.clients.tfchain.list_incoming_transactions_for(['0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb'], network=j.clients.tfchain.network.TESTNET)
Out[1]:
# ...
 23999 - 2f04e9404b719f112372da0c2a8cfb29e7ebdaaf5854ba992f1a95b091f174b7 :
        012a3b0bb55334ffc91fb84e28b0e4099d62d54ad927c9b60dae4c902c2d7eca01f0852f79f1ee -> 0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb : 50000000000,
 23999 - 7e83fd9449515bf5551e64bed5786f017b3a4e6b7521a3af50b9173c43149a4b :
        012a3b0bb55334ffc91fb84e28b0e4099d62d54ad927c9b60dae4c902c2d7eca01f0852f79f1ee -> 0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb : 300000000000,
 23999 - ad5073a626036876caa90f4fcdd4d517c73cb265ad7f8f7a169d6c030270b64a :
        012a3b0bb55334ffc91fb84e28b0e4099d62d54ad927c9b60dae4c902c2d7eca01f0852f79f1ee -> 0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb : 100000000000,
 21890 - 6850541a9d8e8d8ed99d96d1d65a6ad4805b658d74366b3e2bf94dabc16efe59 :
        0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb -> 0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb : 55766179990000,
 21848 - ac473099dc00b9d88a93e6964c6effb298d5e53dc5731a70f77f6ea8f74df52e :
        0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb -> 0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb : 55889699990000,
 12235 - 9116e6d2a9a0ea53cd263963d333c4a2e70ba5fe6cbac080a94d105abe8c01c8 :
        0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2 -> 0198c17d14518655266986a55c6756dc3e79c0e7f49373f23ebaae7db9e67532ccea7043ebd9fb : 55899799990000]
```

You can also get a transaction from any devnet, by using the `explorers` optional parameter.

Note that if you want to look up all transactions linked to the addresses of your wallet,
you can use the `list_addresses` method of a wallet.

## 3Bot commands

Using the `threebot` property available in the `j.clients.tfchain` namespace
as `j.clients.tfchain.threebot` allows you to:

* [get the record of an existing 3Bot](#get-a-3bot-record);
* [register a new 3Bot by creating a 3bot record](#create-a-3bot-record);
* [update the record of an existing 3Bot](#update-a-3bot-record);
* [transfer one or multiple names between two existing 3Bots](#Transfer-names-between-3Bot-records).

Getting a 3Bot record requires only an identifier of a 3Bot.
The other methods require a wallet as well, as these methods require (3Bot)
transactions to be created and signed, and therefore require coin inputs to be funded and signed,
as well as the signature of the 3Bot owning the record(s) to be created/updated.

If you plan to do something other than getting the record of an existing 3Bot,
it is important that you understand how to use the wallet of `j.clients.tfchain` and what it is.
You can read more about the wallet earlier in this document in the [Usage](#Usage) chapter.

### Get a 3Bot record

In order to get the record of an existing 3Bot from the standard network
all you need to know is its (unique integral) identifier and the following method:
```python
In [1]: j.clients.tfchain.threebot.get_record(1) # get the record of the 3Bot with ID 1
Out [1]:
{'id': 1,
 'addresses': ['93.184.216.34', 'example.org', '0:0:0:0:0:ffff:5db8:d822'],
 'names': ['example.threebot'],
 'publickey': 'ed25519:dbcc428065c0bf15216884998400dc079b5ce3ec0ba4904aeaaec2ba19dfa1d6',
 'expiration': 1544344200}
```

Should you want to get a 3Bot record from _testnet_ you would instead do:
```python
In [1]: j.clients.tfchain.threebot.get_record(1, network_addresses=j.clients.tfchain.network.TESTNET.official_explorers())
Out [1]:
{'id': 1,
 'addresses': ['3bot.zaibon.be'],
 'names': ['tf3bot.zaibon'],
 'publickey': 'ed25519:72ebed8fd8b75fce87485ebe7184cf28b838d9e9ff55bbb23b8508f60fdede9e',
 'expiration': 1543650900}
```

You can also get a 3Bot record of any other private/dev network,
but this requires you to give the `network_addresses` manually.

### Create a 3Bot record

In order to register a new 3Bot, you need to create a (3Bot) record.
This can be done as follows:

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot identification using a public/private key pair of this wallet.
In[1]: wallet = j.clients.tfchain.open_wallet('mywallet')

# if no public key is given, a new key pair ill be generated within the given wallet,
# and the public key of that pair will be used. Should you want to use an existing key pair of that wallet,
# you can pass the public key to this function.
In[2]: j.clients.tfchain.threebot.create_record(wallet, names=['example.threebot'], \
    addresses=['93.184.216.34', 'example.org', '2001:db8:85a3::8a2e:370:7334'], months=24)
[Fri09 09:34] - RivineWallet.py   :200 :in.rivine.rivinewallet - INFO     - Current chain height is: 327
[Fri09 09:34] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction
[Fri09 09:34] - utils.py          :247 :lockchain.rivine.utils - INFO     - Transaction committed successfully
Out[2]: <clients.blockchain.rivine.types.transaction.TransactionV144 at 0x7fd27e262eb8>
```

The network is defined here by the given wallet. It can work with any version-up-to-date (tfchain) network,
as long as the wallet is configured for the desired network.

When you register a 3Bot you do not know your unique identifier yet,
as it is only assigned upon creation of the record in the blockchain.
Therefore you'll need to wait until your committed transaction has been confirmed,
such that you can get the unique identifier of the registered 3Bot by passing
the used public key (in string format) to the ["Get a 3Bot record"](#get-a-3bot-record) functionality.

### Update a 3Bot record

In order to update an existing 3Bot, you need to update its (3Bot) record.
This can be done as follows:

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot transaction (as the 3Bot owning the record to be updated)
# using the existing public/private key pair of this wallet.
In[1]: wallet = j.clients.tfchain.open_wallet('mywallet')

# you can do any or more of the following:
# add addresses, remove addresses, add names, remove names, add (activity) months
In[2]: j.clients.tfchain.threebot.update_record(wallet,
    names_to_add=['anewname.formy.threebot'], names_to_remove['example.threebot'], \
    addresses_to_add['example.com'])
[Fri09 09:47] - RivineWallet.py   :200 :in.rivine.rivinewallet - INFO     - Current chain height is: 392
[Fri09 09:47] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction
[Fri09 09:47] - utils.py          :247 :lockchain.rivine.utils - INFO     - Transaction committed successfully
Out[2]: <clients.blockchain.rivine.types.transaction.TransactionV145 at 0x7fd27e2abc50>
```

The network is defined here by the given wallet. It can work with any version-up-to-date (tfchain) network,
as long as the wallet is configured for the desired network.

### Transfer names between 3Bot records

Transferring names involves two 3Bots, meaning two different 3Bots have to sign,
and thus an additional step is required. The exception is when the used wallet
owns the key pairs of both 3Bot parties, in which case the transaction is committed immediately.
In all other cases the Tx will have to be still signed by the other 3Bot.

In case you own a name, and want to give it to another 3Bot,
you'll need to use this feature, as to not risk that someone else registers the name
in the time window between you removing it from bot A, and bot B claiming it
as part of a record update. Instead by using this feature,
the name gets removed from the first bot, and added to the second bot,
as part of the same transaction, making it completely secure.

Transferring names between two 3Bot can be done as follows:

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot transaction (as the 3Bot owning the record to be updated)
# using the existing public/private key pair of this wallet.
In[1]: wallet_b = j.clients.tfchain.open_wallet('wallet-b')

In[2]: sender_bot_id = 1

In[3]: receiver_bot_id = 2

# you can do any or more of the following:
# add addresses, remove addresses, add names, remove names, add (activity) months
In[4]: tx = j.clients.tfchain.threebot.create_name_transfer(wallet_a, \
    sender_bot_id, receiver_bot_id, ['example.threebot'])
[Fri09 08:31] - RivineWallet.py   :200 :in.rivine.rivinewallet - INFO     - Current chain height is: 20
[Fri09 08:31] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction

# pass the tx as json to the other 3Bot
In[5]: tx.json # using any side-channel or software as you choose
```

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot transaction (as the 3Bot owning the record to be updated)
# using the existing public/private key pair of this wallet.
In[1]: wallet_a = j.clients.tfchain.open_wallet('wallet-a')

# create a transaction object from the transaction json
In[2]: txn = j.clients.rivine.create_transaction_from_json(txn_json)

# sign and commit the tx, as you've seen before in other chapter of this document
In[3]: wallet_a.sign_transaction(transaction=txn, commit=True)
[Fri09 08:32] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction
[Fri09 08:32] - utils.py          :247 :lockchain.rivine.utils - INFO     - Transaction committed successfully
```

The network is defined here by the given wallets. It can work with any version-up-to-date (tfchain) network,
as long as the wallets are configured for the (_same_) desired network.

## minter definition transaction

By using transaction version 128, a new minter condition can be specified. The minter
condition defines who can create coins. Redefining the minter definition is largerly
the same as creating new coins, so only the differences are covered here:

Creating a new minter definition transaction is done with the `create_minterdefinition_transaction`
method of the tfchain client factory.

There are no coin outputs, only a single condition, which becomes the new minter definition.
This means that, in order to create coins, this condition will need to be fulfilled after
this transaction has been published and accepted on the chain. The new mint condition
can be either a single sig or multisig condition (in practice this should always be a
multisig). The condition can be added by using the `set_singlesig_mint_condition`
and `set_multisig_mint_condition` methods of the transaction.

These are the only differences. The transaction can be signed exactly the same like
a regular coin creation transaction.

