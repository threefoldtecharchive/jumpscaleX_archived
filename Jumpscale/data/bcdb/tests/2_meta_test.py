from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="meta_test")'

    """

    # get zdb client

    c = j.clients.zdb.client_admin_get(port=9901)
    c.namespace_new("test", secret="1234")
    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9901, secret="1234")
    cl1.flush()

    bcdb, _ = self._load_test_model()

    print(bcdb.meta)

    schema = j.core.text.strip(
        """
    @url = jumpscale.schema.test.a
    category*= ""
    data = ""
    """
    )
    s = j.data.schema.get(schema)

    bcdb.meta.schema_set(s)

    bcdb.meta.data.schemas[0]

    assert len(bcdb.meta.sid2schema) is 5

    assert "jumpscale.schema.test.a" in j.data.schema.schemas
    assert "jumpscale.bcdb.group" in j.data.schema.schemas

    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9901, secret="1234")
    cl1.flush(meta=bcdb.meta)  # remove the data

    redis = cl1.redis
    data = redis.get(b"\x00\x00\x00\x00")
    assert len(data) > 100

    # now completely remove the db, is fully empty
    cl1.flush()
    assert redis.get(b"\x00\x00\x00\x00") == None
    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9901, secret="1234")
    assert cl1.get(key=0) is None

    bcdb.meta.reset()  # make sure we reload from data

    assert bcdb.meta.data.schemas == []

    assert redis.get(b"\x00\x00\x00\x00") == None
    assert redis.set("", value=data) == b"\x00\x00\x00\x00"
    bcdb.meta.reset()  # make sure we reload from data

    assert "jumpscale.schema.test.a" in j.data.schema.schemas
    assert "jumpscale.bcdb.group" in j.data.schema.schemas

    return "OK"
