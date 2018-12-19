from Jumpscale import j

from .GiteaOrg import GiteaOrg

from JumpscaleLib.clients.gitea.client import Client


TEMPLATE = """
url = ""
gitea_token_ = ""
"""

JSConfigBase = j.application.JSBaseClass
JSBASE = j.application.JSBaseClass


class GiteaClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None,interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE,interactive=interactive)
        self._api = None

    def config_check(self):
        """
        check the configuration if not what you want the class will barf & show you where it went wrong
        """

        if self.config.data["url"] == "" or self.config.data["gitea_token_"] == "":
            return "url and gitea_token_ are not properly configured, cannot be empty"

        base_uri = self.config.data["url"]
        if "/api" not in base_uri:
            self.config.data_set("url", "%s/api/v1" % base_uri)
            self.config.save()

        # TODO:*1 need to do more checks that url is properly formated

    @property
    def api(self):
        """
        Return a generated gitea client to connect to the api
        """

        if not self._api:
            self._api = Client(base_uri=self.config.data["url"])
            self._api.security_schemes.passthrough_client_token.set_authorization_header(
                'token {}'.format(self.config.data["gitea_token_"]))
        return self._api

    def orgs_currentuser_list(self, refresh=False):
        """lists all user's organizations

        :param refresh: if true will not use value in cache, defaults to False
        :param refresh: bool, optional
        :return: key-value of org name and id
        :rtype: dict
        """
        def do():
            res = {}
            for item in self.api.user.orgListCurrentUserOrgs()[0]:
                res[item.username] = item.id
            return res
        return self._cache.get("orgs", method=do, refresh=refresh, expire=60)

    def org_get(self, name):
        """returns a gitea org object

        :param name: name of the organization
        :type name: str
        :raises RuntimeError: if couldn't find specified org in current user's orgs
        :return: gitea org object
        :rtype: object
        """
        self._logger.info("org:get:%s" % name)
        if name not in self.orgs_currentuser_list().keys():
            raise RuntimeError("Could not find %s in orgs on gitea" % name)
        return GiteaOrg(self, name)

    def labels_milestones_set(self, orgname="*", reponame="*", remove_old=False):
        """set default labels to specified repo

        :param orgname: name of the organization, defaults to "*" meaning all user's orgs
        :param orgname: str, optional
        :param reponame: [description], defaults to "*" meaning all user's repos in that org
        :param reponame: str, optional
        :param remove_old: removes old labels if true, defaults to False
        :param remove_old: bool, optional
        """

        self._logger.info("labels_milestones_set:%s:%s" % (orgname, reponame))
        if orgname == "*":
            for orgname0 in self.orgs_currentuser_list():
                self.labels_milestones_set(orgname=orgname0, reponame=reponame, remove_old=remove_old)
            return

        org = self.org_get(orgname)

        if reponame == "*":
            for reponame0 in org.repos_list():
                # self._logger.debug(org.repos_list())
                # self._logger.debug("reponame0:%s"%reponame0)
                self.labels_milestones_set(orgname=orgname, reponame=reponame0, remove_old=remove_old)
            return

        repo = org.repo_get(reponame)
        repo.labels_add(remove_old=remove_old)
        repo.milestones_add(remove_old=remove_old)

    def __repr__(self):
        return "gitea client"

    __str__ = __repr__
