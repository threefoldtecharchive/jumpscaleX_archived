# Builders guidlines

## Builder tools 
Builder tools is a set of tools to perform the common tasks in your builder (e.g read a file
, write to a file, execute bash commands and many other handy methods that you will probably need in your builder)

[methods & properties of the tools lib](BuildersInternalToolsLib.md)

use them as much as you can !!!

## methods you should implement in your builder

### build

- builds from source code
- sometimes result is directly in sandbox (for certain components no choice e.g. openresty)
- sometimes result is in a build directory

### install

- copy relevant (only required) files to sandbox (bin/lib/...)

### test()

-  a basic test to see if the build was successfull
- required build(), install() before

### start()

- start (for debug purposes) the server component (if it is a server component)
- no parameters, its just default parameters to test an build

### stop()

- only for servers

### sandbox(destination_dir="tmp/builder/{self.NAME}", flist=True, zhub_instance=None)

this method should be responsible for collecting all bins and libs and dirs that was a result
of the build and copy it to `destination_dir` in the same directory structure.  
example:  
a binary loacted in `/sanbox/bin/{name}` should be copied to `{destinatrion_dir}/sandbox/bin/{name}`

afterward if `flist=True` this method should call `self.flist_create(sandbox_dir,zhub_instance)` which is a method 
implemented in the base builder class which will tar the sandbox directory and upload it the hub using the provided 
zhub instance

### clean()

removes all files as result from building 

### uninstall()

optional, removes installed, build & sandboxed files


## what not to do

- do not model metadata in e.g. _bins ...
