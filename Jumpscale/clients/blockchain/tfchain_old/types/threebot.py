"""
This modules defines types related to 3Bots
"""

import datetime

from clients.blockchain.tfchain.types import signatures as tftsig
from clients.blockchain.tfchain.types import network as tftnet

class ThreeBotRecord:
    """
    ThreeBotRecord defines the class of a 3Bot Record,
    exposing all its properties as public python properties.
    """

    def __init__(self):
        self._identifier = 0
        self._names = []
        self._addresses = []
        self._public_key = None
        self._expiration = 0


    def __str__(self):
        s = 'Record of 3Bot {}:\n'.format(self._identifier)
        if self._addresses:
            s += '* addresses: {}\n'.format(", ".join([str(addr) for addr in self._addresses]))
        if self._names:
            s += '* names: {}\n'.format(", ".join(self._names))
        s += '* public key: {}\n'.format(str(self._public_key))
        s += '* expiration time: {} ({})\n'.format(datetime.datetime.fromtimestamp(self._expiration), self._expiration)
        return s


    def __repr__(self):
        """
        Override so we have nice output in js shell if the object is not assigned
        without having to call the print method.
        """
        return str(self)


    @classmethod
    def from_dict(cls, dict_data):
        """
        Create a ThreeBotRecord from a (JSON-decoded) dictionary,
        with the 'id', 'publickey' and 'expiration' properties assumed as required properties,
        while the 'name' and 'addresses' properties are taken as optional properties.

        A ValueError Exception is raised when a required property is missing.

        @param dict_data: (JSON-decoded) dictionary containing all properties of a 3Bot record
        """

        record = cls()
        if 'id' not in dict_data:
            raise ValueError("required 3Bot record 'id' property is missing")
        record._identifier = int(dict_data['id'])
        if 'names' in dict_data:
            record._names = dict_data['names'].copy()
        if 'addresses' in dict_data:
            for addr in dict_data['addresses']:
                record._addresses.append(tftnet.NetworkAddress.from_string(addr))
        if 'publickey' not in dict_data:
            raise ValueError("required 3Bot record 'publickey' property is missing for 3Bot {}".format(record._identifier))
        record._public_key = tftsig.SiaPublicKey.from_string(dict_data['publickey'])
        if 'expiration' not in dict_data:
            raise ValueError("required 3Bot record 'expiration' property is missing for 3Bot {}".format(record._identifier))
        record._expiration = int(dict_data['expiration'])
        return record


    @property
    def identifier(self):
        """
        Returns the unique (integral) identifier of a 3Bot.
        """
        return self._identifier

    @property
    def names(self):
        """
        Returns all (3Bot) names linked to this 3Bot.
        """
        return self._names

    @property
    def addresses(self):
        """
        Returns all (network) addresses this 3Bot is reachable on,
        directly or by using one of its available 3Bot names instead.
        """
        return self._addresses

    @property
    def public_key(self):
        """
        Returns the (unique) public key of this 3Bot,
        used to verify the signatures of any transactions signed by this 3Bot.
        """
        return self._public_key

    @property
    def expiration_timestamp(self):
        """
        Returns the expiration (UNIX seconds) timestamp of this 3Bot.
        This 3Bot should be considered inactive if this value is less than the current (block)chain timestamp,
        meaning the names property of an inactive 3Bot should be assumed empty, no matter what the record still has defined.
        """
        return self._expiration
