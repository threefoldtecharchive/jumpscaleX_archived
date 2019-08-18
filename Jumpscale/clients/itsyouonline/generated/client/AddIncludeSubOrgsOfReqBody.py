"""
Auto-generated class for AddIncludeSubOrgsOfReqBody
"""
from six import string_types
from Jumpscale import j
from . import client_support


class AddIncludeSubOrgsOfReqBody:
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type globalid: str
        :rtype: AddIncludeSubOrgsOfReqBody
        """

        return AddIncludeSubOrgsOfReqBody(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise j.exceptions.Value("No data or kwargs present")

        class_name = "AddIncludeSubOrgsOfReqBody"
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.globalid = client_support.set_property("globalid", data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
