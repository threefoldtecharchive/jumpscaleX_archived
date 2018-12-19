
# Introduction

This is some paragraph.

Should you have any question, any remark, or if you find a bug,
or if there is something you can do with the API but not with PyGithub,
please `open an issue <https://github.com/jacquev6/PyGithub/issues>`.

```python
res = {}
for item in self.items:
    if item.type == "data" and item.name == ttype:
        res[item.guid] = item.ddict
        key = "%s__%s" % (ttype, item.guid)
        self._dataCache[key] = item
return res
```

| Format   | Tag example |
| -------- | ----------- |
| Headings | =heading1=<br>==heading2==<br>===heading3=== |
| New paragraph | A blank line starts a new paragraph |
| Source code block |  // all on one line<br> {{{ if (foo) bar else   baz }}} |

# header 1

## header 2

### (Very short) tutorial

First create a Github instance::

```toml
!!!data

title = "This one needs to be overwritten"

```

* 1
    * 2
        * 3 
        * 4
    * 5
* 6

* 7
    * 8



!!!include("ays9:events")

### Download and install

This package is in the `Python Package Index <http://pypi.python.org/pypi/PyGithub>`__,
so ``easy_install PyGithub`` or ``pip install PyGithub`` should be enough.
You can also clone it on `Github <http://github.com/jacquev6/PyGithub>`__.

### They talk about PyGithub

```toml
!!!macro1(test="1")
title = "some title in my macro"
```

- [link test](https://github.com/jacquev6/PyGithub/issues)

* http://stackoverflow.com/questions/10625190/most-suitable-python-library-for-github-api-v3
    * http://stackoverflow.com/questions/12379637/django-social-auth-github-authentication
        * http://www.freebsd.org/cgi/cvsweb.cgi/ports/devel/py-pygithub/
* https://bugzilla.redhat.com/show_bug.cgi?id=910565

```toml
!!!data

title = "TOML Example (v0.4.0)"

#------------------------------ Comments ------------------------------

# This is a full-line comment
key = "value" # This is a comment at the end of a line

#--------------------------- Key/Value Pair ---------------------------

bare_key = "value"
bare-key = "value"
1234 = "value"

arr1 = [ 1, 2, 3 ]
arr2 = [ "red", "yellow", "green" ]
arr3 = [ [ 1, 2 ], [3, 4, 5] ]
arr4 = [ "all", 'strings', """are the same""", '''type''']
arr5 = [ [ 1, 2 ], ["a", "b", "c"] ]

arr8 = [
  1,
  2, # this is ok
]


[owner]
name = "Tom Preston-Werner"
organization = "GitHub"
bio = "GitHub Cofounder & CEO\nLikes tater tots and beer."
dob = 1979-05-27T07:32:00Z # First class dates? Why not?

[database]
server = "192.168.1.1"
ports = [ 8001, 8001, 8002 ]
connection_max = 5000
enabled = true

[servers]

  # You can indent as you please. Tabs or spaces. TOML don't care.
  [servers.alpha]
  ip = "10.0.0.1"
  dc = "eqdc10"

  [servers.beta]
  ip = "10.0.0.2"
  dc = "eqdc10"


```
