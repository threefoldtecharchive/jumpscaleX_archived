# Get Started
## Prerequisite
* Mac OS X 10.7 (Lion) or newer or a linux OS (tested on ubuntu 18.04)
* Git installed with a github account
* an [ssh key](https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) added to [github](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account)
    * to see if SSL key has been loaded `ssh-add -L` 
    * :warning: you must have only one ssh key if you choose NOT to provide secret to use for passphrase and use SSH-Agent instead during the install
* Docker installed 

## philosophy
JumpscaleX aka JSX was created at the beginning so that junior system administrators can easily use this tool to manage resources, provision machines, create and deploy containers.

It will evolve even further to be your digital representation that will always be available. Right now this tool works on your machine but soon it will be automatically deployed on the TF grid.
This 3bot, as we call it, will make sure your applications are properly running by creating, monitoring and maintaining your ressources at any time on your behalf.
It will even be able to engage in trade with others and this network of 3bots will act as a decentalized exchange.
  
Don't worry nobody except you can take control over your 3bot as all your config files are encrypted (securely stored) and your keys never leaves your device.


# Starting Steps

## getting the files and installation application

make sure to create a directory `{MY_DIR}` where your user has full access.
For instance I will choose to install inside this directory /home/ben/3bot/
so I will replace here below `{MY_DIR}` by /home/ben/3bot/


```bash
#create directory, make sure your user has full access to this directory
mkdir -p `{MY_DIR}`/github/threefoldtech; \
cd `{MY_DIR}`/github/threefoldtech; \
git clone git@github.com:threefoldtech/jumpscaleX.git; \
cd jumpscaleX; \
git checkout master; \
git pull; \
```
Now go to the [latest release](https://github.com/threefoldtech/jumpscaleX/releases) of the 3bot  
and get the application for your operating system

## launching the installation application
Launch the interactive installation with this command
 
```bash
./3bot_dev --code-path `{MY_DIR}` install
```

Just answer the questions till the end of the installation. If you don't know what to answer just hit enter to continue.

:warning: If you already have multiple ssh key on your machine be sure to answer no and enter a passphrase at the step
```bash
> Optional: provide secret to use for passphrase, if ok to use SSH-Agent just press 'ENTER'
``` 

at the end of the process you should have a container named 3bot running and see this
```bash
install succesfull:

# to login to the docker using ssh use (if std port)
ssh root@localhost -A -p 9122

# to start using the kosmos shell when you're using the 3bot_devel tools do: 
python3 3bot_dev.py connect
```

You can now connect with SSH. Enter this to have a shell access to the container
```bash
ssh root@localhost -A -p 9122
```

## launching kosmos
Now the fun part let's run our kosmos shell
```bash
$ source /sandbox/env.sh; kosmos 
```

# 1. Using kosmos to create a wallet on the TFchain 

In kosmos, create a TFChain client.

**The `network_type` is important, it specify you want to use the TestNet.**
**You will play with real TFT otherwise, so be careful**

```python
c = j.clients.tfchain.new(name='my_client', network_type='TEST')
```

With your new client, create a TFChain wallet, if you don't already have one.
As soon as your wallet is created, please save your seed somewhere. This is the only way to get your
wallet back for recovery.

```python
JSX> w = c.wallets.new("my_wallet")
JSX> w.seed
'trust faculty frame ...'
```

If you already have one, you can recover it using its seed:

```python
JSX> w = c.wallets.new('my_wallet', seed='bullet absurd cabin dose void wink toward oven catalog chef venture edge suggest strategy note merry mechanic buffalo bronze creek select walk click snow')
```

**TIP : at any moment hit the question mark key to display the interactive help to know more about a function arguments.** 


Get the address of your wallet

```python
JSX> w.address
'01d761561e7203276ef2944628bfde5bfcabf0960b69eda69ac1d317bcdcc53af06a0fd08c5f91'
```

note that if you want to be able to quickly get access to your wallet if for instance you loose the connection with your container you can save the variable and load them again

```python
JSX> w.save()
```

kill your terminal then connect to your container and launch kosmos again

```python
JSX> c = j.clients.tfchain.new(name='my_client', network_type='TEST')
JSX> w = c.wallets.get("my_wallet")
Mon 03 13:24:37 BCDB.py          - 428 - bcdb:bcdb                          : load model:jumpscale.tfchain.wallet
JSX> w.address
'01d761561e7203276ef2944628bfde5bfcabf0960b69eda69ac1d317bcdcc53af06a0fd08c5f91'
```
 
# 2. get some test TFT token on our faucet 


Get the address of your wallet

```python
JSX> w.address
'01d761561e7203276ef2944628bfde5bfcabf0960b69eda69ac1d317bcdcc53af06a0fd08c5f91'
```

Head to https://faucet.testnet.threefoldtoken.com/ and fill the from with your wallet address.
Then check the balance on your wallet, after a couple of minutes you should see the `300 TFT` from the faucet.

```python
JSX> w.balance
wallet balance on height 251953 at 2019/04/12 09:39:36
0 TFT available and 0 TFT locked
Unconfirmed: 300 TFT available 0 TFT locked

[... wait some time ...]

JSX> w.balance
wallet balance on height 251955 at 2019/04/12 09:40:50
300 TFT available and 0 TFT locked
```

# 3.Register a ThreeBot

Creating a new 3bot record can be done as follows:

- `months`: for how long time do you want your 3bot, you pay for that amount of time (default is 1, can be from 1 to 24)
- `names`: list of names which will be used later to identify your 3bot
- `addresses`: list of addresses
- `key_index`: optional key index

**TO BE REMOVED result= w.threebot.record_new(1,["robot2000.sonnom"],["robot2000.org"])**

```python
JSX> result = w.threebot.record_new(
    months=1,
    names=["your3bot.name"],
    addresses=["your3bot.org"])


# transaction that was created, signed and if possible submitted
JSX> result.transaction
transaction V144 c16b76f646c64b6464b646479747f99989ec98985647

# True if submitted, False if not possible due to lack of signatures in MultiSig Coin Inputs
JSX> result.submitted
True
```

you can then check your 3bot registration transaction on the [testnet explorer]
(https://explorer.testnet.threefoldtoken.com/)
You can search the 3bot by name. Here we would enter my3bot.example and click the search button. You should see the detail about the 3bot and a link to the creation transaction.


For mode detail about the 3Bot registration and updates, [go to the full documentation](https://github.com/threefoldtech/jumpscaleX/blob/development/Jumpscale/clients/blockchain/tfchain/README.md#create-and-manage-3bot-records)

**You'll need to wait some time before your 3bot being available.**

# 4. Rent a virtual machine running our light weight, secure and super efficient OS called zero OS on the TF grid

First we should look for a farm that provide what we look for. We have a convenient [website for capacity](https://capacity.threefoldtoken.com) selection. Let's say that we need at least 2 CPU 4GiB RAM and we need it to be located in austria. We just have to move a few sliders around and we got the [results](https://capacity.threefoldtoken.com/?cru=2&mru=4&country=Austria&farmer=)
The first result is the node ac1f6b84a330 from the green edge cloud.austria.vienna  Farmer located in Wien (Austria). Click on the details button if you want more information on that node.

Now that we have the node id that suits our need we will book the capacity:

```python
JSX> result = w.capacity.reserve_zos_vm(
    email='user@email.com',       # the email on which you will received the connection information
    threebot_id='your3bot.name', # your threebot id, it can be any of the names you gave to your 3bot
    location='ac1f6b84a330',         # name of the farm or node id where to deploy the workload
    size=2                        # each workload have a different size available
)
```

**TO BE REMOVED result = w.capacity.reserve_zos_vm('ben@cogarius.com','my3bot2.example', 'ac1f6b84a330', 2)**

**Be sure to enter a valid email as we will receive the IP of our reserved virtual machine by mail.**  

As soon as it is ready, usually within a few minutes, you will receive an email with the connection information.


# 5. Connect to your virtual machine

Any workload deployed on the grid will be reachable on the public threefold network. This also means any workload in this network is able to communicate to any other workload deployed anywhere else on the grid, you can see it as the internet of the grid. As long as you don't have to expose your services to the outside of the grid, this network is all you need to use.

This public threefold network is a zero tier public network with the id `9bee8941b5717835`

- Download and install the [zerotier application](https://www.zerotier.com/download.shtml).
- connect to the network `$sudo zerotier-cli join 9bee8941b5717835`
- verify that you are connected by listing the zerotier networks `$sudo zerotier-cli listnetworks` you should see `9bee8941b5717835 tfgrid_public 36:f5:2f:5b:f6:b9 OK` in the output

if you want to quit the network `$sudo zerotier-cli leave 9bee8941b5717835`

Previously when we booked a virtual machine we received a mail that contains a 0-bot url. Now that we are connected we can reach that url e.g., `0-robot url: http://10.244.28.174:6600`. If you browse that url you should be able to see the 0-robot homepage.

Inside the mail you will also find your zos ip e.g.,`0-OS address: 10.244.28.174:6379` . You can use Kosmos shell to connect to it.
```python
$ python3 install/jsx.py container-kosmos
JSX> vm = j.clients.zos.get("zos", host="${your_zos_ip_here_without_the_port}")

# Check for connectivity
JSX> vm.ping()
'PONG Version: master @Revision: b1a1a737352fce69fd71de5f8cf1ae175f4bdcab'
```

more informations about threefold networks [here](https://github.com/threefoldtech/home/blob/master/docs/threefold_grid/networks.md#public-threefold-network-9bee8941b5717835)

# 6. Convert a docker file to a flist

Zero-OS containers are booted using a flist. A flist is basically a recipe of files and folders with pointers to the actual content of the filesystem with which the container is started. These files will get downloaded from the storage backend (typically the [Zero-OS Hub](https://hub.grid.tf/)) when needed.

In this tutorial we will create a flist ourselves, upload it to the Zero-OS Hub, and then use it to start a Zero-OS container to which we'll connect to over its ZeroTier management network.

We'll use a [simple website](https://hub.docker.com/r/nginxdemos/hello/) served by nginx to illustrate creating a flist.

So there are basically two steps:

 * Create the flist
 * Start the container

## 6.1 Creating the flist

Creating a flist is done in two steps:

* First we need to assemble the files and folders we need in the resulting filesystem into a tar.gz archive locally
* Then we need to publish that archive to the hub (https://hub.grid.tf)
The second step will actually result in the creation the flist.

As we already have a docker image we will take advantage of our [docker to flist](https://hub.grid.tf/docker-convert) application. It will automatically create the tar.gz archive and publish it on the hub for us !

Go to the [docker converter page](https://hub.grid.tf/docker-convert) and login (you will need to register first).

Then enter the docker image `nginxdemos/hello` in the corresponding input field and click the __convert docker image__ button.
You should see a success message with your flist url like this

```
Well done
Your flist nginxdemos-hello-latest.flist is available.

To start a container, use the following informations:

Source: https://hub.grid.tf/ben_mat_1/nginxdemos-hello-latest.flist
Storage: zdb://hub.grid.tf:9900
```

## 6.2 Start the container

We will create a container on our previsously reserved zos virtual machine.
If you can connect to your zos vm (see above) you can start making a container with our newly created flist.

```python
$ python3 install/jsx.py container-kosmos
JSX> vm = j.clients.zos.get("zos", host="${your_zos_ip_here_without_the_port}")

JSX> vm.containers.create(name="simple-nginx-website", flist="https://hub.grid.tf/ben_mat_1/nginxdemos-hello-latest.flist", ports={'8081':80})
JSX> site = vm.containers.get(name="simple-nginx-website")
JSX> site.is_running()
True
```
Note that we have mapped the port 80 on the container to the port 8081 on the host vm _ports={host:container}_

That's it ! If everything works as expected, you should be able to reach your nginx served website via http://[your_zos_ip]:8081

### Stream logs
First we need to find the id of the nginx process running in our container
```python
JSX> site.client.job.list()
[
    {'cpu': 0, 'rss': 3555328, 'vms': 14069760, 'swap': 0, 'starttime': 1559737984120, 'cmd': {'id': 'entry', 'command': 'core.system', 'arguments': {'args': ['-g', 'daemon off;'
                ], 'dir': '/', 'env': {'NGINX_VERSION': '1.13.8', 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
                }, 'name': 'nginx'
            }, 'queue': '', 'stream': False, 'tags': None
        }, 'pid': 9
    },
]
```
Here above we can see that the nginx process has the id _entry_.
Let's stream the output of the process
```python
JSX>sub = vm.client.subscribe('entry')
JSX>sub.stream()
10.244.211.254 -[1/Jun/2019:13:55:49 ] "GET / HTTP/1.1" 200 7225 "-" "Mozilla/5.0 (X11; Linux x86_64) Chrome/"
```

If you want to create your flist without using the docker converter you can follow these steps [here](https://github.com/threefoldtech/home/blob/dd7e396a921c74ccfa2c082e34af95c5a28e314e/.archives/zero-os/docs/tutorials/Create_a_Flist_and_Start_a_Container.md)

# 7. Go further with Jumpscale X

## What can we do with it ?

 * Connect and interact with the ThreeFold blockchain (TFT token)
 * provision virtual machines on the ThreeFold grid
 * deploy containers
 * build (builders) and deploy flist (light weight and secure container)
and much more 

Shell interface is intuitive and doesn't need you to learn a syntax.
You have builtin types schema and database (BCDB wich will be decentralized using erasure coding and it is based on redis protocol more efficient than rest can do pipeline etc ..) 

for instance you can define schema (data structure) like this 
```python
my_schema_text = """
@url = my.first.schema.1
mynumber = 42
mydate = 0 (D)
mylist = "1,2,3" (L)
mybool = 1 (B)
mystring= "yolo" (S) #you only live once
mymoney = "10 USD" (N)
myenum = "red,green,blue" (E) #first one specified is the default one
mydictionary = {"number": 468} (dict)
"""
my_schema_object = j.data.schema.get_from_text(my_schema_text)
my_schema_instance = my_schema_object.new()
you can then do 
my_schema_instance.mynumber
it will answer 
42
my_schema_instance.mybool = True
my_schema_instance.mybool = true
my_schema_instance.mybool = 1
my_schema_instance.mybool = "true"
```

they will all have the same result

now try my_schema_instance.mymoney.value_currency("eur") 
play around and try these commands and check the value or the property
```python
my_schema_instance.mylist = "yolo,42,kawai"
my_schema_instance.mylist = [1,[2,5],"yolo"] 
my_schema_instance.myenum = 2
my_schema_instance.mymoney = "10k GBP"
my_schema_instance.mymoney.usd
my_schema_instance.mymoney = my_schema_instance.mymoney * "10%"
my_schema_instance.mydate = "18/04/1980"
my_schema_instance.mydate = "01/18"
my_schema_instance.mydate = "+4d"
my_schema_instance.mydictionary["number"]
my_schema_instance.mydictionary["string"] = "iolo"
```


JSX relies on several Domain Specific Language like the one used by the schema this approach is more efficient than a librairie because you don't need to be a developer to use it.

Builders /sandbox/code/github/threefoldtech/jumpscaleX/docs/Internals/builders 
are a way to create flist 
flist can be deploy inside a zos and package an application basically 
flist can be built on flist
take a look at jumpscale/builders

For the coders who develop JSX 
we need to use JSX to get inspired by it and to know all the functions it can provide. What we see now is coders that uses python to create builders instead of using the fucntions built in in jsx that are more efficient 
self.build(reset=reset)
bin_path = self.tools.joinpaths(self.package_path, "build", "bin", "geth")
bin_dest = self.tools.joinpaths(sandbox_dir, 'sandbox', 'bin')
self.tools.dir_ensure(bin_dest)
self.tools.file_copy(bin_path, bin_dest)


## How it works
The install application will create an image and start a docker container on your machine. It will bind a volume between the directory that holds the JSX code and the container (at /sandbox/code). You will be able to connect securely via ssh to this container and launch kosmos the shell to .
