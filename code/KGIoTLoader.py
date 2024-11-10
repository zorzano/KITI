import sys
from KGIoTDriverNeo4j import KGIoTDriverNeo4j
from KGIoTSynonims import KGIoTSynonims
import os
import csv


kgiotdriver = KGIoTDriverNeo4j("bolt://localhost:7687", "neo4j", os.getenv('PWDNEO4J'))
kgiotdriver.nukeBase()
kgiotdriver.mergeNode("Company", [("name", "Telefonica"),("url", "http://www.telefonica.com")])

if(len(sys.argv)>2):
    kgiotsynonims=KGIoTSynonims(sys.argv[2])
else:
    kgiotsynonims=KGIoTSynonims("")

with open(sys.argv[1], newline='', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    reader.__next__()
    for fields in reader:
        for index, item in enumerate(fields):
            fields[index]=kgiotsynonims.substituteAny(fields[index])
            fields[index]=item.strip(" \"")
            fields[index] = fields[index].replace("\\N", "")
            fields[index]=kgiotsynonims.map(fields[index])
            print(index, " ", fields[index])
        customer=fields[1]
        manufacturer=fields[2]
        model=fields[3]
        devicemode=fields[4]
        devicetype=fields[5]
        deviceusecase=fields[6]
        if(model=="" and ((deviceusecase!="") or (devicetype!=""))):
            model="Generic "+manufacturer+" product"
        deviceprice=fields[7]
        url=fields[8]
        geo=fields[9]
        contactname=fields[10]
        contactmail=fields[11]
        tefcontactname=fields[12]
        tefcontactmail=fields[13]
        ob=fields[14]
        source=fields[15] # Not used yet
        user=fields[16] # Not used yet

        if(manufacturer==""):
            continue
        kgiotdriver.mergeNode("Company", [("name", manufacturer),("url", url)])

        if(geo!=""):
            kgiotdriver.mergeNode("Geo", [("name", geo)])
            kgiotdriver.mergeLink("GEO",[], "Company", [("name", manufacturer),("url", url)], "Geo", [("name", geo)])
        if(model!=""):
            kgiotdriver.mergeNode("Product", [("name", model)])
            kgiotdriver.mergeLink("SELLS",[], "Company", [("name", manufacturer),("url", url)], "Product", [("name", model)])
        if(devicemode!=""):
            kgiotdriver.mergeNode("DeviceType", [("name", devicemode)])
            kgiotdriver.mergeLink("IS",[], "Product", [("name", model)],  "DeviceType", [("name", devicemode)])
#        if(devicetype!=""):
#            kgiotdriver.mergeNode("Service", [("name", devicetype)])
#            kgiotdriver.mergeLink("PROVIDES",[], "Product", [("name", model)],  "Service", [("name", devicetype)])
        if(deviceusecase!=""):
            for x in deviceusecase.split(" "):
                kgiotdriver.mergeNode("Service", [("name", x)])
    #            kgiotdriver.mergeLink("USEDIN",[], "Product", [("name", model)],  "UseCase", [("name", deviceusecase)])
                kgiotdriver.mergeLink("PROVIDES",[], "Product", [("name", model)],  "Service", [("name", x)])
        if(contactname!="" or contactmail!=""):
            kgiotdriver.mergeNode("Person", [("name", contactname),("email", contactmail)])
            kgiotdriver.mergeLink("WORKSFOR",[], "Person", [("name", contactname),("email", contactmail)],"Company", [("name", manufacturer),("url", url)])
        if(tefcontactname!="" or tefcontactmail!=""):
            kgiotdriver.mergeNode("Person", [("name", tefcontactname),("email", tefcontactmail)])
            kgiotdriver.mergeLink("WORKSWITH",[], "Person", [("name", tefcontactname),("email", tefcontactmail)],"Company", [("name", manufacturer),("url", url)])
            kgiotdriver.mergeLink("WORKSFOR",[], "Person", [("name", tefcontactname),("email", tefcontactmail)],"Company", [("name", "Telefonica"),("url", "http://www.telefonica.com")])
        if(ob!=""):
            kgiotdriver.mergeNode("Company", [("name", ob),("url", "http://www.telefonica.com")])
            kgiotdriver.mergeLink("WORKSFOR",[], "Company", [("name", manufacturer),("url", url)],"Company", [("name", ob),("url", "http://www.telefonica.com")])
            kgiotdriver.mergeLink("ISPARTOF",[], "Company", [("name", ob),("url", "http://www.telefonica.com")],"Company", [("name", "Telefonica"),("url", "http://www.telefonica.com")])
