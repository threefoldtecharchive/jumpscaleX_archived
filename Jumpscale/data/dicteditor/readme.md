## dict editor

is a convenient tool to manipulate a dict, is used to manage the jumpscale main config file.
Is also part of each jsconfig class (which has data inside).

### basic usage

```python

def test(self):
    """
    js_shell 'j.data.dict_editor.test()'
    :return:
    """
    import copy
    config = copy.copy(j.core.myenv.config) #to make sure we don't edit the jumpscale config file

    e=j.data.dict_editor.get(config)

    e.DIR_TEMP="/tmp_new"

    assert config["DIR_TEMP"]=="/tmp_new"


```
tab completion works for the editor, can change properties right away

![](images/tab_complete.png)

### when looking at the editor

you get a nicely formatted output.

![](images/e.png)

### can also use the view function

![](images/view.png)


### can also use the edit function

![](images/edit.png)

will use editor micro, make sure its installed.
After editing the file the data will be put back in the dict.

### usage as part of the jsconfig class

- works for each data object which is result of using the jumpscale schema framework.

