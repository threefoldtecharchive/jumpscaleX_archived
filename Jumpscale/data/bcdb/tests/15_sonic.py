from Jumpscale import j

def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="sonic")'

    """

    data = [
        {"name": "test1", "content": "lorem epsum"},
        {"name": "test2", "content": "foo bar"},
        {"name": "test3", "content": "I love threefold"},
    ]

    schema = """
    @url = test.docsites
    name* = (S)
    content*** = (S)
    """
    bcdb = j.data.bcdb.get("test")
    bcdb.reset()
    model = bcdb.model_get_from_schema(schema)

    for obj in data:
        o = model.new()
        o.name = obj["name"]
        o.content = obj["content"]
        o.save()

    res = model.search("lorem")
    assert res[0].name == "test1"

    res = model.search("bar")
    assert res[0].name == "test2"

    res = model.search("love")
    assert res[0].name == "test3"

    res[0].delete()

    assert len(model.search("love")) == 0
