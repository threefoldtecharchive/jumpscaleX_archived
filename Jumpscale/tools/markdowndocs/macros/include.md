# Include macro


## arguments

```
:param name: name of the document to look for (will always be made lowercase)
:param docsite: name of the docsite
:param repo: url of the repo, if url given then will checkout 
    the required content from a git repo
:param start: will walk over the content of the file specified (name) 
    and only include starting from line where the start argument is found
:param end: will match till end

:param paragraph: if True then will include from start till next line is found which is at same prefix (basically taking out a paragraph)
:param codeblock: will put the found result in a codeblock if True
:param docstring: will look for def $name or class $name and include the docstring directly specified after it as markdown
```

## call doc from other repo

in next example we look for a doc of another docsite called jumpscale
the docsite has to be loaded before otherwise we cannot find it

in you're markdown doc do
```
!!!include("docs/install.md", repo="https://github.com/threefoldtech/jumpscaleX")
```

of using docsite name

```
!!!include(name="install.md", docsite="jumpscale")
```

the name needs to be unique

```
#this example shows more complete path
!!!include("docs/install.md")
```

if repo or docsite not mentioned then will look in current repo

```
!!!include(name="install.md",part="A"
```

## example where python code is being included

the code which is in the file Fixer.py

![](images/code_example.png)

### possibility 1: specify start line and end line

```python
!!!include
name = "Fixer.py"
repo = "https://github.com/threefoldtech/jumpscaleX/tree/master/"
start = "def find_changes"
end = "self.replacer.dir_process("
codeblock = True
```

if specified like this, its important to know that there should be no duplicate name Fixer.py otherwise the path in repo = .. needs to be specified better

### possibility 2: use the paragraph argument

```python
!!!include
name = "Fixer.py"
repo = "https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tools/fixer"
start = "def find_changes"
paragraph = True
codeblock = True
```

they will both return the lines of def find_changes... and nothing more

## can also just include a document string from a python method

- this only works for python

```python
!!!include
name = "Fixer.py"
repo = "https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tools/fixer"
docstring = "write_changes"
```
will always include as markdown without code block

Will look for classname or for def name

## any file can be included as markdown

```python
!!!include
name = "jinja2/readme.md"
repo = "https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/"
```

name van be any part of a path





