# What is JumpScale Schema
According to wikipedia *"The word schema comes from the Greek word σχήμα (skhēma), which means shape, or more generally,
 plan"*.  
In databases "Schema" is some files or some structured code describing the tables and it's fields and data types of each
 field.  
JumpScale Schema is a way to define an efficient but yet very powerful schemas for your data, Taking advantage of 
[capnp's]('https://capnproto.org/language.html') high performance and readability of 
[TOML Lang]("https://github.com/toml-lang/toml") combining it with complex data types to achieve both 
usability and high performance.

# What do you need to know to define a new schema

## Schema url
The very first part of the schema is the url, Each schema should have it's unique url over the application.
you can define the schema url like that.  
```toml
@url = schema.test
```
## Data types

| Name | Symbol | Description | sample valid data |
| :----: | :------: | ----------- | --------- |
| String | S | can be any set of characters saved as string | "Hello !" |
| Integer| I | can only be Integer numbers| 1, 2, 200, 1000 |
| Float  | F | just like the primitive float | 1.123, 1.0, 100.99 |
| Boolean| B | can only be True of False |  y , 1 , yes , n , True, False |
| mobile |tel| can be set any mobile number| '+32 475.99.99.99' , '464-4564-464' , 468716420  |
| email |email| can be set any email | changeme@example.com |
| ipport |ipport| can be set only port  | 53  |
| ipaddress |ipaddr| can be set any IP Adress | '192.168.1.1' |
| ipaddressrange |iprange| can be set any IP Adress with range | '192.168.1.1/24' |
| Date   | D | date | 20/11/2018 . see [date supported formats](#date_supported_formats)|
| Date Time   | T | date with time | 01/01/2019 9pm:10. see [date time supported formats](#date_time_supported_formats)|
| Numeric| N | can store any numeric data including currencies | 1, 1.12, 10 USD, 90%, 10.5 EUR| 
| guid| guid | can store any guid   | 5b316587-7162-4bf1-99e6-fe53d9577cd0 | 
| dict| dict | can store any dict type   | {"key":"value"} | 
| yaml| yaml | can store any yaml    | "example:     test1" |
| multiline| multiline | string but with multiple lines   | "example \\n example2 \\n example3" |
| hash| h | hash is 2 value represented as 2 times 4 bytes   | 46:682 |
| bytes | bin | stored as bytes directly   | 'this is binary' |
| percent| p | to deal with percentages < 1 we multiply with 100 before storing   | 99 which would be 99% |
| url| u | Generic url type   | www.example.com  , 'test.example.com/home'|




### <a name="date_supported_formats"></a> Date supported formats
- month/day  (will be current year if specified this way)
- year(4char)/month/day
- year(4char)/month/day
- year(2char)/month/day
- day/month/4char
- year(4char)/month/day

### <a name="date_time_supported_formats"></a> Date Time supported formats
- month/day 22:50
- month/day  (will be current year if specified this way)
- year(4char)/month/day
- year(4char)/month/day 10am:50
- year(2char)/month/day
- day/month/4char
- year(4char)/month/day 22:50
- +4h
- -4h

### List support

You can add L before any symbol from the above table to indicate a list  
example: 
```
list_of_floats = (LF) # can accept [1.1, 1.2, 1.3]
list_of_strings = (LS) # can accept ["a", "aa", "aaa"]
list_of_multiLines =  (Lmultiline) # can accept ["example \\n example2 \\n example4", "example \\n example2 \\n example3"]
list_of_guids = (Lguid) # can accept ['bebe8b34-b12e-4fda-b00c-99979452b7bd', '84b022bd-2b00-4b62-8539-4ec07887bbe4'] 

```

### Complex data types

you can define more complex data types by nesting schemas  
Example:
```toml
@url = schema.address
street = (S)
floor = (I)
apartment = (I)
```
```toml
@url = schema.student
name = (S)
subjects = (LS)
address = (O) !schema.address
```
### How to use schema 
```
schema = """
        @url = despiegk.test
        llist2 = "" (LS) #L means = list, S=String        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        llist = "1,2,3" (LI)
        llist1 = "1,2,3" (L)
        """
```
## to get schema from schema_text
```paython
schema_test = j.data.schema.get(schema_text_path=schema)
schema_object = schema_test.get()
```
## to add data using schema
```paython
schema_object.token_price = "20 USD"
schema_object.llist.append(1)
schema_object.description = "something"
```
### for a full example of using schema see the following [test link](https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/data/schema/tests)


## Schema Test
### run all tests
```python
 js_shell 'j.data.schema.test()'
```
### run specific test
```python
js_shell 'j.data.schema.test(name="base")'
js_shell 'j.data.schema.test(name="capnp_schema")'
js_shell 'j.data.schema.test(name="embedded_schema")'
js_shell 'j.data.schema.test(name="lists")'
js_shell 'j.data.schema.test(name="load_data")'
```




