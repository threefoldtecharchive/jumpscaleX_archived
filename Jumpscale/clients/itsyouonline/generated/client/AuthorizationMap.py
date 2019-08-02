"""
Auto-generated class for AuthorizationMap
"""
from .Label import Label
from Jumpscale import j
from . import client_support


class AuthorizationMap:
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type reallabel: Label
        :type requestedlabel: Label
        :rtype: AuthorizationMap
        """

        return AuthorizationMap(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise j.exceptions.Value("No data or kwargs present")

        class_name = "AuthorizationMap"
        data = json or kwargs

        # set attributes
        data_types = [Label]
        self.reallabel = client_support.set_property("reallabel", data, data_types, False, [], False, True, class_name)
        data_types = [Label]
        self.requestedlabel = client_support.set_property(
            "requestedlabel", data, data_types, False, [], False, True, class_name
        )

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
