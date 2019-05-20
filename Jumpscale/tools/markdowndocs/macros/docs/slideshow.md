# Slideshow macro 
you can use this macro to include slides from different presentations into your docsite

# Prerequisites 
In order to use this macro you must make sure that Gdrive package is working, check the
[docs here](https://github.com/threefoldtech/digitalmeX/blob/master/packages/gdrive/README.md)

# Example
```
presentation_1 = {presentation_guid}
presentation_2 = {presentation_guid}

slide_1 = presentation_1[{slide_name_or_guid}]
slide_2 = presentation_2[{slide_name_or_guid}]
```
