# Github client

### make a client either using 
- login and password
- a secret from: https://github.com/settings/tokens
```
test_client = j.clients.github.get("test_client", token="**********")
testclient.save()
```
### Example of usage:
- Create a repo: <br/>
`test_client.repo_create("repo_test", description="this is a repo created from github client", auto_init=True)`
- Working on a repo: <br/>
`
repo = test_client.api.get_repo("username/repo_test")
`
- Repo clone url: <br/>
`repo.clone_url`
- Create an issue: <br/>
`repo.create_issue("test_issue", body="test an issue"`
- Delete Repo: <br/>
`repo.delete()`


