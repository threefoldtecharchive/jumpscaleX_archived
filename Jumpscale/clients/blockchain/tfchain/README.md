# TFChain JSX Client

See [./tests](./tests) directory for documented tests that explain a lot of this client's functionality.

## TLDR

All methods have docstrings, _read_ them.

## Summary

1. [Client](#client): how to create, save and use a TFChain client:
    1. [Create a Wallet](#create-a-wallet): how to create a TFChain wallet (attached to a TFChain client)
    2. [Unlockhash Get](#unlockhash-get): how to get information for addresses that do not belong to you
2. [Wallet](#wallet): how to save and use a TFChain wallet:
    1. [Get address info](#get-address-info): Get (the) address(es) linked to this wallet
    1. [Check your balance](#check-your-balance)
    2. [Send Coins](#send-coins)
3. [Multi-Signature-Wallet](#multi-signature-wallet): learn how to view and manage Multi-Signature Wallets from your TFChain wallet
4. [3Bot Records](#3bot-records): explains how to get, create new and manage existing 3Bot records
5. [Atomic Swap Contacts](#atomic-swap-contracts): explains how to work with cross-chain atomic swaps, from a TFChain perspective, using your TFChain wallet
6. [ERC20 Interaction](#erc20-interaction): send coins to an ERC20 address and register a TFT address as ERC20 Withdrawel addresses
7. [Coin Minting](#coin-minting): a subsection devoted to the coin minters of the network
8. [Examples](#examples): examples that show how to use the TFChain client as a library
9. [Capacity reservation](#capacity-reservation): reserve and deploy some workloads on the TF grid

### Client

Create a client as follows:

```python
c = j.clients.tfchain.my_client
```

or

```python
c = j.clients.tfchain.new('my_client')
# available as `j.clients.tfchain.my_client` from now on
```

or

```python
# valid types: STD, TEST and DEV, by default it is set to STD
c = j.clients.tfchain.new('my_client', network_type='TEST')
# available as `j.clients.tfchain.my_client` from now on
```

The client is a JS config instance that can be saved.

#### Create a Wallet

```python
w = c.wallets.my_wallet # a new seed will be generated
```

or:

```python
w = c.wallets.my_wallet.new("my_wallet") # a new seed will be generated
# available as `c.wallets.my_wallet` from now on
```

or:

```python
# wallet "recovery"
w = c.wallets.my_wallet.new("my_wallet", seed="carbon boss inject cover mountain fetch fiber fit tornado cloth wing dinosaur proof joy intact fabric thumb rebel borrow poet chair network expire else")
# available as `c.wallets.my_wallet` from now on
```

The wallet is a JS config instance that can be saved.

#### Other actions

Should you desire you can use the client
to get a block by height or ID (`c.block_get`), as well
as transactions by ID (`c.transaction_get`) and more.

Create a TFChain client in Kosmos to explore all its options or check out
the [./tests](./tests) directory for documented tests.

##### Unlockhash Get

One can get all transactions and if applicable linked Multi-Signature Wallet addressed linked to a given Wallet Address
by using the `c.unlockhash_get` method:

```python
# the only parameter of `unlockhash_get` is as flexible as the recipient of the `w.coins_send` method (see for more info further in this doc)
result = c.unlockhash_get('01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214')
result.unlockhash # the unlockhash defined (or generated using the defined value)
result.transactions # a list of all transactions somehow linked to the given unlockhash (value)
result.multisig_addresses # a list of all Multi-Signature Wallet addresses linked to this wallet, only if applicable
```

From the result of `c.unlockhash_get` method one can compute the balance as follows:

```python
balance = result.balance() # human-readable printed in shell by default
# it does return however a very useful object
# should you want to inspect individual (coin) outputs
```

> Did you know that multiple balances can be merged?
> ```python
> balance = balance.balance_add(other_balance)
> ```

Finally, should it be desired, one can drain all available outputs of a balance object as follows:

```python
txns = balance.drain(recipient='01e64ddf014e030e612e7ad2d7f5297f7e74e31100bdf4d194ff23754b622e5f0083d4bedcc18d')
# a list of created transactions, empty if no outputs were available,
# each transaction will be filled as much as possible (taking into account the max coin inputs per transactions accepteable).
```

If unconfirmed avalable coin outputs should be drained with the confirmed coin outputs one can do so as follows:

```python
txns = balance.drain(recipient='01e64ddf014e030e612e7ad2d7f5297f7e74e31100bdf4d194ff23754b622e5f0083d4bedcc18d', unconfirmed=True)
# see the docs for the full info, but FYI: you can also attach optional data as well as an optional lock
```

Draining can for example be useful if you want to stop using a certain wallet and want to make
sure all outputs can be transferred are immediately transferred to your new wallet (`w.balance.drain`).
It can also be used to drain all available outputs of the Free-For-All Wallet (`c.unlockhash_get(None).balance()`).

### Wallet

#### Get address info:

```python
w.address            # the primary address (string)
w.addresses          # all individual addresses (list of strings, at least 1 element)
w.addresses_multisig # returns all known multisig addresses (list of strings, can be empty)
```

#### Check your balance:

```python
w.balance # human-readable printed in shell by default
# it does return however a very useful object
# should you want to inspect individual (coin) outputs
```

#### Send coins

To a single person:

```python
w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount=100)
# equivalent amount specifications:
#   - as a string: '100 tft', '100.0', '100.0 TFT', '100'
#   - as a Decimal: Decimal('100')
```

With a timelock:

```python
w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount='100 TFT',
    lock='01/02/2019 23:44:39') # can also be defined as an epoch timestamp: 1549064679
```

A timelock can also be defined by specifying a duration relative to now:

```python
w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount='200.30',
    lock='+7d') # you can use any of these 4 units, each 1 time: d (day), h (hours), m (minutes), s (seconds)
    # other, more full example: '+ 7d12h30m42s'
```

A timelock can also be defined by specifying a block height:

```python
w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount='10000',
    lock=42000) # will unlock at block height 42000
```

When sending coins you can also attach some data:

```python
w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount='100 TFT',
    data='this is some data') # can also be specified as bytes or bytearray for binary data
# optionally you can still attach a lock to it of course
```

To multiple people (a MultiSignature wallet), with the requirement that _all_ have to sign in order to spend it:

```python
w.coins_send(
    recipient=[
        '01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
        '01e64ddf014e030e612e7ad2d7f5297f7e74e31100bdf4d194ff23754b622e5f0083d4bedcc18d',
    ], amount='100.0')
# optionally you can still attach data and a lock to it of course
```

To multiple people (a MultiSignature wallet), with the requirement that some have to sign in order to spend it:

```python
w.coins_send(
    recipient=([
        '01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
        '01e64ddf014e030e612e7ad2d7f5297f7e74e31100bdf4d194ff23754b622e5f0083d4bedcc18d',
    ], 1), amount=100)
# signature count has to be at least 1,
# and cannot be greater than the amount of people you are sending to
# optionally you can still attach data and a lock to it of course
```

Optionally you can use the `refund` parameter to define the recipient of the refund, should a refund be required:

```python
(txn, submitted) = w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount=250,
    refund='01e64ddf014e030e612e7ad2d7f5297f7e74e31100bdf4d194ff23754b622e5f0083d4bedcc18d')
```

By default the primary wallet address will be used for refunds (`w.address`).
Refunds are required in case the sum of the defined amount and minimum transaction fee
is smaller than the sum value of the used coin inputs.

See [The Wallet Coins Send Unit Test](./tests/24_wallet_coins_send.py)
for detailed examples of sending coins to some address on the used TFChain network.

### Multi-Signature Wallet

You use your regular wallet to manage and use your co-owned Multi-Signature wallets.

#### Check your balance:

The balance contains and reports the balance reports and outputs for all the Multi-Signatures
co-owned by your wallet as well.

```python
w.balance # human-readable printed in shell by default
# it does return however a very useful object
# should you want to inspect individual (coin) outputs
```

#### Send Coins

You send coins from your Multi-Signature wallet through your regular wallet,
by specifying the Multi-Signature wallet address of choice as the `source` parameter of your `coins_send` call:

```python
(txn, submitted) = w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount=10,
    source='039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a',
# optionally you can still attach a lock and data,
# and the recipient is still as flexible as previously defined.
#
# specify the optional 'refund' parameter if you do not want it to refund to the
# 039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a Multi-Signature Wallet,
# should a refund be required.
```

The `coins_send` call will return a pair `(txn, submitted)`, where the second value indicates if the value
was submitted. It is possible that there were not enough signatures collected, and that
other co-owners of you wallet still have to sign. If so you have to pass the returned transaction (`txn`) to them.

Using this client one can signs (and submit if possible)
a transaction using the `w.transaction_sign(txn)` method.

See [The Wallet Coins Send Unit Test](./tests/24_wallet_coins_send.py)
for detailed examples of sending coins to some address on the used TFChain network
using a Multi-Signature wallet to fund and refund.

### 3Bot Records

3Bot records can be fetched using the 3Bot client API as follows:

```python
record = c.threebot.record_get(3) # record fetched by unique ID
record.identifier # the unique identifier of the 3Bot as an integer
record.addresses # a list of NetworkAddresses
record.names # a list of BotNames
record.public_key # the PublicKey of the 3Bot, used for signature verification
record.expiration # the timestamp (epoch UNIX seconds) when the
                  # 3Bot expires if no further action is taken
```
> See [The ThreeBot Record Get Unit Test](./tests/16_threebot_record_get.py) for a detailed example.

3Bot records cannot only be fetched by ID, but also by name or public key:

```python
c.threebot.record_get("chatbot.example")
```

```python
c.threebot.record_get("ed25519:e4f55bc46b5feb37c03a0faa2d624a9ee1d0deb5059aaa9625d8b4f60f29bcab")
```

#### Create and Manage 3Bot Records

Creating a new 3Bot record can be done as follows:

```python
result = w.threebot.record_new(
    months=1, # default is 1, can be omitted to keep it at default,
              # or can be anything of inclusive range of [1,24]
    names=["chatbot.example"], # names can be omitted as well, as long as you have 1 address
    addresses=["example.org"], # addresses can be omitted as well, as long as you have 1 address
    key_index=0) # optionally leave key_index at default value of None
result.transaction # transaction that was created, signed and if possible submitted
result.submitted   # True if submitted, False if not possible
                   # due to lack of signatures in MultiSig Coin Inputs
```
> See [The ThreeBot Record New Unit Test](./tests/17_threebot_record_new.py) for a detailed example.

> Remark: in order to get the 3Bot's unique identifier,
> you'll have to wait until the transaction is registered on the blockchain (+/- 2 minutes waiting time),
> and afterwards you'll be able to get the identifier as part of the 3Bot's created record as follows:
> ```python
> record = c.threebot.record_get(result.transaction.public_key)
> record.identifier # the unique identifier of the 3Bot
> ```
> If the `ThreeBotNotFound` exception gets raised, it probably means
> the transaction is still not registered on the blockchain, wait a bit longer in that case.

Updating an existing 3Bot record can e done as follows:

```python
result = w.threebot.record_update(
    3, # identifier of the 3Bot
    months=2, # months to add, 0 by default
    names_to_add=['thisis.justan.example', 'foobar'], # names to add, None by default
    names_to_remove=['chatbot.example'], # registered names to remove, None by default
    addresses_to_add=['bot.example.org'], # addresses to add, None by default
    addresses_to_remove=['127.0.0.1', 'example.org'], # registered addresses to remove, None by default
    source=w.address, # source address or addresses used to fund this transaction, None by default
                        # in which case all the personal wallet addresses will be used
    refund=w.address, # refund address, None by default
                    # in which case either the source address is used (if only one is defined),
                    # or the primary address is used
)
result.transaction # transaction that was created, signed and if possible submitted
result.submitted   # True if submitted, False if not possible
                   # due to lack of signatures in MultiSig Coin Inputs
```
> See [The ThreeBot Record Update Unit Test](./tests/18_threebot_record_update.py) for a detailed example.

> If the `j.clients.tfchain.errors.ThreeBotInactive` exception gets raised,
> it means your 3Bot is currently marked as inactive,
> and so you'll have to add at least one month (`months=1`) to make it active again.

If you only want to update one or some properties than that is possible
as well, here are some more examples:

```python
# add one month to 3Bot #4
w.threebot.record_update(4, months=1)
```

```python
# add one (IPv6) address to 3Bot #10
w.threebot.record_update(10, addresses_to_add=["2001:db8:85a3::8a2e:370:7334"])
```

```python
# remove one name from 3Bot #1
w.threebot.record_update(1, names_to_remove=["example.chatbot"])
```

```python
# revive an inactive bot (#101) by adding a month,
# plus start using a new name as well
w.threebot.record_update(101, months=1, names_to_add=["example.chatbot"])
```

Transfering one or multiple names between from one existing 3Bot to another can be done as follows:

```python
result = w.threebot.name_transfer(
    sender=3, # identifier of sender 3Bot
    receiver=5, # identifier of receiver 3Bot
    names=["foobar", "chatbot.example"], # names to be transfered from sender to receiver 3Bot,
                                         # at least one name HAS to be defined
)
result.transaction # transaction that was created, signed and if possible submitted
result.submitted   # True if submitted, False if not possible
                   # due to lack of signatures in MultiSig Coin Inputs
```
> See [The ThreeBot Name Transfer Unit Test](./tests/19_threebot_name_transfer.py) for a detailed example.

> If the `j.clients.tfchain.errors.ThreeBotNotFound` exception gets raised,
> it means either the sender or receiver 3Bot could not be found
> (check the raised exceptions' `identifier` property to know which).

> If the `j.clients.tfchain.errors.ThreeBotInactive` exception gets raised,
> it means either the sender or receiver 3Bot is inactive
> (check the raised exceptions' `identifier` property to know which).
> Before you can continue with the name transfer the inactive bot will have
> to be made active again by applying a 3Bot update (`w.threebot.record_update`).

### Atomic Swap Contracts

Atomic swaps allow secure cross-chain transfers of money wihout any need of trust.
You an read more theory on Atomic Swaps as well as an example at <https://github.com/threefoldfoundation/tfchain/blob/master/doc/atomicswaps/atomicswap.md>.

Please ensure that you understand the terminlogy behind atomic swaps as otherwise the commands might make a lot of sense to you.

#### Commands

Create a contract as initiator:

```python
result = w.atomicswap.initiate(
    participator='0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6',
    amount=50, data='the beginning of it all') # data is optional, source and refund options are available as well
result.contract # the contract
result.transaction # contains the created (and if all good sent) transaction
result.submitted # if the contract was submitted (if not it is because more signatures are required)
result.secret # the random generated secret (Save it, but no yet share it)
```
> See [The AtomicSwap Initiate Unit Test](./tests/10_atomicswap_initiate.py) for a detailed example.

> Note: with atomic swap only unlock hashes (strings or `UnlockHash`) are supported, no Multi-Signature wallets can
> be the recipient or used for refunds.
> The refund is also used to identify the sender address of the Atomic Swap Contract.

Creating a contract as initiator without submitting it automatically to the network can be done as follows:

```python
result = w.atomicswap.initiate(
    participator='0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6',
    amount=50, submit=False) # submit=True by default, data, source and refund options are available as well
```

This is not common practise, but should you be in need of pre-submission (custom) validation,
you can do so by following the above approach.

Create a contract as participator:

```python
result = w.atomicswap.participate(
    initiator='01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c',
    amount='50.0', secret_hash='4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba') # data is optional, source and refund options are available as well
result.contract # the contract
result.transaction # contains the created (and if all good sent) transaction
result.submitted # if the contract was submitted (if not it is because more signatures are required)
```
> See [The AtomicSwap Participate Unit Test](./tests/11_atomicswap_participate.py) for a detailed example.

Creating a contract as participant without submitting it automtically to the network can be done as follows:

```python
result = w.atomicswap.participate(
    initiator='01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c',
    amount='50.0', secret_hash='4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba',
    submit=False) # submit=True by default, data is optional, source and refund options are available as well
```

This is not common practise, but should you be in need of pre-submission (custom) validation,
you can do so by following the above approach.

Verify a contract as recipient of an initiation contract:

```python
contract = w.atomicswap.verify('dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486',
    amount=50, secret_hash='e24b6b609b351a958982ba91de7624d3503f428620f5586fbea1f71807b545c1',
    min_refund_time='+1d12h', receiver=True)
# an exception is raised if the contract is not found, has already been spent
# or is not valid according to the defined information
```
> See [The AtomicSwap Verify-As-Receiver Unit Test](./tests/13_atomicswap_verify_receiver.py) for a detailed example.

Redeem a contract:

```python
transaction = w.atomicswap.redeem(
    'dd1babcbab492c742983b887a7408742ad0054ec8586541dd6ee6202877cb486',
    secret='f68d8b238c193bc6765b8e355c53e4f574a2c9da458e55d4402edca621e53756')
# an exception is raised when the contract is not found, has already been spent,
# or the wallet is not authorized as receiver.
```
> See [The AtomicSwap Redeem Unit Test](./tests/14_atomicswap_redeem.py) for a detailed example.

Refund a contract (only possible when the defined contract duration has expired):

```python
transaction = w.atomicswap.refund('a5e0159688d300ed7a8f2685829192d8dd1266ce6e82a0d04a3bbbb080de30d0')
# an exception is raised when the contract is not found, has already been spent,
# the defined secret is incorrect or the wallet is not authorized as sender.
```
> See [The AtomicSwap Refund Unit Test](./tests/15_atomicswap_refund.py) for a detailed example.

### ERC20 Interaction

Sending coins to an ERC20 address can be done as follows:

```python
result = w.coins_send(
        recipient="0x828de486adc50aa52dab52a2ec284bcac75be211", # the ERC20 address to receive the amount, converted from TFT
        amount="200.5 TFT" # the amount of TFT to convert to ERC20 Tokens
    ) # no data or lock can be attached, optionally you can define a source and refund address(es) as well
result.transaction # contains the created (and if all good sent) transaction
result.submitted # if the transaction was submitted (if not it is because more signatures are required)
```
> See [The ERC20 Coins Send Unit Test](./tests/20_erc20_coins_send.py) for a detailed example.

> Note that the above command is an alias for:
> ```python
> w.erc20.coins_send(address="0x828de486adc50aa52dab52a2ec284bcac75be211", amount="200.5 TFT")
> ```
> and that when using the `w.coins_send` shorthand you are not allowed
> to add data or a lock when sending to an ERC20 address. If you do try
> to attach a lock or data to this transaction a `ValueError` will be raised.

In order to be able to withdraw ERC20 Tokens into a TFT wallet,
you first need to register a TFT address (of that wallet) as an ERC20 withdraw address.
You can do this in three ways.

- if you specify nothing (`None`), a new address will be generated and used:
  ```python
  result = w.erc20.address_register() # value=None, optionally you can define a source and refund address(es) as well
  result.transaction # contains the created (and if all good sent) transaction
  result.submitted # if the transaction was submitted (if not it is because more signatures are required)
  ```
- if you specify a valid address index (`int`), the address on that index will be used:
  ```python
  # you can for example register the 5th address of the wallet as follows:
  result = w.erc20.address_register(4) # value=4, optionally you can define a source and refund address(es) as well
  result.transaction # contains the created (and if all good sent) transaction
  result.submitted # if the transaction was submitted (if not it is because more signatures are required)
  ```
- if you specify a valid address (`str`/`UnlockHash`), that address wil be used:
  ```python
  result = w.erc20.address_register('014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a')
  result.transaction # contains the created (and if all good sent) transaction
  result.submitted # if the transaction was submitted (if not it is because more signatures are required)
  ```

An address can only be registered once, a generic `j.clients.tfchain.errors.ExplorerServerError` error
will be raised if you try to double-register an address. If your wallet does not own the defined address,
the `j.clients.tfchain.errors.ERC20RegistrationForbidden` error will be raised.

See [The ERC20 Address Register Unit Test](./tests/21_erc20_address_register.py)
for detailed examples of the registration of an ERC20 withdraw address.

You can get the information for a registered ERC20 address of a wallet:

- by specifying nothing (`None`), the first wallet address will be used:
  ```python
  info = w.erc20.address_get() # value=None
  info.address_tft # tft address (unlock hash)
  info.address_erc20 # erc20 address (ERC20Address)
  info.confirmations # the amount of blocks that confirm this ERC20 Address Withdraw Registration
  # if no (ERC20 address registration) info could be found for the address
  # a j.clients.tfchain.errors.ExplorerNoContent error is raised
  ```
- if you specify a valid address index (`int`), the address on that index will be used:
  ```python
  # you can for example get the ERC20 address registration info for the 5th address of the wallet as follows:
  info = w.erc20.address_get(4) # value=4
  # the index has to be within bounds of the range as indicated by the amount of addresses
  # owned by this wallet, if not a ValueError is raised
  ```
- if you specify a valid address (`str`/`UnlockHash`), that address wil be used:
  ```python
  info = w.erc20.address_get('014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a')
  # the address has to be owned by the wallet,
  # otherwise a j.clients.tfchain.errors.AddressNotInWallet error is raised
  ```

You can get the information for all wallet addresses registered as ERC20 addresses as follows:

```python
info_list = w.erc20.addresses_get() # returns a list of info tuples
info_list[0].address_tft # tft address (unlock hash)
info_list[0].address_erc20 # erc20 address (ERC20Address)
info_list[0].confirmations # the amount of blocks that confirm this ERC20 Address Withdraw Registration
# if no (ERC20 address registration) info could be found for any
# of the wallet addresses an empty list is returned
```

See [The ERC20 Wallet Addresses Get Unit Test](./tests/23_erc20_wallet_addresses_get.py)
for detailed examples of getting information for one or multiple wallet addresses
registered as ERC20 wallet addresses.

You can also get the ER20 withdraw address registration info for an address not owned by
your wallet. You do this by looking the address up using the `c.erc20.address_get` method
(where `c` is a `TFChainClient` instance).
See [The ERC20 Client Address Get Unit Test](./tests/22_erc20_client_address_get.py) for detailed example of this.

### Coin Minting

You can get the current minting condition active at the network as follows:

```python
condition = c.minter.condition_get()
condition.json       # the condition in JSON format
condition.unlockhash # the address of the wallet that is currently the minter
```

You can also get the current minting condition active at a given height in the network as follows:

```python
condition = c.minter.condition_get(height=1000)
condition.json       # the condition in JSON format
condition.unlockhash # the address of the wallet that is currently the minter
```

See [The Minter Condition Get Unit Test](./tests/25_minter_condition_get.py)
for detailed examples for getting the minter condition at a given height as
well as the latest minter condition for the used network.

Only if you have minting powers you can redefine the Mint Condition
(the condition to be fulfilled to proof you have these powers)
as well as create new coins. If you do have these powers, this subsection is for you.

Redefining the Mint Condition can be done as follows:

```python
(txn, submitted) = w.minter.definition_set(minter='01a006599af1155f43d687635e9680650003a6c506934996b90ae8d07648927414046f9f0e936')
# optional data can be attached as well,
# the minter parameter is as flexible as the recipient parameter when sending coins from your wallet.

# if not submitted yet, it's because you might require signatures from others:
# you can pass the txn in that case to the others, such that they can sign using:
(txn, signed, submitted) = w.transaction_sign(txn)
```

See [The Minter Condition Set Unit Test](./tests/26_minter_condition_set.py)
for detailed examples for setting a new minter condition.

Creating coins as a Coin Minter can be done as follows:

```python
(txn, submitted) = w.minter.coins_new(recipient='01a006599af1155f43d687635e9680650003a6c506934996b90ae8d07648927414046f9f0e936', amount=200)
# optional data can be attached as well,
# the recipient parameter is as flexible as the recipient parameter when sending coins from your wallet.

# if not submitted yet, it's because you might require signatures from others:
# you can pass the txn in that case to the others, such that they can sign using:
(txn, signed, submitted) = w.transaction_sign(txn)
```

See [The Minter Coins New Unit Test](./tests/27_minter_coins_new.py)
for detailed examples for minting new coins.

### Examples

The TFChain Client is kept simple and focussed. It can do a lot, and it is very easy to use it.
However, that does mean that we do not support every possible use case out-of-the box.
Building an application on top of the TFChain Client and as such using this client as a library.

#### Wallet Statements

You can find a detailed example in [The Wallet Statements Example](./tests/100_examples_wallet_statements.py)
on how to assemble your own statements for a wallet using the TFChain Wallet Client.

The example is simple and prints the statements directly to the STDOUT as follows:

```
$ kosmos 'j.clients.tfchain.test(name="examples_wallet_statements")'
unconfirmed  Tx: 573290763024ae0a5e981412598a3d41bc02f8da628fa1e1adfe07d98818c689 |                          |         + 10 TFT         |
        > to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
        > from: 01f0f397fd6b7b51b46ddd2ffda1e2240e639b19b47d27a4adc2bed78da0fc3d97c1fe7b972d1e
39997        Tx: 779cf13ecee7f45f032af92429056cd5976cb75ce968bab98e3e2fdf9a9b1034 |         - 1 TFT          |                          |
        > to: this wallet
        > from: this wallet
39995        Tx: b104308e683d4353a5a6b6cdfd4f6dfce39e241ff1218d6d6189bae89945034f |                          |        + 200 TFT         |
        > to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
        > from: 015827a0cabfb4be5531ecd2b42470a25cf9910a868b857029c2bdabdc05cad51e66d5dd899064
39994        Tx: 208d9f524e937176e50a7399fd3886f584290948983bbd0ed781f59cefc343a8 |         - 11 TFT         |                          |
        > to: 01cb0aedd4098efd926195c2f7bba9323d919f99ecd95cf3626f0508f6be33f49bcae3dd62cca6
        > from: this wallet
39991        Tx: e7785bacd0d12f93ab435cf3e29301f15b84be82ae8abbdaed1cfd034f4ed652 |                          |        + 100 TFT         |
        > to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
        > from: 01456d748fc44c753f63671cb384b8cb8a2aebb1d48b4e0be82c302d71c10f2448b2d8e3d164f6
39990        Tx: 544a204f0211e7642f508a7918c5d29334bd7d6892b2612e8acfb6dc36d39bd9 |                          |        + 400 TFT         |
        > to: 0125c0156f6c1c0bc43c7d38e17f8948300564bef63caac05c08b0fd68996e494704bbbe0268cb
        > from: 01773a1dd123347e1030f0822cb8d22082fe3f9b0ea8563d4ac8e7abc377eba920c47efb2fd736
```

### Capacity reservation

During the fist beta phase of the public launch of the TF grid, beta tester will be able to reserve 2 kind of workload on the grid.

- Zero-OS virtual machines
- S3 archive storage instances

**At the time of writing, everything happens on the testnet network**
**Don't send real TFT from the main network !!**

#### How to reserve some capacity on the Threefold Grid

To be able to make a reservation you first need to:

- have a wallet with sufficient funds
- record a threebot on the tfchain

Once you have both, you can then use your wallet client to do a reservation.
The wallet expose a module called `capacity`. On this module you will find function to reserve the different type of capacity.

Examples:

```python
c = j.clients.tfchain.myclient
w = c.wallets.mywallet
result = w.capacity.reserve_s3(
    email='user@email.com', # the email on which you will received the connection information
    threebot_id='my3bot.example.org', # your threebot id, it can be any of the names you gave to your 3bot
    location='farm_name', # name of the farm where to deploy the workload
    size=1, # each workload have a different size available
    duration=1) # number of months the reservation should be valid for
```

The validity of the reservation shouldn't exceed the validity of the 3bot otherwise the reservation will fail.


The result of the `reserve_s3` method call is a tuple containing the transaction and the submission status as a boolean.
You can check it on our [explorer](https://explorer.testnet.threefoldtoken.com/) by entering the transaction ID in the `Search by hash` field of the explorer form or using the tfchain client:

```python
transaction = c.transaction_get(result.transaction.id)
```

As soon as it is ready, usually within a few minutes, you will receive an email with the connection information and expiration date of the reservation.


#### How to extend the expiry of your capacity on the Threefold Grid

If you want to extend the validity of the reservation made in the previous section at any point in time before its expiry, you can use the capacity module to do so. The new expiration date of the reservation must be smaller than or equal to the expiration of the 3bot that was used to create the initial reservation.

```python
result = w.capacity.reservation_extend(
    transaction_id="1bdff90882cc437cb8b781c5eb296edbfdb79777564d70ec8f2120c37d8a7737", # the id of the transaction that was created as a result of the initial reservation (result.transaction.id in the section above)
    email='user@email.com', # the email on which you will received extension confirmation
    duration=1) # number of months you want to extend the reservation by.
```

The result of the `reservation_extend` method call is a tuple containing the transaction and the submission status as a boolean.
You can check it on our [explorer](https://explorer.testnet.threefoldtoken.com/) by entering the transaction ID in the `Search by hash` field of the explorer form or using the tfchain client:

```python
transaction = c.transaction_get(result.transaction.id)
```

As soon as it is ready, usually within a few minutes, you will receive an email with the new expiry date of the reservation.


If you want to list all transactions that were created whenever a reservation was done (not an extension), you can use method `reservations_transactions_list`.

```python
w.capacity.reservations_transactions_list()
- 1bdff90882cc437cb8b781c5eb296edbfdb79777564d70ec8f2120c37d8a7737
- 5b61c9eaa2d28778620d7f60630fceb2884a3948b2cf06d59a033a02cd747439
- ffce9a46a689eddfb69496a414e7df7a10f0c55bcf78e97122a85cdfd6da56e2
```

