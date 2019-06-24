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
        r = vfs.get("schemas/1")
        r = vfs.get("test/schema/sid/5/78")
        r = vfs.get("test/data/md5")
        r = vfs.get("test/data/2/md6")

    r = vfs.get("test/data/1")
    identifier_folders = [i for i in r.list()]
    print(identifier_folders)
    assert (
        len(identifier_folders) == 3
        and "sid" in identifier_folders
        and "url" in identifier_folders
        and "hash" in identifier_folders
    )
    r = vfs.get("data/1/url")
    urls = [i for i in r.list()]
    print(urls)
    assert (
        len(urls) == 9
        and "jumpscale.bcdb.circle.2" in urls
        and "jumpscale.bcdb.acl.circle.2" in urls
        and "threefoldtoken.wallet.test" in urls
    )
    r = vfs.get("/data/1/url/threefoldtoken.wallet.test/")

    objs = [i for i in r.list()]
    print(objs)
    assert len(objs) == 10
    for o in objs:
        obj = j.data.serializers.json.loads(o)
        if obj["addr"] == "something:5":
            assert obj["name"] == "myuser_5"

    r = vfs.get("/data/1/hash/cbf134f55d0c7149ef188cf8a52db0eb/12")

    obj = j.data.serializers.json.loads(r.get())

    assert obj["id"] == 12
    assert obj["addr"] == "something:2"
    assert obj["name"] == "myuser_2"
    self._log_info("TEST GET DATA DONE")

    # schema path
    r = vfs.get("schemas/sid/")
    r2 = vfs.get("schemas/hash/")
    r3 = vfs.get("schemas/url/")
    schemas = [i for i in r.list()]
    schemas2 = [i for i in r2.list()]
    schemas3 = [i for i in r3.list()]
    print(schemas)
    print(schemas2)
    print(schemas3)
    assert len(schemas) == len(schemas2) == 7
    assert len(schemas3) == 9  # multiple url link to the same schema id ?
    r = vfs.get("schemas/url/threefoldtoken.wallet.test")
    schema = r.get()
    print(schema)
    obj = j.data.serializers.json.loads(schema)
    self._log_info("TEST GET SCHEMA DONE")
    self._log_info("TODO TEST SET DELETE DATA DONE")
    self._log_info("TODO TEST SET DELETE SCHEMA DONE")
    self._log_info("TEST DONE")
    return "OK"
