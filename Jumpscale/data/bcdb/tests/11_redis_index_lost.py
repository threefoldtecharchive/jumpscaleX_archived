from Jumpscale import j


def main(self):
    """
    to run:
    kosmos 'j.data.bcdb.test(name="redis_index_lost")'

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
    m = bcdb.model_get_from_schema(SCHEMA)
    m.reset()

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

    assert "test" in j.data.bcdb._config

    j.data.bcdb.bcdb_instances = {}  # make sure we don't have instances in memory

    # stop redis
    j.core.redistools.core_stop()
    assert j.core.redistools.core_running() == False

    db = j.core.redistools.core_get()
    assert j.core.redistools.core_running()

    # check the redis is really empty
    assert j.core.db.keys() == []

    bcdb = j.data.bcdb.get("test")
    m = bcdb.model_get_from_schema(SCHEMA)

    assert len(m.find()) == 10
    r = m.get_by_name("myuser_8")
    assert r[0].addr == "something:8"

    self._log_info("TEST DONE")
    return "OK"
