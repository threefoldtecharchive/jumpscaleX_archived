from Jumpscale import j
from unittest import TestCase


def main(self):
    """
    to run:
    kosmos 'j.data.bcdb.test(name="vfs")'

    """

    SCHEMA = """
    @url = threefoldtoken.wallet.test
    name* = "wallet"
    addr = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    
    """
    # md5 = "cbf134f55d0c7149ef188cf8a52db0eb"
    # sid = "7"

    bcdb = j.data.bcdb.get("test")
    bcdb.reset()
    m = bcdb.model_get_from_schema(SCHEMA)
    test_case = TestCase()
    for i in range(10):
        o = m.new()
        assert o._model.schema.url == "threefoldtoken.wallet.test"
        o.addr = "something:%s" % i
        o.email = "myemail"
        o.name = "myuser_%s" % i
        o.save()

    # we now have some data
    assert len(m.find()) == 10
    r = m.get_by_name("myuser_8")
    assert r[0].addr == "something:8"
    vfs = j.data.bcdb._get_vfs("test")

    with test_case.assertRaises(Exception):
        r = vfs.get("test/schema/md5")
        r = vfs.get("test/schema/sid/5/78")
        r = vfs.get("test/data/md5")
        r = vfs.get("test/data/2/md6")
    r = vfs.get("test/data/1")
    identifier_folders = vfs.serializer.loads(r.list())
    assert (
        len(identifier_folders) == 3
        and "sid" in identifier_folders
        and "url" in identifier_folders
        and "hash" in identifier_folders
    )
    r = vfs.get("data/1/url")
    urls = vfs.serializer.loads(r.list())
    assert (
        len(urls) == 9
        and "jumpscale.bcdb.circle.2" in urls
        and "jumpscale.bcdb.acl.circle.2" in urls
        and "threefoldtoken.wallet.test" in urls
    )
    r = vfs.get("/data/1/url/threefoldtoken.wallet.test/")
    urls = vfs.serializer.loads(r.list())
    assert len(r.list()) == 10
    print(r)
    self._log_info("TEST DONE")
    return "OK"
