from Jumpscale import j
import random
from uuid import uuid4

from unittest import TestCase


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="unique_data")' --debug

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
    j.core.tools.log("Create schema with unique attributes and save it", level=20)

    scm = """
    @url = test.schema.1
    name* = "" (S)
    new_name = "" (S)
    &test = "" (S)
    &number = 0 (I)
    """
    test_case = TestCase()

    j.servers.zdb.start_test_instance()
    self.zdb = j.clients.zdb.client_get(port=9901)
    self.bcdb = j.data.bcdb.new("test", zdbclient=self.zdb)
    schema = j.data.schema.get(scm)
    self.model = self.bcdb.model_get_from_schema(schema)
    schema_obj = self.model.new()
    name = "s" + str(uuid4()).replace("-", "")[:10]
    new_name = "s" + str(uuid4()).replace("-", "")[:10]
    test = "s" + str(uuid4()).replace("-", "")[:10]
    number = random.randint(1, 99)
    schema_obj.name = name
    schema_obj.new_name = new_name
    schema_obj.test = test
    schema_obj.number = number
    schema_obj.save()
    j.core.tools.log(
        "Create another object and try to use same name for first one, should fail",
        level=20,
    )

    schema_obj2 = self.model.new()
    schema_obj2.name = name
    with test_case.assertRaises(Exception):
        schema_obj2.save()
    schema_obj2.name = "s" + str(uuid4()).replace("-", "")[:10]
    j.core.tools.log(
        "On the second object, try to use same test var for first one, should fail",
        level=20,
    )

    schema_obj2.test = test
    with test_case.assertRaises(Exception):
        schema_obj2.save()
    schema_obj2.test = "s" + str(uuid4()).replace("-", "")[:10]
    j.core.tools.log(
        "On the second object, try to use same new_name for first one, should success",
        level=20,
    )

    schema_obj2.new_name = new_name
    schema_obj2.save()
    j.core.tools.log(
        "On the second object, try to use same number for first one, should fail",
        level=20,
    )

    schema_obj2.number = number
    with test_case.assertRaises(Exception):
        schema_obj2.save()
    schema_obj2.number = random.randint(100, 199)
    j.core.tools.log(
        "Change name of the first object and try to use the first name again, should success",
        level=20,
    )

    schema_obj.name = "s" + str(uuid4()).replace("-", "")[:10]
    schema_obj.save()
    schema_obj2.name = name
    schema_obj2.save()
    j.core.tools.log(
        "Change test var of the first object and try to use the first test var again, should success",
        level=20,
    )

    schema_obj.test = "s" + str(uuid4()).replace("-", "")[:10]
    schema_obj.save()
    schema_obj2.test = test
    schema_obj2.save()
    j.core.tools.log(
        "Change number of the first object and try to use the first number again, should success",
        level=20,
    )

    schema_obj.number = random.randint(200, 299)
    schema_obj.save()
    schema_obj2.number = number
    schema_obj2.save()
    j.core.tools.log("Delete the second object and create new one.", level=20)
    schema_obj2.delete()
    schema_obj3 = self.model.new()
    j.core.tools.log(
        "Set the new object's attributes with the same attributes of the second object, should success.",
        level=20,
    )

    schema_obj3.name = name
    schema_obj3.save()
    schema_obj3.test = test
    schema_obj3.save()
    schema_obj3.new_name = new_name
    schema_obj3.save()
    schema_obj3.number = number
    schema_obj3.save()
    self.bcdb.reset()
    j.servers.zdb.stop()

