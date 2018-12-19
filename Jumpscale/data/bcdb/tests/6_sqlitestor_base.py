from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="sqlitestor_base")'

    use a bcdb which is using sqlite

    """


    bcdb,model = self._load_test_model(reset=True,sqlitestor=True)

    mpath = self._dirpath+"/tests/models"
    assert j.sal.fs.exists(mpath)

    #make sure we remove the maybe already previously generated model file
    for item in j.sal.fs.listFilesInDir(mpath, filter="*.py"):
        j.sal.fs.remove(item)


    bcdb.models_add(mpath)


    m = bcdb.model_get('jumpscale.bcdb.test.house')
    assert m.get_all() == []

    assert m.bcdb.zdbclient == None

    o = m.new()
    o.cost = "10 USD"
    o.save()
    m.cache_reset()
    data = m.get(o.id)
    assert data.cost_usd == 10
    assert o.cost_usd == 10

    assert  [i for i in m.id_iterator]==[1]
    assert [i for i in m.obj_cache.keys()]==[1]  #there need to be 1 in cache

    assert m._ids_last == 1

    m.cache_reset()
    assert [i for i in m.obj_cache.keys()]==[]


    o.cost = "11 USD"
    o.save()
    assert m._ids_last == 1
    data = m.get(o.id)
    #is with cash
    assert data.cost_usd == 11
    m.cache_reset()
    assert m.obj_cache == {}  #cache needs to be empty
    data = m.get(o.id)
    assert data.cost_usd == 11
    assert m.obj_cache != {} #now there needs to be something in
    
    assert [i for i in m.id_iterator]==[1] #still needs to be only 1 entry, because was update

    m.cache_reset()
    o = m.new()
    o.cost = "12 USD"
    o.save()
    assert m._ids_last == 2 #a new one, so ids need to go up


    assert m.obj_cache == {} #we dont save at set
    m.get(o.id)
    assert m.obj_cache != {} #now needs to be in cache

    assert o.id == 2

    m.get(1)._ddict == {'name': '',
         'active': False,
         'cost': b'\x00\x97\x0b\x00\x00\x00',
         'room': [],
         'id': 2}

    m.get(2)._ddict == {'name': '',
         'active': False,
         'cost': b'\x00\x97\x0c\x00\x00\x00',
         'room': [],
         'id': 2}



    assert m.index.select().first().cost == 11.0  #is always in usd

    print ("TEST FOR MODELS DONE in SQLITE")

    return ("OK")

