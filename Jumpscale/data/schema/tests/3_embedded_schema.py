from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="embedded_schema")'
    """
    schema = """
        @url = jumpscale.schema.test3.cmd
        name = ""
        comment = ""
        schemacode = ""

        @url = jumpscale.schema.test3.serverschema
        cmds = (LO) !jumpscale.schema.test3.cmdbox

        @url = jumpscale.schema.test3.cmdbox
        @name = GedisServerCmd1
        cmd = (O) !jumpscale.schema.test3.cmd
        cmd2 = (O) !jumpscale.schema.test3.cmd
        
        """
    j.data.schema.get(schema)
    schema_object2 = j.data.schema.get(url="jumpscale.schema.test3.serverschema")
    schema_object3 = j.data.schema.get(url="jumpscale.schema.test3.cmdbox")

    schema_test = schema_object2.get()
    for i in range(4):
        schema_object = schema_test.cmds.new()
        schema_object.name = "test%s" % i

    assert schema_test.cmds[2].name == "test2"
    schema_test.cmds[2].name = "test_two"
    assert schema_test.cmds[2].name == "test_two"

    bdata = schema_test._data

    print(schema_test._data)

    schema_test3 = schema_object3.get()
    schema_test3.cmd.name = "test"
    schema_test3.cmd2.name = "test"
    assert schema_test3.cmd.name == "test"
    assert schema_test3.cmd2.name == "test"

    bdata = schema_test3._data
    schema_test4 = schema_object3.get(capnpbin=bdata)
    assert schema_test4._ddict == schema_test3._ddict

    assert schema_test3._data == schema_test4._data

    self._log_info("TEST DONE SCHEMAEMBED")

    return ("OK")
