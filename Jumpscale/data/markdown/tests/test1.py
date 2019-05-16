from Jumpscale import j


def test():

    md = j.data.markdown.document_get()

    # COMON EXAMPLES
    md.header_add(2, "this is title on level 2")

    table = md.table_add()
    table.header_add(["name", "descr"])
    table.row_add(["ghent", "best town ever"])
    table.row_add(["antwerp", "trying to be best town ever"])

    # EXAMPLE TO ADD DATA IN MARKDOWN
    test = {}
    test["descr"] = "some description"
    test["nr"] = 3
    test["subd"] = {"nr2": 3, "item": "sss"}

    md.data_add(test, "test", "myguid")

    test["nr"] = 4
    md.data_add(test, "test", "myguid2")

    md2 = j.data.markdown.document_get(str(md))

    # print (md2.hashlist_get("test"))

    print(md)


if __name__ == "__main__":
    test()
