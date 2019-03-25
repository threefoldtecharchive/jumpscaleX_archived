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
        description2 = (S)
        llist4 = [1,2,3] (L)
        llist5 = [1,2,3] (LI)
        llist6 = "1,2,3" (LI)
        U = 0.0
        nrdefault = 0
        nrdefault2 = (I)
        nrdefault3 = 0 (I)
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

    assert schema_object.property_llist3.js_typelocation == "j.data.types._types['list_281be192c3ea134b85dd0c368d7d1b36']"


    o = schema_object.get()

    assert o.nrdefault == 0
    assert o.nrdefault2 == 4294967295
    assert o.nrdefault == 0
    assert o.description == ""
    assert o.description2 == ""

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

    o1 = schema_object1.get()
    o2 = schema_object2.get()
    o1.llist2.append("5")
    o1.llist2.append(6)

    assert "5" in o1.llist2
    assert "6" in o1.llist2

    c= o1._cobj
    c2= o1._cobj

    assert c.llist2[0] == '5'
    assert c2.llist2[0] == '5'

    dd = o1._ddict

    assert dd["enum"] == 1
    assert dd["llist2"][1] == '6'
    assert dd["nr"] == 4


    o2.llist.append("1")

    assert o1.enum == 'RED'
    assert o1._cobj.enum == 1

    o1.enum = 2
    assert o1.enum == 'GREEN'
    assert o1._cobj.enum == 2
    o1.enum = "  green"
    assert o1.enum == 'GREEN'
    assert o1.enum == ' GREEN'
    assert o1.enum == ' Green'

    assert o1._ddict_hr["enum"] == "GREEN"

    assert o1._cobj.nr == 4
    assert o1._cobj.llist2[0] == '5'


    assert o1._data.find(b"GREEN") == -1  # needs to be stored as int
    assert len(o1._data) <= 30
    x = len(o1._data)+0

    o1.enum = 4
    assert o1.enum == "ZHISISAVERYLONGONENEEDITTOTESTLETSDOSOMEMORE"
    assert len(o1._data) <= 30
    assert len(o1._data) == x

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
