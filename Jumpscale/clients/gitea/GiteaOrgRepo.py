from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaOrgRepo(j.builder._BaseClass):
    def __init__(
            self,
            organization=None,
            clone_url=None,
            created_at=None,
            default_branch=None,
            description=None,
            empty=True,
            fork=True,
            forks_count=0,
            full_name=None,
            html_url=None,
            id=0,
            mirror=True,
            name=None,
            open_issues_count=0,
            owner=None
    ):
        self.organization = organization
        self.clone_url= clone_url
        self.created_at = created_at
        self.default_branch = default_branch
        self.description = description
        self.empty = empty
        self.fork = fork
        self.forks_count = forks_count
        self.full_name = full_name
        self.html_url=html_url
        self.id = id
        self.mirror = mirror
        self.name = name
        self.open_issues_count = open_issues_count
        self.owner = owner

