# Copyright (C) July 2018:  TF TECH NV in Belgium see https://www.threefold.tech/
# In case TF TECH NV ceases to exist (e.g. because of bankruptcy)
#   then Incubaid NV also in Belgium will get the Copyright & Authorship for all changes made since July 2018
#   and the license will automatically become Apache v2 for all code related to Jumpscale & DigitalMe
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.
# LICENSE END


from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="models")'

    work with toml files and see if models get generated properly

    """
    mpath = self._dirpath + "/tests/models"
    assert j.sal.fs.exists(mpath)

    # make sure we remove the maybe already previously generated model file
    for item in j.sal.fs.listFilesInDir(mpath, filter="*.py"):
        j.sal.fs.remove(item)

    bcdb, _ = self._load_test_model()

    bcdb.models_add(mpath)

    model = bcdb.model_get_from_url("jumpscale.bcdb.test.house")

    model_obj = model.new()
    model_obj.cost = "10 USD"
    model_obj.save()

    data = model.get(model_obj.id)

    assert data.cost_usd == 10

    assert model_obj.cost_usd == 10

    # assert model.index.select().first().cost == 10.0  # is always in usd
    # TODO:*1 need to get the sqlite index to work again

    print("TEST FOR MODELS DONE, but is still minimal")

    return "OK"
