
from Jumpscale import j

class A():

    def __init__(self):
        self.__class__.name = "a"

class B(A):
    def __init__(self):
        A.__init__(self)
        self.__class__.name = "b"

if __name__ == "__main__":
    a=A()
    b=B()

    j.shell()
