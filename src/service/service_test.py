'''
Created on Nov 13, 2019

@author: cjr
'''
import unittest
import datetime
from service.BucketService import Period


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_Period_generate(self):
        period = Period()
        start = datetime.datetime(2019,10,1)
        end = datetime.datetime(2019,10,20)
        lst = period.generate(start,end)
        self.assertEqual(len(lst), 20, "Period size %s to %s" % (start,end))
        print("Got here")
        
    def test_Period_analyse_dates(self):
        print("analyse dates")
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()