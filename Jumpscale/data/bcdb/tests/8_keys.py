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


    SCHEMA3="""
    @url = threefoldtoken.wallet.test2
    @name = wallet
    jwt = "" (S)                # JWT Token
    addr* = "aa"                   # Address
    ipaddr* = "" (ipaddr)           # IP Address
    email* =  (S)              # Email address 
    nr = 10 (I)
    nr2 =  (I)
    nr3 =  (N)
    nr4 = 5 (N)
    date = (D)   
    
    """
    m3 = bcdb.model_get_from_schema(SCHEMA3)
    o=m3.new()

    #default
    assert o.addr == "aa"
    assert o.ipaddr == ""
    assert o.email == ""
    assert o.nr == 10
    assert o.nr2 == 4294967295
    assert o.nr3 == b'\x00\x97\x00\x00\x00\x00'
    assert o.nr3_usd == 0
    assert o.nr4_usd == 5
    assert o.date == 0

    o.ipaddr = "something"
    o.email = "ename"
    o.addr = "test"
    o.save()

    data=bcdb._hset_index_key_get(schema=m3.schema,returndata=True)
    redisid = data[bcdb.name][m3.schema.url]
    rkey=bcdb._hset_index_key_get(schema=m3.schema)
    assert rkey.decode().endswith(str(redisid))  #check that the raw info is same as the info from function

    assert len(j.clients.credis_core.keys(rkey+b":*")) == 3

    assert len(m3.get_all())==1

    assert [i for i in m3.id_iterator] == [m3.get_all()[0].id]  #should only be the 1 id in there

    assert len(m.get_all())==3

    assert m.get_all()[0].model.schema.sid == o2.model.schema.sid

    assert len(m3.get_by_addr("test"))==1

    assert len(m3.get_from_keys(addr="test",email="ename",ipaddr="something")) == 1
    assert len(m3.get_from_keys(addr="test",email="ename",ipaddr="something2")) == 0

    bcdb2 = j.data.bcdb.new("test2",bcdb.zdbclient,reset=True)
    assert len(m3.get_from_keys(addr="test",email="ename",ipaddr="something")) == 1
    bcdb2.reset()
    assert len(m3.get_from_keys(addr="test",email="ename",ipaddr="something")) == 1

    #now we know that the previous indexes where not touched

    m4  = bcdb2.model_get_from_schema(SCHEMA3)
    o=m4.new()
    o.ipaddr = "something"
    o.email = "ename"
    o.addr = "test"
    o.save()

    myid = o.id+0 #make copy

    assert len(m4.get_from_keys(addr="test",email="ename",ipaddr="something")) == 1

    o5=m4.get_from_keys(addr="test",email="ename",ipaddr="something")[0]
    assert o5.id == myid

    self._logger.info("TEST DONE")

    bcdb.reset()

    assert m3.get_from_keys(addr="test",email="ename",ipaddr="something") == []
    assert len(m4.get_from_keys(addr="test",email="ename",ipaddr="something")) == 1

    bcdb2.reset()

    #check 2 bcdb are empty
    assert len(j.sal.fs.listDirsInDir("/sandbox/var/bcdb/test"))==0
    assert len(j.sal.fs.listDirsInDir("{DIR_BASE}/var/bcdb/test2"))==0
    assert len(j.sal.fs.listDirsInDir("{DIR_VAR}/bcdb/test2"))==0

    return ("OK")
