import pytest
from Jumpscale import j

@pytest.mark.integration
def test_main(self=None):
    """test coredns installation

    to run:
    js_shell 'j.builder.network.coredns._test(name="coreDns")'
    """

    if not j.sal.process.checkInstalled(j.builder.network.coredns.NAME):
        # j.builder.network.coredns.stop()
        # j.builder.network.coredns.build(reset=True)
        j.builder.network.coredns.sandbox(reset=True)

    # try to start/stop
    tmux_pane = j.builder.network.coredns.start()
    tmux_process = tmux_pane.process_obj
    child_process = tmux_pane.process_obj_child
    assert child_process.is_running()