### 0-Test Continuous-Integration

#### Requirement:

- Ubuntu:18.04 with (jumpscaleX and docker) installed.
- Telegram group chat.
- Telegram bot added to this group chat and saved in config manager.
  ```
  cl = j.clients.telegram_bot.get("test", bot_token_=<your bot token>)
  cl.save()
  ```
- Docker account.
- Dockerfile has the installation of your project.
- repo/0-Test.sh should has bash commands(should one line for each test) for how to run tests(exp: pytest jumpscaleX).
- config.ini:

```
chat_id=                            # Telegram chat ID
server_ip=                          # (http://ip:port) ip should be public

username=                           # Docker Hub ID
password=                           # Docker Hub password

access_token=                       # Github access token for user
repo=threefoldtech/jumpscaleX       # Repository name
```

for exports, can put list of environment variables needed to be exported before running tests.

- Add webhook in Repository's settings.

#### Run:

```bash
python3.6 0-Test.py
```
