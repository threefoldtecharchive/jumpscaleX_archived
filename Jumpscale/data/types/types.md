
## string

- s, str, string

## integer 

- i, int, integer

## float

- f, float

## bool

- b, bool

## numeric

- n, numeric 

we have then represented as 2 different implementations

for more info see

- https://github.com/threefoldtech/jumpscale_core/blob/development/Jumpscale/data/numtools/numtools.md
- https://github.com/threefoldtech/jumpscale_/lib/blob/development/JumpscaleLib/clients/currencylayer/currencies.md 

### numeric as string:  

- is a string representation of a number with potentially a currency symbol

e.g. ```10 USD```


### numeric as set

- (id,val)  e.g. 10 aed is (1,10)

### bytes

= 1byteForID+4bytesForVal

in other words 5 bytes store currency uniquely identified 

## multiline

string but with multiple lines

## list = array

e.g. [1,2,3]

### list string

can be represented as string with comma's eg ```1,2,3,4``` or ```jan,piet ,pol```
there can be spaces inside, they are ignored

[] can be used as well, but will be ignored

## dict

e.g. 
{
    name:val
}

### dict string

toml representation of dict

- duration e.g. 1w, 1d, 1h, 1m, 1

## duration

duration e.g. 1w, 1d, 1h, 1m, 1

- w = week
- d = day
- h = hour
- m = minute

translates to seconds when used

## date

### epoch

is 4 bytes integer, can be retrieved using

```python
```

### human readable



##  others

- guid
- tel, mobile
- ipaddr, ipaddress
- ipport, tcpport
- iprange
- email
