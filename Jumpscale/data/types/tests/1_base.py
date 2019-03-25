from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.types.test(name="base")'
    """


    assert j.data.types.string.__class__.NAME == 'string'

    assert j.data.types.get("s") == j.data.types.get("string")
    assert j.data.types.get("s") == j.data.types.get("str")

    t = j.data.types.get("i")

    assert t.clean("1") == 1
    assert t.clean(1) == 1
    assert t.clean(0) == 0
    assert t.default_get() == 4294967295

    t = j.data.types.get("li",default="1,2,3")  #list of integers

    assert t._default == [1,2,3]


    assert t.default_get() == [1,2,3]

    t2 = j.data.types.get("ls",default="1,2,3")  #list of strings
    assert t2.default_get() == ['1', '2', '3']

    t3 = j.data.types.get("ls")
    assert t3.default_get() == []

    t=j.data.types.email
    assert t.check("kristof@in.com")
    assert t.check("kristof.in.com") == False

    t = j.data.types.bool
    assert t.clean("true")==True
    assert t.clean("True")==True
    assert t.clean(1)==True
    assert t.clean("1")==True
    assert t.clean("False")==False
    assert t.clean("false")==False
    assert t.clean("0")==False
    assert t.clean(0)==False
    assert t.check(1) == False
    assert t.check(True) == True


    b = j.data.types.get('b',default='true')

    assert b.default_get() == True

    #TODO: need more tests here

    self._log_info("TEST DONE FOR TYPES BASE")

    return ("OK")
