# template for how to build components or servers into jumpscale

## goals

- use the new config manager which has lots less code & is strongly typed
- takes care of all building & installing in development mode
- a consistent way how to build & run in development mode
- allow 100% automated testing

## remarks

- we don't use prefab any longer
    - we can copy lots of code from prefab ofcourse
- this is not intended to ever be used in production
- only support ubuntu 18.04 for now
- can be used to build components or servers

## relation to production

- goal is that once the installation/building/sandboxing is done we can create an flist
-  the flist allows us to run the packaged result in a zero-os

## tips

- can use small bash snippets, remember {} can be used to insert e.g. dir locations
- investigate the template code, try to be consistent
