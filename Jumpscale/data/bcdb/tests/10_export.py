from Jumpscale import j


def main(self):
    """
    to run:
    kosmos 'j.data.bcdb.test(name="export")'

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

    SCHEMA = """
    @url = threefoldtoken.wallet.test2
    name* = "wallet"
    addr = ""                   # Address    
    """

    m2 = bcdb.model_get_from_schema(SCHEMA)
    m2.reset()

    for i in range(10):
        o = m2.new()
        assert o._model.schema.url == "threefoldtoken.wallet.test2"
        o.addr = "something:%s" % i
        o.name = "myuser_%s" % i
        o.save()

    def export_import(encr=False, export=True):
        p = "/tmp/bcdb_export"
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

        assert obj2._data == obj._data
        assert obj2._data == obj._data

        assert obj._schema == obj2._schema

    export_import()
    return "OK"

    # test we can update data, so we overwrite
    export_import(False, export=False)

    # now test with encryption
    export_import(True)

    # now get other BCDB with sqlite & import & do checks #TODO:*1

    self._log_info("TEST DONE")
    return "OK"
