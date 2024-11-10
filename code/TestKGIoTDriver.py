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
        # Comment this line to leave the base full
        self.kgiotdriver.nukeBase()

    def test_mergeNode01(self):
        res=self.kgiotdriver.mergeNode("Manufacturer", [("name", "Telit"), ("contact", "me")])
        self.assertTrue(res==True)
        # Returns list of lists of Nodes.
        # https://neo4j.com/docs/api/python-driver/current/api.html#neo4j.graph.Node
        res=self.kgiotdriver.readNode("Manufacturer", [("name", "Telit")])
        self.assertTrue(res[0][0]["name"]=="Telit")

    def test_mergeNode02(self):
        res=self.kgiotdriver.mergeNode("Manufacturer", [])
        self.assertTrue(res==True)

    def test_mergeLink01(self):
        self.kgiotdriver.mergeNode("Manufacturer", [("name", "Telit"), ("contact", "me")])
        self.kgiotdriver.mergeNode("Manufacturer", [("name", "Quectel"), ("contact", "him")])
        res=self.kgiotdriver.mergeLink("IS",[("name", "theLink")], "Manufacturer", [("name", "Telit"), ("contact", "me")], "Manufacturer", [("name", "Quectel")])
        self.assertTrue(res==True)

    def test_readNodeAndLinked(self):
        self.kgiotdriver.mergeNode("Manufacturer", [("name", "Telit"), ("contact", "me")])
        self.kgiotdriver.mergeNode("Manufacturer", [("name", "Quectel"), ("contact", "him")])
        self.kgiotdriver.mergeNode("Manufacturer", [("name", "Ublox"), ("contact", "other")])
        self.kgiotdriver.mergeLink("IS",[("name", "theLink")], "Manufacturer", [("name", "Telit"), ("contact", "me")], "Manufacturer", [("name", "Quectel")])
        self.kgiotdriver.mergeLink("IS",[("name", "theLink")], "Manufacturer", [("name", "Telit"), ("contact", "me")], "Manufacturer", [("name", "Ublox")])
        res=self.kgiotdriver.readNodeAndLinked("Manufacturer", [("name", "Telit")])
        # print(res[1])
        # print(isinstance(res[0][0], neo4j.graph.Relationship))
        self.assertTrue(res[0][1]["name"]=="theLink")
        self.assertTrue(res[1][1]["name"]=="theLink")
        self.assertTrue(res[0][0]["name"]=="Telit")
        self.assertTrue(res[1][0]["name"]=="Telit")
        self.assertTrue((res[0][2]["name"]=="Quectel") or (res[0][2]["name"]=="Ublox"))
        self.assertTrue((res[1][2]["name"]=="Quectel") or (res[1][2]["name"]=="Ublox"))
        # The type is in labels, which is a frozenset
        # x, *_ = (res[0][0].labels)


if __name__ == '__main__':
    unittest.main()
