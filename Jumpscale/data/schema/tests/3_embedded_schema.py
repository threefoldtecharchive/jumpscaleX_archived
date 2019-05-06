from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="embedded_schema")'
    """

    def onelevel():

        schema = """
            @url = jumpscale.schema.test3.a
            cmd = (O) !jumpscale.schema.test3.b
    
            @url = jumpscale.schema.test3.b
            name = ""
            comment = ""
            schemacode = ""
            """

        j.data.schema.add(schema)
        so = j.data.schema.get(url="jumpscale.schema.test3.a")
        so2 = j.data.schema.get(url="jumpscale.schema.test3.b")
        o = so.new()

        o.cmd.name = "a"

        assert o.cmd.name == "a"
        assert o.cmd.comment == ""

        data = o._data

        so3 = j.data.schema.get(url="jumpscale.schema.test3.a",data=data)

        j.shell()

    def onelevellist():

        schema = """
            @url = jumpscale.schema.test3.a
            cmds = (LO) !jumpscale.schema.test3.b
    
            @url = jumpscale.schema.test3.b
            name = ""
            comment = ""
            schemacode = ""
            """

        j.data.schema.add(schema)
        so = j.data.schema.get(url="jumpscale.schema.test3.a")
        so2 = j.data.schema.get(url="jumpscale.schema.test3.b")
        o = so.new()

        cmd=o.cmds.new()
        cmd.name = "a"

        assert o.cmds[0].name == "a"

        assert o.cmds[0]._ddict == {'name': 'a', 'comment': '', 'schemacode': ''}

        assert len(o.cmds)==1

        data = o._data

        #to make sure after serialization is still ok
        assert o.cmds[0].name == "a"

        assert o.cmds[0]._ddict == {'name': 'a', 'comment': '', 'schemacode': ''}

        assert len(o.cmds)==1

        o2 = so.get(data=data)

        assert o2.cmds[0].name == "a"

        assert o2.cmds[0]._ddict == {'name': 'a', 'comment': '', 'schemacode': ''}

        assert len(o2.cmds)==1

        o3 = so.get(data=o._ddict)


        assert o3.cmds[0].name == "a"

        assert o3.cmds[0]._ddict == {'name': 'a', 'comment': '', 'schemacode': ''}

        assert len(o3.cmds)==1

        print(o)

        cmd=o.cmds.new()
        cmd.name = "cc"

        assert len(o.cmds)==2
        assert o.cmds[1].name == "cc"



    onelevel()
    onelevellist()



    #more deep embedded (2 levels)
    
    schema = """
        @url = jumpscale.schema.test3.cmd
        name = ""
        comment = ""
        schemacode = ""

        @url = jumpscale.schema.test3.serverschema
        cmds = (LO) !jumpscale.schema.test3.cmdbox
        cmd = (O) !jumpscale.schema.test3.cmd

        @url = jumpscale.schema.test3.cmdbox
        cmd = (O) !jumpscale.schema.test3.cmd
        cmd2 = (O) !jumpscale.schema.test3.cmd
        
        """
    j.data.schema.add(schema) #just add
    schema_object2 = j.data.schema.get(url="jumpscale.schema.test3.serverschema")
    schema_object3 = j.data.schema.get(url="jumpscale.schema.test3.cmdbox")

    schema_test = schema_object2.get()

    j.shell()
    w

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
    schema_test4 = schema_object3.get(data=bdata)
    assert schema_test4._ddict == schema_test3._ddict

    assert schema_test3._data == schema_test4._data

    self._log_info("TEST DONE SCHEMA EMBED")

    return ("OK")
