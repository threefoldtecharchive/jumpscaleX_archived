# Builders guidlines

## methods / properties available in each builder class

### .reset()  

reset the state of your builder, important to let the state checking restart

### .tools:  Builder tools 
Builder tools is a set of tools to perform the common tasks in your builder (e.g read a file
, write to a file, execute bash commands and many other handy methods that you will probably need in your builder)

[methods & properties of the tools lib](BuildersInternalToolsLib.md)

use them as much as you can !!!

they are under self.tools

### .system:  Some System Tools

see [BuildersInternalSystemLib](BuildersInternalSystemLib.md)

they are under self.system


## methods you should implement in your builder

### .build()

- builds from source code
- sometimes result is directly in sandbox (for certain components no choice e.g. openresty)
- sometimes result is in a build directory
- is optional, maybe the installer uses already build packages e.g. on ubuntu 

### .install()

- copy relevant (only required) files to sandbox (bin/lib/...)
- will automatically call build() at start

### .test()

-  a basic test to see if the build was successfull
- will automatically call start() at start
- is optional

### .test_api(ipaddr="localhost")

- will test the api on specified ipaddr e.g. rest calls, tcp calls, port checks, ...

### .test_zos(zhub_client,zos_client)

- a basic test to see if the build was successfull
- will automatically call sandbox(zhub_client=zhub_client) at start
- will start the container on specified zos_client with just build flist
- will call .test_api() with ip addr of the container


### .start()

- will automatically call install() at start
- start (for debug purposes) the server component (if it is a server component)
- is optional
- will use self.startup_cmds as basis 

### .stop()

- only for servers
- is optional
- will use self.startup_cmds as basis 

### .sandbox(zhub_client)

- this method should be responsible for collecting all bins and libs and dirs that was a result
of the build and copy it to `destination_dir` in the same directory structure.  
- example: a binary loacted in `/sanbox/bin/{name}` should be copied to `{destination_dir}/sandbox/bin/{name}`
- this method will call: self._flist_create(zhub_client=zhub_client) which will create flist & upload to your zhub
- will return: the flist url 

### .clean()

- removes all files as result from building 

### .uninstall()

- optional, removes installed, build & sandboxed files


## IMPORTANT INSTRUCTIONS HOW TO CREATE A BUILDER CLASS

- do not model metadata in e.g. _bins ...
    - no properties, no hidden models, ...
- maintain actor based paradigm where every method as described above is implemented using ONLY
    - self.tools...
    - j.builder....
    - j...
    - self.system...- 
- use the DSL in order as specified above first tools, then j.builder, then ...
