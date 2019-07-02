from Jumpscale import j


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


class Cars(j.application.JSBaseConfigsClass):
    """
    ...
    """

    _CHILDCLASS = Car


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


class Ships(j.application.JSBaseConfigsClass):
    """
    ...
    """

    _CHILDCLASS = Ship


class World(j.application.JSBaseConfigsFactoryClass):
    """
    some text explaining what the class does
    """

    _CHILDCLASSES = [Cars, Ships, Ship]


def main(self):
    """
    to run:

    kosmos 'j.tutorials.base._code_run("tutorials",name="object_structure")'
    """

    ships = Ships()
    ship1 = ships.new(name="ibizaboat")
    assert ship1.name == "ibizaboat"

    j.shell()

    w = World()
    car = w.cars.new()
    assert w.ship.onsea
    w.ship.onsea = False
    assert w.ship.onsea == False
    j.shell()


main(1)
