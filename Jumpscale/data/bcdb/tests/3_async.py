from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="async")'

    this is a test where we use the queuing mechanism for processing data changes

    """


    db, m = self._load_test_model()

    def get_obj(i):
        o = m.new()
        o.nr = i
        o.name= "somename%s"%i
        return o

    o = get_obj(1)

    #should be empty
    assert m.bcdb.queue.empty() == True

    # j.shell()
    m.set_dynamic(o)

    o2 = m.get(o.id)
    assert o2._data == o._data

    #will process 1000 obj (set)
    for x in range(1000):
        m.set_dynamic(get_obj(x))

    #should be nothing in queue
    assert m.bcdb.queue.empty() == True

    #now make sure index processed and do a new get
    m.index_ready()

    o2 = m.get(o.id)
    assert o2._data == o._data

    assert m.bcdb.queue.empty()

    self._logger.info("TEST2 DONE")

    return ("OK")

