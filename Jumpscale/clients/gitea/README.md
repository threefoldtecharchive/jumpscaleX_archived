**Get Gitea Client**
```

In [1]: cl = j.clients.gitea.get()
In [2]: cl
Out[2]: <Gitea Client: v=1.1.0+898-ge2e692ce user=nasrb admin=False>
```

**Get Gitea Client version**
```
In [3]: cl.version
Out[3]: '1.1.0+898-ge2e692ce'
```

**Markdown Manager**
```
In [4]: cl.markdowns
Out[4]: <Gitea MarkDown Manager>
In [5]: cl.markdowns.render(text="##This is header")
Out[5]: b'<h2>This is header</h2>\n'

In [8]: cl.markdowns.render_raw(text="##This is header")
Out[8]: b'<p>{&quot;body&quot;: &quot;##This is header&quot;}</p>\n'

```

### Users Manager

**Current user**
```
In [2]: cl.users.current
Out[2]:

<Current User>
{
    "id": 127,
    "username": "nasrb",
    "password": null,
    "full_name": "",
    "login_name": null,
    "source_id": null,
    "send_notify": null,
    "email": "nasrb@codescalers.com",
    "active": null,
    "admin": null,
    "allow_git_hook": false,
    "allow_import_local": false,
    "location": null,
    "max_repo_creation": null,
    "website": null,
    "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon"
}

# Client automatically detects that `nasrb` is current user

In [3]: cl.users.get(username='nasrb')
Out[3]:

<Current User>
{
    "id": 127,
    "username": "nasrb",
    "password": null,
    "full_name": "",
    "login_name": null,
    "source_id": null,
    "send_notify": null,
    "email": "nasrb@codescalers.com",
    "active": null,
    "admin": null,
    "allow_git_hook": false,
    "allow_import_local": false,
    "location": null,
    "max_repo_creation": null,
    "website": null,
    "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon"
}

In [2]: cl.users.current.is_admin
Out[2]: False

In [3]: cl.users.current.follow('hamdy')
Out[3]: True

In [4]: cl.users.current.is_following('hamdy')
Out[4]: True

In [5]: cl.users.current.unfollow('hamdy')
Out[5]: True

In [6]: cl.users.current.is_following('hamdy2')
Out[6]: False


In [4]: cl.users.current.follow('BolaE.Nasr')
[Wed23 15:11] - GiteaUserCurrent.py:21  :j.giteausercurrent   - DEBUG    - username does not exist
Out[4]: False

In [5]: cl.users.current.unfollow('BolaE.Nasr')
[Wed23 15:11] - GiteaUserCurrent.py:30  :j.giteausercurrent   - DEBUG    - username does not exist
Out[5]: False

In [2]: cl.users.current.emails
Out[2]: <Emails Iterator for user: nasrb>

In [3]: [e for e in cl.users.current.emails]
Out[3]:
[
 <Email>
 {
     "email": "nasrb@codescalers.com",
     "verified": true,
     "primary": true
 }]


In [4]: cl.users.current.emails.add(emails=['ham@e.com'])
Out[4]: True

In [5]: cl.users.current.emails.add(emails=['ham@e.com'])
[Wed23 20:59] - GiteaUserCurrentEmails.py:21  :giteausercurrentemails - DEBUG    - b'{"message":"Email address has been used: ham@e.com","url":"https://godoc.org/github.com/go-gitea/go-sdk/gitea"}'
Out[5]: False

In [6]: cl.users.current.emails.remove(emails=['ham@e.com'])
Out[6]: True

In [7]:

In [7]: cl.users.current.emails.remove(emails=['ham@e.com'])
[Wed23 20:59] - GiteaUserCurrentEmails.py:29  :giteausercurrentemails - DEBUG    - b'{"message":"Email address does not exist","url":"https://godoc.org/github.com/go-gitea/go-sdk/gitea"}'
Out[7]: False

```

**Search**

```
In [4]: cl.users
Out[4]: <Users>

In [2]: cl.users.is_following('nasrb', 'BolaE.Nasr')
[Wed23 21:16] - GiteaUsers.py     :66  :j.giteausers         - DEBUG    - follower or followee not found
Out[2]: False

In [3]: cl.users.is_following('nasrb', 'hamdy')
Out[3]: True

In [2]: cl.users.search(query='nas')
Out[2]:
[
 <User>
 {
     "id": 131,
     "username": "nashaatp",
     "password": null,
     "full_name": "",
     "login_name": null,
     "source_id": null,
     "send_notify": null,
     "email": "nashaatp@greenitglobe.com",
     "active": null,
     "admin": null,
     "allow_git_hook": false,
     "allow_import_local": false,
     "location": null,
     "max_repo_creation": null,
     "website": null,
     "avatar_url": "https://docs.grid.tf/avatars/e73004ba99f793dac5822f17d7ec8089"
 }, 
 <Current User>
 {
     "id": 127,
     "username": "nasrb",
     "password": null,
     "full_name": "",
     "login_name": null,
     "source_id": null,
     "send_notify": null,
     "email": "nasrb@codescalers.com",
     "active": null,
     "admin": null,
     "allow_git_hook": false,
     "allow_import_local": false,
     "location": null,
     "max_repo_creation": null,
     "website": null,
     "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon"
 }]


In [3]: cl.users.search(query='nas', limit=1)
Out[3]:
[
 <User>
 {
     "id": 131,
     "username": "nashaatp",
     "password": null,
     "full_name": "",
     "login_name": null,
     "source_id": null,
     "send_notify": null,
     "email": "nashaatp@greenitglobe.com",
     "active": null,
     "admin": null,
     "allow_git_hook": false,
     "allow_import_local": false,
     "location": null,
     "max_repo_creation": null,
     "website": null,
     "avatar_url": "https://docs.grid.tf/avatars/e73004ba99f793dac5822f17d7ec8089"
 }]


```

**Get a user by username**

```
In [5]: cl.users.get(username='hamdy')
Out[5]:

<User>
{
    "id": 13,
    "username": "hamdy",
    "password": null,
    "full_name": "",
    "login_name": null,
    "source_id": null,
    "send_notify": null,
    "email": "hamdy@greenitglobe.com",
    "active": null,
    "admin": null,
    "allow_git_hook": false,
    "allow_import_local": false,
    "location": null,
    "max_repo_creation": null,
    "website": null,
    "avatar_url": "https://secure.gravatar.com/avatar/859fe0c48f17055d3893ebd4fb218b91?d=identicon"
}

```

**Admin Operations**

`If current user is not admin, these operations will fail`

```
In [2]: user = cl.users.new()
In [3]: user.save()

[Wed23 22:22] - GiteaUser.py      :152 :j.giteauser          - DEBUG    - create Error {"password": "Missing", "username": "Missing", "email": "Missing"}
Out[3]: False

In [4]: user.username = 'bola2'

In [5]: user.password = '123456'

In [6]: user.email = 'bola@readme.com'

In [7]: user.save()
Out[7]: True

In [8]: user.save()
[Wed23 22:23] - GiteaUser.py      :152 :j.giteauser          - DEBUG    - create Error {"id": "Already existing"}
Out[8]: False

In [9]: user.email = 'oto@er.com'
In [10]: user.update()
Out[10]: True

In [11]: user.delete()
Out[11]: True

In [12]: user.save()
Out[12]: True
```

**Keys management**
```
In [2]: cl.users.current.keys
Out[2]: <PublicKeys Iterator for user: nasrb>

In [4]: [k for k in cl.users.current.keys]
Out[4]: []

In [5]: k = cl.users.current.keys.new()

In [6]: k.title = 'helllo key'

In [7]: k.key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC4IN8ZGDgdgDeul8h49yResQBfVI1wIFsleD+O8Y3YTdYw97A9MgFZJcNGM
   ...: OOs1vGXYlyzVT6+gCFADHyzpSCYjs82qn6UljjUNes0OyxmCnE1wuPCPIV7IuUkr9Zt+Ca3+hOAArQgs9X172mDj1vojLYg/ttBCNCvv1Y
   ...: H+khZSmSxdhgFICrUa2ROP98REwPG9vMl5KQzUnO8xnBUYHucLGPYn9stECM81SQRTOK6hZPhok/38ymecL8NtFws47MeqkeD4k4tvB69L
   ...: GYc3A1iXbnyghFp6tqjQ5s2H7EWkBU4v2jNnCQALWGJX5mJpvEXMxkGbJgM8gUnCEKVCkP1"

In [8]: k.save()
Out[8]: True

In [12]: k.delete()
Out[12]: True

In [13]: [k for k in cl.users.current.keys]
Out[13]: []

# Create a pub key for user / requires admin

In [8]: k = cl.users.get(username='hamdy', fetch=False).keys.new()

In [9]: k.title= 'ss'

In [10]: k.key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC4IN8ZGDgdgDeul8h49yResQBfVI1wIFsleD+O8Y3YTdYw97A9MgFZJcNG
    ...: MOOs1vGXYlyzVT6+gCFADHyzpSCYjs82qn6UljjUNes0OyxmCnE1wuPCPIV7IuUkr9Zt+Ca3+hOAArQgs9X172mDj1vojLYg/ttBCNCvv
    ...: 1YH+khZSmSxdhgFICrUa2ROP98REwPG9vMl5KQzUnO8xnBUYHucLGPYn9stECM81SQRTOK6hZPhok/38ymecL8NtFws47MeqkeD4k4tvB
    ...: 69LGYc3A1iXbnyghFp6tqjQ5s2H7EWkBU4v2jNnCQALWGJX5mJpvEXMxkGbJgM8gUnCEKVCkP1"

In [11]: k.save()
Out[11]: True

In [12]: k.id
Out[12]: 19

In [8]: cl.users.current.keys.get(20)
Out[8]:

<Public Key: user=nasrb>
{
    "id": 20,
    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDyzyHtXkpyMejonGGBWmueUDoPoQ0J3FgK5D4+iFs5QQtDGsMJUgIIw84pm4aVeURjUn3MSFgRF6iMo3R37Wzu/F2IB1e8pmvayIAAPwNLKXsG68ZweMnSRyZezQID1Q9rTMx+KWtvM3YlPi++HdyNvuF8G8a7p+ux+3GI5tHJCHY/Q6V301NbTD80d0A7sNjY/MUFD1u0RfOBqV/KxdqA4TfWzhLL9K31NSgVYEmE0kI8sgO1YRZyFcbOX/HQlT+Ima1diiAFHwCCGPlNtSFDYQHaK8Rc/U3bGDADjAhstlXe0XoKXOTj2tsyOni3bgU2SzcGYZr23Xgl8JF4FnHx root@vm-1045",
    "title": "root@vm-1045",
    "created_at": "2018-01-09T10:33:08Z",
    "fingerprint": "SHA256:TBixObPaW+NCr4dq9SmQVFkP+9V0qKf1Uq/+zLVB/uI",
    "url": "https://docs.grid.tf/api/v1/user/keys/20"
}
```

**User Organizations**

```
In [2]: [o for o in cl.users.current.organizations]
Out[2]:
[
 <Organization>
 {
     "id": 137,
     "avatar_url": "https://docs.grid.tf/avatars/137",
     "description": "",
     "full_name": "",
     "location": "",
     "username": "GiteaClient",
     "website": ""
 }]


In [2]: cl.users.get(username='hamdy').is_member_of_org('GiteaClient')
[Thu24 13:21] - GiteaOrgs.py      :37  :j.giteaorgs          - DEBUG    - hamdy is not member of organization GiteaClient
Out[2]: False

In [3]: cl.users.current.is_member_of_org('GiteaClient')
[Thu24 13:21] - GiteaOrgs.py      :34  :j.giteaorgs          - DEBUG    - nasrb is member of organization GiteaClient
Out[3]: True
```

- Only members of an org, can update/try to delete
```
In [6]: org = cl.users.current.organizations.get('GiteaClient')
[Thu24 13:24] - GiteaOrgs.py      :34  :j.giteaorgs          - DEBUG    - nasrb is member of organization GiteaClient


In [7]: org = cl.users.current.organizations.get('GiteaClient')
[Thu24 13:24] - GiteaOrgs.py      :34  :j.giteaorgs          - DEBUG    - nasrb is member of organization GiteaClient

In [8]: org
Out[8]:

[
 <Organization>
 {
     "id": 137,
     "avatar_url": "https://docs.grid.tf/avatars/137",
     "description": "",
     "full_name": "",
     "location": "",
     "username": "GiteaClient",
     "website": ""
 }]

In [9]: org.description = "New desc"

In [10]: org.update()
Out[10]: True

In [11]: cl.users.current.organizations.get('GiteaClient')
[Thu24 13:24] - GiteaOrgs.py      :34  :j.giteaorgs          - DEBUG    - nasrb is member of organization GiteaClient
Out[11]:

[
 <Organization>
 {
     "id": 137,
     "avatar_url": "https://docs.grid.tf/avatars/137",
     "description": "New desc",
     "full_name": "",
     "location": "",
     "username": "GiteaClient",
     "website": ""
 }]


In [12]: org = cl.users.get(username='hamdy').organizations.get('GiteaClient')
[Thu24 13:25] - GiteaOrgs.py      :37  :j.giteaorgs          - DEBUG    - ooo is not member of organization koki

In [13]: org
Out[13]:


<Organization>
{
    "id": 137,
    "avatar_url": "https://docs.grid.tf/avatars/137",
    "description": "New desc",
    "full_name": "",
    "location": "",
    "username": "GiteaClient",
    "website": ""
}


In [14]: org.description = "yet another desc"

In [15]: org.update()
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
/usr/local/bin/js9 in <module>()
----> 1 org.update()

AttributeError: 'GiteaOrgForNonMember' object has no attribute 'update'
```

- Only admins can create organizations
```
In [3]: user = cl.users.get(username='nasrb')

In [4]: org = user.organizations.new()

In [5]: org.username = 'BolaE.Nasr'

In [6]: org.save()
[Thu24 13:27] - GiteaOrgForMember.py:9   :j.giteaorgformember  - DEBUG    - create Error {"permissions": "Admin permissions required", "full_name": "Missing"}
Out[6]: False

In [7]: user = cl.users.current

In [8]: user.is_admin
Out[8]: True

In [9]: org = user.organizations.new()

In [10]: org.username = 'BolaE.Nasr'

In [11]: org.save()
[Thu24 13:28] - GiteaOrgForMember.py:9   :j.giteaorgformember  - DEBUG    - create Error {"full_name": "Missing"}
Out[11]: False

In [12]: org.full_name = 'Bola Nasr'

In [13]: org.save()
Out[13]: True

```

### Repo Manager

```
In [8]: cl.repos
Out[8]: <General Repos finder and getter (by ID)>
```

**Search(name, mode, page_number=1, page_size=150, exclusive=False)**  *modes=("fork", "source", "mirror", "collaborative")*

```
        # search user repos
        repos = cl.users.get('nasrb').repos.search('GiteaClient', mode='source')
# OR
        # search all repos

# Warning currently they produce same results (no idea why)

In [3]: repos = cl.repos.search('GiteaClient', mode='source')


In [4]: repos
Out[4]:

[
 <Repo: owned by current user: nasrb>
 {
     "id": 213,
     "clone_url": "https://docs.grid.tf/nasrb/GiteaClient.git",
     "full_name": "nasrb/GiteaClient",
     "created_at": "2018-08-02T08:40:56Z",
     "default_branch": "master",
     "empty": true,
     "html_url": "https://docs.grid.tf/nasrb/GiteaClient",
     "name": "GiteaClient",
     "owner": {
         "id": 127,
         "login": "nasrb",
         "full_name": "",
         "email": "nasrb@codescalers.com",
         "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon",
         "username": "nasrb"
     },
     "watchers_count": 1,
     "ssh_url": "ssh://git@docs.grid.tf:7022/nasrb/GiteaClient.git"
 }]



In [6]: repos[0].user
Out[6]:

<Current User>
{
    "id": 127,
    "username": "nasrb",
    "password": null,
    "full_name": "",
    "login_name": null,
    "source_id": null,
    "send_notify": null,
    "email": "nasrb@codescalers.com",
    "active": null,
    "admin": null,
    "allow_git_hook": false,
    "allow_import_local": false,
    "location": null,
    "max_repo_creation": null,
    "website": null,
    "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon"
}

```

**Get repo by ID**

```
In [4]: cl.repos.get(38)
Out[4]:

<Repo>
{
    "id": 38,
    "clone_url": "https://docs.grid.tf/sabrina/prod_tf_app.git",
    "full_name": "sabrina/prod_tf_app",
    "created_at": "2017-12-22T12:42:07Z",
    "default_branch": "master",
    "html_url": "https://docs.grid.tf/sabrina/prod_tf_app",
    "name": "prod_tf_app",
    "owner": {
        "id": 34,
        "login": "sabrina",
        "full_name": "",
        "email": "sabrina@gig.tech",
        "avatar_url": "https://secure.gravatar.com/avatar/f7fd84a28efbf23a491c37e6ddcbd3ab?d=identicon",
        "username": "sabrina"
    },
    "watchers_count": 1,
    "ssh_url": "ssh://git@docs.grid.tf:7022/sabrina/prod_tf_app.git"
}


In [5]: cl.repos.get(35)
Out[5]:
[Thu02 17:23] - GiteaReposForClient.py:78  :j.giteareposforclient - ERROR    - id not found

```

**User Repos**
```
In [3]: cl.users.current.repos
Out[3]: <Repos Iterator for user: nasrb>

In [7]: [r for r in cl.users.current.repos]
Out[7]:
[
 <Repo: owned by current user: nasrb>
 {
     "id": 213,
     "clone_url": "https://docs.grid.tf/nasrb/GiteaClient.git",
     "full_name": "nasrb/GiteaClient",
     "created_at": "2018-08-02T08:40:56Z",
     "default_branch": "master",
     "empty": true,
     "html_url": "https://docs.grid.tf/nasrb/GiteaClient",
     "name": "GiteaClient",
     "owner": {
         "id": 127,
         "login": "nasrb",
         "full_name": "",
         "email": "nasrb@codescalers.com",
         "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon",
         "username": "nasrb"
     },
     "watchers_count": 1,
     "ssh_url": "ssh://git@docs.grid.tf:7022/nasrb/GiteaClient.git"
 }]




# For another user

In [2]: u = cl.users.get('hamdy')

In [3]: u.repos
Out[3]: <Repos Iterator for user: hamdy>

In [4]: [a for a in u.repos]
Out[4]:
[]
```
**repo milestones**

```
In [2]: x = cl.repos.get(447)
In [3]: [m for m in x.milestones ]
Out[3]: 
[Milestone {"closed_issues": 0, "due_on": null, "open_issues": 1, "description": "test", "title": "test_milestone-01", "id": 771, "closed_at": null},
 Milestone {"closed_issues": 0, "due_on": "2018-09-20T00:00:00Z", "open_issues": 1, "description": "test-02", "title": "test_milestone-02", "id": 772, "closed_at": null}]

```

**Create repo for another user (requires admin permissions)**

```
In [2]: u = cl.users.get('hamdy')
In [3]: repo = u.repos.new()
In [5]: repo.name = 'Newone'

In [8]: repo.save()
Out[8]: True


# create repo for current user (no admin permissions required)

In [9]: repo = cl.users.current.repos.new()

In [10]: repo.name = 'new_repo'

In [13]: repo.save()
Out[13]: True

```

**Starring**

```
In [3]: bola = cl.users.get('nasrb')

In [4]: curr = cl.users.current

In [5]: curr.repos.starred
Out[5]: []

In [6]: repo = bola.repos.get('new_repo')

In [7]: repo.is_starred_by_current_user
Out[7]: False

In [8]: repo.unstar()
Out[8]: True

In [9]: repo.star()
Out[9]: True

In [10]: repo.star()
Out[10]: True

In [11]: repo.is_starred_by_current_user
Out[11]: True

In [12]: curr.repos.starred
Out[12]:
[
 <Repo: owned by current user: nasrb>
 {
     "id": 215,
     "clone_url": "https://docs.grid.tf/nasrb/new_repo.git",
     "full_name": "nasrb/new_repo",
     "created_at": "2018-08-02T15:41:34Z",
     "default_branch": "master",
     "empty": true,
     "html_url": "https://docs.grid.tf/nasrb/new_repo",
     "name": "new_repo",
     "owner": {
         "id": 127,
         "login": "nasrb",
         "full_name": "",
         "email": "nasrb@codescalers.com",
         "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon",
         "username": "nasrb"
     },
     "stars_count": 1,
     "watchers_count": 1,
     "ssh_url": "ssh://git@docs.grid.tf:7022/nasrb/new_repo.git"
 }]

```

**Subscriptions**

```
In [13]: curr.repos.subscriptions
Out[13]:
[
 <Repo: owned by current user: nasrb>
 {
     "id": 213,
     "clone_url": "https://docs.grid.tf/nasrb/GiteaClient.git",
     "full_name": "nasrb/GiteaClient",
     "created_at": "2018-08-02T08:40:56Z",
     "default_branch": "master",
     "empty": true,
     "html_url": "https://docs.grid.tf/nasrb/GiteaClient",
     "name": "GiteaClient",
     "owner": {
         "id": 127,
         "login": "nasrb",
         "full_name": "",
         "email": "nasrb@codescalers.com",
         "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon",
         "username": "nasrb"
     },
     "watchers_count": 1,
     "ssh_url": "ssh://git@docs.grid.tf:7022/nasrb/GiteaClient.git"
 }, 
 <Repo: owned by current user: nasrb>
 {
     "id": 215,
     "clone_url": "https://docs.grid.tf/nasrb/new_repo.git",
     "full_name": "nasrb/new_repo",
     "created_at": "2018-08-02T15:41:34Z",
     "default_branch": "master",
     "empty": true,
     "html_url": "https://docs.grid.tf/nasrb/new_repo",
     "name": "new_repo",
     "owner": {
         "id": 127,
         "login": "nasrb",
         "full_name": "",
         "email": "nasrb@codescalers.com",
         "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon",
         "username": "nasrb"
     },
     "stars_count": 1,
     "watchers_count": 1,
     "ssh_url": "ssh://git@docs.grid.tf:7022/nasrb/new_repo.git"
 }]

```


**Repo Migrations**

```
In [14]: curr.repos.migrate('nasrb', 'my-secret', 'https://github.com/hamdy/knn', 'knn')
Out[14]:

<Repo: owned by current user: nasrb>
{
    "id": 216,
    "clone_url": "https://docs.grid.tf/nasrb/knn.git",
    "full_name": "nasrb/knn",
    "created_at": "0001-01-01T00:00:00Z",
    "default_branch": "master",
    "html_url": "https://docs.grid.tf/nasrb/knn",
    "mirror": true,
    "name": "knn",
    "owner": {
        "id": 127,
        "login": "nasrb",
        "full_name": "",
        "email": "nasrb@codescalers.com",
        "avatar_url": "https://secure.gravatar.com/avatar/941386a68a71900be12c839a32826ba1?d=identicon",
        "username": "nasrb"
    },
    "size": 28,
    "watchers_count": 1,
    "ssh_url": "ssh://git@docs.grid.tf:7022/nasrb/knn.git"
}


```

**Repo Download**

```
In [2]: curr = cl.users.current

In [3]: knn = curr.repos.get('knn')

In [4]: knn.download(dir='/tmp/knn', type='tar.gz')
Out[4]: True

In [5]: knn.download(dir='/tmp/knn', branch='master', type='tar.gz')
Out[5]: True

In [6]: knn.download(dir='/tmp/knn', branch='master', type='zip')
Out[6]: True

In [7]: knn.download(dir='/tmp/knn') # master.zip
Out[7]: True
```

**Download single file**
```
In [2]: curr = cl.users.current

In [3]: knn = curr.repos.get('knn')

In [4]: knn.download_file(destination_dir='/tmp/downloads', filename='knn.py', branch='master')
Out[4]: True

In [5]: knn.download_file(destination_dir='/tmp/downloads', filename='knn.py') # download from master
   ...:
Out[5]: True

```

--


