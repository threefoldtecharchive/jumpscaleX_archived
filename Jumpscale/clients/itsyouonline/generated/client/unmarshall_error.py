from Jumpscale import j


class UnmarshallError(Exception):
    def __init__(self, resp, message=""):
        pass
        self.response = resp
        self.message = message
