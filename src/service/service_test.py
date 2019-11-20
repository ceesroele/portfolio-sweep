'''
Created on Nov 13, 2019

@author: cjr
'''
import unittest
import datetime
from service.BucketService import TimeBucket, Period
import Config

class Test(unittest.TestCase):

    def setUp(self):
        Config.app = Config.App()
        Config.config = Config.Config("../../sweep.yaml")

    def tearDown(self):
        pass

    def test_TimeBucket_cumulative(self):
        dictionary = {
            0: 10,
            1: 20,
            2: 30
        }
        bs = TimeBucket(Config.config, [])
        output = bs.cumulative(dictionary)
        # result of TimeBucket.cumulative should have same number of elements as input
        self.assertEqual(len(dictionary), len(output), "Number of elements in dictionary changed")

        # max value should be equal to the sum of all values
        self.assertEqual(sum(dictionary.values()), max(output.values()), "Sum of values of input must equal max of values of output")

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