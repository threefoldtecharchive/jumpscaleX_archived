from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="async",start=True)'

    this is a test where we use the queuing mechanism for processing data changes

    """

    _, model = self._load_test_model()

    def get_obj(i):
        model_obj = model.new()
        model_obj.nr = i
        model_obj.name = "somename%s" % i
        return model_obj

    model_obj = get_obj(1)

    # should be empty
    assert model.bcdb.queue.empty() is True

    model.set_dynamic(model_obj)

    model_obj2 = model.get(model_obj.id)
    assert model_obj2._data == model_obj._data

    # will process 1000 obj (set)
    for x in range(1000):
        model.set_dynamic(get_obj(x))

    # should be nothing in queue
    assert model.bcdb.queue.empty() is True

    # now make sure index processed and do a new get
    model.index_ready()

    model_obj2 = model.get(model_obj.id)
    assert model_obj2._data == model_obj._data

    assert model.bcdb.queue.empty()

    self._logger.info("TEST DONE")

    return ("OK")
