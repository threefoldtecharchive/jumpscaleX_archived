from Jumpscale import j


def test():

    md = j.data.markdown.document_get()

    t = md.table_add()

    t.header_add("name,description,date")
    t.row_add("aname, this is my city, 11/1/22")
    t.row_add("2, 'this is my city2', 11/3/22")
    t.row_add("1,2,3")
    t.row_add(["1", "2", "3"])

    r = """
    |name |description     |date   |
    |-----|----------------|-------|
    |aname|this is my city |11/1/22|
    |2    |this is my city2|11/3/22|
    |1    |2               |3      |
    |1    |2               |3      |
    """
    r = j.core.text.strip(r)

    assert t.markdown.strip() == r.strip()

    assert t.rows[2] == ["1", "2", "3"]


if __name__ == "__main__":
    test()
