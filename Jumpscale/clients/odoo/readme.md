# Odoo Client
### Odoo is an all-in-one business software including CRM, website/e-commerce, billing, accounting, manufacturing, warehouse - and project management, and inventory. The Community version is the open source version, while the Enterprise version supplements the Community edition with proprietary features and services.

## Install odoo 
```python
j.builders.apps.odoo.install(reset=True) 
```
## start Odoo
### Schema
```
name* = "default" (S)
host = "127.0.0.1" (S)
port = 8069 (I)
admin_login = "admin"(S)
admin_passwd_ = "admin" (S)
admin_email = "info@example.com" (S)
db_login = "odoouser"
db_passwd_ = "admin"            
databases = (LO) !jumpscale.odoo.server.db.1
           
@url =  jumpscale.odoo.server.db.1
name* = "user" (S)
admin_email = "info@example.com" (S)                      
admin_passwd_ = "123456" (S)
country_code = "be"
lang="en_US"
phone = ""
```

```python
server = j.server.odoo.get(name="main",databases=[{"name":"test"}])
server.start()
```

### see on web
```
http://IP:8069
```

### to create new database
```
server =j.servers.odoo.get(databases=[{"name":"odoo_client"}])
server.databases_create() 
```

### to add new user 
```
cl = j.clients.odoo.get(name="test",password_="admin",login_admin="admin")
cl.user_add("test","123456")
```

### to install module
```
cl = j.clients.odoo.get(name="test",password_="admin",login_admin="admin")
cl.module_install("MODULE_NAME")
```

### to list all database 
```
cl = j.clients.odoo.get(name="test",password_="admin",login_admin="admin")
cl.module_install("MODULE_NAME")
```

           

