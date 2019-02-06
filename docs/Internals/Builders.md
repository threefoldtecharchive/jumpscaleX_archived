

## methods 

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

### sandbox(zerohubclient)

- call sandboxing library to sandbox the solution & copy to /sandbox/var/builds/sandboxes/$name/
- the  /sandbox/var/builds/sandboxes/$name/ can then be made an flist but result path is /sandbox/... 
- results in an flist & the relevant files pushed to given zerohubclient (which uses config mgr)
- flist is in /sandbox/var/builds/sandboxes/$name/$flistname.flist

### clean()

removes all files as result from building 

### uninstall()

optional, removes installed, build & sandboxed files



## what not to do

- do not model metadata in e.g. _bins ...
