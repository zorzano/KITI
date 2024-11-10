from neo4j import GraphDatabase
from KGIoTDriver import KGIoTDriver
import os

class KGIoTDriverNeo4j(KGIoTDriver):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)

    def close(self):
        self._driver.close()

    @staticmethod
    def _listifyIterable(iterable):
        list=[]
        for record in iterable:
            list.append(record)
        return list

    @staticmethod
    def _createValueHolder(attributes):
        if (len(attributes) >0):
            valueHolder=" {"
            for atr,val in attributes:
                valueHolder+=str(atr)+":'"+str(val)+"' ,"
            valueHolder=valueHolder[:-1]
            valueHolder+="} "
        else:
            valueHolder=""
        return valueHolder

    def nukeBase(self):
        with self._driver.session() as session:
            txresult = session.write_transaction(self._nukeBase)
            return txresult

    # Type is a string with the item name.
    # attributes = [("a", 1), ("b", 2), ("c", 3)]
    # returns an array of arrays of dictionaries. The [0][0] dictionary is composed by atr-val pairs
    def readNode(self, type, attributes):
        with self._driver.session() as session:
            txresult = session.read_transaction(self._readNode, type, attributes)
            return txresult

    def readNodeAndLinked(self, type, attributes):
        with self._driver.session() as session:
            txresult = session.read_transaction(self._readNodeAndLinked, type, attributes)
            return txresult

    # Type is a string with the item name.
    # attributes = [("a", 1), ("b", 2), ("c", 3)]
    # Creates or merges the node. Returns TRUE if can do it.
    def mergeNode(self, type, attributes):
        with self._driver.session() as session:
            txresult = session.write_transaction(self._mergeNode, type, attributes)
            return txresult

    # Type is a string with the item name.
    # attributes = [("a", 1), ("b", 2), ("c", 3)]
    # Creates or merges the node. Returns TRUE if can do it.
    def mergeLink(self, typeLink, attributesLink, typeA, attributesA, typeB, attributesB):
        with self._driver.session() as session:
            txresult = session.write_transaction(self._mergeLink, typeLink, attributesLink, typeA, attributesA, typeB, attributesB)
            return txresult

    @staticmethod
    def _nukeBase(tx):
        result = tx.run("MATCH ()-[r]->() "
                        "DELETE r ")
        result = tx.run("MATCH (a) "
                        "DELETE a ")

        return KGIoTDriverNeo4j._listifyIterable(result)


    @staticmethod
    def _readNode(tx, type, attributes):
        valueHolder=KGIoTDriverNeo4j._createValueHolder(attributes)
        result = tx.run("MATCH (c1:"+type+valueHolder+") "
                        "RETURN c1 ")
        return KGIoTDriverNeo4j._listifyIterable(result)

    @staticmethod
    def _readNodeAndLinked(tx, type, attributes):
        valueHolder=KGIoTDriverNeo4j._createValueHolder(attributes)
        result = tx.run("MATCH (c1:"+type+valueHolder+")-[r]->(c2)"
                        "RETURN c1, r, c2")
        return KGIoTDriverNeo4j._listifyIterable(result)

    @staticmethod
    def _mergeNode(tx, type, attributes):
        valueHolder=KGIoTDriverNeo4j._createValueHolder(attributes)
        result = tx.run("MERGE (c1:"+type+valueHolder+") "
                        "RETURN c1.name ")

        return True

    @staticmethod
    def _mergeLink(tx, typeLink, attributesLink, typeA, attributesA, typeB, attributesB):
        valueHolderLink=KGIoTDriverNeo4j._createValueHolder(attributesLink)
        valueHolderA=KGIoTDriverNeo4j._createValueHolder(attributesA)
        valueHolderB=KGIoTDriverNeo4j._createValueHolder(attributesB)


        result = tx.run("MATCH (o:"+typeA+valueHolderA+") "
                        "MATCH (d:"+typeB+valueHolderB+") "
                        "MERGE (o)-[:"+typeLink+valueHolderLink+"]->(d);")
        return True
