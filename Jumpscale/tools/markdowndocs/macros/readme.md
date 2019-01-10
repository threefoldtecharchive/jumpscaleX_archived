# macro's

## how to call the macro

can put the macro in code block or without

![](images/include_example.png)

![](images/include_example_2.png)

there should be no language specified on the ``` line

when there are many arguments then there is also a multiline one

```python
!!!include
name = "Fixer.py"
repo = "https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tools/fixer"
docstring = "write_changes"
```

the arguments need to be a dict in toml format

in this case the include macro will be called with the 3 arguments specified: name, repo, docstring



