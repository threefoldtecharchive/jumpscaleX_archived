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

    assert len(bcdb.get_all()) == 0

    assert len(bcdb.meta.data.schemas) == 7
    s = bcdb.meta.data.schemas[-1]
    assert s.url == "despiegk.test"

    m = bcdb.model_get_from_url("despiegk.test")

    schema_text = """
    @url = jumpscale.schema.test.a
    category*= ""
    txt = ""
    i = 0
    """
    s = j.data.schema.get_from_text(schema_text)

    assert s.properties_unique == []

    bcdb.meta._schema_set(s)

    assert len(bcdb.meta.data.schemas) == 8

    assert "jumpscale.schema.test.a" in j.data.schema.url_to_md5
    assert "jumpscale.bcdb.circle.1" in j.data.schema.url_to_md5

    schema = bcdb.model_get_from_url("jumpscale.schema.test.a")
    o = schema.new()

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

    assert "jumpscale.schema.test.a" in j.data.schema.url_to_md5
    assert "jumpscale.bcdb.circle.1" in j.data.schema.url_to_md5

    s0 = j.data.schema.get_from_url_latest(url="jumpscale.schema.test.a")
    s0_sid = s0.sid + 0  # to make sure we have copy

    model = bcdb.model_get_from_schema(schema=s0)

    assert bcdb.get_all() == []  # just to make sure its empty

    assert len(bcdb.meta.data._ddict["schemas"]) == 8

    a = model.new()
    a.category = "acat"
    a.txt = "data1"
    a.i = 1
    a.save()

    a2 = model.new()
    a2.category = "acat2"
    a2.txt = "data2"
    a2.i = 2
    a2.save()

    myid = a.id + 0
    assert myid == 1

    assert a._model.schema.sid == s0_sid

    schema_text = """
    @url = jumpscale.schema.test.a
    category*= ""
    txt = ""
    i = 0
    """
    # lets upgrade schema to float
    s_temp = j.data.schema.get_from_text(schema_text)

    assert len(bcdb.meta.data._ddict["schemas"]) == 8  # should be same because is same schema, should be same md5
    assert s_temp._md5 == s0._md5

    schema_text = """
    @url = jumpscale.schema.test.a
    category*= ""
    txt = ""
    i = 0
    """
    # lets upgrade schema to float
    s2 = j.data.schema.get_from_text(schema_text)

    model2 = bcdb.model_get_from_schema(schema=s2)

    assert len(bcdb.meta.data._ddict["schemas"]) == 8  # acl, user, circle, despiegktest and the 1 new one

    s2_sid = s2.sid + 0

    assert s2_sid == s0_sid  # means a new sid was created

    a3 = model2.new()
    a3.category = "acat3"
    a3.txt = "data3"
    a3.i = 3
    a3.save()
    assert a3.i == 3.0
    assert a2.i == 2  # int
    assert a3._model.schema.sid == s2_sid  # needs to be the new sid

    assert len(model2.get_all()) == 3  # needs to be 3 because model is for all of them
    assert len(model.get_all()) == 3  # needs to be 3 because model is for all of them

    all = model2.get_all()

    a4 = model2.get(all[0].id)
    a4_ = model.get(all[0].id)
    assert a4_ == a4
    a5 = model2.get(all[1].id)
    a6 = model.get(all[2].id)
    a6_ = model.get(all[2].id)
    assert a6_ == a6

    assert a4._model.schema.sid == s0_sid  # needs to be the original schemaid
    assert a6.id == a3.id
    assert (
        a6._model.schema.sid == s2_sid
    )  # needs to be the new one, so the object coming back has the schema as originally intended
    assert a6.i == a3.i

    return "OK"
