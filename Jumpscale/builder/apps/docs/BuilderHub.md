# 0-hub builder
### Allow people to create their own hub: create flist + launch script which launches container who has everything which hub has so people can use this to develop full life cycle management

## Install locally

### Get client id and client secret from ```https://itsyou.online/#/organizations```

```python
export CLIENT_ID = client id of your iyo 
export CLIENT_SECRET = client secret of your iyo 
export IP_PORT = localhost
```
### Using kosmos
```
j.builders.apps.hub.install()
```

## Start locally
### Using kosmos
```
j.builders.apps.hub.start()
```
You can view it 

``` localhost:80```


## Install in container
### Create flist 
Using kosmos 
```
j.builders.apps.hub.sandbox(zhub_client=your_zhub_cleint, flist_create=True, reset=True) 
```

**Then merge this flist with JSX flist :**

**Base on** : your flist

**merge with** : ```https://hub.grid.tf/tf-autobuilder/threefoldtech-jumpscaleX-autostart-development.flist```

## Create container :

Using kosmos

```
cl =j.clients.zos.get("zhub", host="IP_Node", password=jwt)


cl.client.container.create(name='testzhub',root_url='your_flist_after_merge',nics=[{'type':'default', 'name':'defaultnic', 'id':' None'}], port{2015:2015,8080:80, 5555:5555}, env={"CLIENT_SECRET":"your_client_secret", "CLIENT_ID":"your_client_id", "IP_PORT":"IP_Node:8080"}).get()
```

You can view it 

```IP_Node:8080```
example ```10.102.178.130:8080```