from Jumpscale import j


class World(j.application.JSBaseConfigsFactoryClass):
    """
    some text explaining what the class does
    """

    __jslocation__ = "j.data.world"

    _CHILDCLASSES = [Cars, Ships]


class Cars(j.application.JSBaseConfigsClass):
    """
    ...
    """

    _CHILDCLASS = Car


class Car(j.application.JSBaseConfigClass):
    """
    one car instance
    """

    _SCHEMATEXT = """
        @url = jumpscale.example.car.1
        name* = ""
        city = ""
        """

    def _init(self):
        pass


class Ships(j.application.JSBaseConfigsClass):
    """
    ...
    """

    _CHILDCLASS = Ship


class Ship(j.application.JSBaseConfigClass):
    """
    one ship instance
    """

    _SCHEMATEXT = """
        @url = jumpscale.example.ship.1
        name* = ""
        location = ""
        onsea = true (b)
        """

    def _init(self):
        pass


def main(self):
    """
    to run:

    kosmos 'j.tutorials._code_run(name="object_structure")'
    """
