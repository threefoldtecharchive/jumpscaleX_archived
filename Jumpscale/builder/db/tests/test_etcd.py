import pytest
from Jumpscale import j

@pytest.mark.integration
def test_main(self=None):
    """test etcd installation

    to run:
    js_shell 'j.builder.db.etcd._test(name="etcd")'
    """

    if not j.sal.process.checkInstalled(j.builder.db.etcd.NAME):
        j.builder.db.etcd.stop()
        j.builder.db.etcd.build(reset=True)
        j.builder.db.etcd.sandbox()

    # try to start/stop
    tmux_pane = j.builder.db.etcd.start()
    tmux_process = tmux_pane.process_obj
    child_process = tmux_pane.process_obj_child
    assert child_process.is_running()

    client = j.builder.db.etcd.client_get('etcd_test')
    j.sal.nettools.waitConnectionTest(client.host, client.port)
    client.api.put('foo', 'etcd_bar')
    assert client.get('foo') == 'etcd_bar'
    j.builder.db.etcd.stop(tmux_process.pid)

