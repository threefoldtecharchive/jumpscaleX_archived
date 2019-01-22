from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.rivine.test(name="basic")'
    """
    j.shell()

    e=j.data.rivine.encoder_bin()

    e.add(1)
    e.add("a")
    e.add([1,2,3,4])

    e.add_int8(1)

    print(e.data)

    j.shell()


