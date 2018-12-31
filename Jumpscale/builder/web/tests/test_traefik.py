import pytest
from Jumpscale import j

@pytest.mark.integration
def test_main(self=None):
    """test traefik installation

    to run:
    js_shell 'j.builder.web.traefik._test(name="traefik")'
    """

    if not j.sal.process.checkInstalled(j.builder.web.traefik.NAME):
        j.builder.web.traefik.install(reset=True)

    # try to start/stop
    tmux_pane = j.builder.web.traefik.start()
    tmux_process = tmux_pane.process_obj
    child_process = tmux_pane.process_obj_child
    assert child_process.is_running()
    j.builder.web.traefik.stop(tmux_process.pid)

