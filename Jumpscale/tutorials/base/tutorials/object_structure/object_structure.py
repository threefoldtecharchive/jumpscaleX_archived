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

    def _init(self, **kwargs):
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

    def _init(self, **kwargs):
        self.a = "some"
        pass


class Ships(j.application.JSBaseConfigsClass):
    """
    ...
    """

    _CHILDCLASS = Ship

    def _init(self, **kwargs):
        self.a = "a"

    def test(self):
        pass


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
    ship1 = ships.get(name="ibizaboat")
    assert ship1.name == "ibizaboat"

    # small test to see that the dataprops are visible
    assert len(ship1._dataprops_names_get()) == 3

    w = World()

    j.shell()

    car = w.cars.get("rabbit")
    car2 = w.cars.get("bobby")
    assert car.name == "rabbit"
    assert w.ship.onsea
    w.ship.onsea = False
    assert w.ship.onsea == False

    assert len(w.cars.find()) == 2

    assert len(w.cars.find(name="rabbit")) == 1

    allchildren = w._children_recursive_get()
    assert len(allchildren) == 5

    w.save()
    assert len(w.cars._model.find()) == 2  # proves that the data has been saved in the DB

    print("TEST OK")


main(1)
