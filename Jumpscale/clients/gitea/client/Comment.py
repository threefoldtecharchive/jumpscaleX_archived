# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.

"""
Auto-generated class for Comment
"""
from .User import User
from datetime import datetime
from six import string_types

from . import client_support


class Comment(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type body: string_types
        :type created_at: datetime
        :type html_url: string_types
        :type id: int
        :type issue_url: string_types
        :type pull_request_url: string_types
        :type updated_at: datetime
        :type user: User
        :rtype: Comment
        """

        return Comment(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise j.exceptions.Value("No data or kwargs present")

        class_name = "Comment"
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.body = client_support.set_property("body", data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.created_at = client_support.set_property(
            "created_at", data, data_types, False, [], False, False, class_name
        )
        data_types = [string_types]
        self.html_url = client_support.set_property("html_url", data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.id = client_support.set_property("id", data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.issue_url = client_support.set_property("issue_url", data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.pull_request_url = client_support.set_property(
            "pull_request_url", data, data_types, False, [], False, False, class_name
        )
        data_types = [datetime]
        self.updated_at = client_support.set_property(
            "updated_at", data, data_types, False, [], False, False, class_name
        )
        data_types = [User]
        self.user = client_support.set_property("user", data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
