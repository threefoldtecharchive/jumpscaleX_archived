from Jumpscale import j

from .BaseDataType import BaseDataTypeClass

from .PrimitiveTypes import BinaryData, Hash, Currency, Blockstake
from .FulfillmentTypes import FulfillmentBaseClass, FulfillmentSingleSignature 
from .ConditionTypes import ConditionBaseClass, ConditionNil 

class CoinInput(BaseDataTypeClass):
    """
    CoinIput class
    """
    def __init__(self, parentid=None, fulfillment=None, parent_output=None):
        self._parent_id = None
        self.parentid = parentid
        self._fulfillment = None
        self.fulfillment = fulfillment
        # property that can be set if known, but which is not part of the actual CoinInput
        self._parent_output = None
        self.parent_output = parent_output

    @classmethod
    def from_json(cls, obj):
        return cls(
            parentid=Hash.from_json(obj['parentid']),
            fulfillment=j.clients.tfchain.types.fulfillments.from_json(obj['fulfillment']))

    @property
    def parentid(self):
        return self._parent_id
    @parentid.setter
    def parentid(self, value):
        if isinstance(value, Hash):
            self._parent_id = Hash(value=value.value)
            return
        self._parent_id = Hash(value=value)
    
    @property
    def fulfillment(self):
        return self._fulfillment
    @fulfillment.setter
    def fulfillment(self, value):
        if not value:
            self._fulfillment = FulfillmentSingleSignature()
        else:
            assert isinstance(value, FulfillmentBaseClass)
            self._fulfillment = value
    
    @property
    def parent_output(self):
        return self._parent_output
    @parent_output.setter
    def parent_output(self, value):
        if not value:
            self._parent_output = CoinOutput()
        else:
            assert isinstance(value, CoinOutput)
            self._parent_output = value

    def json(self):
        return {
            'parentid': self._parent_id.json(),
            'fulfillment': self._fulfillment.json()
        }

    def sia_binary_encode(self, encoder):
        """
        Encode this CoinInput according to the Sia Binary Encoding format.
        """
        encoder.add_all(self._parent_id, self._fulfillment)

    def rivine_binary_encode(self, encoder):
        """
        Encode this CoinInput according to the Rivine Binary Encoding format.
        """
        encoder.add_all(self._parent_id, self._fulfillment)


class CoinOutput(BaseDataTypeClass):
    """
    CoinOutput class
    """
    def __init__(self, value=None, condition=None, id=None):
        self._value = None
        self.value = value
        self._condition = None
        self.condition = condition
        # property that can be set if known, but which is not part of the actual CoinOutput
        self._id = None
        self.id = id
        

    @classmethod
    def from_json(cls, obj):
        return cls(
            value=Currency.from_json(obj['value']),
            condition=j.clients.tfchain.types.conditions.from_json(obj['condition']))

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if isinstance(value, Currency):
            self._value = value
            return
        self._value = Currency(value=value)
    
    @property
    def condition(self):
        return self._condition
    @condition.setter
    def condition(self, value):
        if not value:
            self._condition = ConditionNil()
        else:
            assert isinstance(value, ConditionBaseClass)
            self._condition = value

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        if isinstance(value, Hash):
            self._id = Hash(value=value.value)
            return
        self._id = Hash(value=value)


    def json(self):
        return {
            'value': self._value.json(),
            'condition': self._condition.json()
        }

    def sia_binary_encode(self, encoder):
        """
        Encode this CoinOutput according to the Sia Binary Encoding format.
        """
        encoder.add_all(self._value, self._condition)
    
    def rivine_binary_encode(self, encoder):
        """
        Encode this CoinOutput according to the Rivine Binary Encoding format.
        """
        encoder.add_all(self._value, self._condition)


class BlockstakeInput(BaseDataTypeClass):
    """
    BlockstakeInput class
    """
    def __init__(self, parentid=None, fulfillment=None, parent_output=None):
        self._parent_id = None
        self.parentid = parentid
        self._fulfillment = None
        self.fulfillment = fulfillment
        # property that can be set if known, but which is not part of the actual BlockstakeInput
        self._parent_output = None
        self.parent_output = parent_output

    @classmethod
    def from_json(cls, obj):
        return cls(
            parentid=Hash.from_json(obj['parentid']),
            fulfillment=j.clients.tfchain.types.fulfillments.from_json(obj['fulfillment']))

    @property
    def parentid(self):
        return self._parent_id
    @parentid.setter
    def parentid(self, value):
        if isinstance(value, Hash):
            self._parent_id = Hash(value=value.value)
            return
        self._parent_id = Hash(value=value)

    @property
    def fulfillment(self):
        return self._fulfillment
    @fulfillment.setter
    def fulfillment(self, value):
        if not value:
            self._fulfillment = FulfillmentSingleSignature()
        else:
            assert isinstance(value, FulfillmentBaseClass)
            self._fulfillment = value

    @property
    def parent_output(self):
        return self._parent_output
    @parent_output.setter
    def parent_output(self, value):
        if not value:
            self._parent_output = BlockstakeOutput()
        else:
            assert isinstance(value, BlockstakeOutput)
            self._parent_output = value

    def json(self):
        return {
            'parentid': self._parent_id.json(),
            'fulfillment': self._fulfillment.json()
        }

    def sia_binary_encode(self, encoder):
        """
        Encode this BlockstakeInput according to the Sia Binary Encoding format.
        """
        encoder.add_all(self._parent_id, self._fulfillment)

    def rivine_binary_encode(self, encoder):
        """
        Encode this BlockstakeInput according to the Rivine Binary Encoding format.
        """
        encoder.add_all(self._parent_id, self._fulfillment)


class BlockstakeOutput(BaseDataTypeClass):
    """
    BlockstakeOutput class
    """
    def __init__(self, value=None, condition=None, id=None):
        self._value = None
        self.value = value
        self._condition = None
        self.condition = condition
        # property that can be set if known, but which is not part of the actual BlockstakeOutput
        self._id = None
        self.id = id


    @classmethod
    def from_json(cls, obj):
        return cls(
            value=Blockstake.from_json(obj['value']),
            condition=j.clients.tfchain.types.conditions.from_json(obj['condition']))

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if isinstance(value, Blockstake):
            self._value = value
            return
        self._value = Blockstake(value=value)

    @property
    def condition(self):
        return self._condition
    @condition.setter
    def condition(self, value):
        if not value:
            self._condition = ConditionNil()
        else:
            assert isinstance(value, ConditionBaseClass)
            self._condition = value

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        if isinstance(value, Hash):
            self._id = Hash(value=value.value)
            return
        self._id = Hash(value=value)


    def json(self):
        return {
            'value': self._value.json(),
            'condition': self._condition.json()
        }

    def sia_binary_encode(self, encoder):
        """
        Encode this BlockstakeOutput according to the Sia Binary Encoding format.
        """
        encoder.add_all(self._value, self._condition)

    def rivine_binary_encode(self, encoder):
        """
        Encode this BlockstakeOutput according to the Rivine Binary Encoding format.
        """
        encoder.add_all(self._value, self._condition)
