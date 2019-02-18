from Jumpscale import j

from Jumpscale.data.types.TypeBaseClasses import TypeBaseObjClassNumeric

def main(self):
    """
    to run:

    js_shell 'j.data.types.test(name="baseclasses")'
    """

    class myclass(TypeBaseObjClassNumeric):

        pass

    a = myclass(j.data.types.string,"1")
    b = myclass(j.data.types.string,"2")

    assert a._value_ == '1'
    assert a._value == 1
    assert b._value_ == '2'

    assert a+b==3.0
    assert b-a==1.0
    assert b/a==2.0
    assert b*a==2.0
    assert not b==a

    a._value = "2"
    assert a._value_ == '2'
    assert a._value == 2

    assert b==a

    assert b*a==4.0

    print ("TESTS FOR BASECLASSES TYPES OK")

    return ("OK")


main("")
