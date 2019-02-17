# GoogleSlides tool

based on [slides2html](https://github.com/threefoldtech/slides2html) to export slides of certian presentation to PNG images with optional background option.



## Example usage
```ipython
j.tools.googleslides.export('https://docs.google.com/presentation/d/1N8YWE7ShqmhQphT6L29-AcEKZfZg2QripM4L0AK8mSU/edit#slide=id.p', credfile='/root/service_credentials.json', serviceaccount=True, background='https://docs.google.com/presentation/d/1F6abB7ceOROpmbaMIWcx9RNbW_oIiLg8B5J77M5hy3s
/edit#slide=id.p', websitedir="/tmp/revealsite")
```

- `slideid` presentation id (or full url)
- `credfile` service account credentials (for server applications) or normal account oauth credentials
- `serviceaccount` tell the application if it's using serviceaccount credentials. (False by default) 
- `background` optional background for all the exported images
- `websitedir` reveal.js website directory
 