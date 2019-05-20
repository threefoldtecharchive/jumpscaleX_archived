from Jumpscale import j

from abc import abstractmethod, abstractclassmethod


class BaseDataTypeClass(j.data.rivine.BaseSiaObjectEncoder, j.data.rivine.BaseRivineObjectEncoder):
    """
    Base type defines the type all TFChain data types inheret from.
    """

    @abstractclassmethod
    def from_json(cls, obj):
        pass

    @abstractmethod
    def json(self):
        pass
