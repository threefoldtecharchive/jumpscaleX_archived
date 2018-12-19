from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="models")'

    work with toml files and see if models get generated properly

    """
    mpath = self._dirpath+"/tests/models"
    assert j.sal.fs.exists(mpath)

    #make sure we remove the maybe already previously generated model file
    for item in j.sal.fs.listFilesInDir(mpath, filter="*.py"):
        j.sal.fs.remove(item)

    bcdb,model = self._load_test_model()

    bcdb.models_add(mpath)

    m = bcdb.model_get('jumpscale.bcdb.test.house')

    o = m.new()
    o.cost = "10 USD"
    o.save()

    data = m.get(o.id)

    assert data.cost_usd == 10

    assert o.cost_usd == 10

    assert m.index.select().first().cost == 10.0  #is always in usd

    print ("TEST FOR MODELS DONE, but is still minimal")

    return ("OK")

