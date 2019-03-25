# Zero-OS Hub Client

## Staging
Install upstream client:
```
pip3 install -e 'git+https://github.com/threefoldtech/0-hub#egg=zerohub&subdirectory=client'
```

## Using the client

### Creating the client in JSX

```
zhubcl = j.clients.zhub.zhubcl
zhubcl.username = "$your_zhub_username"
zhubcl.token = "$your_itsyouonline_token"

zhubcl.authenticate()
zhubcl.save()
```

### Public
You can make basic requests without authentication like:
```
cl = j.clients.zhub.getClient('$your_zhub_client_name')

cl.repositories()
cl.list()
cl.list('maxux')
cl.get('maxux', 'ubuntu1604.flist')
```

### Authentication

In order to use upload, delete, ... feature, you need to authenticate yourself by setting a token on your client. In order to push flists to the hub under the official apps repository you will need to be a member of this organisation on itsyouonline.

```
iyo_client = j.clients.itsyouonline
token = iyo_client.jwt_get(scope="user:memberof:tf-official-apps").jwt
```

Note: above will prompt you for application id / application secret. You can create this on your itsyouonline profile.

```
cl = j.clients.zhub.getClient('$your_zhub_client_name')
cl.token = token
cl.username = 'tf-official-apps'
cl.authenticate()
cl.save()
```

This allows you to do following

Example:
```
cl = j.clients.zhub.getClient('$your_zhub_client_name')

cl.upload('/tmp/my-upload-file.tar.gz')
cl.rename('my-upload-file.flist', 'my-super-flist.flist')
```

### Example flow

```
zhubcl = j.clients.zhub.zhubcl
zhubcl.username = "$your_zhub_username"

iyo_client = j.clients.itsyouonline
token = iyo_client.jwt_get(scope="user:memberof:tf-official-apps").jwt

zhubcl.token = token
zhubcl.username = "tf-official-apps"

zhubcl.save()
zhubcl.authenticate()

zhubcl.upload('/tmp/my-upload-file.tar.gz')
zhubcl.rename('my-upload-file.flist', 'my-super-flist.flist')
```
