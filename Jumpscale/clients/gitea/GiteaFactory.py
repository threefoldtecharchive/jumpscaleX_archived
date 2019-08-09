from Jumpscale import j
import os
import sys

from .GiteaClient import GiteaClient
from pprint import pprint as print

# https://docs.grid.tf/api/swagger example api source


# TODO: (phase 2): export/import a full repo (with issues, milestones & labels) (per repo)

JSConfigBase = j.application.JSBaseConfigsClass
JSBASE = j.application.JSBaseClass


class GiteaFactory(JSConfigBase):
    __jslocation__ = "j.clients.gitea"
    _CHILDCLASS = GiteaClient

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def get_by_params(self, instance, url, gitea_token):
        """get gitea client instance without using config manager

        :param instance: name of the instance
        :type instance: str
        :param url: url of gitea server
        :type url: str
        :param gitea_token: generated gittea user token
        :type gitea_token: str
        """
        data = {}
        data["url"] = instance
        data["gitea_token_"] = gitea_token
        self.get(instance=instance, data=data)

    def generate(self):
        """
        generate the client out of the raml specs

        get your token from https://docs.grid.tf/user/settings/applications

        """
        c = j.tools.raml.get(self._path)
        c.client_python_generate()

    def test(self):
        """
        kosmos 'j.clients.gitea.test()'
        """
        # self.generate()
        cl = self.get()
        cl.cache.reset()

        print(cl.orgs_currentuser_list())

        names = [item for item in cl.orgs_currentuser_list().keys()]
        names.sort()
        if "test" in names:
            name = "test"
        else:
            raise j.exceptions.Base("can only run test if test org exists")

        org = cl.org_get(name)

        if "testrepo" not in org.repos_list():
            # means no test repo yet, lets create one
            org.repo_new("testrepo")

        print(org.repos_list())
        repo_name = [item for item in org.repos_list(refresh=True).keys()][0]  # first reponame

        repo = org.repo_get(repo_name)

        print(repo.issues_get())

        org.labels_milestones_add(remove_old=True)
