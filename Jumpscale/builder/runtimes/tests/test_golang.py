import pytest
from Jumpscale import j

@pytest.mark.integration
def test_main(self=None):
    """test go installation

    to run:
    js_shell 'j.builder.runtimes.golang._test(name="golang")'
    """

    if not j.sal.process.checkInstalled(j.builder.runtimes.golang.NAME):
        j.builder.runtimes.golang.install(reset=True)

    assert j.builder.runtimes.golang.is_installed

    # test go get
    j.builder.runtimes.golang.get('github.com/containous/go-bindata')
    package_path = j.builder.runtimes.golang.package_path_get('containous/go-bindata')
    j.builder.runtimes.golang.execute('cd %s && go install' % package_path)

