from .GithubClient import GitHubClient
from Jumpscale import j

JSConfigFactory = j.application.JSFactoryBaseClass


class GitHubFactory(JSConfigFactory):

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

        js_shell 'j.clients.github.test()'

        """

        # use config manager
        # go to configured github account
        # create repo test_1
        # list repo
        # create some issues on repo
        # populate labels / milestones
        # list the issues
        # ...
