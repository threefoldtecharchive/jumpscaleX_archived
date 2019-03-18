
from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="capnp_schema")'
    """
    schema0 = """
        @url = despiegk.test.group
        description = ""
        llist =  (LO) !despiegk.test.users
        listnum = (LI)
        """

    schema1 = """
        @url = despiegk.test.users
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate = 0.0 (N) #this is a comment
        """

    o1_schema = j.data.schema.get(schema0)
    o2_schema = j.data.schema.get(schema1)

    o1=o1_schema.new()

    print(o1_schema)

    print(o1_schema._capnp_schema)
    print(o2_schema._capnp_schema)

    o1.listnum.append("1")
    assert o1.listnum[0] == 1

    jsx_obj = o1.llist.new()

    assert jsx_obj.cost_estimate == 0.0
    assert jsx_obj.cost_estimate == 0


    self._log_info("TEST DONE CAPNP")

    return ("OK")
