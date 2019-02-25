# j.date.types

implement some basic types in jumpscale

## basic methods on each type class

### clean(val)

-  will convert any possible input to a representation as it can be used in jumpscale environment (not how it will be stored in the DB/capnp)
- e.g. in case of IPAddres its an IPAddressObject()
- e.g. in case of ENUMERATION its an EnumerationObject()
- e.g. in case of a Guid its a string
- e.g. in case of Float its a Float

### default_get()

- returns the default value if any as how it will be used in jumpscale environment (see result clean)
- e.g. in case of int:0, float:0.0, ...
- e.g. in case of ENUMERATION = raise Error

### get(**kwargs)

- only implemented where objects can be returned e.g. IPAddress, ENUMERATION, ...
- the object will represent the data format and offer some extra methods e.g. IPAddress will have a ping()
- not done for int, float, ... (all basics)

### check(val)

- if there is a specific implementation e.g. string, float, enumeration, it will check if the input is that implementation
- if not strict implementation or we cannot know e.g. an address will return None

### possible(val)

- will check if it can be converted to the jumpscale representation, basically the clean works without error

### toString()

- representation in a string format
- the clean() needs to be able to use the toString result back to the jumpscale representation we can work with
- its a dense representation in string format

### toData()

- convert the object to the smallest possible representation in binary
- is stored inside the capnp objects (can be used to store elsewhere as well)

### toHR()  convert to human readable format

- representation in a string format
- the clean() needs to be able to use the toHR result back to the jumpscale representation we can work with
- its the most readable format format, ideal to e.g. represent in screen

## capnp_schema_get()

- returns how to represent it in capnp

### toDict()

- only relevant for types which have a dict representation
