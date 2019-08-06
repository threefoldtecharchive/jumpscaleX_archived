"""
Auto-generated class for Label
"""

from . import client_support
from Jumpscale import j


class Label(str):
    """
    auto-generated. don't touch.
    """

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    @staticmethod
    def create(**kwargs):
        """
        :rtype: Label
        """

        return Label(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise j.exceptions.Value("No data or kwargs present")

        class_name = "Label"
        data = json or kwargs

        # set attributes

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
