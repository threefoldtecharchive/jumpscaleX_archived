from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.schema.test(name="base")'
    """
    schema = """
        @url = despiegk.test
        llist2 = "" (LS) #L means = list, S=String        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate = 0.0 #this is a comment
        llist = []
        llist3 = "1,2,3" (LF)
        llist4 = "1,2,3" (L)
        llist5 = "1,2,3" (LI)
        U = 0.0
        #pool_type = "managed,unmanaged" (E)  #NOT DONE FOR NOW
        """

    schema_object = j.data.schema.get(schema_text=schema)

    assert schema_object.url == "despiegk.test"
    print(schema_object)
    schema_test = schema_object.get()

    schema_test.llist2.append("yes")
    schema_test.llist2.append("no")
    schema_test.llist3.append(1.2)
    schema_test.llist5.append(1)
    schema_test.llist5.append(2)
    schema_test.U = 1.1
    schema_test.nr = 1
    schema_test.token_price = "10 USD"
    schema_test.description = "something"

    usd2usd = schema_test.token_price_usd  # convert USD-to-USD... same value
    assert usd2usd == 10
    inr = schema_test.token_price_cur("inr")
    # print ("convert 10 USD to INR", inr)
    assert inr > 100  # ok INR is pretty high... check properly in a bit...
    eur = schema_test.token_price_eur
    # print ("convert 10 USD to EUR", eur)
    cureur = j.clients.currencylayer.cur2usd["eur"]
    curinr = j.clients.currencylayer.cur2usd["inr"]
    # print (cureur, curinr, o.token_price)
    assert usd2usd * cureur == eur
    assert usd2usd * curinr == inr

    # try EUR to USD as well
    schema_test.token_price = "10 EUR"
    assert schema_test.token_price == b"\x000\n\x00\x00\x00"
    eur2usd = schema_test.token_price_usd
    assert eur2usd * cureur == 10

    schema_test._cobj

    schema = """
        @url = despiegk.test2
        llist2 = "" (LS)
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate = 0.0 #this is a comment
        llist = []
        enum = "red,green,blue,zhisisaverylongoneneedittotestletsdosomemore" (E) #first one specified is the default one

        @url = despiegk.test3
        llist = []
        description = ""
        """
    j.data.schema.get(schema_text=schema)
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

    self._logger.info("TEST DONE BASE")

    return ("OK")
