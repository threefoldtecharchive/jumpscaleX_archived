from Jumpscale import j


def main(self):
    return
    """
    to run:

    kosmos 'j.data.bcdb.test(name="acls")'

    test around acls

    """

    def test(name):
        if name == "RDB":
            sqlitestor = False
            rdbstor = True
        elif name == "ZDB":
            sqlitestor = False
            rdbstor = False
        elif name == "SQLITE":
            sqlitestor = True
            rdbstor = False
        else:
            raise RuntimeError("not supported type")

        def load():

            # don't forget the record 0 is always a systems record

            schema = """
            @url = despiegk.test5.acl
            name = "" 
            an_id = 0
            """

            db, model = self._load_test_model(type=name, reset=True, schema=schema)

            return db, model

        bcdb, m = load()

        self._log_info("POPULATE DATA")

        for i in range(10):
            u = bcdb.user.new()
            u.name = "ikke_%s" % i
            u.email = "user%s@me.com" % i
            u.dm_id = "user%s.ibiza" % i
            u.save()

        for i in range(10):
            g = bcdb.circle.new()
            g.name = "gr_%s" % i
            g.email = "circle%s@me.com" % i
            g.dm_id = "circle%s.ibiza" % i
            # g.circle_members = [(0, x) for x in range(i + 1)]
            j.shell()
            w
            g.user_members = [x for x in range(i + 1)]
            g.save()

        assert len(bcdb.user.find()) == 10
        assert len(bcdb.circle.find()) == 10
        assert len([i for i in bcdb.circle.index._id_iterator()]) == 10
        assert bcdb.storclient.list() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        self._log_info("ALL DATA INSERTED (DONE)")

        self._log_info("walk over all data")
        l = bcdb.get_all()

        self._log_info("walked over all data (DONE)")

        assert len(l) == 20
        assert bcdb.acl.autosave is False

        a = m.new()
        a.name = "aname"

        change = a.acl.rights_set(userids=[1], circleids=[(0, 2), (0, 3)], rights="rw")
        assert change is True

        # assert a.acl.readonly is False
        a.save()
        assert a.acl.readonly is True

        # means we have indeed the index for acl == 2
        assert len(bcdb.acl.find()) == 1

        assert a.acl.hash == "4743dd07a7b22c2d80b884ebb7437ff8"

        self._log_debug("MODIFY RIGHTS")
        a.acl.rights_set(userids=[1], rights="r")
        a.save()
        assert a.acl.readonly

        assert len(bcdb.acl.find()) == 2  # there needs to be a new acl
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

        self._log_info("TEST ACL DONE: %s" % name)

    test("RDB")
    test("ZDB")
    test("SQLITE")

    self._log_info("ACL TESTS ALL DONE")
