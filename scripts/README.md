## 0-Test Continuous-Integration

### Server life cycle:
#### There are two scenarios:

##### 1- Pushing in development branch, the following steps will be done:

    - Server had already a nightly build image for JS from development branch
    - Create a docker container from this image
    - Get tests commands from 0-Test.sh file from development branch
    - Run those commands one by one against this docker container
    - Produce a log file with all results 
    - Send log file url to Telegram chat and Change commit status on github

##### 2- Having a PR from branch X, the following steps will be done: 

    - Server will build an ubuntu 18 image with JS installed from X branch
    - Create a docker container from this image
    - Get tests commands from 0-Test.sh file from this X branch
    - Run those commands one by one against this docker container
    - Produce a log file with all results 
    - Change commit status on github

### How to install:

- Create a vm with Ubuntu:18.04.
- Install [JS](https://github.com/threefoldtech/jumpscaleX/tree/development/install#base-environment-variables-which-can-be-used-in-a-script) and [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-using-the-repository)
- Create a Telegram group chat.
- Create Telegram bot and add it to this group chat
- Save this bot in config manager:
  ```
    cl = j.clients.telegram_bot.get("test", bot_token_=<your bot token>)
    cl.save()
    ```
- Create a docker account (only used after the nightly bulid to push the image)
- config.ini:

```
[main]
chat_id=                            # Telegram chat ID
server_ip=                          # (http://ip:port) ip should be public
result_path=                        # The result log file will stored in

[docker]
username=                           # Docker Hub ID
password=                           # Docker Hub password

[github]
access_token=                       # Github access token for user
repo=threefoldtech/jumpscaleX       # Repository name

[exports]                           # under this a list of environment variables needed to be exported before running tests.
```

- Add server IP as webhook in Repository's settings.

### How tests run:

Repo/0-Test.sh should has bash commands(should one line for each test) for how to run tests.

Example:
```bash
source /sandbox/env.sh; pytest -v /sandbox/code/github/threefoldtech/jumpscaleX
```
If this file is not found, it will result in `Didn't find tests` in result log file.
### How to run the server:

```bash
python3.6 0-Test.py
```
