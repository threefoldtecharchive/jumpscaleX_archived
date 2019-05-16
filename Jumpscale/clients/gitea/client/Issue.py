# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.

"""
Auto-generated class for Issue
"""
from .Label import Label
from .Milestone import Milestone
from .PullRequestMeta import PullRequestMeta
from .User import User
from datetime import datetime
from six import string_types

from . import client_support


class Issue(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type assignee: User
        :type body: string_types
        :type comments: int
        :type created_at: datetime
        :type id: int
        :type labels: list[Label]
        :type milestone: Milestone
        :type number: int
        :type pull_request: PullRequestMeta
        :type state: string_types
        :type title: string_types
        :type updated_at: datetime
        :type url: string_types
        :type user: User
        :rtype: Issue
        """

        return Issue(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError("No data or kwargs present")

        class_name = "Issue"
        data = json or kwargs

        # set attributes
        data_types = [User]
        self.assignee = client_support.set_property("assignee", data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.body = client_support.set_property("body", data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.comments = client_support.set_property("comments", data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.created_at = client_support.set_property(
            "created_at", data, data_types, False, [], False, False, class_name
        )
        data_types = [int]
        self.id = client_support.set_property("id", data, data_types, False, [], False, False, class_name)
        data_types = [Label]
        self.labels = client_support.set_property("labels", data, data_types, False, [], True, False, class_name)
        data_types = [Milestone]
        self.milestone = client_support.set_property("milestone", data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.number = client_support.set_property("number", data, data_types, False, [], False, False, class_name)
        data_types = [PullRequestMeta]
        self.pull_request = client_support.set_property(
            "pull_request", data, data_types, False, [], False, False, class_name
        )
        data_types = [string_types]
        self.state = client_support.set_property("state", data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.title = client_support.set_property("title", data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.updated_at = client_support.set_property(
            "updated_at", data, data_types, False, [], False, False, class_name
        )
        data_types = [string_types]
        self.url = client_support.set_property("url", data, data_types, False, [], False, False, class_name)
        data_types = [User]
        self.user = client_support.set_property("user", data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
