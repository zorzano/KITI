from KGIoTDriverNeo4j import KGIoTDriverNeo4j
import unittest
import logging
import sys
import os

class TestKGIoTDriver(unittest.TestCase):
    # Instantiate the final driver to test. And remember to import the corresponding class
    kgiotdriver = KGIoTDriverNeo4j("bolt://localhost:7687", "neo4j", os.getenv('PWDNEO4J'))

    def setUp(self):
        print("setUp TestKGIoT")

    def tearDown(self):
        print("tearDown TestKGIoT. Limpiando la base")
        self.kgiotdriver.nukeBase()

    def test_01(self):
        res=self.kgiotdriver.write("Manufacturer", "Telit")
        self.assertTrue(res[0][0]=="Telit")
        res=self.kgiotdriver.read("Manufacturer", "Telit")
        self.assertTrue(res[0][0]=="Telit")

if __name__ == '__main__':
    unittest.main()
