from Jumpscale import j


from .GiteaIssue import GiteaIssue
from .GiteaIssueTime import GiteaIssueTime

JSBASE = j.application.JSBaseClass


class GiteaIssues(j.application.JSBaseClass):
    def __init__(self, user, repo=None):
        JSBASE.__init__(self)
        self.user = user
        self.repo = repo
        self.position = -1
        self.page = 0
        self._items = []

    def new(self):
        return GiteaIssue(self.user.client, self.user, self.repo)

    def get(self, id, fetch=False):
        from .GiteaUser import GiteaUser
        from .GiteaRepo import GiteaRepo

        issue = self.new()
        if fetch:
            resp = self.user.client.api.repos.issueGetIssue(str(id), self.repo.name, self.user.username).json()
            for k, v in resp.items():
                setattr(issue, k, v)
            issue.id = issue.number

        if hasattr(issue, "user") and type(issue.user) == dict:
            u = GiteaUser(self.user.client)
            for k, v in issue.user.items():
                setattr(u, k, v)
            issue.user = u

        if hasattr(issue, "repo") and type(issue.repo) == dict:
            r = GiteaRepo(self.user.client)
            for k, v in issue.repo.items():
                setattr(r, k, v)
            issue.repo = r
        return issue

    def tracked_times(self):
        result = []
        if not self.user.is_current:
            raise Exception("You can not use this API call in behalf of another user")
        resp = self.user.client.api.user.userCurrentTrackedTimes().json()
        for item in resp:
            t = GiteaIssueTime(self.user)
            for k, v in item.items():
                setattr(t, k, v)
            result.append(t)
        return result

    def list(self, page=1, state=None):
        if state is None:
            state = "open"

        if state not in ["open", "closed", "all"]:
            raise Exception("Invalid state. only allowed [closed, open, all]")
        result = []
        resp = self.user.client.api.repos.issueListIssues(self.repo.name, self.user.username, page, state).json()
        for item in resp:
            issue = GiteaIssue(self.user.client, self.user, self.repo)
            for k, v in item.items():
                setattr(issue, k, v)
            issue.id = issue.number
            result.append(issue)
        return result

    def __next__(self):
        if len(self._items) == 0 or self.position == len(self._items) - 1:
            self.page += 1
            search_results = self.list(self.page)
            if not search_results:
                self.position = -1
                self.page = 0
                self._items = []
                raise StopIteration()

            self._items.extend(search_results)

        self.position += 1

        return self._items[self.position]

    def __iter__(self):
        return self

    def __str__(self):
        for_ = "user", self.user.username
        if self.repo:
            for_ = "repo", self.repo.name

        return "Issues for {0}: {1}".format(for_[0], for_[1])

    __repr__ = __str__
