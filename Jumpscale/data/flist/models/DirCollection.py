from Jumpscale import j

from data.capnp.ModelBaseCollection import ModelBaseCollection


class DirCollection(ModelBaseCollection):
    """
    It's used to list/find/create new Instance of Dir Model object
    """

    def find(self, location=""):
        """
        part of path can use regex expression
        do not walk over full big fs like that because mem will blow up

        DO Not forget to add .* at end otherwise you won't find much, its a real regex instruction
        """
        res = []
        for item in self.list(location=location):
            res.append(self.get(item[1]))
        return res

    def list(self, location=".*"):
        """
        DO Not forget to add .* at end otherwise you won't find much, its a real regex instruction
        """
        res = self._index.list(location, returnIndex=True)
        return res
