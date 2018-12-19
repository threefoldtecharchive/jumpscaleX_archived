# Zero-OS Hub Client

## Staging
Install upstream client:
```
pip install --user -e 'git+https://github.com/zero-os/0-hub@api-client#egg=zerohub&subdirectory=client'
```

## Using the client

### Public
You can make basic requests without authentification like:
```
cl = j.clients.zerohub.getClient()

cl.repositories()
cl.list()
cl.list('maxux')
cl.get('maxux', 'ubuntu1604.flist')
```

### Authentification
In order to use upload, delete, ... feature, you need to authentificate yourself.
There are two ways to authentificate youself:

- By providing a token during `getClient`
- By authentificate yourself on an existing client with: `cl.authentificate()`

Note: the second method allows to change your username and enable switch-user feature.

Example:
```
cl = j.clients.zerohub.getClient('jwt-token')

cl.upload('/tmp/my-upload-file.tar.gz')
cl.rename('my-upload-file.flist', 'my-super-flist.flist')
```

```
cl = j.clients.zerohub.getClient()

cl.authentificate('jwt-token', 'gig-official-apps')
cl.upload('/tmp/my-upload-file.tar.gz')
cl.rename('my-upload-file.flist', 'my-super-flist.flist')
```

## JWT Token
> Warning: FIXME. This should not be related to openvcloud.

You can generate a jwt token using jumpscale:
```
token = j.clients.openvcloud.getJWTTokenFromItsYouOnline('app-id', 'app-secret')
```

Your app-id and app-secret can be retreived/generated on the itsyouonline settings page.

With this token, you can now easily authentificate yourself: `cl.authentificate(token)`

