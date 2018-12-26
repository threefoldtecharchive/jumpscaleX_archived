
# jumpscale schemas

## format of the schema


```python
@url = despiegk.test.1
llist2 = "" (LS) #L means = list, S=String        
nr = 4
date_start = 0 (D)
description = ""
token_price = "10 USD" (N)
cost_estimate:hw_cost = 0.0 #this is a comment
llist = []
llist3 = "1,2,3" (LF)
llist4 = "1,2,3" (L)
llist5 = "1,2,3" (LI)
U = 0.0
pool_type = "managed,unmanaged" (E)
```

- @url is the unique locator of the schema, try to have this unique on global basis
  - its good practice to put an version nr at the end of the url

### simple types

- I
  - Integer
- F:
  - Float
- N:
  - Numeric, has support for currencies
  - can e.g. insert 10 EUR, 10 USD, 10k USD
- S:
  - string
- B:
  - boolean
  - true,True,1 are all considered to be True

TODO:*1 complete

there are also more capable types like ipaddress, tel nrs, ...

### collection types

- L
- e.g. LI is list of integer

#### collection of other objects

```python
@url =  jumpscale.digitalme.package
name = "UNKNOWN" (S)           #official name of the package, there can be no overlap (can be dot notation)
enable = true (B)
args = (LO) !jumpscale.digitalme.package.arg
loaders= (LO) !jumpscale.digitalme.package.loader

@url =  jumpscale.digitalme.package.arg
key = "" (S)
val =  "" (S)

@url =  jumpscale.digitalme.package.loader
giturl =  "" (S)
dest =  "" (S)
enable = true (B)
```

- generic format ```(LO) !URL```

### defaults

- ```enable = true (B)```
    - in this case the default is true, so basically everything in between = and (
- ```name = myname (S)``` or ```name = myname```
    - if type not specified the schemas will try to guess the type e.g. Int, String, ...

## how to get a new schema

```python
def get(self, schema_text="", url=None, die=True):
    """
    get schema from the url or schema_text_path

    Keyword Arguments:
        schema_text {str} -- schema file path or shcema string  (default: {""})
        url {[type]} -- url of your schema e.g. @url = despiegk.test  (default: {None})
        
    if die False and schema is not found e.g. based on url, then will return None

    Returns:
        Schema
    """
    ...

SCHEMA="""
@url =  jumpscale.digitalme.package.1
name = "UNKNOWN" (S)           #official name of the package, there can be no overlap (can be dot notation)
enable = true (B)
"""

s=j.data.schema.get(SCHEMA)

#if the schema already exists then can do
s=j.data.schema.get(url="jumpscale.digitalme.package.1") #will die if not exists


```

## how to get a new object

s.new()
