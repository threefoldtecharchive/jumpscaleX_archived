from Jumpscale.data.schema.tests.testsuite.testcases.base_test import BaseTest
from Jumpscale import j
from unittest import TestCase
from uuid import uuid4
from datetime import datetime
import random, time, unittest

class SchemaTest(BaseTest):
    def setUp(self):
        super().setUp() 

    def test001_validate_list_of_strings(self):
        """
        SCM-023
        *Test case for validating list of strings *

        **Test Scenario:**

        #. Create schema with list of strings parameter, should succeed.
        #. Try to set parameter with non string type, should fail.
        #. Try to set parameter with string type, should succeed.
        """
        self.log("Create schema with list of strings parameter, should succeed.")
        scm = """
        @url = test.schema
        list_names = (LS)
        list_str = ['test', "example"] (LS)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non string type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.list_names = [random.randint(1, 1000), self.random_string()]
        
        with self.assertRaises(Exception):
            schema_obj.list_names.append(random.randint(1, 1000))

        self.log("Try to set parameter with string type, should succeed.")
        list_names = [self.random_string(), self.random_string()]
        schema_obj.list_names = list_names
        self.assertEqual(schema_obj.list_names, list_names)

        value = self.random_string()
        list_names.append(value)
        schema_obj.list_names.append(value)
        self.assertEqual(schema_obj.list_names, list_names)
        self.log("schema list %s" % schema_obj.list_str)
        self.assertEqual(schema_obj.list_str, ['test', 'example'])
    
    def test002_validate_list_of_integers(self):
        """
        SCM-024
        *Test case for validating list of integers *

        **Test Scenario:**

        #. Create schema with list of integers parameter, should succeed.
        #. Try to set parameter with non integer type, should fail.
        #. Try to set parameter with integer type, should succeed.
        """
        self.log("Create schema with list of integers parameter, should succeed.")
        scm = """
        @url = test.schema
        list_numbers = (LI)
        list_int = [1, 2, 3] (LI)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non integer type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.list_numbers = [random.randint(1, 1000), self.random_string()]
        
        with self.assertRaises(Exception):
            schema_obj.list_numbers.append(self.random_string())

        self.log("Try to set parameter with integer type, should succeed.")
        list_numbers = [random.randint(1, 1000), random.randint(1, 1000)]
        schema_obj.list_numbers = list_numbers
        self.assertEqual(schema_obj.list_numbers, list_numbers)

        value = random.randint(1, 100)
        list_numbers.append(value)
        schema_obj.list_numbers.append(value)
        self.assertEqual(schema_obj.list_numbers, list_numbers)
        self.log("schema list %s" % schema_obj.list_int)
        self.assertEqual(schema_obj.list_int, [1, 2, 3])
    
    def test003_validate_list_floats(self):
        """
        SCM-025
        *Test case for validating list of floats *

        **Test Scenario:**

        #. Create schema with list of floats parameter, should succeed.
        #. Try to set parameter with non float type, should fail.
        #. Try to set parameter with float type, should succeed.
        """
        self.log("Create schema with list of floats parameter, should succeed.")
        scm = """
        @url = test.schema
        list_numbers = (LF)
        list_floats = [1.5, 2.67, 3.7] (LF)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non float type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.list_numbers = [random.uniform(1, 1000), self.random_string()]
        
        with self.assertRaises(Exception):
            schema_obj.list_numbers.append(self.random_string())

        self.log("Try to set parameter with float type, should succeed.")
        list_numbers = [random.uniform(1, 1000), random.uniform(1, 1000)]
        schema_obj.list_numbers = list_numbers
        self.assertEqual(schema_obj.list_numbers, list_numbers)

        value = random.uniform(1, 100)
        list_numbers.append(value)
        schema_obj.list_numbers.append(value)
        self.assertEqual(schema_obj.list_numbers, list_numbers)
        self.log("schema list %s" % schema_obj.list_floats)
        self.assertEqual(schema_obj.list_floats, [1.5, 2.67, 3.7])
    
    def test004_validate_list_of_boolean(self):
        """
        SCM-026
        *Test case for validating list of boolean *

        **Test Scenario:**

        #. Create schema with list of boolean parameter, should succeed.
        #. Try to set parameter[P1] with False or non True value, should be False.
        #. Try to set parameter[P1] with True value, should be True.
        """
        self.log("Create schema with list of boolean parameter, should succeed.")
        scm = """
        @url = test.schema
        list_check = (LB)
        list_bool = [1, 'yes', 'y', 'true', True, 'f'] (LB)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with False or non True value, should be False.")
        schema_obj.list_check = [random.uniform(2, 1000), self.random_string()]
        self.assertEqual(schema_obj.list_check, [False, False])

        self.log("Try to set parameter[P1] with True value, should be True.") 
        schema_obj.list_check = [1, 'yes', 'y', 'true', True, 'f']
        check = [True, True, True, True, True, False]
        self.assertEqual(schema_obj.list_check, check)
        self.log("schema list %s" % schema_obj.list_bool)
        self.assertEqual(schema_obj.list_bool, [True,False])
    
    def test005_validate_list_of_mobiles(self):
        """
        SCM-027
        *Test case for validating list of mobiles *

        **Test Scenario:**

        #. Create schema with list of mobiles parameter, should succeed.
        #. Try to set parameter with non mobile type, should fail.
        #. Try to set parameter with mobile type, should succeed.
        """
        self.log("Create schema with list of mobiles parameter, should succeed.")
        scm = """
        @url = test.schema
        mobile_list = (Ltel)
        list_tel = [464-4564-464, +45687941, 468716420] (Ltel)
        """
        schema = self.schema(scm)
        time.sleep(1)
        schema_obj = schema.new()

        self.log("Try to set parameter with non mobile type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.mobile_list = [random.uniform(1, 100), random.randint(100000, 1000000)]
        
        with self.assertRaises(Exception):
            schema_obj.mobile_list.append(random.uniform(1, 100))

        self.log("Try to set parameter with mobile type, should succeed.")
        mobile_list = ['{}'.format(random.randint(100000, 1000000)), '{}'.format(random.randint(100000, 1000000))]
        schema_obj.mobile_list = mobile_list
        self.assertEqual(schema_obj.mobile_list, mobile_list)

        value = '{}'.format(random.randint(100000, 1000000))
        mobile_list.append(value)
        schema_obj.mobile_list.append(value)
        self.assertEqual(schema_obj.mobile_list, mobile_list)
        self.log("schema list %s" % schema_obj.list_tel)
        self.assertEqual(schema_obj.list_tel, ['4644564464', '+45687941', '468716420'])
    
    def test006_validate_list_of_emails(self):
        """
        SCM-028
        *Test case for validating list of emails *

        **Test Scenario:**

        #. Create schema with list of emails parameter, should succeed.
        #. Try to set parameter with non email type, should fail.
        #. Try to set parameter with email type, should succeed.
        """
        self.log("Create schema with list of emails parameter, should succeed.")
        scm = """
        @url = test.schema
        email_list = (Lemail)
        list_emails = ['test.example@domain.com', "test.example2@domain.com"] (Lemail)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non email type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.email_list = [random.uniform(1, 100), 'test.example@domain.com']

        with self.assertRaises(Exception):
            schema_obj.email_list.append(random.uniform(1, 100))

        self.log("Try to set parameter with email type, should succeed.")
        email_list = ['test.example@domain.com', "test.example2@domain.com"]
        schema_obj.email_list = email_list
        self.log("schema list %s" % schema_obj.list_emails)
        self.assertEqual(schema_obj.email_list, email_list)
        self.assertEqual(schema_obj.list_emails, email_list)

        value = 'test.example1@domain.com'
        email_list.append(value)
        schema_obj.email_list.append(value)
        self.log("schema list %s" % schema_obj.email_list)
        self.assertEqual(schema_obj.email_list, email_list)
    
    def test007_validate_list_of_ipports(self):
        """
        SCM-029
        *Test case for validating list of ipports *

        **Test Scenario:**

        #. Create schema with list of ipports parameter, should succeed.
        #. Try to set parameter with non ipport type, should fail.
        #. Try to set parameter with ipport type, should succeed.
        """
        self.log("Create schema with list of ipports parameter, should succeed.")
        scm = """
        @url = test.schema
        port_list = (Lipport)
        list_ports = [3164, 15487] (Lipport)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non ipport type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.port_list = [self.random_string(), random.randint(1, 10000)]

        with self.assertRaises(Exception):
            schema_obj.port_list.append(random.uniform(1, 100))

        self.log("Try to set parameter with ipport type, should succeed.")
        port_list = [random.randint(1, 10000), random.randint(1, 10000)]
        schema_obj.port_list = port_list
        self.assertEqual(schema_obj.port_list, port_list)

        value = random.randint(1, 10000)
        port_list.append(value)
        schema_obj.port_list.append(value)
        self.assertEqual(schema_obj.port_list, port_list)
        self.log("schema list %s" % schema_obj.list_ports)
        self.assertEqual(schema_obj.list_ports, [3164, 15487])
    
    def test008_validate_list_of_ipaddrs(self):
        """
        SCM-030
        *Test case for validating list of ipaddrs *

        **Test Scenario:**

        #. Create schema with list of ipaddrs parameter, should succeed.
        #. Try to set parameter with non ipaddr type, should fail.
        #. Try to set parameter with ipaddr type, should succeed.
        """
        self.log("Create schema with list of ipaddrs parameter, should succeed.")
        scm = """
        @url = test.schema
        ip_list = (Lipaddr)
        list_ip = ['127.0.0.1', "192.168.1.1"] (Lipaddr)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non ipaddr type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.ip_list = [self.random_string(), random.randint(1, 10000)]

        with self.assertRaises(Exception):
            schema_obj.ip_list.append(random.uniform(1, 100))

        self.log("Try to set parameter with ipaddr type, should succeed.")
        ip_list = ['10.15.{}.1'.format(random.randint(0, 255)), '192.168.{}.1'.format(random.randint(0, 255))]
        schema_obj.ip_list = ip_list
        self.assertEqual(schema_obj.ip_list, ip_list)

        value = '127.0.{}.1'.format(random.randint(0, 255))
        ip_list.append(value)
        schema_obj.ip_list.append(value)
        self.log("schema list %s" % schema_obj.ip_list)
        self.assertEqual(schema_obj.ip_list, ip_list)
    
    def test009_validate_list_of_ipranges(self):
        """
        SCM-031
        *Test case for validating list of ipranges *

        **Test Scenario:**

        #. Create schema with list of ipranges parameter, should succeed.
        #. Try to set parameter with non iprange type, should fail.
        #. Try to set parameter with iprange type, should succeed.
        """
        self.log("Create schema with list of ipranges parameter, should succeed.")
        scm = """
        @url = test.schema
        range_list = (Liprange)
        list_ranges = ['127.0.0.1/24', "192.168.1.1/16"] (Liprange)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non iprange type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.range_list = [self.random_string(), '10.15.{}.1/24'.format(random.randint(0, 255))]

        with self.assertRaises(Exception):
            schema_obj.range_list.append(random.uniform(1, 100))

        self.log("Try to set parameter with iprange type, should succeed.")
        range_list = ['10.15.{}.1/24'.format(random.randint(0, 255)), '10.15.{}.1/24'.format(random.randint(0, 255))]
        schema_obj.range_list = range_list
        self.assertEqual(schema_obj.range_list, range_list)

        value = '127.0.{}.1/16'.format(random.randint(0, 255))
        range_list.append(value)
        schema_obj.range_list.append(value)
        self.assertEqual(schema_obj.range_list, range_list)
        self.log("schema list %s" % schema_obj.list_ranges)
        self.assertEqual(schema_obj.list_ranges, ['127.0.0.1/24', "192.168.1.1/16"])

    @unittest.skip("should be test dates only without any times")
    def test010_validate_list_of_dates(self):
        """
        SCM-032
        *Test case for validating list of dates *

        **Test Scenario:**

        #. Create schema with list of dates parameter, should succeed.
        #. Try to set parameter with non date type, should fail.
        #. Try to set parameter with date type, should succeed.
        """
        self.log("Create schema with list of dates parameter, should succeed.")
        scm = """
        @url = test.schema
        date_list = (LD)
        list_dates = [05/03/1994, 01/01/2019] (LD)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non date type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.date_list = [self.random_string(), '01/08/2018 8am:30']

        with self.assertRaises(Exception):
            schema_obj.date_list.append(self.random_string())

        self.log("Try to set parameter with date type, should succeed.")
        year = random.randint(1000, 2020)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour_12 = random.randint(1, 11)
        minutes = random.randint(0, 59)
        am_or_pm = random.choice(['am', 'pm'])
        hours = hour_12 if am_or_pm == 'am' else hour_12 + 12
        date_1 = random.randint(1, 100)
        date_2 = datetime(datetime.now().year, month, day, hours, minutes).timestamp()

        date_list = [date_1, '{}/{:02}/{:02} {:02}{}:{:02}'.format(year, month, day, hour_12, am_or_pm, minutes)]
        schema_obj.date_list = date_list
        self.assertEqual(schema_obj.date_list, [date_1, date_2])

        value = '{}/{:02}/{:02} {:02}{}:{:02}'.format(year, month, day, hour_12, am_or_pm, minutes)
        schema_obj.date_list.append(value)
        self.assertEqual(schema_obj.date_list, [date_1, date_2, date_2])
        self.assertEqual(schema_obj.list_dates, [50, 1546377000])

    def test011_validate_list_of_percents(self):
        """
        SCM-033
        *Test case for validating list of percents *

        **Test Scenario:**

        #. Create schema with list of percents parameter, should succeed.
        #. Try to set parameter with non percent type, should fail.
        #. Try to set parameter with percent type, should succeed.
        """
        self.log("Create schema with list of percents parameter, should succeed.")
        scm = """
        @url = test.schema
        percent_list = (Lpercent)
        list_percents = [84, 73.4, '95', '72.8', '54%', '64.44%'] (Lpercent)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non percent type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.percent_list = [self.random_string(), self.random_string()]

        with self.assertRaises(Exception):
            schema_obj.percent_list.append(self.random_string())

        self.log("Try to set parameter with percent type, should succeed.")        
        percent_list = [random.randint(1, 100), random.uniform(1, 100)]
        check_list = [percent_list[0], round(percent_list[1]*100)]
        schema_obj.percent_list = percent_list
        self.assertEqual(schema_obj.percent_list, check_list)

        value = random.randint(1, 100)
        check_list.append(value)
        schema_obj.percent_list.append(value)
        self.assertEqual(schema_obj.percent_list, check_list)
        self.log("schema list %s" % schema_obj.list_percents)
        self.assertEqual(schema_obj.list_percents, [84, 7340, 95, 7280, 54, 6444])

    def test012_validate_list_of_urls(self):
        """
        SCM-034
        *Test case for validating list of urls *

        **Test Scenario:**

        #. Create schema with list of urls parameter, should succeed.
        #. Try to set parameter with non url type, should fail.
        #. Try to set parameter with url type, should succeed.
        """
        self.log("Create schema with list of urls parameter, should succeed.")
        scm = """
        @url = test.schema
        url_list = (Lu)
        list_urls = ['test.example.com/home', "test.example.com/login"] (Lu)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non url type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.url_list = [random.uniform(1, 100), 'test.example.com/home']

        with self.assertRaises(Exception):
            schema_obj.url_list.append(self.random_string())

        self.log("Try to set parameter with url type, should succeed.")
        url_list = ['test.example.com/home', "test.example.com/login"]
        schema_obj.url_list = url_list
        self.log("schema list %s" % schema_obj.list_urls)
        self.assertEqual(schema_obj.url_list, url_list)
        self.assertEqual(schema_obj.list_urls, url_list)

        value = 'test.example.com/settings'
        url_list.append(value)
        schema_obj.url_list.append(value)
        self.assertEqual(schema_obj.url_list, url_list)
    
    @unittest.skip("can't reach the currency methods(in list) to change between them")
    def test013_validate_list_of_numerics(self):
        """
        SCM-035
        *Test case for validating list of numerics *

        **Test Scenario:**

        #. Create schema with list of numerics parameter, should succeed.
        #. Try to set parameter with non numeric type, should fail.
        #. Try to set parameter with numeric type, should succeed.
        """
        self.log("Create schema with list of numerics parameter, should succeed.")
        scm = """
        @url = test.schema
        currency = (N)
        curr_list = (LN)
        list_numerics = ['10 usd', 10, 4.98] (LN)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non numeric type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.curr_list = [random.uniform(1, 100), self.random_string()]

        self.log("Try to set parameter with numeric type, should succeed.")
        curr_list = [random.randint(1, 100), random.uniform(1, 100), '{} usd'.format(random.randint(1, 100))]
        schema_obj.curr_list = curr_list
        # self.assertEqual(schema_obj.curr_list, curr_list)
        # self.assertEqual(schema_obj.list_numerics, curr_list)
    
    def test014_validate_list_of_guids(self):
        """
        SCM-036
        *Test case for validating list of guids *

        **Test Scenario:**

        #. Create schema with list of guids parameter, should succeed.
        #. Try to set parameter with non guid type, should fail.
        #. Try to set parameter with guid type, should succeed.
        """
        self.log("Create schema with list of guids parameter, should succeed.")
        scm = """
        @url = test.schema
        guid_list = (Lguid)
        list_guids = [bebe8b34-b12e-4fda-b00c-99979452b7bd, 84b022bd-2b00-4b62-8539-4ec07887bbe4] (Lguid)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non guid type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.guid_list = [str(uuid4())[:15], str(uuid4())]
        
        with self.assertRaises(Exception):
            schema_obj.guid_list.append(self.random_string())
        self.log("Try to set parameter with guid type, should succeed.")
        guid_list = [str(uuid4()), str(uuid4())]
        schema_obj.guid_list = guid_list
        self.assertEqual(schema_obj.guid_list, guid_list)
        self.log("schema list %s"%schema_obj.list_guids)
        self.assertEqual(schema_obj.list_guids, ['bebe8b34-b12e-4fda-b00c-99979452b7bd', '84b022bd-2b00-4b62-8539-4ec07887bbe4'])

        value = str(uuid4())
        guid_list.append(value)
        schema_obj.guid_list.append(value)
        self.assertEqual(schema_obj.guid_list, guid_list)

    def test015_validate_list_of_dicts(self):
        """
        SCM-037
        *Test case for validating list of dicts *

        **Test Scenario:**

        #. Create schema with list of dicts parameter, should succeed.
        #. Try to set parameter with non dict type, should fail.
        #. Try to set parameter with dict type, should succeed.
        """
        self.log("Create schema with list of dicts parameter, should succeed.")
        scm = """
        @url = test.schema
        dict_list = (Ldict)
        list_dicts = [{'number1':10, 'number2':100}, {'number1':10, "number2": 12}] (Ldict)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non dict type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.dict_list = [self.random_string(), {'number1':10, "number2": 12}]

        with self.assertRaises(Exception):
            schema_obj.dict_list.append(self.random_string())

        self.log("Try to set parameter with dict type, should succeed.")
        dict_list = [{'number1':10, 'number2':100}, {'number1':10, "number2": 12}]
        schema_obj.dict_list = dict_list
        self.assertEqual(schema_obj.dict_list, dict_list)
        self.assertEqual(schema_obj.list_dicts, dict_list)

        value = {'number1':5, 'number2':4}
        dict_list.append(value)
        schema_obj.dict_list.append(value)
        self.assertEqual(schema_obj.dict_list, dict_list)

    @unittest.skip("we didn't have set type anymore")
    def test016_validate_list_of_sets(self):
        """
        SCM-038
        *Test case for validating list of sets *

        **Test Scenario:**

        #. Create schema with list of sets parameter, should succeed.
        #. Try to set parameter with non set type, should fail.
        #. Try to set parameter with set type, should succeed.
        """
        self.log("Create schema with list of sets parameter, should succeed.")
        scm = """
        @url = test.schema
        set_list = (Lset)
        list_sets = [{1, 2, 3, 2}, {46, 284, 284, 259}] (Lset)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non set type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.set_list = [self.random_string(), {1, 2, 3, 2}]
        
        with self.assertRaises(Exception):
            schema_obj.set_list.append(self.random_string())

        self.log("Try to set parameter with set type, should succeed.")
        set_list = [{2, random.randint(1, 100), 2}, {random.randint(1, 100), random.randint(1, 100)}]
        schema_obj.set_list = set_list
        self.assertEqual(schema_obj.set_list, set_list)
        self.assertEqual(schema_obj.list_sets, [{1, 2, 3, 2}, {46, 284, 284, 259}])
        
        value = {random.randint(1, 100), random.randint(1, 100)}
        set_list.append(value)
        schema_obj.set_list.append(value)
        self.assertEqual(schema_obj.set_list, set_list)

    def test017_validate_list_of_hashs(self):
        """
        SCM-039
        *Test case for validating list of hashs *

        **Test Scenario:**

        #. Create schema with list of hashs parameter, should succeed.
        #. Try to set parameter with non hash type, should fail.
        #. Try to set parameter with hash type, should succeed.
        """
        self.log("Create schema with list of hashs parameter, should succeed.")
        scm = """
        @url = test.schema
        hash_list = (Lh)
        list_hashs = ["46:682", "10:861"] (Lh)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non hashs type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.hash_list = [self.random_string(), (10, 861)]
        
        with self.assertRaises(Exception):
            schema_obj.hash_list.append(self.random_string())

        self.log("Try to set parameter with hash type, should succeed.")
        hash_list = [(random.randint(1, 100), random.randint(1, 100)), (random.randint(1, 100), random.randint(1, 100))]
        schema_obj.hash_list = hash_list
        self.assertEqual(schema_obj.hash_list, hash_list)
        self.assertEqual(schema_obj.list_hashs, [(46, 682), (10, 861)])

        value = (random.randint(1, 100), random.randint(1, 100))
        hash_list.append(value)
        schema_obj.hash_list.append(value)
        self.assertEqual(schema_obj.hash_list, hash_list)

    def test018_validate_list_of_multilines(self):
        """
        SCM-040
        *Test case for validating list of multilines *

        **Test Scenario:**

        #. Create schema with list of multilines parameter, should succeed.
        #. Try to set parameter with non multiline type, should fail.
        #. Try to set parameter with multiline type, should succeed.
        """
        self.log("Create schema with list of multilines parameter, should succeed.")
        scm = """
        @url = test.schema
        lines_list = (Lmultiline)
        list_mlines = ['example \\n example2 \\n example4', "example \\n example2 \\n example3"] (Lmultiline)
        """
        schema = self.schema(scm)
        time.sleep(1)
        schema_obj = schema.new()

        self.log("Try to set parameter with non multiline type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.lines_list = [random.randint(1, 1000), "example \n example2 \n example3"]

        with self.assertRaises(Exception):
            schema_obj.lines_list.append(self.random_string())

        self.log("Try to set parameter with multiline type, should succeed.")
        lines_list = ["example \n example2 \n example4", "example \n example2 \n example3"]
        schema_obj.lines_list = lines_list
        self.assertEqual(schema_obj.lines_list, lines_list)

        value = "example4 \n example5 \n example6"
        lines_list.append(value)
        schema_obj.lines_list.append(value)
        self.assertEqual(schema_obj.lines_list, lines_list)

    def test019_validate_list_of_yaml(self):
        """
        SCM-041
        *Test case for validating list of yaml *

        **Test Scenario:**

        #. Create schema with list of yaml parameter, should succeed.
        #. Try to set parameter with non yaml type, should fail.
        #. Try to set parameter with yaml type, should succeed.
        """
        self.log("Create schema with list of yaml parameter, should succeed.")
        scm = """
        @url = test.schema
        yaml_list = (Lyaml)
        list_yaml = ["example:     test1", 'test'] (Lyaml)
        """
        schema = self.schema(scm)
        time.sleep(1)
        schema_obj = schema.new()

        self.log("Try to set parameter with non yaml type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.yaml_list = [random.randint(1, 1000), self.random_string()]
        
        with self.assertRaises(Exception):
            schema_obj.yaml_list.append(random.randint(1, 1000))

        self.log("Try to set parameter with yaml type, should succeed.")
        yaml_list = ["example:     test1", self.random_string()]
        schema_obj.yaml_list = yaml_list
        self.assertEqual(schema_obj.yaml_list, yaml_list)
        self.log("schema list %s" % schema_obj.list_yaml)

        self.assertEqual(schema_obj.list_yaml, ["example:     test1", 'test'])

        value = self.random_string()
        yaml_list.append(value)
        schema_obj.yaml_list.append(value)
        self.log("schema list %s" % schema_obj.list_yaml)
        self.assertEqual(schema_obj.yaml_list, yaml_list)

    def test020_validate_list_of_binary(self):
        """
        SCM-042
        *Test case for validating list of binary *

        **Test Scenario:**

        #. Create schema with list of binary parameter, should succeed.
        #. Try to set parameter with non binary type, should fail.
        #. Try to set parameter with binary type, should succeed.
        """
        self.log("Create schema with list of binary parameter, should succeed.")
        scm = """
        @url = test.schema
        bin_list = (Lbin)
        list_bin = ['test', 'example'] (Lbin)
        """
        schema = self.schema(scm)
        time.sleep(1)
        schema_obj = schema.new()

        self.log("Try to set parameter with non binary type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.bin_list = [self.random_string().encode(), self.random_string()]
        
        with self.assertRaises(Exception):
            schema_obj.bin_list.append(random.randint(1, 1000))

        self.log("Try to set parameter with binary type, should succeed.")
        bin_list = [self.random_string().encode(), self.random_string().encode()]
        schema_obj.bin_list = bin_list
        self.assertEqual(schema_obj.bin_list, bin_list)
        self.log("schema list %s" % schema_obj.list_bin)
        self.assertEqual(schema_obj.list_bin, [b'test', b'example'])

        value = self.random_string().encode()
        bin_list.append(value)
        schema_obj.bin_list.append(value)
        self.assertEqual(schema_obj.bin_list, bin_list)
