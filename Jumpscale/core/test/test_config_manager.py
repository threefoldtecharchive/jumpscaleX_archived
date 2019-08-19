from Jumpscale import j
from .base_test import BaseTest


class TestIConfigManager(BaseTest):
    def setUp(self):
        print("\t")
        self.info('Test case: {}'.format(self._testMethodName))

    def tearDown(self):
        pass

    def test01_create_new_client(self):
        """
        TC198

        ** create new user with certain schema, should success **
           we will use IYO client as an example 

        #. Create new github client, and save it.
        #. Check the shema and make sure that the use is created successfully. 
        """

        self.info("Create github client and save it, should success")
        c=j.clients.github.new("test_create_client", token="test_create_new_client"); c.save()
        self.info("Check that the client is created correctly")
        self.assertEqual("test_create_client", c.name)
        
    def test02_create_user_with_name_exists_before(self):
        """
        TC256

        ** create use with name exist before, should fail. **

        #. Create user with the same name as TC198. 
        #. Check the output, should fail. 
        """

        self.info("Create github user with test name, should fail.")
        self.info("Check the creation of client is failed")
        with self.assertRaises(Exception):
            c=j.clients.github.new("test_create_client", token="test_create_new_client"); c.save()
        
    def test03_modify_exists_client(self):
        """
        TC195

        ** Test update user cleint data, should success ** 

        #. Update github "test_create_client" user token. 
        #. Check the updated token, should success. 
        """

        self.info("Update github user token")
        c=j.clients.github.new("test_modify_client", token="test_modify_client"); c.save()
        c.token="test_update"; c.save()
        self.info(" check cleint token ")
        self.assertEqual("test_update", c.token)
        
    def test04_test_delete_client_for_exists_cient(self):
        """
        TC196

        ** Test delete github client for exists client, should success. **

        #. Delete "test_create_client" github client.
        #. check that the client is deleted successfully.

        """

        self.info("Delete test github client")
        c=j.clients.github.new("test_delete_client", token="test_delete_client"); c.save()
        c.delete()
        self.info("Check that the client is not existing")
        with self.assertRaises(RuntimeError):
            j.clients.github.get("test_delete_client")
        
        
