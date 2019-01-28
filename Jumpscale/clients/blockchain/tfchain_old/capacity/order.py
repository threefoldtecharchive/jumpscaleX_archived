"""
This modules defines the Capacity Order Class,
that can be used to easily encode and decode a capacity order,
as the binary arbitrary data of a regular coin transaction to the relevant 3Bot.

For more information see story: https://github.com/threefoldtech/home/issues/52

TODO: move this module to the correct (digitalme?) file location
"""


MAX_VALUE_CRU = (1<<8)-1
MAX_VALUE_MRU = (1<<16)-1
MAX_VALUE_HRU = (1<<32)-1
MAX_VALUE_SRU = (1<<32)-1
MAX_VALUE_NRU = (1<<16)-1

MAX_VALUE_DURATION = (1<<16)-1

MAX_LENGTH_DESCRIPTION = 32

class CapacityOrder:
    def __init__(self):
        # resource units
        self._cru = 0 # core unit
        self._mru = 0 # memory unit
        self._hru = 0 # HD unit
        self._sru = 0 # SSD unit
        self._nru = 0 # network unit
        # duration, expressed in cycles of 30 days
        self._duration = 0
        # optional `bytearray` description of maximum 32 bytes
        self._description = bytearray()


    def __repr__(self):
        output = 'Capacity order for {} days:\n'.format(self._duration*30)
        resources = [('cru', 'cores'), ('mru', 'GB'), ('hru', 'GB'), ('sru', 'GB'), ('nru', 'GB in/out')]
        for name, unit in resources:
            value = getattr(self, name)
            if value == 0:
                continue # skip if not defined
            output += '\t- {}: {} {}\n'.format(name.upper(), value, unit)
        if self._description:
            output += '\t- description: {}\n'.format(self._description)
        return output

    
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__


    @property
    def cru(self):
        """
        Core Unit, expressed in cores.
        """
        return self._cru
    @cru.setter
    def cru(self, value):
        """
        Set the desired Core Unit, expressed in cores.
        """
        value = int(value)
        if value > MAX_VALUE_CRU:
            raise ValueError("{} exceeds maximum CRU value of {}".format(value, MAX_VALUE_CRU))
        self._cru = value

    @property
    def mru(self):
        """
        Memory Unit, expressed in GB.
        """
        return self._mru
    @mru.setter
    def mru(self, value):
        """
        Set the desired Memory Unit, expressed in GB.
        """
        value = int(value)
        if value > MAX_VALUE_MRU:
            raise ValueError("{} exceeds maximum MRU value of {}".format(value, MAX_VALUE_MRU))
        self._mru = value

    @property
    def hru(self):
        """
        HD Unit, expressed in GB.
        """
        return self._hru
    @hru.setter
    def hru(self, value):
        """
        Set the desired HD Unit, expressed in GB.
        """
        value = int(value)
        if value > MAX_VALUE_HRU:
            raise ValueError("{} exceeds maximum HRU value of {}".format(value, MAX_VALUE_HRU))
        self._hru = value

    @property
    def sru(self):
        """
        SSD Unit, expressed in GB.
        """
        return self._sru
    @sru.setter
    def sru(self, value):
        """
        Set the desired SSD Unit, expressed in GB.
        """
        value = int(value)
        if value > MAX_VALUE_SRU:
            raise ValueError("{} exceeds maximum SRU value of {}".format(value, MAX_VALUE_SRU))
        self._sru = value

    @property
    def nru(self):
        """
        Network Unit, expressed in GB in/out.
        """
        return self._nru
    @nru.setter
    def nru(self, value):
        """
        Set the desired Network Unit, expressed in GB in/out.
        """
        value = int(value)
        if value > MAX_VALUE_NRU:
            raise ValueError("{} exceeds maximum NRU value of {}".format(value, MAX_VALUE_NRU))
        self._nru = value


    @property
    def duration(self):
        """
        Amount of 30-day cycles the capacity is to be reserved.
        """
        return self._duration
    @duration.setter
    def duration(self, value):
        """
        Set the amount of 30-day cycles the capacity is to be reserved,
        at least one cycle is required.
        """
        value = int(value)
        if value < 1:
            raise ValueError("at least one duration cycle is required")
        if value > MAX_VALUE_DURATION:
            raise ValueError("{} exceeds maximum duration value of {}".format(value, MAX_VALUE_DURATION))
        self._duration = value


    @property
    def description(self):
        """
        Optional short description, attached to the Capacity order.
        """
        return self._description
    @description.setter
    def description(self, value):
        """
        Set the optional short description, attached to the Capacity order,
        has to be a str or bytearray and can be maximum 32 bytes.
        """
        if isinstance(value, str):
            value = bytearray(value, 'utf-8')
        elif value is None:
            value = bytearray()
        if not isinstance(value, bytearray):
            raise ValueError("description has to be either a string or a bytearray")
        if len(value) > MAX_LENGTH_DESCRIPTION:
            raise ValueError("description can have maximum a length of {} bytes".format(MAX_LENGTH_DESCRIPTION))
        self._description = value


    def binary(self):
        """
        Encode this capacity order as a binary bytearray value,
        in the following format:
        +---------------+--------------+----------+--------------------+--------------+
        | resource flag | resources... | duration | description_length | description? |
        +---------------+--------------+----------+--------------------+--------------+
        | 1 byte        | n bytes      | 2 bytes  | 1 byte             | 0-32 bytes   | byte count
        +---------------+--------------+----------+--------------------+--------------+

        All integral values are encoded using the little-endian format.

        In which the resource flag is a single byte, where the first 5 bits are used
        as flags, indicating if the resource unit is defined (1) or not (0). The bits are
        layed out as following:
        +-----+-----+-----+-----+-----+---+---+---+
        | cru | mru | hru | sru | nru | / | / | / |
        +-----+-----+-----+-----+-----+---+---+---+
        |  0  |  1  |  2  |  3  | 4   | 5 | 6 | 7 | position
        +-----+-----+-----+-----+-----+---+---+---+

        A resource is encoded only if defined (meaning it has a value greater than 0).
        All defined resources are encoded in the order as defined by the resource flags.
        CRU is encoded as a single byte (uint8), HRU and SRU are encoded as 4 bytes (uint32),
        MRU and NRU are encoded as two bytes (uint16).

        The duration is encoded as 2 bytes (uint16). The description length is encoded
        as a single byte (uint8). The description is the amount of bytes as
        defined by the description length, and comes right after the description length.
        If description length equals 0, than no bytes are used for the description itself.

        The resource flag, duration and description length are always encoded.
        At least one resource flag is usually encoded (even though it is not enforced).
        The description is optional.
        """
        output = bytearray()
        # encode the resoure flag
        resource_flag = 0
        resoure_units = [(self._cru, 1), (self._mru, 2), (self._hru, 4), (self._sru, 4), (self._nru, 2)]
        for index, value in enumerate([value for value, kind in resoure_units]):
            resource_flag |= int(value > 0) << (7-index)
        output.extend(resource_flag.to_bytes(1, byteorder='little'))
        # encode the resource units
        for value, size in [(value, kind) for value, kind in resoure_units if value > 0]:
            output.extend(value.to_bytes(size, 'little'))
        # encode the duration
        output.extend(self._duration.to_bytes(2, 'little'))
        # always encode the description length
        desclen = len(self._description)
        if desclen > MAX_LENGTH_DESCRIPTION:
            # ensure the description does not go OOB
            raise ValueError("description can have maximum a length of {} bytes".format(MAX_LENGTH_DESCRIPTION))
        # encode the length as an uint8
        output.extend(desclen.to_bytes(1, 'little'))
        # if the length is greater than 0, also follow it up with the raw binary description
        if desclen > 0:
            # follow it up by the raw binary description
            output.extend(self._description)
        # return the fully encoded capacity order as a single bytearray
        return output

    @classmethod
    def from_binary(cls, b):
        """
        Binary decode a capacity order, usually needed to decode
        an order as defined as the arbitrary data of a tfhain money trasaction.

        See the documentation of the binary method of the CapacityOrder
        to learn more about the expected format of the given bytearay value.

        @param b: bytearay value which contains the binary data to be decoded as a Capacity Order.
        """
        if isinstance(b, bytes):
            b = bytearray(b)
        if not b or not isinstance(b, bytearray) or len(b) < 4:
            raise ValueError("given binary value cannot be decoded: not a valid (bytearray) value")

        # create the Capacity Order to fill
        co = cls()
        
        # decode the first byte as the resource flags
        position = 0
        resource_flags = b[position]
        position += 1
        # decode all the resource units
        resource_names_and_sizes = [('cru', 1), ('mru', 2), ('hru', 4), ('sru', 4), ('nru', 2)]
        for index in range(5):
            if (resource_flags >> (7-index))&1 == 0:
                continue # flag not set
            name, size = resource_names_and_sizes[index]
            start = position
            position += size
            setattr(co, name, int.from_bytes(b[start:position], byteorder='little'))
        
        # decode the duration
        start = position
        position += 2
        co.duration = int.from_bytes(b[start:position], byteorder='little')

        # decode the description length
        start = position
        position += 1
        desclen = int.from_bytes(b[start:position], byteorder='little')
        if desclen > 0:
            # if the desclen is greater than 0, also decode the description
            start = position
            position += desclen
            co.description = b[start:position]
        
        # ensure the byre array is completely decoded
        if position != len(b):
            raise ValueError("not everything of the given bytearray was decoded")
        # all good, return the correctly decoded Capacity Order
        return co
