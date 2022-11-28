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

    def nukeBase(self):
        with self._driver.session() as session:
            txresult = session.write_transaction(self._nukeBase)
            return txresult

    def write(self, type, name):
        with self._driver.session() as session:
            txresult = session.write_transaction(self._write, type, name)
            return txresult

    def read(self, type, name):
        with self._driver.session() as session:
            txresult = session.write_transaction(self._read, type, name)
            return txresult

    @staticmethod
    def _nukeBase(tx):
        result = tx.run("MATCH ()-[r]->() "
                        "DELETE r ")
        result = tx.run("MATCH (a) "
                        "DELETE a ")

        return KGIoTDriverNeo4j._listifyIterable(result)


    @staticmethod
    def _write(tx, type, name):
        result = tx.run("MERGE (c1:"+type+" {name:$s2}) "
                        "RETURN c1.name ",
                        s1=type, s2=name)
        return KGIoTDriverNeo4j._listifyIterable(result)

    @staticmethod
    def _read(tx, type, name):
        result = tx.run("MATCH (c1:"+type+" {name:$s2}) "
                        "RETURN c1.name ",
                        s1=type, s2=name)
        return KGIoTDriverNeo4j._listifyIterable(result)
