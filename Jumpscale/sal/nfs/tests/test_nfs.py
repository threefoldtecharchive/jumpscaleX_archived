from Jumpscale import j
from Jumpscale.sal.nfs.NFS import NFS
from uuid import uuid4
import pytest

def test_add_remove_list_clients():
    nfs = NFS()
    home = nfs.add('/home')
    client_1 = str(uuid4()).replace('-', '')[:10]
    client_2 = str(uuid4()).replace('-', '')[:10]
    home.addClient(client_1, 'rw,sync')
    home.addClient(client_2)
    with pytest.raises(Exception):
        home.addClient(client_1)

    assert home.clients[0][0] == client_1
    assert home.clients[0][1] == 'rw,sync'
    home.removeClient(client_1)
    with pytest.raises(Exception):
        home.removeClient(client_1)
    for client in home.clients:
        assert client_1 not in client

def test_add_remove_paths():
    nfs = NFS()
    home = nfs.add('/home')
    var = nfs.add('/var')
    etc = nfs.add('/etc')
    with pytest.raises(Exception):
        home = nfs.add('/home')

    assert '/home' == nfs.exports[0].path
    assert '/var' == nfs.exports[1].path
    assert '/etc' == nfs.exports[2].path
    nfs.delete('/home')
    with pytest.raises(Exception):
        nfs.delete('/home')
    for export in nfs.exports:
        assert '/home' not in export.path
    nfs.erase()
    assert nfs.exports  == []
