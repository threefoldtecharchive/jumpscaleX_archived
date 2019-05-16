from Jumpscale import j
from manager import Samba

s = j.ssh.samba

print("========================")
print("===   SAMBA SHARES   ===")
print("========================")

print("-> Get")
print(s.getShare("sysvol"))
print(s.getShare("hello"))

print("-> Add")
print(s.addShare("test", "/tmp/"))
print(s.addShare("homes", "/tmp/"))
print(s.addShare("noread", "/tmp/", {"read only": "true"}))

print("-> Remove")
print(s.removeShare("global"))
print(s.removeShare("notexists"))
print(s.removeShare("test"))

print("-> Commit")
print(s.commitShare())

print("=======================")
print("===   SAMBA USERS   ===")
print("=======================")

print("-> List")
print(s.listUsers())

print("-> Add")
print(s.addUser("test", "test"))
print(s.addUser("test", "test@1234xxx"))

print("-> Remove")
print(s.removeUser("test"))
print(s.removeUser("test"))
print(s.removeUser("test2"))
