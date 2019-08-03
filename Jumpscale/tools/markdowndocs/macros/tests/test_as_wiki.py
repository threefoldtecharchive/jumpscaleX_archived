from Jumpscale import j

j.builders.runtimes.pip.install("webbrowser")

url = "https://github.com/threefoldtech/jumpscaleX/tree/development/docs/tools/wiki/docsites/examples/docs/"
examples = j.tools.markdowndocs.load(url, name="examples")
examples.write()

j.servers.threebot.get('test').start(background=True)

import webbrowser
webbrowser.open('localhost:8090/wiki/examples#/test_include')