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
        #self.kgiotdriver.nukeBase()

    def test_01(self):
        res=self.kgiotdriver.write("Manufacturer", "Telit")
        self.assertTrue(res[0][0]=="Telit")
        res=self.kgiotdriver.read("Manufacturer", [("name", "Telit")])
        # Returns list of lists of Nodes.
        # https://neo4j.com/docs/api/python-driver/current/api.html#neo4j.graph.Node
        self.assertTrue(res[0][0]["name"]=="Telit")

    def test_mergeNode01(self):
        res=self.kgiotdriver.mergeNode("Manufacturer", [("name", "Telit"), ("contact", "me")])
        self.assertTrue(res==True)
        res=self.kgiotdriver.read("Manufacturer", [("name", "Telit")])
        self.assertTrue(res[0][0]["name"]=="Telit")

    def test_mergeNode02(self):
        res=self.kgiotdriver.mergeNode("Manufacturer", [])
        self.assertTrue(res==True)

    def test_mergeLink01(self):
        self.kgiotdriver.mergeNode("Manufacturer", [("name", "Telit"), ("contact", "me")])
        self.kgiotdriver.mergeNode("Manufacturer", [("name", "Quectel"), ("contact", "him")])
        res=self.kgiotdriver.mergeLink("IS",[("name", "theLink")], "Manufacturer", [("name", "Telit"), ("contact", "me")], "Manufacturer", [("name", "Quectel")])
        self.assertTrue(res==True)

if __name__ == '__main__':
    unittest.main()
