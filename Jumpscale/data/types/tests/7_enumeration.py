from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.types.test(name="enumeration")'
    """


    e = j.data.types.get("e",default="yellow,blue,red")

    assert str(e)=="ENNUM: BLUE,RED,YELLOW (default:YELLOW)"

    assert e.toString(1)=="BLUE"
    assert e.toString(2)=="RED"

    try:
        e.clean(3)
        raise RuntimeError("should not work")
    except Exception:
        pass

    try:
        e.clean(0)
        raise RuntimeError("should not work")
    except Exception:
        pass

    assert e.toString(" blue")=="BLUE"
    assert e.toString("Red ")=="RED"

    assert e.clean("Red ")== "RED"
    assert e.clean("BLUE ")== "BLUE"
    assert e.clean("YELLOW ")== "YELLOW"

    #start count from 1 (0 is for None)
    assert e.toData("BLUE ")== 1
    assert e.toData("Red ")== 2
    assert e.toData("YELLOW ")== 3


    assert e._jumpscale_location=="j.data.types.enumerations['6d9fe6d18a520e26fce3841a7065c93b']"

    # self._log_info("TEST DONE")

    return ("OK")
