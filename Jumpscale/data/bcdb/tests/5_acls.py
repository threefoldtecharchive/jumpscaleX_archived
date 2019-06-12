from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="acls")'

    test around acls

    """
    return  # needs to be done later

    schema = """
    @url = despiegk.test5.acl
    name = "" 
    an_id = 0
    """

    def do(bcdb):

        # model has now been added to the DB
        m = bcdb.model_get_from_schema(schema)

        self._log_info("POPULATE DATA")

        for i in range(10):
            u = bcdb.user.new()
            u.name = "ikke_%s" % i
            u.email = "user%s@me.com" % i
            u.dm_id = "user%s.ibiza" % i
            u.save()

        for i in range(10):
            g = bcdb.group.new()
            g.name = "gr_%s" % i
            g.email = "group%s@me.com" % i
            g.dm_id = "group%s.ibiza" % i
            g.group_members = [x for x in range(i + 1)]
            g.user_members = [x for x in range(i + 1)]
            g.save()

        self._log_info("ALL DATA INSERTED (DONE)")

        self._log_info("walk over all data")
        l = bcdb.get_all()

        self._log_info("walked over all data (DONE)")

        assert len(l) == 20
        assert bcdb.acl.autosave is False

        a = m.new()
        a.name = "aname"

        change = a.acl.rights_set(userids=[1], groupids=[2, 3], rights="rw")
        assert change is True

        # assert a.acl.readonly is False
        a.save()
        assert a.acl.readonly is True

        # means we have indeed the index for acl == 2
        assert len(bcdb.acl.get_all()) == 1

        assert a.acl.hash == "4743dd07a7b22c2d80b884ebb7437ff8"

        self._log_debug("MODIFY RIGHTS")
        a.acl.rights_set(userids=[1], rights="r")
        a.save()
        assert a.acl.readonly

        assert len(bcdb.acl.get_all()) == 2  # there needs to be a new acl
        assert a.acl.hash == "6c91e0d74f2ee7f42a7e0c0bf697d647"

        assert a.acl.rights_check(1, "r") is True
        assert a.acl.rights_check(1, "d") is False

        a.acl.rights_set([1], [], "rw")
        assert a.acl.rights_check(1, "r") is True
        assert a.acl.rights_check(1, "w") is True
        assert a.acl.rights_check(1, "rw") is True
        assert a.acl.rights_check(1, "rwd") is False
        assert a.acl.rights_check(1, "d") is False
        a.save()

        # NEED TO DO TESTS WITH GROUPS

    zdbclient_admin = j.servers.zdb.client_admin_get()
    zdbclient = zdbclient_admin.namespace_new("test", secret="1234")
    zdbclient.flush()  # empty
    bcdb = j.data.bcdb.get(name="test", zdbclient=zdbclient, reset=True)

    do(bcdb)
    bcdb.reset()

    bcdb = j.data.bcdb.get(name="test", zdbclient=None, reset=True)
    do(bcdb)

    self._log_info("ACL TESTS ALL DONE")
