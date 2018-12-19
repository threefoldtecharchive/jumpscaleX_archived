from Jumpscale import j

def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="keys")'

    """

    SCHEMA="""
    @url = threefoldtoken.wallet.test
    @name = wallet
    jwt = "" (S)                # JWT Token
    addr* = ""                   # Address
    ipaddr* = (ipaddr)           # IP Address
    email* = "" (S)              # Email address
    username* = "" (S)           # User name
    
    
    """


    bcdb = j.data.bcdb.get("test")
    m = bcdb.model_get_from_schema(SCHEMA)

    m.reset()


    o = m.new()
    o.addr = "something"
    o.email = "myemail"
    o.username="myuser"
    o.save()

    o2= m.get_by_addr(o.addr)[0]
    assert len(m.get_by_addr(o.addr))==1
    o3= m.get_by_email(o.email)[0]
    o4= m.get_by_username(o.username)[0]

    assert o2.id == o.id
    assert o3.id == o.id
    assert o4.id == o.id

    o = m.new()
    o.addr = "something2"
    o.email = "myemail2"
    o.username="myuser"
    o.save()

    o = m.new()
    o.addr = "something2"
    o.email = "myemail2"
    o.username="myuser2"
    o.save()


    l= m.get_by_username("myuser")
    assert len(l)==2


    l = m.get_from_keys(email="myemail2",username="myuser")
    assert len(l)==1

    SCHEMA2="""
    @url = threefoldtoken.wallet.test
    @name = wallet
    jwt = "" (S)                # JWT Token
    addr* = ""                   # Address
    ipaddr* = (ipaddr)           # IP Address
    email* = "" (S)              # Email address    
    
    """

    m2 = bcdb.model_get_from_schema(SCHEMA)
    assert m2.schema.sid==m.schema.sid

    m3 = bcdb.model_get_from_schema(SCHEMA2)

    assert m3.schema.sid==m.schema.sid+1  #its a new model so the sid should be 1 higher

    self._logger.info("TEST DONE")

    return ("OK")
