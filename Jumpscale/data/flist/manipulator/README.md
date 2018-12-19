# Flist manipulator

This class allow you to update the content of an existing flist

example:
```python
# get a manipulator object from an existing flist 
manip = j.tools.flist.manipulator.get('/tmp/flist_test')

# you can inspect the file from the existing flist
# list all dirs from the root path
dirs = manip.root.dirs()
# only return the directories that start with 'abc'
abc_dirs = manip.root.dirs('abc*')

# list files from the root directory
files = manip.root.files()

# create a new directory at the root of the flist
etc = manip.root.mkdir('ect')
# copy /etc/app/config.yaml from the local system into the flist at /etc/config.yaml
ect.copy('/etc/app/config.yaml)

# once you are done with editing the flist, upload the new content of the added file to the hub
# this method task the instance name of a hudirect client that needs to be configure in the
# config manager of jumpscale
flist_path = manip.upload_diff('main')
```
