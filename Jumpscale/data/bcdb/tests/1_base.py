from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="base")'

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

            if not rdbstor:
                schema = """
                @url = despiegk.test
                llist2 = "" (LS)
                name** = ""
                email** = ""
                nr** = 0
                date_start** = 0 (D)
                description = ""
                token_price** = "10 USD" (N)
                hw_cost = 0.0 #this is a comment
                llist = []
                llist3 = "1,2,3" (LF)
                llist4 = "1,2,3" (L)
                llist5 = "1,2,3" (LI)
                U = 0.0
                pool_type = "managed,unmanaged" (E)
                """
            else:
                schema = """
                @url = despiegk.test
                llist2 = "" (LS)
                name* = ""
                email* = ""
                nr* = 0
                date_start* = 0 (D)
                description = ""
                token_price* = "10 USD" (N)
                hw_cost = 0.0 #this is a comment
                llist = []
                llist3 = "1,2,3" (LF)
                llist4 = "1,2,3" (L)
                llist5 = "1,2,3" (LI)
                U = 0.0
                pool_type = "managed,unmanaged" (E)
                """

            db, model = self._load_test_model(sqlitestor=sqlitestor, rdbstor=rdbstor, reset=True, schema=schema)

            if not sqlitestor and not rdbstor:
                print(model.zdbclient.nsinfo["entries"])
                assert model.zdbclient.nsinfo["entries"] == 1
            else:
                assert len(model.get_all()) == 0

            for i in range(10):
                model_obj = model.new()
                model_obj.llist.append(1)
                model_obj.llist2.append("yes")
                model_obj.llist2.append("no")
                model_obj.llist3.append(1.2)
                model_obj.date_start = j.data.time.epoch
                model_obj.U = 1.1
                model_obj.nr = i
                model_obj.token_price = "10 EUR"
                model_obj.description = "something"
                model_obj.name = "name%s" % i
                model_obj.email = "info%s@something.com" % i
                model_obj2 = model._set(model_obj)

            assert len(model.get_all()) == 10

            model_obj3 = model.get(model_obj2.id)

            assert model_obj3.id == model_obj2.id

            assert model_obj3._ddict == model_obj2._ddict
            assert model_obj3._ddict == model_obj._ddict

            return db

        db = load()
        db_model = db.model_get_from_url(url="despiegk.test")

        if not rdbstor:
            query = db_model.index.select()
            qres = [(item.name, item.nr) for item in query]

            assert qres == [
                ("name0", 0),
                ("name1", 1),
                ("name2", 2),
                ("name3", 3),
                ("name4", 4),
                ("name5", 5),
                ("name6", 6),
                ("name7", 7),
                ("name8", 8),
                ("name9", 9),
            ]

            assert db_model.index.select().where(db_model.index.nr == 5)[0].name == "name5"

            query = db_model.index.select().where(db_model.index.nr > 5)  # should return 4 records
            qres = [(item.name, item.nr) for item in query]

            assert len(qres) == 4

            res = db_model.index.select().where(db_model.index.name == "name2")
            assert len(res) == 1
            assert res.first().name == "name2"

            res = db_model.index.select().where(db_model.index.email == "info2@something.com")
            assert len(res) == 1
            assert res.first().name == "name2"

            first_id = res.first().id

        model_obj = db_model.get(3)
        n2 = model_obj.name + ""
        model_obj.name = n2

        # because data did not change, was already that data

        assert model_obj._changed_items == {}
        model_obj.name = "name3"
        assert model_obj._changed_items == {"name": "name3"}  # now it really changed

        assert model_obj._ddict["name"] == "name3"

        model_obj.token_price = "10 USD"
        assert model_obj.token_price_usd == 10
        db_model._set(model_obj)
        model_obj2 = db_model.get(model_obj.id)
        assert model_obj2.token_price_usd == 10

        if not rdbstor:
            assert db_model.index.select().where(db_model.index.id == model_obj.id).first().token_price == 10
        else:
            o = db_model.get_by_name("name1")[0]
            o.name == "name1"

        def do(id, obj, result):
            result[obj.nr] = obj.name
            return result

        result = {}
        for obj in db_model.iterate():
            result[obj.nr] = obj.name

        print(result)
        assert result == {
            0: "name0",
            1: "name1",
            2: "name3",
            3: "name3",
            4: "name4",
            5: "name5",
            6: "name6",
            7: "name7",
            8: "name8",
            9: "name9",
        }

        assert db_model.id_exists(1)
        assert db_model.id_exists(10) == False

        j.shell()

        self._log_info("TEST DONE: %s" % name)

    test("RDB")
    # test("ZDB")
    # test("SQLITE")

    return "OK"
