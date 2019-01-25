from Jumpscale import j

from .BaseDataType import BaseDataTypeClass

from .PrimitiveTypes import BinaryData, Currency
from .FulfillmentTypes import FulfillmentBaseClass, FulfillmentSingleSignature 
from .ConditionTypes import ConditionBaseClass, ConditionNil 

class CoinInput(BaseDataTypeClass):
    """
    CoinIput class
    """
    def __init__(self, parent_id=None, fulfillment=None):
        self._parent_id = BinaryData()
        self.parent_id = parent_id
        self._fulfillment = FulfillmentSingleSignature()
        self.fulfillment = fulfillment

    @classmethod
    def from_json(cls, obj):
        return cls(
            parent_id=BinaryData.from_json(obj['parentid']),
            fulfillment=j.clients.tfchain.types.fulfillments.from_json(obj['fulfillment']))

    @property
    def parent_id(self):
        return self._parent_id
    @parent_id.setter
    def parent_id(self, value):
        if isinstance(value, BinaryData):
            self._parent_id.value = value.value
            return
        if not value:
            self._parent_id = BinaryData()
        else:
            self._parent_id.value = value
    
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

    def json(self):
        return {
            'parentid': self._parent_id.json(),
            'fulfillment': self._fulfillment.json()
        }

    # binary encoding is not supported for coin inputs, as this client does not require it
    def sia_binary_encode(self, encoder):
        raise Exception("sia binary encoding not supported for coin inputs by this client")
    def rivine_binary_encode(self, encoder):
        raise Exception("rivine binary encoding not supported for coin inputs by this client")


class CoinOutput(BaseDataTypeClass):
    """
    CoinOutput calss
    """
    def __init__(self, value=None, condition=None):
        self._value = Currency()
        self.value = value
        self._condition = ConditionNil()
        self.condition = condition

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
        if not value:
            self._value = Currency()
        else:
            self._value.value = value
    
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
