from Jumpscale import j


class ZeroStorClient:
    def __init__(self, *kwargs):
        pass

    def put(self, data, *kwargs):
        raise j.exceptions.NotImplemented()

    def getFile(self, metadata):
        """
        @return the data
        """
        raise j.exceptions.NotImplemented()

    def putFile(self, path, *kwargs):
        """
        params for erasurecoding or replication or...

        @return metadata as json what is needed to restore the file
        """
        raise j.exceptions.NotImplemented()

    def getFile(self, metadata, path):
        """
        """
        raise j.exceptions.NotImplemented()

    def startClient(self):
        """
        """
        # use prefab to start the client so we can connect to it using grpc
        raise j.exceptions.NotImplemented()

    def installClient(self):
        """
        """
        # use prefab to build/install the client for zerostor
        raise j.exceptions.NotImplemented()

    def testPerformance(self):

        # ... do some performance test
        raise j.exceptions.NotImplemented()
