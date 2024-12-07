import unittest
import logging
import sys

class TestKGIoT(unittest.TestCase):

    def setUp(self):
        print("setUp TestKGIoT")

    def tearDown(self):
        print("tearDown TestKGIoT")

    def test_01(self):
        self.assertTrue(1==1)

if __name__ == '__main__':
    unittest.main()
