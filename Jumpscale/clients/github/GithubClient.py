from Jumpscale import j

from .User import User
from .Issue import Issue

import github
NotSet = github.GithubObject.NotSet

JSConfigClient = j.application.JSBaseConfigClass


class GitHubClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.github.client
        name* = "" (S)
        login = "" (S)
        token_ = "" (S)
        password_ = "" (S)
        """

    def _int(self):
        if not (self.token_ or (self.login and self.password_)):
            raise RuntimeError("Missing Github token_ or login/password_")

        login_or_token = self.token_ or self.login
        password_ = self.password_ if self.password_ != "" else None
        self.api = github.Github(login_or_token, password_, per_page=100)

    def _data_trigger_new(self):
        self.users = {}
        self.repos = {}
        self.milestones = {}

    # def getRepo(self, fullname):
    #     """
    #     fullname e.g. incubaid/myrepo
    #     """
    #     if fullname not in self.repos:
    #         r = self.api.get_repo(fullname)
    #         self.repos[fullname] = r
    #     return self.repos[fullname]

    def user_login_get(self, githubObj):
        if githubObj is None:
            return ""
        if githubObj.login not in self.users:
            user = User(self, githubObj=githubObj)
            self.users[githubObj.login] = user
        return self.users[githubObj.login].login

    def user_get(self, login="", githubObj=None):
        if login in self.users:
            return self.users[login]

        if githubObj is not None:
            if githubObj.login not in self.users:
                user = User(self, githubObj=githubObj)
                self.users[githubObj.login] = user
            return self.users[githubObj.login]

    def organizations_get(self):
        """gets all organization for an authorized user

        :return: paginated list of all the organizations
        :rtype: class:'github.PaginatedList.PaginatedList' of class:'github.Organization.Organization'
        """

        return self.api.get_user().get_orgs()

    def repos_get(self, organization_id=None):
        """gets all repos for a user if organization_id=None otherwise it return only repos for this organization

        :param organization_id: Id for the organization to get repos from if set, defaults to None
        :param organization_id: str, optional
        :raises RuntimeError: If no organization with that name was found
        :return: Pagination list of repos
        :rtype: class:'github.PaginatedList.PaginatedList' of class:'github.Repository.Repository'
        """

        if not organization_id:
            return self.api.get_user().get_repos()
        else:
            orgs = self.api.get_user().get_orgs()
            for org in orgs:
                if org.id == organization_id:
                    return org.get_repos()
            raise RuntimeError("Cannot find Organization with id :%s" % organization_id)

    def repo_get(self, repo_name):
        """gets a specific repo by name

        :param repo_name: repo name to look for
        :type repo_name: string
        :return: repo information
        :rtype: class:'github.Repository.Repository'
        """

        return self.api.get_user().get_repo(repo_name)

    def repo_create(self, name, description=NotSet, homepage=NotSet, private=NotSet, has_issues=NotSet, has_wiki=NotSet,
                    has_downloads=NotSet, auto_init=NotSet, gitignore_template=NotSet):
        """
        creates a repo

        :param:   name:               the repo name
        :type:   name:               string
        :param:   description:        repo description
        :type:   description:        string
        :param:   homepage:           home page for this repo
        :type:   homepage:           string
        :param:   private:            if true the repo will be created as private repo
        :type:   private:            boolean
        :param:   has_issues:         indicates that the repo has issues or no
        :type:   has_issues:         boolean
        :param:   has_wiki:           indicates that the repo has wiki or no
        :type:   has_wiki:           boolean
        :param:   has_downloads:      indicates that the repo has downloads or no
        :type:   has_downloads:      boolean
        :param:   auto_init:          if true the repo will be automaticly initialized
        :type:   auto_init:          boolean
        :param:   gitignore_template: the gitignore template
        :type:   gitignore_template: boolean
        :return:  the created repo
        :rtype:   class:'github.Repository.Repository'
        """
        return self.api.get_user().create_repo(
            name, description=description, homepage=homepage, private=private, has_issues=has_issues, has_wiki=has_wiki,
            has_downloads=has_downloads, auto_init=auto_init, gitignore_template=gitignore_template)

    def repo_delete(self, repo):
        """deletes a repo

        :param repo: repo to be deleted
        :type repo: class:'github.Repository.Repository'
        """

        repo.delete()
