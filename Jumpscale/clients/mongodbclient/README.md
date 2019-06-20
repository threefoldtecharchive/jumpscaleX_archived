# Mongodb Client

Interacts with mongodb

## Usage
- get a new jumpscale client with mongo configurations: `mcl = j.clients.mongodb.get("new_client", host="localhost", port=27017, ssl=False, replicaset="")`

- var for client to make operations easier `mongo_client = mcl.client`

### Operations

- Getting a database: `db = mongo_client.test_database`
- Getting a Collection: `collection = db.test_collection`

## Examples

### Documents:

Data is represented using JSON-style
```
test_doc = {"name": "xyz", 
            "age": "20",
            "hobbies": ["football", "reading", "games"]}
```

## insert a document:
```
clients = db.clients
client_id = clients.insert_one(test_doc).inserted_id
```
## check it's inserted
`>>> client_id` <br/>
`>>> db.list_collection_names()`

## get one client
```
from pprint import pprint
pprint(clients.find_one())
```

## find a client
`clients.find_one({"name": "xyz"})`