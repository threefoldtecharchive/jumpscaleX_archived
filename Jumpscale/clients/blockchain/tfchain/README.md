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
4. [Atomic Swap Contacts](#atomic-swap-contracts): explains how to work with cross-chain atomic swaps, from a TFChain perspective, using your TFChain wallet
5. [Coin Minting](#coin-minting): a subsection devoted to the coin minters of the network

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

### Atomic Swap Contracts

_TODO_

### Coin Minting

Only if you have minting powers you can redefine the Mint Condition (the condition to be fulfilled to proof you have these powers)
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

Creating coins 

```python
(txn, submitted) = w.minter.coins_new(recipient='01a006599af1155f43d687635e9680650003a6c506934996b90ae8d07648927414046f9f0e936', amount=200)
# optional data can be attached as well,
# the recipient parameter is as flexible as the recipient parameter when sending coins from your wallet.

# if not submitted yet, it's because you might require signatures from others:
# you can pass the txn in that case to the others, such that they can sign using:
(txn, signed, submitted) = w.transaction_sign(txn)
```
