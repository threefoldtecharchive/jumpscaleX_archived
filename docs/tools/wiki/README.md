# Markdown docsites:

[Docsites](docsites/readme.md) are a collection of markdown documents, images and data files that can be generated using jumpscale `markdowndocs` tool.

The tool pre-process the given markdown directory (it adds some extension to markdown like custom link format and macros), also, it verifies and follows all the links and download it if needed, so you end up having a static directory that can be served using e.g. **openresty**.

### Markdown extensions:
* [Custom Link format](links.md) to make it easy to reference other documents and files.
* [Macros](docsites/macros/readmen.md):
    * [data](docsites/macros/data.md): to add data that can be
    * [include](docsites/macros/include.md)


### Tool usage

Given a markdown documents directory (a link to repository), the tool will pull, pre-process and generate the docsite.

Example:

```python
url = "https://github.com/threefoldtech/jumpscaleX/tree/development_markdown/docs/tools/wiki/docsites/examples/docs"
docsite = j.tools.markdowndocs.load(url, name="test_example"
docsite.write()
```

This will pull the repo at the branch specified, then generate a docsite at `$DIR_VAR/docsites` with the name `test_example`.


### Openresty
* TODO (about serving docsite directory using openresty)

### Docsites at front-end
* TODO (about docsite.js)

#### Wiki
* TODO (about docsify.js)
