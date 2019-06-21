from Jumpscale import j


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
    bcdb = j.data.bcdb.get("test")
    bcdb.reset()
    m = bcdb.model_get_from_schema(SCHEMA)

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

    self._log_info("TEST DONE")
    return "OK"
