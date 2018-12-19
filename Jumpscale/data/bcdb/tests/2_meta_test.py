from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="meta_test")'

    """


    c=j.servers.zdb.start_test_instance(destroydata=True,namespaces=["test"])


    bcdb,model = self._load_test_model()


    bcdb.meta._logger_enable()

    print(bcdb.meta)

    SCHEMA = j.core.text.strip("""
    @url = jumpscale.schema.test.a
    category*= ""
    data = ""
    """)
    s = j.data.schema.get(SCHEMA)

    id = bcdb.meta.schema_set(s)

    bcdb.meta.data.schemas[0]

    assert bcdb.meta.data.schemas[-2].url=="despiegk.test"
    assert bcdb.meta.data.schemas[-1].url=="jumpscale.schema.test.a"

    l0=len(bcdb.meta.data.schemas)

    bcdb.meta.reset()

    assert len(bcdb.meta.url2sid) == 2

    assert bcdb.meta.data.schemas[-2].url=="despiegk.test"
    assert bcdb.meta.data.schemas[-1].url=="jumpscale.schema.test.a"

    assert "jumpscale.schema.test.a" in j.data.schema.schemas


    cl1 = j.clients.zdb.client_get("test", addr="localhost", port=9901, secret="1234")
    cl1.flush(meta=bcdb.meta) #remove the data


    data1 = bcdb.zdbclient.redis.get(b'\x00\x00\x00\x00')
    data2 = bcdb.zdbclient.get(0)
    assert data1==data2
    assert len(data2)>100

    #now completely remove the db, is fully empty
    cl1.flush()
    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9901, secret="1234")
    assert cl1.get(key=0) == None

    bcdb.meta.reset() #make sure we reload from data


    assert bcdb.meta.data._ddict == {'schemas': []}

    bcdb.zdbclient.set(data2)
    bcdb.meta.reset() #make sure we reload from data

    s = bcdb.meta.schema_get_from_url("jumpscale.schema.test.a")
    assert s.url == "jumpscale.schema.test.a"

    return("OK")
