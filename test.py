from Jumpscale import j
import traceback
import sys
# JSBASE = j.application.JSBaseClass
# class DevelopmentTest(JSBASE):
#     def __init__(self):
#         JSBASE.__init__(self)
#         self.path = ''

#     def run_tests(self, path):
#         self.path = path
#         self._test_run(name='', obj_key='main')
    
#     @property
#     def _dirpath(self):
#         path = '/sandbox/code/github/threefoldtech/jumpscaleX/Jumpscale/'
#         return path + self.path

# if __name__ == "__main__":
#     run = DevelopmentTest()
#     run.run_tests(path='data/schema/')

#     cla=j.servers.zdb.start_test_instance(destroydata=True,namespaces=["test"])
#     cl = cla.namespace_get("test","1234")
#     assert cla.ping()
#     assert cl.ping()
#     bcdb = j.data.bcdb.new("test", zdbclient=cl)
#     bcdb.reset()
#     run.run_tests(path='data/bcdb')

try:
    j.clients.zdb.test()
except Exception as e:
    sys.stderr.write('\nError In ZDB Client\n')
    traceback.print_exc()

try:
    j.data.bcdb.test()
except Exception as e:
    sys.stderr.write('\nError In BCDB\n')
    traceback.print_exc()

try:
    j.data.schema.test()
except Exception as e:
    sys.stderr.write('\nError In SCHEMA\n')
    traceback.print_exc()

try:
    j.servers.zdb.test()
except Exception as e:
    sys.stderr.write('\nError In ZDB Server\n')
    traceback.print_exc()
