
from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.schema.test(name="capnp_schema")'
    """
    schema0 = """
        @url = despiegk.test.group
        description = ""
        llist = "" (LO) !despiegk.test.users
        listnum = "" (LI)
        """

    schema1 = """
        @url = despiegk.test.users
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 (N) #this is a comment
        """

    schema_object1 = j.data.schema.get(schema1)
    schema_object0 = j.data.schema.get(schema0)
    print(schema_object0)

    print(schema_object1.capnp_schema)
    print(schema_object0.capnp_schema)

    self.logger.info("TEST DONE")

    return ("OK")
