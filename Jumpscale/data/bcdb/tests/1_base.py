from Jumpscale import j

def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="base")'

    """

    def load():

        #don't forget the record 0 is always a systems record

        db,model = self._load_test_model()

        assert model.zdbclient.nsinfo["entries"]==1

        for i in range(10):
            o = model.new()
            o.llist.append(1)
            o.llist2.append("yes")
            o.llist2.append("no")
            o.llist3.append(1.2)
            o.date_start = j.data.time.epoch
            o.U = 1.1
            o.nr = i
            o.token_price = "10 EUR"
            o.description = "something"
            o.name = "name%s" % i
            o.email = "info%s@something.com" % i
            o2 = model.set_dynamic(o)

        o3 = model.get(o2.id)
        assert o3.id == o2.id

        assert o3._ddict == o2._ddict
        assert o3._ddict == o._ddict

        return db

    db = load()
    m = db.model_get(url="despiegk.test")
    query = m.index.select()
    qres = [(item.name, item.nr) for item in query]

    assert qres == [('name0', 0),
         ('name1', 1),
         ('name2', 2),
         ('name3', 3),
         ('name4', 4),
         ('name5', 5),
         ('name6', 6),
         ('name7', 7),
         ('name8', 8),
         ('name9', 9)]

    assert m.index.select().where(m.index.nr == 5)[0].name == "name5"


    query =  m.index.select().where(m.index.nr > 5) # should return 4 records
    qres = [(item.name,item.nr) for item in query]

    assert len(qres) == 4

    res = m.index.select().where(m.index.name=="name2")
    assert len(res) == 1
    assert res.first().name == "name2"

    res = m.index.select().where(m.index.email=="info2@something.com")
    assert len(res) == 1
    assert res.first().name == "name2"

    o = m.get(res.first().id)

    o.name = "name2"

    assert o._changed_items == {}  # because data did not change, was already that data
    o.name = "name3"
    assert o._changed_items ==  {'name': 'name3'}  # now it really changed

    assert o._ddict["name"] == "name3"

    o.token_price = "10 USD"
    assert o.token_price_usd == 10
    m.set_dynamic(o)
    o2=m.get(o.id)
    assert o2.token_price_usd == 10

    assert m.index.select().where(m.index.id == o.id).first().token_price == 10

    def do(id,obj,result):
        result[obj.nr]=obj.name
        return result

    result = {}
    for obj in m.iterate():
        result[obj.nr] = obj.name

    print (result)
    assert result == {0: 'name0',
         1: 'name1',
         2: 'name3',
         3: 'name3',
         4: 'name4',
         5: 'name5',
         6: 'name6',
         7: 'name7',
         8: 'name8',
         9: 'name9'}


    m.reset()
    assert  [i for i in  m.index.select()]==[]
    assert  m.get_all() == []
    assert  [i for i in m.id_iterator] == []

    self._logger.info("TEST DONE")

    return ("OK")
