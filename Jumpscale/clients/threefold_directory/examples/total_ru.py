"""
This example script show how to use the capacity directory client to
compute the total number of ressource units present on the grid.
"""
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
