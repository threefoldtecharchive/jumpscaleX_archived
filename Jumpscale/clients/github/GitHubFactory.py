from .GithubClient import GitHubClient
from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass


class GitHubFactory(JSConfigs):

    __jslocation__ = "j.clients.github"
    _CHILDCLASS = GitHubClient

    def __init__(self):
        self.__imports__ = "PyGithub"
        self._clients = {}
        super(GitHubFactory, self).__init__()

    def issue_class_get(self):
        # return Issue
        return Issue

    def test(self):
        """

        kosmos 'j.clients.github.test()'

        """

        # use config manager
        # go to configured github account
        # create repo test_1
        # list repo
        # create some issues on repo
        # populate labels / milestones
        # list the issues
        # ...
