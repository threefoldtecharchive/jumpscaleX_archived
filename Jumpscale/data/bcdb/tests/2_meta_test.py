from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="meta_test")'

    """
    j.servers.zdb.start_test_instance(destroydata=True)
    # get zdb client
    c = j.clients.zdb.client_admin_get(port=9901)
    c.namespace_new("test", secret="1234")
    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9901, secret="1234")
    cl1.flush()

    bcdb, _ = self._load_test_model(reset=True)

    assert len(bcdb.get_all()) == 0

    assert len(bcdb.meta._data.schemas) == 7
    s = bcdb.meta._data.schemas[-1]
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

    sid = bcdb.meta._schema_set(s)
    assert isinstance(sid, int)
    assert si

    assert len(bcdb.meta.data.schemas) == 8

    assert "jumpscale.schema.test.a" in j.data.schema.url_to_md5
    assert "jumpscale.bcdb.circle.2" in j.data.schema.url_to_md5

    schema = bcdb.model_get_from_url("jumpscale.schema.test.a")
    o = schema.new()

    cl1 = j.clients.zdb.client_get(nsname="test", addr="localhost", port=9901, secret="1234")
    cl1.flush(meta=bcdb.meta)  # remove the data

    redis = cl1.redis
    data = redis.get(b"\x00\x00\x00\x00")
    assert len(data) > 100

    assert "jumpscale.schema.test.a" in j.data.schema.url_to_md5
    assert "jumpscale.bcdb.circle.2" in j.data.schema.url_to_md5

    s0 = j.data.schema.get_from_url_latest(url="jumpscale.schema.test.a")
    s0md5 = s0._md5 + ""

    model = bcdb.model_get_from_schema(schema=s0)

    assert bcdb.get_all() == []  # just to make sure its empty

    assert len(bcdb.meta._data._ddict["schemas"]) == 10

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

    assert len([i for i in model.index._id_iterator()]) == 2

    myid = a.id + 0

    assert a._model.schema._md5 == s0md5

    schema_text = """
    @url = jumpscale.schema.test.a
    category*= ""
    txt = ""
    i = 0
    """
    # lets upgrade schema to float
    s_temp = j.data.schema.get_from_text(schema_text)

    assert len(bcdb.meta._data._ddict["schemas"]) == 10  # should be same because is same schema, should be same md5
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

    assert len(bcdb.meta._data._ddict["schemas"]) == 10  # acl, user, circle, despiegktest and the 1 new one

    a3 = model2.new()
    a3.category = "acat3"
    a3.txt = "data3"
    a3.i = 3
    a3.save()
    assert a3.i == 3.0
    assert a2.i == 2  # int

    assert len(model2.find()) == 3  # needs to be 3 because model is for all of them
    assert len(model.find()) == 3  # needs to be 3 because model is for all of them

    all = model2.find()

    a4 = model2.get(all[0].id)
    a4_ = model.get(all[0].id)
    assert a4_ == a4
    a5 = model2.get(all[1].id)
    a6 = model.get(all[2].id)
    a6_ = model.get(all[2].id)
    assert a6_ == a6

    assert a6.id == a3.id
    assert a6.i == a3.i
    return "OK"
