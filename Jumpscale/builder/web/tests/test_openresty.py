import pytest
from Jumpscale import j


@pytest.mark.integration
def test_main(self=None):
    """test openResty installation

    to run:
    kosmos 'j.builder.web.openresty._test(name="openResty")'
    """

    if not j.sal.process.checkInstalled(j.builder.web.openresty.NAME):
        # j.builder.web.openresty.stop()
        # openresty is built with lapis in lua builder
        j.builder.runtimes.lua.build(reset=True)
        j.builder.runtimes.lua.install()

    # try to start/stop lapis with lua
    tmux_pane = j.builder.web.openresty.start()
    tmux_process = tmux_pane.process_obj
    child_process = tmux_pane.process_obj_child
    assert child_process.is_running()
    assert j.sal.nettools.waitConnectionTest("localhost", 8080)
