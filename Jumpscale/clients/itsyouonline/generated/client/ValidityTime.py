"""
Auto-generated class for ValidityTime
"""
from Jumpscale import j
from . import client_support


class ValidityTime:
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :rtype: ValidityTime
        """

        return ValidityTime(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise j.exceptions.Value("No data or kwargs present")

        class_name = "ValidityTime"
        data = json or kwargs

        # set attributes

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
