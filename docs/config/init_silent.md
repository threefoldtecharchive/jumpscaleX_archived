# how to init jumpscale config


## silent

the silent configuration will 

- check that ssh-agent has 1 key loaded & if so use that one
- will try to find config git directory, if 1 found will use that one
- if no git config dir found will put in '~/jumpscale/cfg/myconfig/'


```bash
js_config init -s
```

