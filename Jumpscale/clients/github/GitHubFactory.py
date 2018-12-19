from Jumpscale import j

JSConfigFactory = j.application.JSFactoryBaseClass

from .GithubClient import GitHubClient

class GitHubFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.github"
        self.__imports__ = "PyGithub"
        self._clients = {}
        JSConfigFactory.__init__(self, GitHubClient)

    def issue_class_get(self):
        # return Issue
        return Issue

    def test(self):
        """

        js_shell 'j.clients.github.test()'

        """

        #use config manager
        #go to configured github account
        # create repo test_1
        # list repo
        # create some issues on repo
        # populate labels / milestones
        # list the issues
        # ...



