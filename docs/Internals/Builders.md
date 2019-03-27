# Builders guidlines

## there are 3 directories used

- /sandbox      : sandbox directory, has the files in production 
- /builddir     : is the directory used for building e.g. compilation of a C program
    - build dir should only be relevant during build step and as starting point for install step 
    - property: self.DIR_BUILD
- /packagedir   : the location from which we create an flist, files are copied in here from /sandbox (dont copy from /builddir)
  - property: self.DIR_PACKAGE

## internal properties used

- self._sandbox_dir is where the sandboxed files will reside, if not specified then its     
    - self._sandbox_dir = /tmp/builders/$NAME

## methods / properties available in each builder class

### .reset()  

reset the state of your builder, important to let the state checking restart

### .tools:  Builder tools 
Builder tools is a set of tools to perform the common tasks in your builder (e.g read a file
, write to a file, execute bash commands and many other handy methods that you will probably need in your builder)

### txt = self.replace(txt)

will replace arguments like {DIR_PACKAGE} but also arguments from  j.core.myenv.config inside the text

### .write(path,txt)

- will write and also call self._replace()

### .execute(txt)

- will write in {DIR_BUILD}/cmds/run.sh (which will replace)
- will run the {DIR_BUILD}/cmds/run.sh

[methods & properties of the tools lib](BuildersInternalToolsLib.md)

use them as much as you can !!!

they are under self.tools

### .system:  Some System Tools

see [BuildersInternalSystemLib](BuildersInternalSystemLib.md)

they are under self.system


## methods you should implement in your builder

### .build()

- builds from source code
- if possible build to separate directory, build to self.DIR_BUILD
- sometimes result is directly in sandbox (for certain components no choice e.g. openresty)
- is optional, maybe the installer uses already build packages e.g. on ubuntu 
- result: all components build which will be required by install

### .install()

- will automatically call build() at start
- copy relevant (only required) files to sandbox (bin/lib/...) from self.DIR_BUILD
- create config files if needed

### .test()

-  a basic test to see if the build was successfull
- will automatically call start() at start
- will automatically call test_api() at end, is against localhost 
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
    - j.sal...
    - j.tools...
    - self.system... 
- use the DSL in order as specified above first tools, then j.builder, then ...
- in each method you will not import python, use databases of any sort
- best practice: dont execute bash commands if primitive exists in self.tools or j...
