
from Jumpscale.data.schema.tests.testsuite.testcases.base_test import BaseTest
from Jumpscale import j
from unittest import TestCase
from uuid import uuid4
from datetime import datetime
import random, time, unittest

class SchemaTest(BaseTest):
    def setUp(self):
        super().setUp()    
    
    def test001_validate_string_type(self):
        """
        SCM-001
        *Test case for validating string type *

        **Test Scenario:**

        #. Create schema with string parameter[P1], should succeed.
        #. Try to set parameter[P1] with non string type, should fail.
        #. Try to set parameter[P1] with string type, should succeed.
        """
        self.log("Create schema with string parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        name = (S)
        init_str_1 = "test string 1" (S)
        init_str_2 = 'test string 2' (S)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non string type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.name = random.randint(1, 100)

        with self.assertRaises(Exception):
            schema_obj.name = random.uniform(10, 20)

        with self.assertRaises(Exception):
            schema_obj.name = [self.random_string(), self.random_string()]

        with self.assertRaises(Exception):
            schema_obj.name = {'name': self.random_string}

        self.log("Try to set parameter[P1] with string type, should succeed.")
        name = self.random_string()
        schema_obj.name = name
        self.assertEqual(schema_obj.name, name)
        self.assertEqual(schema_obj.init_str_1, 'test string 1')
        self.assertEqual(schema_obj.init_str_2, 'test string 2')

    def test002_validate_integer_type(self):
        """
        SCM-002
        *Test case for validating integer type *

        **Test Scenario:**

        #. Create schema with integer parameter[P1], should succeed.
        #. Try to set parameter[P1] with non integer type, should fail.
        #. Try to set parameter[P1] with integer type, should succeed.
        """
        self.log("Create schema with integer parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        number = (I)
        init_int = 123 (I)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non integer type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.number = "{}".format(random.randint(1, 1000))

        with self.assertRaises(Exception):
            schema_obj.number = random.uniform(10, 20)
        
        with self.assertRaises(Exception):
            schema_obj.number = self.random_string()
        
        with self.assertRaises(Exception):
            schema_obj.number = [random.randint(1, 1000), random.randint(1, 1000)]
        
        with self.assertRaises(Exception):
            schema_obj.number = {'number': random.randint(1, 1000)}

        self.log("Try to set parameter[P1] with integer type, should succeed.")
        rand_num = random.randint(1, 1000)
        schema_obj.number = rand_num
        self.assertEqual(schema_obj.number, rand_num)
        self.assertEqual(schema_obj.init_int, 123)

    def test003_validate_float_type(self):
        """
        SCM-003
        *Test case for validating float type *

        **Test Scenario:**

        #. Create schema with float parameter[P1], should succeed.
        #. Try to set parameter[P1] with non float type, should fail.
        #. Try to set parameter[P1] with float type, should succeed.
        """
        self.log("Create schema with float parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        number = (F)
        init_float = 84.32 (F)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non float type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.number = "{}".format(random.uniform(10, 20))
        
        with self.assertRaises(Exception):
            schema_obj.number = self.random_string()
        
        with self.assertRaises(Exception):
            schema_obj.number = [random.uniform(10, 20), random.uniform(10, 20)]
        
        with self.assertRaises(Exception):
            schema_obj.number = {'number': random.uniform(10, 20)}

        self.log("Try to set parameter[P1] with float type, should succeed.")
        rand_num = random.uniform(10, 20)
        schema_obj.number = rand_num
        self.assertEqual(schema_obj.number, rand_num)
        self.assertEqual(schema_obj.init_float, 84.32)

    def test004_validate_boolean_type(self):
        """
        SCM-004
        *Test case for validating boolean type *

        **Test Scenario:**

        #. Create schema with boolean parameter[P1], should succeed.
        #. Try to set parameter[P1] with False or non True value, should be False.
        #. Try to set parameter[P1] with True value, should be True.
        """
        self.log("Create schema with boolean parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        check = (B)
        init_bool_1 = 'y' (B)
        init_bool_2 = 1 (B)
        init_bool_3 = 'yes' (B)
        init_bool_4 = 'true' (B)
        init_bool_5 = True (B)
        init_bool_6 = 'n' (B)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with False or non True value, should be False.")
        schema_obj.check = False
        self.assertEqual(schema_obj.check, False)

        schema_obj.check = random.randint(10, 20)
        self.assertEqual(schema_obj.check, False)

        schema_obj.check = random.uniform(10, 20)
        self.assertEqual(schema_obj.check, False)

        schema_obj.check = self.random_string()
        self.assertEqual(schema_obj.check, False)

        schema_obj.check = [True, False]
        self.assertEqual(schema_obj.check, False)

        schema_obj.check = {'number': True}
        self.assertEqual(schema_obj.check, False)
        self.assertEqual(schema_obj.init_bool_6, False)

        self.log("Try to set parameter[P1] with True value, should be True.")
        schema_obj.check = True
        self.assertEqual(schema_obj.check, True)
        
        schema_obj.check = 1
        self.assertEqual(schema_obj.check, True)

        schema_obj.check = "1"
        self.assertEqual(schema_obj.check, True)

        schema_obj.check = "yes"
        self.assertEqual(schema_obj.check, True)

        schema_obj.check = "y"
        self.assertEqual(schema_obj.check, True)

        schema_obj.check = "true"
        self.assertEqual(schema_obj.check, True)
        self.assertEqual(schema_obj.init_bool_1, True)
        self.assertEqual(schema_obj.init_bool_2, True)
        self.assertEqual(schema_obj.init_bool_3, True)
        self.assertEqual(schema_obj.init_bool_4, True)
        self.assertEqual(schema_obj.init_bool_5, True)

    def test005_validate_mobile_type(self):
        """
        SCM-005
        *Test case for validating mobile type *

        **Test Scenario:**

        #. Create schema with mobile parameter[P1], should succeed.
        #. Try to set parameter[P1] with non mobile type, should fail.
        #. Try to set parameter[P1] with mobile type, should succeed.
        """
        self.log("Create schema with mobile parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        mobile = (tel)
        init_tel_1 = '464-4564-464' (tel)
        init_tel_2 = '+45687941' (tel)
        init_tel_3 = 468716420 (tel)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non mobile type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.mobile = "+s{}".format(self.random_string())

        with self.assertRaises(Exception):
            schema_obj.mobile = random.randint(10, 20)
        
        with self.assertRaises(Exception):
            schema_obj.mobile = random.uniform(10, 20)
        
        with self.assertRaises(Exception):
            schema_obj.mobile = ['{}'.format(random.randint(100000, 1000000)), '{}'.format(random.randint(100000, 1000000))]
        
        with self.assertRaises(Exception):
            schema_obj.mobile = {'number': '{}'.format(random.randint(100000, 1000000))}

        self.log("Try to set parameter[P1] with mobile type, should succeed.")
        number = '{}'.format(random.randint(100000, 1000000))
        schema_obj.mobile = number
        self.assertEqual(schema_obj.mobile, number)

        number = '+{}'.format(random.randint(100000, 1000000))
        schema_obj.mobile = number
        self.assertEqual(schema_obj.mobile, number)

        schema_obj.mobile = "464-4564-464"
        self.assertEqual(schema_obj.mobile, '4644564464')
        self.assertEqual(schema_obj.init_tel_1, '4644564464')
        self.assertEqual(schema_obj.init_tel_2, '+45687941')
        self.assertEqual(schema_obj.init_tel_3, '468716420')

    def test006_validate_email_type(self):
        """
        SCM-006
        *Test case for validating email type *

        **Test Scenario:**

        #. Create schema with email parameter[P1], should succeed.
        #. Try to set parameter[P1] with non email type, should fail.
        #. Try to set parameter[P1] with email type, should succeed.
        """
        self.log("Create schema with email parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        email = (email)
        init_email_1 = 'test.example@domain.com' (email)
        init_email_2 = test.example@domain.com (email)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non email type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.email = random.randint(1, 100)

        with self.assertRaises(Exception):
            schema_obj.email = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.email = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.email = 'example.com'

        with self.assertRaises(Exception):
            schema_obj.email = 'example@com'
        
        with self.assertRaises(Exception):
            schema_obj.email = ['test.example@domain.com', 'test.example@domain.com']
        
        with self.assertRaises(Exception):
            schema_obj.email = {'number': 'test.example@domain.com'}

        self.log("Try to set parameter[P1] with email type, should succeed.")
        schema_obj.email = 'test.example@domain.com'
        self.assertEqual(schema_obj.email, 'test.example@domain.com')
        self.assertEqual(schema_obj.init_email_1, 'test.example@domain.com')
        self.assertEqual(schema_obj.init_email_2, 'test.example@domain.com')

    def test007_validate_ipport_type(self):
        """
        SCM-007
        *Test case for validating ipport type *

        **Test Scenario:**

        #. Create schema with ipport parameter[P1], should succeed.
        #. Try to set parameter[P1] with non ipport type, should fail.
        #. Try to set parameter[P1] with ipport type, should succeed.
        """
        self.log("Create schema with ipport parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        port = (ipport)
        init_port = 12315 (ipport)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non ipport type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.port = random.randint(10000000, 100000000)

        with self.assertRaises(Exception):
            schema_obj.port = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.port = self.random_string()
        
        with self.assertRaises(Exception):
            schema_obj.port = [random.randint(1, 10000), random.randint(1, 10000)]
        
        with self.assertRaises(Exception):
            schema_obj.port = {'port': random.randint(1, 10000)}

        self.log("Try to set parameter[P1] with ipport type, should succeed.")
        port = random.randint(1, 10000)
        schema_obj.port = port
        self.assertEqual(schema_obj.port, port)
        self.assertEqual(schema_obj.init_port, 12315)

    def test008_validate_ipaddr_type(self):
        """
        SCM-008
        *Test case for validating ipaddr type *

        **Test Scenario:**

        #. Create schema with ipaddr parameter[P1], should succeed.
        #. Try to set parameter[P1] with non ipaddr type, should fail.
        #. Try to set parameter[P1] with ipaddr type, should succeed.
        """
        self.log("Create schema with ipaddr parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        ip = (ipaddr)
        init_ip_1 = '127.0.0.1' (ipaddr)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non ipaddr type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.ip = random.randint(1, 100)

        with self.assertRaises(Exception):
            schema_obj.ip = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.ip = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.ip = '10.20.256.1'
        
        with self.assertRaises(Exception):
            schema_obj.ip = '10.20.1'
        
        with self.assertRaises(Exception):
            schema_obj.ip = [random.randint(0, 255), random.randint(0, 255)]
        
        with self.assertRaises(Exception):
            schema_obj.ip = {'number': random.randint(0, 255)}

        self.log("Try to set parameter[P1] with ipaddr type, should succeed.")
        ip = '10.15.{}.1'.format(random.randint(0, 255))
        schema_obj.ip = ip
        self.assertEqual(schema_obj.ip, ip)
        self.assertEqual(schema_obj.init_ip_1, '127.0.0.1')

    def test009_validate_iprange_type(self):
        """
        SCM-009
        *Test case for validating iprange type *

        **Test Scenario:**

        #. Create schema with iprange parameter[P1], should succeed.
        #. Try to set parameter[P1] with non iprange type, should fail.
        #. Try to set parameter[P1] with iprange type, should succeed.
        """
        self.log("Create schema with iprange parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        iprange = (iprange)
        init_iprange = '127.0.0.1/16' (iprange)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non iprange type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.iprange = random.randint(1, 100)

        with self.assertRaises(Exception):
            schema_obj.iprange = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.iprange = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.iprange = '10.20.256.1'
        
        with self.assertRaises(Exception):
            schema_obj.iprange = '10.20.1'

        with self.assertRaises(Exception):
            schema_obj.iprange = '10.20.1.0'
        
        with self.assertRaises(Exception):
            schema_obj.iprange = '10.20.1.0/'

        with self.assertRaises(Exception):
            schema_obj.iprange = [random.randint(1, 100), random.randint(1, 100)]
        
        with self.assertRaises(Exception):
            schema_obj.iprange = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with iprange type, should succeed.")
        iprange = '10.15.{}.1/24'.format(random.randint(0, 255))
        schema_obj.iprange = iprange
        self.assertEqual(schema_obj.iprange, iprange)
        self.assertEqual(schema_obj.init_iprange, '127.0.0.1/16')
    
    def test010_validate_date_type(self):
        """
        SCM-010
        *Test case for validating date type *

        **Test Scenario:**

        #. Create schema with date parameter[P1], should succeed.
        #. Try to set parameter[P1] with non date type, should fail.
        #. Try to set parameter[P1] with date type, should succeed.
        """
        self.log("Create schema with date parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        date = (D)
        init_date_1 = 01/01/2019 9pm:10 (D)
        init_date_2 = '01/08/2018 8am:30' (D)
        init_date_3 = 50 (D)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non date type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.date = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.date = self.random_string()

        with self.assertRaises(Exception):
            date = '{:02}/31'.format(random.choice([2, 4, 6, 9, 11]))
            schema_obj.date = date
            self.assertEqual(schema_obj.date, date)
        
        with self.assertRaises(Exception):
            date = '2014/02/29'
            schema_obj.date = date
            self.assertEqual(schema_obj.date, date)

        with self.assertRaises(Exception):
            date = '201/02/29'
            schema_obj.date = date
            self.assertEqual(schema_obj.date, date)

        with self.assertRaises(Exception):
            date = '2014/{}/29'.format(random.randint(1, 9))
            schema_obj.date = date
            self.assertEqual(schema_obj.date, date)

        with self.assertRaises(Exception):
            date = '2014/02/{}'.format(random.randint(1, 9))
            schema_obj.date = date
            self.assertEqual(schema_obj.date, date)
        
        with self.assertRaises(Exception):
            date = '2014/02/01 {}{}:12'.format(random.choice(random.randint(13, 23), 0), random.choice('am', 'pm'))
            schema_obj.date = date
            self.assertEqual(schema_obj.date, date)

        with self.assertRaises(Exception):
            schema_obj.date = [random.randint(1, 9), random.randint(1, 9)]
        
        with self.assertRaises(Exception):
            schema_obj.date = {'date': random.randint(1, 9)}

        self.log("Try to set parameter[P1] with date type, should succeed.")
        self.assertEqual(schema_obj.init_date_1, 1546377000)
        self.assertEqual(schema_obj.init_date_2, 1533112200)
        self.assertEqual(schema_obj.init_date_3, 50)

        date = 0
        schema_obj.date = date
        self.assertEqual(schema_obj.date, date)

        date = random.randint(1, 200)
        schema_obj.date = date
        self.assertEqual(schema_obj.date, date)

        year = random.randint(1000, 2020)
        year_2c = random.randint(1, 99)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        hour_12 = random.randint(1, 11)
        minutes = random.randint(0, 59)
        am_or_pm = random.choice(['am', 'pm'])
        hours = hour_12 if am_or_pm == 'am' else hour_12 + 12
        years = 1900 if year_2c >= 69 else 2000

        date = datetime(datetime.now().year, month, day).timestamp()
        schema_obj.date = '{:02}/{:02}'.format(month, day)
        self.assertEqual(schema_obj.date, int(date))

        date = datetime(datetime.now().year, month, day, hour, minutes).timestamp()
        schema_obj.date = '{:02}/{:02} {:02}:{:02}'.format(month, day, hour, minutes)
        self.assertEqual(schema_obj.date, int(date))

        date = datetime(year, month, day).timestamp()
        schema_obj.date = '{}/{:02}/{:02}'.format(year, month, day)
        self.assertEqual(schema_obj.date, int(date))

        date = datetime(2016, 2, 29).timestamp()
        schema_obj.date = '2016/02/29'
        self.assertEqual(schema_obj.date, int(date))

        date = datetime(year, month, day, hour, minutes).timestamp()
        schema_obj.date = '{}/{:02}/{:02} {:02}:{:02}'.format(year, month, day, hour, minutes)
        self.assertEqual(schema_obj.date, int(date))

        date = datetime((year_2c + years), month, day).timestamp()
        schema_obj.date = '{:02}/{:02}/{:02}'.format(year_2c, month, day)
        self.assertEqual(schema_obj.date, int(date))

        date = datetime((year_2c + years), month, day, hour, minutes).timestamp()
        schema_obj.date = '{:02}/{:02}/{:02} {:02}:{:02}'.format(year_2c, month, day, hour, minutes)
        self.assertEqual(schema_obj.date, int(date))

        date = datetime(year, month, day, hours, minutes).timestamp()
        schema_obj.date = '{}/{:02}/{:02} {:02}{}:{:02}'.format(year, month, day, hour_12, am_or_pm, minutes)
        self.assertEqual(schema_obj.date, int(date))

        date = datetime(year, month, day).timestamp()
        schema_obj.date = '{:02}/{:02}/{}'.format(day, month, year)
        self.assertEqual(schema_obj.date, int(date))

        added_hours = random.randint(1, 12)
        added_day = 0 if (datetime.now().hour + added_hours) / 24 < 1 else 1
        added_hours_from_now = datetime.now().hour + added_hours if added_day == 0 else (datetime.now().hour + added_hours) % 24
        date = datetime(datetime.now().year, datetime.now().month, datetime.now().day + added_day, added_hours_from_now, datetime.now().minute, datetime.now().second).timestamp()
        schema_obj.date = '+{}h'.format(added_hours)
        self.assertAlmostEqual(schema_obj.date, int(date), delta=3)

    def test011_validate_percent_type(self):
        """
        SCM-011
        *Test case for validating percent type *

        **Test Scenario:**

        #. Create schema with percent parameter[P1], should succeed.
        #. Try to set parameter[P1] with non percent type, should fail.
        #. Try to set parameter[P1] with percent type, should succeed.
        """
        self.log("Create schema with percent parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        percent = (percent)
        init_percent_1 = 84 (percent)
        init_percent_2 = 73.4 (percent)
        init_percent_3 = '95' (percent)
        init_percent_4 = '72.8' (percent)
        init_percent_5 = '54%' (percent)
        init_percent_6 = '64.44%' (percent)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non percent type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.percent = 's' + self.random_string()

        with self.assertRaises(Exception):
            schema_obj.percent = '10$'

        with self.assertRaises(Exception):
            schema_obj.percent = ["10", "20"]
        
        with self.assertRaises(Exception):
            schema_obj.percent = [random.randint(1, 100), random.randint(1, 100)]
        
        with self.assertRaises(Exception):
            schema_obj.percent = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with percent type, should succeed.")
        percent = random.randint(0, 250)
        schema_obj.percent = percent
        self.assertEqual(schema_obj.percent, percent)
        
        percent = random.uniform(0, 250)
        schema_obj.percent = percent
        self.assertEqual(schema_obj.percent, percent*100)
        
        value = random.randint(1, 100)
        percent = '{}'.format(value)
        schema_obj.percent = percent
        self.assertEqual(schema_obj.percent, value)

        value = random.randint(1, 100)
        percent = '{}%'.format(value)
        schema_obj.percent = percent
        self.assertEqual(schema_obj.percent, value)

        value = random.uniform(1, 100)
        percent = '{}'.format(value)
        schema_obj.percent = percent
        self.assertEqual(schema_obj.percent, value*100)

        percent = '{}%'.format(value)
        schema_obj.percent = percent
        self.assertEqual(schema_obj.percent, (value)*100)
        self.assertEqual(schema_obj.init_percent_1, 84)
        self.assertEqual(schema_obj.init_percent_2, 7340)
        self.assertEqual(schema_obj.init_percent_3, 95)
        self.assertEqual(schema_obj.init_percent_4, 7280)
        self.assertEqual(schema_obj.init_percent_5, 54)
        self.assertEqual(schema_obj.init_percent_6, 6444)

    def test012_validate_url_type(self):
        """
        SCM-012
        *Test case for validating url type *

        **Test Scenario:**

        #. Create schema with url parameter[P1], should succeed.
        #. Try to set parameter[P1] with non url type, should fail.
        #. Try to set parameter[P1] with url type, should succeed.
        """
        self.log("Create schema with url parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        site = (u)
        init_url = 'test.example.com/home' (u)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non url type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.site = random.randint(1, 100)

        with self.assertRaises(Exception):
            schema_obj.site = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.site = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.site = 'example@com'

        with self.assertRaises(Exception):
            schema_obj.site = 'test/example.com'
        
        with self.assertRaises(Exception):
            schema_obj.site = [random.randint(1, 100), random.randint(1, 100)]
        
        with self.assertRaises(Exception):
            schema_obj.site = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with url type, should succeed.")
        schema_obj.site = 'test.example.com'
        self.assertEqual(schema_obj.site, 'test.example.com')

        schema_obj.site = 'test.example.com/home'
        self.assertEqual(schema_obj.site, 'test.example.com/home')
        self.assertEqual(schema_obj.init_url, 'test.example.com/home')

    def test013_validate_numeric_type(self):
        """
        SCM-013
        *Test case for validating numeric type *

        **Test Scenario:**

        #. Create schema with numeric parameter[P1], should succeed.
        #. Try to set parameter[P1] with non numeric type, should fail.
        #. Try to set parameter[P1] with numeric type, should succeed.
        """
        self.log("Create schema with numeric parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        number = (N)
        currency = (N)
        init_numeric_1 = '10 usd' (N)
        init_numeric_2 = 10 (N)
        init_numeric_3 = 10.54 (N)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non numeric type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.currency = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.currency = [random.randint(1, 100), random.randint(1, 100)]
        
        with self.assertRaises(Exception):
            schema_obj.currency = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with numeric type, should succeed.")
        number = random.randint(1, 1000)
        schema_obj.number = number
        self.assertEqual(schema_obj.number_usd, number)

        number = random.uniform(1, 1000)
        schema_obj.number = number
        self.assertEqual(schema_obj.number_usd, number)

        value = random.randint(1, 100)
        currency = '{} USD'.format(value)
        schema_obj.currency = currency
        self.assertEqual(schema_obj.currency_usd, value)
        self.assertEqual(schema_obj.init_numeric_1_usd, 10)
        self.assertEqual(schema_obj.init_numeric_2_usd, 10)
        self.assertEqual(schema_obj.init_numeric_3_usd, 10.54)

    def test014_validate_currency_conversion(self):
        """
        SCM-014
        *Test case for validating currencies conversion *

        **Test Scenario:**

        #. Create schema with numeric parameter[P1], should succeed.
        #. Put one of currencies and convert it to the other currencies and Check result is same as calculated. 
        """
        self.log("Create schema with numeric parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        currency = (N)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Put one of currencies and convert it to the other currencies and Check result is same as calculated")
        currency = j.clients.currencylayer.get(self.random_string())
        currencies = currency.cur2usd
        for curr1 in currencies:
            value = random.uniform(1, 100)
            currency = '{} {}'.format(value, curr1)
            schema_obj.currency = currency
            for curr2 in currencies:
                self.assertAlmostEqual(schema_obj.currency_cur(curr2), value*currencies[curr2]/currencies[curr1], delta=0.0001)
        
    def test015_validate_guid_type(self):
        """
        SCM-015
        *Test case for validating guid type *

        **Test Scenario:**

        #. Create schema with guid parameter[P1], should succeed.
        #. Try to set parameter[P1] with non guid type, should fail.
        #. Try to set parameter[P1] with guid type, should succeed.
        """
        self.log("Create schema with guid parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        guid = (guid)
        init_guid_1 = bebe8b34-b12e-4fda-b00c-99979452b7bd (guid)
        init_guid_2 = '84b022bd-2b00-4b62-8539-4ec07887bbe4' (guid)
        """.format(str(uuid4()))
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non guid type, should fail.")    
        with self.assertRaises(Exception):
            schema_obj.guid = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.guid = str(uuid4())[:15]

        with self.assertRaises(Exception):
            schema_obj.guid = random.randint(1, 1000)

        with self.assertRaises(Exception):
            schema_obj.guid = random.uniform(1, 1000)
        
        with self.assertRaises(Exception):
            schema_obj.guid = [random.randint(1, 100), random.randint(1, 100)]
        
        with self.assertRaises(Exception):
            schema_obj.guid = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with guid type, should succeed.")
        guid = str(uuid4())
        schema_obj.guid = guid
        self.assertEqual(schema_obj.guid, guid)
        self.assertEqual(schema_obj.init_guid_1, 'bebe8b34-b12e-4fda-b00c-99979452b7bd')
        self.assertEqual(schema_obj.init_guid_1, '84b022bd-2b00-4b62-8539-4ec07887bbe4')

    def test016_validate_dict_type(self):
        """
        SCM-016
        *Test case for validating dict type *

        **Test Scenario:**

        #. Create schema with dict parameter[P1], should succeed.
        #. Try to set parameter[P1] with non dict type, should fail.
        #. Try to set parameter[P1] with dict type, should succeed.
        """
        self.log("Create schema with dict parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        info = (dict)
        init_dict = {"number": 468} (dict)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non dict type, should fail.")    
        with self.assertRaises(Exception):
            schema_obj.info = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.info = random.randint(1, 1000)

        with self.assertRaises(Exception): 
            schema_obj.info = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.info = [random.randint(1, 100), random.randint(1, 100)]

        self.log("Try to set parameter[P1] with dict type, should succeed.")
        value = random.randint(1, 1000)
        schema_obj.info = {'number': value}
        self.assertEqual(schema_obj.info, {'number': value})
        self.assertEqual(schema_obj.init_dict, {'number': 468})

    def test017_validate_set_type(self):
        """
        SCM-017
        *Test case for validating set type *

        **Test Scenario:**

        #. Create schema with set parameter[P1], should succeed.
        #. Try to set parameter[P1] with non set type, should fail.
        #. Try to set parameter[P1] with set type, should succeed.
        """
        self.log("Create schema with set parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        data = (set)
        init_set = {1, 2, 3, 2} (set)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non set type, should fail.")    
        with self.assertRaises(Exception):
            schema_obj.data = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.data = random.randint(1, 1000)

        with self.assertRaises(Exception): 
            schema_obj.data = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.data = {'number': random.randint(1, 1000)}

        self.log("Try to set parameter[P1] with set type, should succeed.")
        int_set = {random.randint(1, 1000), random.randint(1, 1000)}
        schema_obj.data = int_set
        self.assertEqual(schema_obj.data, int_set)

        float_set = {random.uniform(1, 100), random.uniform(1, 100)}
        schema_obj.data = float_set
        self.assertEqual(schema_obj.data, float_set)

        str_set = {self.random_string(), self.random_string()}
        schema_obj.data = str_set
        self.assertEqual(schema_obj.data, str_set)
        self.assertEqual(schema_obj.init_set, {1, 2, 3})
    
    def test018_validate_hash_type(self):
        """
        SCM-018
        *Test case for validating hash type *

        **Test Scenario:**

        #. Create schema with hash parameter[P1], should succeed.
        #. Try to set parameter[P1] with non hash type, should fail.
        #. Try to set parameter[P1] with hash type, should succeed.
        """
        self.log("Create schema with hash parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        data = (h)
        init_hash = [46, 682] (h)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non hash type, should fail.")   
        with self.assertRaises(Exception):
            schema_obj.data = [random.randint(1, 100), random.randint(10, 1000), random.randint(1, 500)]

        with self.assertRaises(Exception):
            schema_obj.data = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.data = random.randint(1, 1000)

        with self.assertRaises(Exception): 
            schema_obj.data = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.data = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with hash type, should succeed.")
        data = (random.randint(1, 1000), random.randint(1000, 1000000))
        schema_obj.data = data
        self.assertEqual(schema_obj.data, data)

        data = [random.randint(1, 100), random.randint(1, 100)]
        schema_obj.data = data
        self.assertEqual(schema_obj.data[0], data[0])
        self.assertEqual(schema_obj.data[1], data[1])
        self.assertEqual(schema_obj.init_hash_2, (46, 682))
    
    def test019_validate_multiline_type(self):
        """
        SCM-019
        *Test case for validating multiline type *

        **Test Scenario:**

        #. Create schema with multiline parameter[P1], should succeed.
        #. Try to set parameter[P1] with non multiline type, should fail.
        #. Try to set parameter[P1] with multiline type, should succeed.
        """
        self.log("Create schema with multiline parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        lines = (multiline)
        init_mline = "example \\n example2 \\n example3" (multiline)

        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non multiline type, should fail.")    
        with self.assertRaises(Exception):
            schema_obj.lines = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.lines = random.randint(1, 1000)

        with self.assertRaises(Exception): 
            schema_obj.lines = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.lines = [random.randint(1, 100), random.randint(1, 100)]
        
        with self.assertRaises(Exception):
            schema_obj.lines = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with multiline type, should succeed.")
        schema_obj.lines = "example \n example2 \n example3"
        self.assertEqual(schema_obj.lines, "example \n example2 \n example3")
        self.assertEqual(schema_obj.init_mline, "example \n example2 \n example3")

    def test020_validate_yaml_type(self):
        """
        SCM-020
        *Test case for validating yaml type *

        **Test Scenario:**

        #. Create schema with yaml parameter[P1], should succeed.
        #. Try to set parameter[P1] with non yaml type, should fail.
        #. Try to set parameter[P1] with yaml type, should succeed.
        """
        self.log("Create schema with yaml parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        data = (yaml)
        init_yaml = "example:     test1" (yaml)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non yaml type, should fail.")    
        with self.assertRaises(Exception):
            schema_obj.data = random.randint(1, 1000)

        with self.assertRaises(Exception): 
            schema_obj.data = random.uniform(1, 100)
        
        with self.assertRaises(Exception):
            schema_obj.data = [random.randint(1, 100), random.randint(1, 100)]
        
        with self.assertRaises(Exception):
            schema_obj.data = {'number': random.randint(1, 100)}

        self.log("Try to set parameter[P1] with yaml type, should succeed.")
        data = self.random_string()
        schema_obj.data = data
        self.assertEqual(schema_obj.data, data)

        schema_obj.data = "example:     test1"
        self.assertEqual(schema_obj.data, "example:     test1")
        self.assertEqual(schema_obj.init_yaml, "example:     test1")

    def test021_validate_enum_type(self):
        """
        SCM-021
        *Test case for validating enum type *

        **Test Scenario:**

        #. Create schema with enum parameter[P1], should succeed.
        #. Try to set parameter[P1] with non enum type, should fail.
        #. Try to set parameter[P1] with enum type, should succeed.
        """
        self.log("Create schema with enum parameter[P1], should succeed.")
        scm = """
        @url = test.schema
        colors = 'red, green, blue, black' (E)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter[P1] with non enum type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.colors = self.random_string()

        with self.assertRaises(Exception):
            schema_obj.colors = random.randint(5, 1000)

        with self.assertRaises(Exception): 
            schema_obj.colors = random.uniform(5, 100)
        
        with self.assertRaises(Exception):
            schema_obj.colors = ['RED', 'GREEN', 'BLUE', 'BLACK']
        
        with self.assertRaises(Exception):
            schema_obj.colors = {'colors': ['RED', 'GREEN', 'BLUE', 'BLACK']}

        self.log("Try to set parameter[P1] with enum type, should succeed.")
        colors = ['BLACK', 'BLUE', 'GREEN', 'RED']
        color = random.choice(colors)
        schema_obj.colors = color
        self.assertEqual(schema_obj.colors, color)

        index = random.randint(0,3)
        schema_obj.colors = index + 1
        self.assertEqual(schema_obj.colors, colors[index])

    def test022_validate_list_of_strings(self):
        """
        SCM-022
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

        self.log("Try to set parameter with string type, should succeed.")
        list_names = [self.random_string(), self.random_string()]
        schema_obj.list_names = list_names
        self.assertEqual(schema_obj.list_names, list_names)
        self.assertEqual(schema_obj.list_str, ['test', 'example'])
    
    def test023_validate_list_of_integers(self):
        """
        SCM-023
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

        self.log("Try to set parameter with integer type, should succeed.")
        list_numbers = [random.randint(1, 1000), random.randint(1, 1000)]
        schema_obj.list_numbers = list_numbers
        self.assertEqual(schema_obj.list_numbers, list_numbers)
        self.assertEqual(schema_obj.list_int, [1, 2, 3])
    
    def test024_validate_list_floats(self):
        """
        SCM-024
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

        self.log("Try to set parameter with float type, should succeed.")
        list_numbers = [random.uniform(1, 1000), random.uniform(1, 1000)]
        schema_obj.list_numbers = list_numbers
        self.assertEqual(schema_obj.list_numbers, list_numbers)
        self.assertEqual(schema_obj.list_floats, [1.5, 2.67, 3.7])
    
    def test025_validate_list_of_boolean(self):
        """
        SCM-025
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
        self.assertEqual(schema_obj.list_check, [True, True, True, True, True, False])
        self.assertEqual(schema_obj.list_bool, [True, True, True, True, True, False])
    
    def test026_validate_list_of_mobiles(self):
        """
        SCM-026
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
        list_tel = ['464-4564-464', '+45687941', 468716420] (Ltel)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non mobile type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.mobile_list = [random.uniform(1, 100), random.randint(100000, 1000000)]

        self.log("Try to set parameter with mobile type, should succeed.")
        mobile_list = ['{}'.format(random.randint(100000, 1000000)), '{}'.format(random.randint(100000, 1000000))]
        schema_obj.mobile_list = mobile_list
        self.assertEqual(schema_obj.mobile_list, mobile_list)
        self.assertEqual(schema_obj.list_tel, ['4644564464', '+45687941', '468716420'])
    
    def test027_validate_list_of_emails(self):
        """
        SCM-027
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

        self.log("Try to set parameter with email type, should succeed.")
        email_list = ['test.example@domain.com', "test.example@domain.com"]
        schema_obj.email_list = email_list
        self.assertEqual(schema_obj.email_list, email_list)
        self.assertEqual(schema_obj.list_emails, ['test.example@domain.com', 'test.example2@domain.com'])
    
    def test028_validate_list_of_ipports(self):
        """
        SCM-028
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

        self.log("Try to set parameter with ipport type, should succeed.")
        port_list = [random.randint(1, 10000), random.randint(1, 10000)]
        schema_obj.port_list = port_list
        self.assertEqual(schema_obj.port_list, port_list)
        self.assertEqual(schema_obj.list_ports, [3164, 15487])
    
    def test029_validate_list_of_ipaddrs(self):
        """
        SCM-029
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

        self.log("Try to set parameter with ipaddr type, should succeed.")
        ip_list = ['127.0.0.1', "192.168.1.1"]
        schema_obj.ip_list = ip_list
        self.assertEqual(schema_obj.ip_list, ip_list)
        self.assertEqual(schema_obj.list_ip, ip_list)
    
    def test030_validate_list_of_ipranges(self):
        """
        SCM-030
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

        self.log("Try to set parameter with iprange type, should succeed.")
        range_list = ['10.15.{}.1/24'.format(random.randint(0, 255)), '10.15.{}.1/24'.format(random.randint(0, 255))]
        schema_obj.range_list = range_list
        self.assertEqual(schema_obj.range_list, range_list)
        self.assertEqual(schema_obj.list_ranges, ['127.0.0.1/24', "192.168.1.1/16"])

    def test031_validate_list_of_dates(self):
        """
        SCM-031
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
        list_dates = [50, '01/01/2019 9pm:10'] (LD)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non date type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.date_list = [self.random_string(), '01/08/2018 8am:30']

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
        self.assertEqual(schema_obj.list_dates, [50, 1546377000])

    def test032_validate_list_of_percents(self):
        """
        SCM-032
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

        self.log("Try to set parameter with percent type, should succeed.")        
        percent_list = [random.randint(1, 100), random.uniform(1, 100)]
        schema_obj.percent_list = percent_list
        self.assertEqual(schema_obj.percent_list, [percent_list[0], percent_list[1]*100])
        self.assertEqual(schema_obj.list_percents, [84, 7340, 95, 7280, 54, 6444])

    def test033_validate_list_of_urls(self):
        """
        SCM-033
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

        self.log("Try to set parameter with url type, should succeed.")
        url_list = ['test.example.com/home', "test.example.com/login"]
        schema_obj.url_list = url_list
        self.assertEqual(schema_obj.url_list, url_list)
        self.assertEqual(schema_obj.list_urls, url_list)
    
    @unittest.skip("can't reach the currency methods(in list) to change between them")
    def test034_validate_list_of_numerics(self):
        """
        SCM-034
        *Test case for validating list of numerics *

        **Test Scenario:**

        #. Create schema with list of numerics parameter, should succeed.
        #. Try to set parameter with non numeric type, should fail.
        #. Try to set parameter with numeric type, should succeed.
        """
        self.log("Create schema with list of numerics parameter, should succeed.")
        scm = """
        @url = test.schema
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
    
    def test035_validate_list_of_guids(self):
        """
        SCM-035
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
        list_guids = ['bebe8b34-b12e-4fda-b00c-99979452b7bd', "84b022bd-2b00-4b62-8539-4ec07887bbe4"] (Lguid)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non guid type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.guid_list = [str(uuid4())[:15], str(uuid4())]

        self.log("Try to set parameter with guid type, should succeed.")
        guid_list = [str(uuid4()), str(uuid4())]
        schema_obj.guid_list = guid_list
        self.assertEqual(schema_obj.guid_list, guid_list)
        self.assertEqual(schema_obj.list_guids, ['bebe8b34-b12e-4fda-b00c-99979452b7bd', '84b022bd-2b00-4b62-8539-4ec07887bbe4'])

    def test036_validate_list_of_dicts(self):
        """
        SCM-036
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

        self.log("Try to set parameter with dict type, should succeed.")
        dict_list = [{'number1':10, 'number2':100}, {'number1':10, "number2": 12}]
        schema_obj.dict_list = dict_list
        self.assertEqual(schema_obj.dict_list, dict_list)
        self.assertEqual(schema_obj.list_dicts, dict_list)

    def test037_validate_list_of_sets(self):
        """
        SCM-037
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

        self.log("Try to set parameter with set type, should succeed.")
        set_list = [{1, 2, 3, 2}, {46, 284, 284, 259}]
        schema_obj.set_list = set_list
        self.assertEqual(schema_obj.set_list, set_list)
        self.assertEqual(schema_obj.list_sets, set_list)

    def test038_validate_list_of_hashs(self):
        """
        SCM-038
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
        list_hashs = [[46, 682], [10, 861]] (Lh)
        """
        schema = self.schema(scm)
        schema_obj = schema.new()

        self.log("Try to set parameter with non hashs type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.hash_list = [self.random_string(), (10, 861)]

        self.log("Try to set parameter with hash type, should succeed.")
        hash_list = [(46, 682), (10, 861)]
        schema_obj.hash_list = hash_list
        self.assertEqual(schema_obj.hash_list, hash_list)
        self.assertEqual(schema_obj.list_hashs, hash_list)

    def test039_validate_list_of_multilines(self):
        """
        SCM-039
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
        list_mlines = ['example \\n example2 \\n example3', "example \\n example2 \\n example3"] (Lmultiline)
        """
        schema = self.schema(scm)
        time.sleep(1)
        schema_obj = schema.new()

        self.log("Try to set parameter with non multiline type, should fail.")
        with self.assertRaises(Exception):
            schema_obj.lines_list = [random.randint(1, 1000), "example \n example2 \n example3"]

        self.log("Try to set parameter with multiline type, should succeed.")
        lines_list = ["example \n example2 \n example3", "example \n example2 \n example3"]
        schema_obj.lines_list = lines_list
        self.assertEqual(schema_obj.lines_list, lines_list)
        self.assertEqual(schema_obj.list_mlines, lines_list)

    def test040_nested_concatenated_schema(self):
        """
        SCM-040
        *Test case for concatenated nesting schema *

        **Test Scenario:**

        #. Create three schemas on one schema with different datatypes, should succeed.
        #. Set data to schema parameters, should succeed.
        #. Check that data reflected correctly.
        """
        self.log("Create three schemas with different datatypes, should succeed.")
        scm3 = """
        @url = student.schema
        name = (S)
        numbers = (O) !phone.schema
        address = (O) !address.schema
        grades = (Lp)

        @url = phone.schema
        mobile_number = (tel)
        home_number = (tel)

        @url = address.schema
        country = (S)
        city = (S)
        street = (S)
        building = (I)
        """

        schema3 = self.schema(scm3)
        schema_obj3 = schema3.new()

        self.log("Set data to schema parameters, should succeed.")
        name = self.random_string()
        mobile_number = '{}'.format(random.randint(1000000000, 2000000000))
        home_number = '{}'.format(random.randint(500000000, 900000000))
        country = self.random_string()
        city = self.random_string()
        street = self.random_string()
        building = random.randint(1, 100)
        grades = [random.randint(50, 100), random.randint(50, 100)]

        schema_obj3.name = name
        schema_obj3.numbers.mobile_number = mobile_number
        schema_obj3.numbers.home_number = home_number
        schema_obj3.address.country = country
        schema_obj3.address.city = city
        schema_obj3.address.street = street
        schema_obj3.address.building = building
        schema_obj3.grades = grades

        self.log("Check that data reflected correctly")
        self.assertEqual(schema_obj3.name, name)
        self.assertEqual(schema_obj3.numbers.mobile_number, mobile_number)
        self.assertEqual(schema_obj3.numbers.home_number, home_number)
        self.assertEqual(schema_obj3.address.country, country)
        self.assertEqual(schema_obj3.address.city, city)
        self.assertEqual(schema_obj3.address.street, street)
        self.assertEqual(schema_obj3.address.building, building)
        self.assertEqual(schema_obj3.grades, grades)

    def test041_nested_sperated_schema(self):
        """
        SCM-041
        *Test case for concatenated nesting schema *

        **Test Scenario:**

        #. Create three schemas on one schema with different datatypes, should succeed.
        #. Set data to schema parameters, should succeed.
        #. Check that data reflected correctly.
        """
        self.log("Create three schemas with different datatypes, should succeed.")
        scm1 = """
        @url = phone.schema
        mobile_number = (tel)
        home_number = (tel)
        """
        scm2 = """
        @url = address.schema
        country = (S)
        city = (S)
        street = (S)
        building = (I)
        """
        scm3 = """
        @url = student.schema
        name = (S)
        numbers = (O) !phone.schema
        address = (O) !address.schema
        grades = (Lp)
        """ 
        schema1 = self.schema(scm1)
        schema_obj1 = schema1.new()

        schema2 = self.schema(scm2)
        schema_obj2 = schema2.new()

        schema3 = self.schema(scm3)
        schema_obj3 = schema3.new()

        self.log("Set data to schema parameters, should succeed.")
        name = self.random_string()
        mobile_number = '{}'.format(random.randint(1000000000, 2000000000))
        home_number = '{}'.format(random.randint(500000000, 900000000))
        country = self.random_string()
        city = self.random_string()
        street = self.random_string()
        building = random.randint(1, 100)
        grades = [random.randint(50, 100), random.randint(50, 100)]

        schema_obj3.name = name
        schema_obj3.numbers.mobile_number = mobile_number
        schema_obj3.numbers.home_number = home_number
        schema_obj3.address.country = country
        schema_obj3.address.city = city
        schema_obj3.address.street = street
        schema_obj3.address.building = building
        schema_obj3.grades = grades

        self.log("Check that data reflected correctly")
        self.assertEqual(schema_obj3.name, name)
        self.assertEqual(schema_obj3.numbers.mobile_number, mobile_number)
        self.assertEqual(schema_obj3.numbers.home_number, home_number)
        self.assertEqual(schema_obj3.address.country, country)
        self.assertEqual(schema_obj3.address.city, city)
        self.assertEqual(schema_obj3.address.street, street)
        self.assertEqual(schema_obj3.address.building, building)
        self.assertEqual(schema_obj3.grades, grades)
    
