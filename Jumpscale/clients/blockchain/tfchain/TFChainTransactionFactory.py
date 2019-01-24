from Jumpscale import j

class TFChainTransactionFactory(j.application.JSBaseClass):
    """
    TFChain Transaction Factory class
    """

    def new(self, version=1):
        """
        Creates and return a transaction of the speicfied verion

        @param version: Version of the transaction
        """
        if version == 1:
            return TransactionV1()
        raise ValueError("transaction version {} is not supported".format(version))


from abc import ABC, abstractmethod, abstractclassmethod

class TransactionBaseClass(ABC, j.application.JSBaseClass):
    @property
    @abstractmethod
    def version(self):
        """
        Version of this Transaction.
        """
        pass
    
    @property
    @abstractmethod
    def id(self):
        """
        ID attached to this Transaction,
        returned only when known.
        """
        pass


    @property
    def coin_inputs(self):
        """
        Coin inputs of this Transaction,
        used as funding for coin outputs, fees and any other kind of coin output.
        """
        return []

    @property
    def coin_outputs(self):
        """
        Coin outputs of this Transaction,
        funded by the Transaction's coin inputs.
        """
        return []

    @property
    def minerfees(self):
        """
        Miner fees, paid to the block creator of this Transaction,
        funded by this Transaction's coin inputs.
        """
        return []
    
    @property
    def data(self):
        """
        Optional binary data attached to this Transaction,
        with a max length of 83 bytes.
        """
        return bytearray()
    
    @abstractmethod
    def json(self):
        pass


class TransactionV1(TransactionBaseClass):
    def __init__(self):
        self._id = None
    
    @classmethod
    def from_json(cls, s):
        raise Exception("TODO")

    @property
    def version(self):
        return 1
    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        if type(id) is type(self._id):
            self._id = id
        else:
            self._id = j.clients.tfchain.types.hash_new(value=id)
    
    def json(self):
        raise Exception("TODO")
