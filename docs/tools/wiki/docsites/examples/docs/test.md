## same repo
!!!include("threefoldtech:jumpscaleX(master):test_src.md", remarks_skip=True)

!!!include("threefoldtech:jumpscaleX(master):test_src.md", header_levels_modify=2)



## external repos
!!!include("abom:test_custom_md:test_src.md!A")

```
!!!include
link = "abom:test_custom_md:docs/test_src.md!B"
```


```!!!dot
 graph graphname {
     a -- b -- c;
     b -- d;
 }
```

actual content

[circle template](threefoldfoundation:info_foundation(development):/docs/circles/circle_template.md)
[circles](threefoldfoundation:info_foundation(development):/docs/circles)
