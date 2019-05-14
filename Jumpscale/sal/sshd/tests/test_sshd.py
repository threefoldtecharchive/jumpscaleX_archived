import subprocess
from Jumpscale.sal.sshd.SSHD import SSHD
from Jumpscale import j
import uuid

OP_ADD = "+"
OP_DEL = "-"
OP_ERS = "--"


def test_add_key():
    sshd = SSHD()
    random_key = str(uuid.uuid4()).replace("-", "")[:10]
    sshd.key_add(random_key)
    assert random_key not in sshd.keys
    sshd.commit()
    assert random_key in sshd.keys
    authorized_keys = sshd.ssh_authorized_keys_path.bytes().decode("utf-8")
    assert random_key in authorized_keys


def test_remove_key():
    sshd = SSHD()
    random_key = str(uuid.uuid4()).replace("-", "")[:10]
    sshd.key_add(random_key)
    sshd.commit()
    sshd.key_delete(random_key)
    assert random_key in sshd.keys
    sshd.commit()
    assert random_key not in sshd.keys
    authorized_keys = sshd.ssh_authorized_keys_path.bytes().decode("utf-8")
    assert random_key not in authorized_keys


def test_remove_all_keys():
    sshd = SSHD()
    random_key1 = str(uuid.uuid4()).replace("-", "")[:10]
    random_key2 = str(uuid.uuid4()).replace("-", "")[:10]
    sshd.key_add(random_key1)
    sshd.key_delete(random_key2)
    sshd.commit()
    assert random_key1 in sshd.keys
    sshd.erase()
    sshd.commit()
    assert random_key1 not in sshd.keys
    assert random_key2 not in sshd.keys
    authorized_keys = sshd.ssh_authorized_keys_path.bytes().decode("utf-8")
    assert random_key1 not in authorized_keys
    assert random_key2 not in authorized_keys
