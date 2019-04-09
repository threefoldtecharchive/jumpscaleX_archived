## same repo

### modify headers

!!!include("threefoldtech:jumpscaleX(development):test_src.md", header_levels_modify=2)

### docstrings

!!!include("threefoldtech:jumpscaleX(development):test.py", doc_only=True)

### skip remarks (lines start with hash)
!!!include("threefoldtech:jumpscaleX(development):test.py", remarks_skip=True)

### get only part A
!!!include("threefoldtech:jumpscaleX(development):test_src.md!A")


## external repo

!!!include("abom:test_custom_md:test_src.md!A")

!!!include("https://github.com/abom/test_custom_md/tree/master/docs/test_src.md")
