# Threefold Directory Client
Views and monitors threefold connected capacitites and farmers from: https://capacity.threefoldtoken.com/

## making a client using config manager
```
test_client = j.clients.threefold_directory.test_client 
test_client.save()
```
## methods
- `j.clients.threefold_directory.farmers`: shows all connected farmers
- `j.clients.threefold_directory.capacity`: shows all connected capacities
- `j.clients.threefold_directory.resource_units()`: overall capacity

## API methods
- To get a specific capacity by:

` test_client.api.GetCapacity({node_id}, headers={headers}, query_params={query_params}, content_type="application/json")`

- To get a specific Farmer by: 

`test_client.api.GetFarmer(iyo_organization, headers=None, query_params=None, content_type='application/json') `

## Example
This example script show how to use the capacity directory client to
compute the total number of ressource units present on the grid.

```
from Jumpscale import j


directory = j.clients.threefold_directory.get("main")
nodes, _ = directory.api.ListCapacity()

resource_units = {"cru": 0, "mru": 0, "hru": 0, "sru": 0}

for node in nodes:
    resource_units["cru"] += node.total_resources.cru
    resource_units["mru"] += node.total_resources.mru
    resource_units["hru"] += node.total_resources.hru
    resource_units["sru"] += node.total_resources.sru

print(resource_units)

j.shell()
```
Some other intersting methods under api autocompletion 