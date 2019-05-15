from Jumpscale import j
from Jumpscale.sal.nfs.NFS import NFS
from uuid import uuid4
import pytest, os


def test_add_remove_list_clients():
    found = os.path.exists("/etc/exports")
    if found:
        with open("/etc/exports", "r") as f:
            file = f.read()

    open("/etc/exports", "w+").close()
    nfs = NFS()
    home = nfs.add("/home")
    client_1 = str(uuid4()).replace("-", "")[:10]
    client_2 = str(uuid4()).replace("-", "")[:10]
    home.client_add(client_1, "rw,sync")
    home.client_add(client_2)
    with pytest.raises(Exception):
        home.client_add(client_1)

    assert home.clients[0][0] == client_1
    assert home.clients[0][1] == "rw,sync"
    home.client_remove(client_1)
    with pytest.raises(Exception):
        home.client_remove(client_1)
    for client in home.clients:
        assert client_1 not in client

    if found:
        with open("/etc/exports", "w+") as f:
            f.write(file)


def test_add_remove_paths():
    found = os.path.exists("/etc/exports")
    if found:
        with open("/etc/exports", "r") as f:
            file = f.read()

    open("/etc/exports", "w+").close()
    nfs = NFS()
    home = nfs.add("/home")
    var = nfs.add("/var")
    etc = nfs.add("/etc")
    with pytest.raises(Exception):
        home = nfs.add("/home")

    assert "/home" == nfs.exports[0].path
    assert "/var" == nfs.exports[1].path
    assert "/etc" == nfs.exports[2].path
    nfs.delete("/home")
    with pytest.raises(Exception):
        nfs.delete("/home")
    for export in nfs.exports:
        assert "/home" not in export.path
    nfs.erase()
    assert nfs.exports == []

    if found:
        with open("/etc/exports", "w+") as f:
            f.write(file)


def main(self=None):
    """
    to run:

    kosmos 'j.sal.nfs._test(name="nfs")'

    """
    test_add_remove_paths()
    test_add_remove_list_clients()
