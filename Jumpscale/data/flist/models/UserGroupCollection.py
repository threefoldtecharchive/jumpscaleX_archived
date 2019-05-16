from Jumpscale import j

from data.capnp.ModelBase import ModelBaseCollection


class UserGroupCollection(ModelBaseCollection):
    """
    """

    def find(self, name="", state=""):
        """
        @param state
            new
            ok
            error
            disabled
        """
        # @TODO: *1 needs to be properly implemented
        res = []
        for key in self._list_keys(name, state):
            res.append(self.get(key))
        return res
