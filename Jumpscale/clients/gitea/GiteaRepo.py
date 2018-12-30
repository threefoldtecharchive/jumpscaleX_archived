from Jumpscale import j
from datetime import datetime
import calendar

JSBASE = j.application.JSBaseClass


class GiteaRepo(j.application.JSBaseClass):

    def __init__(self, org, name, data):
        JSBASE.__init__(self)
        self.name = data.name
        self.owner = data.owner.login
        self.data = data
        self.org = org
        self.id = data.id
        self.client = org.client
        self.api = self.client.api.repos

    def labels_add(self, labels=None, remove_old=False):
        """Add multiple labels to 1 or more repo's.
        If a label with the same name exists on a repo, it won't be added.

        :param labels: a list of labels  ex: [{'color': '#fef2c0', 'name': 'state_blocked'}] if none will use default org labels, defaults to None
        :param labels: list, optional
        :param remove_old: removes old labels if true, defaults to False
        :param remove_old: bool, optional
        """

        self._logger.info("labels add")

        labels_default = labels or self.org.labels_default_get()

        repo_labels = self.api.issueListLabels(self.name, self.owner)[0]
        # @TODO: change the way we check on label name when this is fixed
        names = [l.name for l in repo_labels]
        for label in labels_default:
            if label["name"] in names:
                continue
            self.client.api.repos.issueCreateLabel(label, self.name, self.owner)

        def get_label_id(name):
            for item in repo_labels:
                if item.name == name:
                    return str(item.id)

        if remove_old:
            labels_on_repo = [item.name for item in repo_labels]
            labels_default = [item['name'] for item in labels_default]
            for label in labels_on_repo:
                if label not in labels_default:
                    self.client.api.repos.issueDeleteLabel(get_label_id(label), self.name, self.owner)

    def milestones_add(self, milestones=None, remove_old=False):
        """Add multiple milestones to multiple repos.
        If a milestone with the same title exists on a repo, it won't be added.
        If no milestones are supplied, the default milestones for the current quarter will be added.

        :param milestones: a list of milestones ex: [['Q1','2018-03-31'],...], defaults to None
        :param milestones: list, optional
        :param remove_old: removes old milestones if true, defaults to False
        :param remove_old: bool, optional
        """

        self._logger.info("milestones add")

        if not milestones:
            milestones = self.milestones_default

        def deadline_get(year_month_day):
            year, month, day = year_month_day.split("-")
            return '%s-%s-%sT23:59:00Z' % (year, str(month).zfill(2), str(day).zfill(2))

        def milestone_get(title, deadline):
            deadline = deadline_get(deadline)
            return {"title": title, "due_on": deadline}

        repo_milestones = self.client.api.repos.issueGetMilestones(self.name, self.owner)[0]
        # @TODO: change the way we check on milestone title when this is fixed https://github.com/Jumpscale/go-raml/issues/396
        names = [m.title for m in repo_milestones]
        for title, deadline in milestones:
            if title in names:
                continue
            milestone = milestone_get(title, deadline)
            self.client.api.repos.issueCreateMilestone(milestone, self.name, self.owner)

        milestone = milestone_get("roadmap", "2100-12-30")
        self.client.api.repos.issueCreateMilestone(milestone, self.name, self.owner)

        if remove_old:
            milestones_default = [item[0] for item in milestones]
            for item in repo_milestones:
                if item.title not in milestones_default:
                    self.client.api.repos.issueDeleteMilestone(str(item.id), self.name, self.owner)

    @property
    def milestones_default(self):
        """property for generating default milestones

        :return: default milestones according to the cuurent quarter
        :rtype: list
        """


        today = datetime.today()
        thismonth = today.month
        months = [i for i in range(thismonth, thismonth + 5)]
        year = today.year
        milestones = []

        # Set the begining of the week to Sunday
        c = calendar.Calendar(calendar.SUNDAY)

        # Add weekly milestones
        for month in months:
            lastdate = [item for item in c.itermonthdates(2018, month) if item.month == month][-1]
            month_name = calendar.month_name[month].lower()[0:3]
            # weeks = c.monthdayscalendar(year, month)

            due_on = '%s-%s-%s' % (lastdate.year, str(lastdate.month).zfill(2), str(lastdate.day).zfill(2))
            milestones.append((month_name, due_on))

            # if month == thismonth:
            #     for i, week in enumerate(weeks):
            #         # check if this week has a value for Saturday
            #         day = week[6]
            #         if day:
            #             title = '%s_w%s' % (month_name, i + 1)
            #             due_on = '%s-%s-%s' % (year, str(month).zfill(2), str(day).zfill(2))
            #             milestones.append((title, due_on))
            # else:
            #     res=[]
            #     for i, week in enumerate(weeks):
            #         # check if this week has a value for Saturday
            #         day = week[6]
            #         if day:
            #             res.append((i,day))
            #     i,day=res[-1]
            #     title = '%s_w%s' % (month_name, i + 1)
            #     due_on = '%s-%s-%s' % (year, str(month).zfill(2), str(day).zfill(2))
            #     milestones.append((title, due_on))

        # Add quarter milestone
        for quarter in range(1, 5):
            title = 'Q%s' % quarter
            quarter_month = quarter * 3
            last_day = calendar.monthrange(year, quarter_month)[1]
            due_on = '%s-%s-%s' % (year, str(quarter_month).zfill(2), last_day)
            milestones.append((title, due_on))

        return milestones

    def issues_get(self):
        """used to get issues in the repo

        :return: a list of issue objects from the generated client
        :rtype: list
        """

        return self.api.issueListIssues(self.name, self.owner)[0]

    def __repr__(self):
        return "repo:%s" % self.name

    __str__ = __repr__
