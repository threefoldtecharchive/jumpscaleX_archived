from Jumpscale import j


def main(self):
    """
    to run:
    kosmos 'j.data.bcdb.test(name="export")'

    """
    j.servers.zdb.test_instance_start()

    SCHEMA = """
    @url = threefoldtoken.wallet.test
    name* = "wallet"
    addr = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    
    """
    bcdb = j.data.bcdb.new("test_export")
    bcdb.reset()
    m = bcdb.model_get_from_schema(SCHEMA)
    for i in range(10):
        o = m.new()
        assert o._model.schema.url == "threefoldtoken.wallet.test"
        o.addr = "something:%s" % i
        o.email = "myemail"
        o.name = "myuser_%s" % i
        o.save()

    SCHEMA = """
    @url = threefoldtoken.wallet.test2
    name* = "wallet"
    addr = ""                   # Address    
    """

    m2 = bcdb.model_get_from_schema(SCHEMA)

    for i in range(10):
        o = m2.new()
        assert o._model.schema.url == "threefoldtoken.wallet.test2"
        o.addr = "something:%s" % i
        o.name = "myuser_%s" % i
        o.save()

    p = "/tmp/bcdb_export"

    def export_import(encr=False, export=True, remove=False):
        if export:
            j.sal.fs.remove(p)
            bcdb.export(path=p, encrypt=encr)

        obj = m2.get(3)

        bcdb.reset()

        try:
            m2.get(3)
            raise RuntimeError("should not exist")
        except:
            pass

        bcdb.import_(path=p)

        m3 = bcdb.model_get_from_schema(SCHEMA)
        obj2 = m3.get(3)

        assert obj2._ddict_hr == obj._ddict_hr
        assert obj2._data == obj._data

        assert obj._schema == obj2._schema

        if remove:
            j.sal.fs.remove(p)

    export_import(encr=False, export=True, remove=False)
    # will now test if we can import
    export_import(False, export=False, remove=True)
    # now do other test because there will be stuff changed
    export_import(encr=False, export=True, remove=True)

    # now test with encryption
    export_import(encr=True, export=True, remove=False)
    export_import(encr=True, export=False, remove=True)

    self._log_info("TEST DONE")
    return "OK"
