from Jumpscale import j


class ZeroStorClient:
    def __init__(self, *kwargs):
        pass

    def put(self, data, *kwargs):
        raise NotImplementedError()

    def getFile(self, metadata):
        """
        @return the data
        """
        raise NotImplementedError()

    def putFile(self, path, *kwargs):
        """
        params for erasurecoding or replication or...

        @return metadata as json what is needed to restore the file
        """
        raise NotImplementedError()

    def getFile(self, metadata, path):
        """
        """
        raise NotImplementedError()

    def startClient(self):
        """
        """
        # use prefab to start the client so we can connect to it using grpc
        raise NotImplementedError()

    def installClient(self):
        """
        """
        # use prefab to build/install the client for zerostor
        raise NotImplementedError()

    def testPerformance(self):

        # ... do some performance test
        raise NotImplementedError()
