# TFChain JSX Client

See [./tests](./tests) directory for documented tests that explain a lot of this client's functionality.

## TLDR

All methods have docstrings, _read_ them.

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

### Wallet

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
    amount='100 TFT')
# equivalent amount specifications:
#   - also as a string: '100 tft', '100.0', '100.0 TFT', '100000000000'
#   - as an int: 100000000000
```

With a timelock:

```python
w.coins_send(
    recipient='01f7e0686b2d38b3dee9295416857b06037a632ffe1d769153abcd522ab03d6a11b2a7d9383214',
    amount=100000000000
    lock=1549064679) # TODO: support more human-friendly approaches for the lock parameter
```

With some data:

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
    ], 1), amount='100.0')
# signature count has to be at least 1,
# and cannot be greater than the amount of people you are sending to
# optionally you can still attach data and a lock to it of course
```
