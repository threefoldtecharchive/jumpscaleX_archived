from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="meta_test")'

    """

    # get zdb client

    c = j.clients.zdb.client_admin_get()
    c.namespace_new("test", secret="1234")
    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9901, secret="1234")
    cl1.flush()

    bcdb, _ = self._load_test_model()

    bcdb.meta.logger_enable()

    print(bcdb.meta)

    schema = j.core.text.strip("""
    @url = jumpscale.schema.test.a
    category*= ""
    data = ""
    """)
    s = j.data.schema.get(schema)

    bcdb.meta.schema_set(s)

    bcdb.meta.data.schemas[0]

    def data_valid(bcdb):
        assert bcdb.meta.data.schemas[0].sid == 1
        assert bcdb.meta.data.schemas[1].sid == 2
        assert bcdb.meta.data.schemas[2].sid == 3
        assert bcdb.meta.data.schemas[3].sid == 4
        assert bcdb.meta.data.schemas[4].sid == 5
        assert bcdb.meta.data.schemas[2].url == "jumpscale.bcdb.group"
        assert bcdb.meta.data.schemas[3].url == "despiegk.test"
        assert bcdb.meta.data.schemas[4].url == "jumpscale.schema.test.a"

    data_valid(bcdb)
    bcdb.meta.reset()
    data_valid(bcdb)

    assert len(bcdb.meta.url2schema) is 5

    assert "jumpscale.schema.test.a" in j.data.schema.schemas

    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9900, secret="1234")
    cl1.flush(meta=bcdb.meta)  # remove the data

    redis = bcdb.meta._db
    data = redis.get(b'\x00\x00\x00\x00')
    assert len(data) > 100

    # now completely remove the db, is fully empty
    cl1.flush()
    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9900, secret="1234")
    assert cl1.get(key=0) is None

    bcdb.meta.reset()  # make sure we reload from data

    assert bcdb.meta.data.schemas == []

    redis.set(b'\x00\x00\x00\x00', data)
    bcdb.meta.reset()  # make sure we reload from data
    data_valid(bcdb)  # means DB was made empty and now we check if data still there, was manually put in

    return("OK")
