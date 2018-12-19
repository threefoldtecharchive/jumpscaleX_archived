from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.bcdb.test(name="acls")'

    test around acls

    """

    S = """
    @url = despiegk.test5.acl
    name = "" 
    an_id = 0
    """

    def do(bcdb):

        m=bcdb.model_get_from_schema(S) #model has now been added to the DB

        self._logger.info("POPULATE DATA")

        for i in range(10):
            u=bcdb.user.new()
            u.name="ikke_%s"%i
            u.email="user%s@me.com"%i
            u.dm_id = "user%s.ibiza"%i
            u.save()

        for i in range(10):
            g=bcdb.group.new()
            g.name="gr_%s"%i
            g.email="group%s@me.com"%i
            g.dm_id = "group%s.ibiza"%i
            g.group_members = [x for x in range(i+1)]
            g.user_members = [x for x in range(i+1)]
            g.save()

        self._logger.info("ALL DATA INSERTED (DONE)")

        self._logger.info("walk over all data")
        l = bcdb.get_all()

        self._logger.info("walked over all data (DONE)")

        assert len(l)==20
        u0=l[0]
        g0=l[10]


        self._logger.info("ACL TESTS PART1")

        a=bcdb.acl.new()
        user = a.users.new()
        user.rights="wrwd"
        user.uid = 1
        group = a.groups.new()
        group.rights="wwd"
        group.uid = 2
        group = a.groups.new()
        group.rights="e"
        group.uid = 3


        assert len(a.model.get_all()) == 0 #there should be no acl's in the DB yet

        a=a.save()
        a_id2 = a.id+0

        assert len([i for i in a.model.id_iterator])==1


        assert len(bcdb.get_all())==21

        res =  a.model.get_from_keys(hash=a.hash)

        assert len(res)==1

        assert a.id==a_id2

        assert a.readonly == True

        #new model new

        a= m.new()
        a.name = "aname"

        change = a.acl.rights_set(userids=[1],groupids=[2,3],rights="rw")
        assert change == True

        assert a.acl.readonly==True
        a.save()
        assert a.acl.readonly

        assert len(bcdb.acl.get_all())==2
        assert a.acl.hash == 'fa53cc2c53702aef90db0026b4e023f4'

        self._logger.debug("MODIFY RIGHTS")

        a.acl.rights_set(userids=[1],rights="r")
        a.save()

        assert len(bcdb.acl.get_all())==3

        assert a.acl.readonly

        assert a.acl.hash == '240481437f4c67f40c2683883b755ac3'


        assert a.acl.rights_check(1,"r") == True
        assert a.acl.rights_check(1,"d") == False

        a.acl.rights_set([1],[],"rw")
        assert a.acl.rights_check(1,"r") == True
        assert a.acl.rights_check(1,"w") == True
        assert a.acl.rights_check(1,"rw") == True
        assert a.acl.rights_check(1,"rwd") == False
        assert a.acl.rights_check(1,"d") == False
        a.save()

        #NEED TO DO TESTS WITH GROUPS


    zdbclient_admin = j.servers.zdb.client_admin_get()
    zdbclient = zdbclient_admin.namespace_new("test",secret="1234")
    zdbclient.flush() #empty
    bcdb = j.data.bcdb.new(name="test",zdbclient=zdbclient)
    bcdb.reset()
    do(bcdb)

    bcdb = j.data.bcdb.new(name="test",zdbclient=None)
    bcdb.reset()
    do(bcdb)

    self._logger.info("ACL TESTS ALL DONE")

