# KITI

A simple system to create and update a Knowledge Graph storing a description of Internet of Things technical ecosystem. 

Content of this base:
- /ontology Ontology of the KITI base
- /data Contains data to be loaded in the KG. Data files are samples of the full files.
  loadbase.sh is the script that launches all the different data loaders
  dictionary.txt holds translations to be executed between different names that refer to the same concepts
  DeviceManufacturers.v2.csv is a CSV version of the main manufacturers inventory
  manufacturers.csv stores a dump of the Maria DB that stores the devices tested in the lab. Again, we store here only a sample row
  kiticontent.csv stores some triplets that are inserted also in KITI with context information
  TTTWiki.3.txt stores some internal procedures
- /webservice as the code that links KITI to the team MS-Teams chat. It uses a flask https server
  launchServer.sh is a stub. Not used
  kitiServer.py is the access point, configured in the flask server
- /code stores the project code
  xxxLoader.py are the loader files that take the data files and upload them in the knowledge graph
  GordopiloDialog.py is the entry point for the requests from the MS-Teams chat
  KGIoTDriver is the neutral prototype for database access.
  KGIoTDriverNeo4j.py is the implementation of the driver for Neo4j
  Test* are the files employed for unit testing

Environment:
- Ubuntu linux server
- flask
- Neo4j database
