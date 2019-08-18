## tutorial with sql alchemy

```
cl = j.clients.postgres.get(
    name="cl", ipaddr="localhost", port=5432, login="root", passwd_="rooter", dbname="main"
)
cl.save()

base,session=cl.initsqlalchemy()
session.add(base.classes.address(email_address="foo@bar.com", user=(base.classes.user(name="foo")))
session.commit()


```
