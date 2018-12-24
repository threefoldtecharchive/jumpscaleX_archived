from Jumpscale import j
from .GiteaRepo import GiteaRepo

default_labels = [
    {'color': '#e11d21', 'name': 'priority_critical'},
    {'color': '#f6c6c7', 'name': 'priority_major'},
    {'color': '#f6c6c7', 'name': 'priority_minor'},
    {'color': '#d4c5f9', 'name': 'process_duplicate'},
    {'color': '#d4c5f9', 'name': 'process_wontfix'},
    {'color': '#bfe5bf', 'name': 'state_inprogress'},
    {'color': '#bfe5bf', 'name': 'state_question'},
    {'color': '#bfe5bf', 'name': 'state_verification'},
    {'color': '#fef2c0', 'name': 'type_bug'},
    {'color': '#fef2c0', 'name': 'type_task'},
    {'color': '#fef2c0', 'name': 'type_story'},
    {'color': '#fef2c0', 'name': 'type_feature'},
    {'color': '#fef2c0', 'name': 'type_question'}
]

JSBASE = j.application.JSBaseClass


class GiteaOrg(j.application.JSBaseClass):

    def __init__(self, client, name):
        JSBASE.__init__(self)
        self.name = name
        self.id = client.orgs_currentuser_list()[name]
        self.client = client
        self.api = self.client.api.orgs

    def labels_default_get(self):
        return default_labels

    def _repos_get(self, refresh=False):
        def do():
            res = {}
            for item in self.client.api.orgs.orgListRepos(self.name)[0]:
                res[item.name] = item
            return res
        return self._cache.get("orgs", method=do, refresh=refresh, expire=60)

    def repos_list(self, refresh=False):
        """list repos in that organization

        :param refresh: if true will not use value in cache, defaults to False
        :param refresh: bool, optional
        :return: key-value of repo name and id
        :rtype: dict
        """

        res = {}
        for name, item in self._repos_get(refresh=refresh).items():
            res[name] = item.id
        return res

    def repo_get(self, name):
        """returns a gitea repo object

        :param name: name of the repo
        :type name: str
        :raises RuntimeError: if soecified name not in org's repos
        :return: gitea object
        :rtype: object
        """

        self._logger.info("repo:get:%s" % name)
        if name not in self._repos_get().keys():
            raise RuntimeError("cannot find repo with name:%s in %s" % (name, self))
        data = self._repos_get()[name]
        return GiteaRepo(self, name, data)

    def repo_new(self, name):
        """create a new repo if it doesn't exist

        :param name: name of the new repo
        :type name: str
        :return: response data which includes repo info and repo object from generated client
        :rtype: tuple
        """

        self._logger.info("repo:new:%s" % name)
        if name in self._repos_get().keys():
            self._logger.debug("no need to create repo on gitea, exists:%s"%name)
            return self._repos_get()[name]
        else:

            data = {'name': name}
            return self.client.api.org.createOrgRepo(data, org=self.name)

    def labels_milestones_add(self, labels=default_labels, remove_old=False):
        """Adds new labels to the organization. If a label with the same name exists on a repo, it won't be added.

        :param labels: list of dict representing labels ex {'color': '#e11d21', 'name': 'priority_critical'}, defaults to default_labels
        :param labels: list, optional
        :param remove_old: removes old labels if true, defaults to False
        :param remove_old: bool, optional
        """

        for repo_name in self.repos_list():
            repo = self.repo_get(repo_name)

            repo.milestones_add(remove_old=remove_old)
            repo.labels_add(labels, remove_old=remove_old)

    def __repr__(self):
        return "org:%s" % self.name

    __str__ = __repr__
