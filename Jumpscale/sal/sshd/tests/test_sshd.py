import subprocess 
from Jumpscale.sal.tls.TLS import TLS
from Jumpscale import j
import uuid
OP_ADD = '+'
OP_DEL = '-'
OP_ERS = '--'

def test_add_key():
    random_key =  str(uuid.uuid4()).replace('-', '')[:10]
    j.sal.sshd.addKey(random_key)
    assert random_key not in j.sal.sshd.keys    
    j.sal.sshd.commit() 
    assert random_key in j.sal.sshd.keys    
    authorized_keys = j.sal.sshd.ssh_authorized_keys_path.bytes()
    assert random_key in authorized_keys

def test_remove_key():
    random_key =  str(uuid.uuid4()).replace('-', '')[:10]
    j.sal.sshd.addKey(random_key)
    j.sal.sshd.commit()
    j.sal.sshd.deleteKey(random_key)
    assert random_key in j.sal.sshd.keys    
    j.sal.sshd.commit()
    assert random_key not in j.sal.sshd.keys    
    authorized_keys = j.sal.sshd.ssh_authorized_keys_path.bytes()
    assert random_key not in authorized_keys

def test_remove_all_keys():
    random_key1 =  str(uuid.uuid4()).replace('-', '')[:10]
    random_key2 =  str(uuid.uuid4()).replace('-', '')[:10]
    j.sal.sshd.addKey(random_key1)
    j.sal.sshd.addKey(random_key2)
    j.sal.sshd.commit()
    assert random_key1 in j.sal.sshd.keys    
    j.sal.sshd.erase()
    j.sal.sshd.commit()
    assert random_key1 not in j.sal.sshd.keys    
    assert random_key2 not in j.sal.sshd.keys    
    authorized_keys = j.sal.sshd.ssh_authorized_keys_path.bytes()
    assert random_key1 not in authorized_keys
    assert random_key2 not in authorized_keys
