from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="lists")'

    tests an issue with lists, they were gone at one point after setting a value

    test readonly behaviour

    """

    schema0 = """
        @url = jumpscale.schema.test3.cmd
        name = ""
        comment = ""        
        nr = 0
        """
    j.data.schema.get(schema0)

    schema1 = """
        @url = jumpscale.myjobs.job
        category*= ""
        time_start* = 0 (D)
        time_stop = 0 (D)
        state* = ""
        timeout = 0
        action_id* = 0
        args = ""   #json
        kwargs = "" #json
        result = "" #json
        error = ""
        return_queues = (LS)
        cmds = (LO) !jumpscale.schema.test3.cmd
        cmd = (O) !jumpscale.schema.test3.cmd
        
        """
    schema_object = j.data.schema.get(schema1)
    schema_test = schema_object.new()
    schema_test.return_queues = ["a", "b"]
    assert schema_test._return_queues.pylist() == ["a", "b"]
    assert schema_test._return_queues._inner_list == ["a", "b"]
    assert schema_test.return_queues == ["a", "b"]

    schema_test.return_queues[1] = "c"
    assert schema_test._return_queues.pylist() == ["a", "c"]
    assert schema_test._return_queues._inner_list == ["a", "c"]
    assert schema_test.return_queues == ["a", "c"]

    schema_test.return_queues.pop(0)
    assert schema_test._return_queues.pylist() == ["c"]
    assert schema_test._return_queues._inner_list == ["c"]
    assert schema_test.return_queues == ["c"]

    cmd = schema_test.cmds.new()
    cmd.name = "aname"
    cmd.comment = "test"
    cmd.nr = 10

    schema_test.cmd.name = "aname2"
    schema_test.cmd.nr = 11

    schema_test.category = "acategory"

    schema_test1 = {
        "category": "acategory",
        "time_start": 0,
        "time_stop": 0,
        "state": "",
        "timeout": 0,
        "action_id": 0,
        "args": "",
        "kwargs": "",
        "result": "",
        "error": "",
        "cmd": {"name": "aname2", "comment": "", "nr": 11},
        "return_queues": ["c"],
        "cmds": [{"name": "aname", "comment": "test", "nr": 10}],
    }

    for item1, item2 in zip(schema_test._ddict, schema_test1):
        assert item1 == item2

    schema_test._data
    schema_test._json

    for item1, item2 in zip(schema_test._ddict, schema_test1):
        assert item1 == item2

    schema_test2 = schema_object.get(capnpbin=schema_test._data)

    for item1, item2 in zip(schema_test._ddict, schema_test2._ddict):
        assert item1 == item2
    assert schema_test._data == schema_test2._data

    assert schema_test.readonly == False
    schema_test.readonly = True

    # test we cannot change a subobj
    try:
        schema_test.category = "s"
    except Exception as e:
        assert str(e).find("object readonly, cannot set") != -1

    # THERE IS STILL ERROR, readonly does not work for subobjects, need to change template

    self._log_info("TEST DONE LIST")

    return ("OK")
