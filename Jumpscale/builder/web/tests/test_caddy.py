import pytest
from Jumpscale import j

@pytest.mark.integration
def test_main(self=None):
    """test caddy installation

    to run:
    js_shell 'j.builder.web.caddy._test(name="caddy")'
    """

    if not j.sal.process.checkInstalled(j.builder.web.caddy.NAME):
        j.builder.web.caddy.stop()
        j.builder.web.caddy.build(reset=True)
        j.builder.web.caddy.install()
        j.builder.web.caddy.sandbox()

    # try to start/stop
    tmux_pane = j.builder.web.caddy.start()
    tmux_process = tmux_pane.process_obj
    child_process = tmux_pane.process_obj_child
    assert child_process.is_running()
    assert j.sal.nettools.waitConnectionTest("localhost", 2015)

