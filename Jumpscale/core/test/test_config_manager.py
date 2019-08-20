from Jumpscale import j
from base_tests import BaseTest


class TestIConfigManager(BaseTest):
    def setUp(self):
        print("\t")
        self.info('Test case: {}'.format(self._testMethodName))

    def tearDown(self):
        self.info("Delete DataBase")
        j.application.bcdb_system_destroy() 
        j.data.bcdb.destroy_all() 

    def test01_create_new_client(self):
        """
        TC198

        ** create new user with certain schema, should success **
           we will use IYO client as an example 

        #. Create new github client, and save it.
        #. Check the shema and make sure that the use is created successfully. 
        """

        client_name = self.generate_random_str()
        self.info("Create github client {} and save it, should success".format(client_name))
        c = j.clients.github.new(client_name, token="test_create_new_client")
        self.info("Saving client in database")
        c.save()
        self.info("Check that the client {} is created correctly".format(client_name))
        self.assertEqual(client_name, c.name)
        
    def test02_create_user_with_name_exists_before(self):
        """
        TC256

        ** create use with name exist before, should fail. **

        #. Create user with the same name as TC198. 
        #. Check the output, should fail. 
        """

        client_name = self.generate_random_str()
        self.info("Create github client with {} name, should success.".format(client_name))
        c = j.clients.github.new(client_name, token="test_create_new_client")
        self.info("Saving client in database")
        c.save()
        self.info("create user with the same name {}, should fail. ".format(client_name))
        with self.assertRaises(RuntimeError):
            c=j.clients.github.new(client_name, token="test_create_new_client")
            c.save()
        
    def test03_modify_exists_client(self):
        """
        TC195

        ** Test update user cleint data, should success ** 

        #. Update github "test_create_client" user token. 
        #. Check the updated token, should success. 
        """

        client_name = self.generate_random_str()
        self.info("Update github user token")
        c=j.clients.github.new(client_name, token="test_modify_client")
        self.info("Saving client with updated token in database")
        c.save()
        c.token="test_update"
        c.save()
        self.info("Check client token")
        self.assertEqual("test_update", c.token)
        
    def test04_test_delete_client_for_exists_cient(self):
        """
        TC196

        ** Test delete github client for exists client, should success. **

        #. Delete "test_create_client" github client.
        #. check that the client is deleted successfully.

        """

        client_name = self.generate_random_str()
        self.info("Delete client {}".format(client_name))
        c=j.clients.github.new(client_name, token="test_delete_client")
        c.save()
        c.delete()
        self.info("Check that the client is not existing")
        with self.assertRaises(RuntimeError):
            j.clients.github.get(client_name)
        
        
