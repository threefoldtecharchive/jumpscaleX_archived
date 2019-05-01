from Jumpscale.data.schema.tests.testsuite.testcases.base_test import BaseTest
from Jumpscale import j
import random

raise RuntimeError("needs to be part of tests on BCDB not here")

class Unique(BaseTest):
    def setUp(self):
        super().setUp()
        j.servers.zdb.start_test_instance()
        self.admin_zdb = j.clients.zdb.client_admin_get(port=9901)
        self.admin_zdb.namespace_new("unique")
        self.zdb = j.clients.zdb.client_get(nsname="unique", port=9901)
        self.bcdb = j.data.bcdb.new("test", zdbclient=self.zdb)

    def tearDown(self):
        self.admin_zdb.namespace_delete("unique")
        j.servers.zdb.stop()
        super().tearDown()

    def test022_unique_attributes(self):
        """
        SCM-022
        *Test case for unique attribute *

        **Test Scenario:**

        #. Create schema with unique attributes and save it.
        #. Create another object and try to use same name for first one, should fail.
        #. On the second object, try to use same test var for first one, should fail.
        #. On the second object, try to use same new_name for first one, should success.
        #. On the second object, try to use same number for first one, should fail.
        #. Change name of the first object and try to use the first name again, should success.
        #. Change test var of the first object and try to use the first test var again, should success.
        #. Change number of the first object and try to use the first number again, should success.
        #. Delete the second object and create new one.
        #. Set the new object's attributes with the same attributes of the second object, should success. 
        """
        self.log("Create schema with unique attributes and save it")
        scm = """
        @url = test.schema.1
        name* = "" (S)
        new_name = "" (S)
        &test = "" (S)
        &number = 0 (I)
        """
        schema = j.data.schema.get(scm)
        self.model = self.bcdb.model_get_from_schema(schema)
        schema_obj = self.model.new()
        name = self.random_string()
        new_name = self.random_string()
        test = self.random_string()
        number = random.randint(1, 99)
        schema_obj.name = name
        schema_obj.new_name = new_name
        schema_obj.test = test
        schema_obj.number = number
        schema_obj.save()

        self.log(
            "Create another object and try to use same name for first one, should fail"
        )
        schema_obj2 = self.model.new()
        schema_obj2.name = name
        with self.assertRaises(Exception):
            schema_obj2.save()
        schema_obj2.name = self.random_string()

        self.log(
            "On the second object, try to use same test var for first one, should fail"
        )
        schema_obj2.test = test
        with self.assertRaises(Exception):
            schema_obj2.save()
        schema_obj2.test = self.random_string()

        self.log(
            "On the second object, try to use same new_name for first one, should success"
        )
        schema_obj2.new_name = new_name
        schema_obj2.save()

        self.log(
            "On the second object, try to use same number for first one, should fail"
        )
        schema_obj2.number = number
        with self.assertRaises(Exception):
            schema_obj2.save()
        schema_obj2.number = random.randint(100, 199)

        self.log(
            "Change name of the first object and try to use the first name again, should success"
        )
        schema_obj.name = self.random_string()
        schema_obj.save()
        schema_obj2.name = name
        schema_obj2.save()

        self.log(
            "Change test var of the first object and try to use the first test var again, should success"
        )
        schema_obj.test = self.random_string()
        schema_obj.save()
        schema_obj2.test = test
        schema_obj2.save()

        self.log(
            "Change number of the first object and try to use the first number again, should success"
        )
        schema_obj.number = random.randint(200, 299)
        schema_obj.save()
        schema_obj2.number = number
        schema_obj2.save()

        self.log("Delete the second object and create new one.")
        schema_obj2.delete()
        schema_obj3 = self.model.new()

        self.log(
            "Set the new object's attributes with the same attributes of the second object, should success."
        )
        schema_obj3.name = name
        schema_obj3.save()
        schema_obj3.test = test
        schema_obj3.save()
        schema_obj3.new_name = new_name
        schema_obj3.save()
        schema_obj3.number = number
        schema_obj3.save()
