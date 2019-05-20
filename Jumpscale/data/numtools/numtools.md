
## text2val


```python
j.tools.numtools.text2val("0.1mEUR")
```

- value can be 10%,0.1,100,1m,1k  m=million
- USD/EUR/CH/EGP/GBP are also understood
- all gets translated to usd
- e.g.: 10%
- e.g.: 10EUR or 10 EUR (spaces are stripped)
- e.g.: 0.1mEUR or 0.1m EUR or 100k EUR or 100000 EUR

## currencies

see https://github.com/threefoldtech/jumpscale_/lib/blob/development/JumpscaleLib/clients/currencylayer/currencies.md for more info

```
import pprint; pprint.pprint(j.tools.numtools.currencies)
```

there are unique id's for each currency, see above link

## examples

```bash
kosmos 'j.tools.numtools.test()'
```

```python
assert  self.text2val("10k")==10000.0

assert (1/self.currencies["egp"])*10000000 == self.text2val("10 m egp")
assert (1/self.currencies["egp"])*10000000 == self.text2val("10m egp")
assert (1/self.currencies["egp"])*10000000 == self.text2val("10mEGP")

assert self.int_to_bitstring(10)=='00001010'
assert self.bitstring8_to_int('00001010')==10

assert self.bitstring_set_bit("00000000",7) == 128
assert self.bitstring_set_bit("00000000",0) == 1

assert self.bitstring_get_bit("00000000",0) == False
assert self.bitstring_get_bit(128,7) == True
assert self.bitstring_get_bit("00000001",0) == True
assert self.bitstring_get_bit("00000011",1) == True
assert self.bitstring_get_bit("00000011",2) == False
assert self.bitstring_get_bit("10000011",7) == True
assert self.bitstring_get_bit("00000011",7) == False


llist0=[1,2,3,4,5,6,7,8,9,10]
bbin=self.listint_to_bin(llist0)
llist=self.bin_to_listint(bbin)
assert llist==llist0
assert  len(bbin)==21

#now the binary struct will be double as big because there is 1 long int in (above 65000)
llist2=[1,2,3,400000,5,6,7,8,9,10]
bbin2=self.listint_to_bin(llist2)
assert  len(bbin2)==41
llist3=self.bin_to_listint(bbin2)
assert llist3==llist2

#max value in short format
llist2=[1,2,3,65535,5,6,7,8,9,10]
bbin2=self.listint_to_bin(llist2)
assert  len(bbin2)==21
llist3=self.bin_to_listint(bbin2)
assert llist3==llist2
```
