from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="base")' --debug
    """
    schema = """
        @url = despiegk.test
        llist = []
        llist2 = "" (LS) #L means = list, S=String
        llist3 = [1,2,3] (LF)
        nr = 4
        date_start = 0 (D)
        description = ""        
        llist4 = [1,2,3] (L)
        llist5 = [1,2,3] (LI)
        llist6 = "1,2,3" (LI)
        U = 0.0
        """

    schema_object = j.data.schema.get(schema_text=schema)

    assert schema_object.url == "despiegk.test"
    print(schema_object)

    assert schema_object.property_llist.default.value == []
    assert schema_object.property_llist2.default.value == []
    assert schema_object.property_llist3.default.value == [1.0,2.0,3.0]
    #works with & without value
    assert schema_object.property_llist3.default == [1.0,2.0,3.0]
    assert schema_object.property_llist4.default == [1,2,3]
    assert schema_object.property_llist5.default == [1,2,3]
    assert schema_object.property_llist6.default == [1,2,3]

    ll = schema_object.property_llist3.jumpscaletype.default_get()
    assert ll.value == [1.0,2.0,3.0]

    assert schema_object.property_llist3.js_typelocation == "j.data.types.custom._types['lf_1_2_3']"


    o = schema_object.get()

    assert o.llist3 == [1.0,2.0,3.0]

    o.llist2.append("yes")
    o.llist2.append("no")
    o.llist3.append(1.2)
    o.llist5.append(1)
    o.llist5.append(2)
    o.U = 1.1
    o.nr = 1
    o.description = "something"

    assert o.llist2 == ["yes","no"]
    assert o.description == "something"
    assert o.llist3 == [1.0, 2.0, 3.0, 1.2]
    assert o.U == 1.1
    o.U = "1.1"
    assert o.U == 1.1


    schema = """
        @url = despiegk.test2
        enum = "red,green,blue,zhisisaverylongoneneedittotestletsdosomemore" (E) #first one specified is the default one
        llist2 = "" (LS)
        nr = 4
        date_start = 0 (D)
        description = ""
        cost_estimate = 0.0 #this is a comment
        llist = []
        @url = despiegk.test3
        llist = []
        description = ""
        """

    j.data.schema.get(schema_text=schema)

    s=j.data.schema.schemas['despiegk.test2']
    e = s.properties[0] #is the enumerator
    assert e.js_typelocation != 'j.data.types.enum' #should not the default location

    schema_object1 = j.data.schema.get(url="despiegk.test2")
    schema_object2 = j.data.schema.get(url="despiegk.test3")

    schema_test1 = schema_object1.get()
    schema_test2 = schema_object2.get()
    schema_test1.llist2.append("5")
    schema_test2.llist.append("1")

    assert schema_test1.enum == 'RED'

    schema_test1.enum = 2
    assert schema_test1.enum == 'GREEN'
    schema_test1.enum = "  green"
    assert schema_test1.enum == 'GREEN'

    assert schema_test1._ddict["enum"] == "GREEN"

    assert schema_test1._data.find(b"GREEN") == -1  # needs to be stored as int
    assert len(schema_test1._data) <= 30
    x = len(schema_test1._data)+0

    schema_test1.enum = 4
    assert schema_test1.enum == "ZHISISAVERYLONGONENEEDITTOTESTLETSDOSOMEMORE"
    assert len(schema_test1._data) <= 30
    assert len(schema_test1._data) == x

    schema = """
        @url = despiegk.test2
        #lets check the defaults
        bool1 = true (B)
        bool2 = True (B)
        bool3 = false (B)
        bool4 = False (B)
        bool5 = 1 (B)
        bool6 = '1' (B)
        bool7 = '0' (B)
        bool8 = 'n' (B)
        int1 =  10 (I)
    """

    o = j.data.schema.get(schema).new()

    assert o.bool1 == True
    assert o.bool2 == True
    assert o.bool3 == False
    assert o.bool4 == False
    assert o.bool5 == True
    assert o.bool6 == True
    assert o.bool7 == False
    assert o.bool8 == False
    assert o.int1 == 10

    self._log_info("TEST DONE BASE")

    return ("OK")
