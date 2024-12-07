import sys
from KGIoTDriverNeo4j import KGIoTDriverNeo4j
from KGIoTSynonims import KGIoTSynonims
import os
import csv
import time
import argparse
from KGIoTOpenAI import KGIoTOpenAI

clientOpenAI = KGIoTOpenAI()


def loadZorzoFormatFirstTwoLines(f1, f2, kgiotdriver):
    print(f1, "\n")
    print(f2, "\n")
    father=""
    firstService=0
    for i in range (1,len(f2)):
        #print(str(i)+"#"+f1[i]+"#"+father+"#"+f2[i]+"\n")
        if f1[i]!="":
            father=f1[i]
            if firstService==0:
                firstService=i
            print("Creando servicio de nivel superior "+father)
            kgiotdriver.mergeNode("Service:Searchable", [("name", father)])
            vector=clientOpenAI.get_embedding(father)
            kgiotdriver.addEmbeddings("Searchable", "name", father, "embedding", vector)

        if f2[i]=="Platform":
            return f2, firstService, i
        if f2[i] != "" and father!="":
            print(f2[i]+"->"+father)
            kgiotdriver.mergeNode("Service:Searchable", [("name", f2[i])])
            kgiotdriver.mergeLink("serviceType",[], "Service", [("name", f2[i])],  "Service", [("name", father)])
            vector=clientOpenAI.get_embedding(f2[i])
            kgiotdriver.addEmbeddings("Searchable", "name", f2[i], "embedding", vector)

    return f2, firstService, i
    
def loadZorzoFormat(args, kgiotsynonims, kgiotdriver):
    with open(args.filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        headers, firstService, maxServices=loadZorzoFormatFirstTwoLines(reader.__next__(), reader.__next__(), kgiotdriver)
        for fields in reader:
            # print(fields)
            manufacturer=fields[0]
            model="Generic "+manufacturer+" product"
            url=fields[2]
            mainActivity=fields[3] #Temporarily not used
            geo=fields[4]
            platform=fields[153] #Temporarily not used
            tier=fields[154] #Temporarily not used
            contactname=fields[155] 
            tefcontactname=fields[156] 
            referenceProject=fields[157] #Temporarily not used
            if(manufacturer==""):
                continue
            kgiotdriver.mergeNode("Organization:Searchable", [("name", manufacturer),("url", url)])
            kgiotdriver.addEmbeddings("Searchable", "name", manufacturer, "embedding", clientOpenAI.get_embedding(manufacturer))
            
            kgiotdriver.mergeNode("Product:Searchable", [("name", model)])
            kgiotdriver.addEmbeddings("Searchable", "name", model, "embedding", clientOpenAI.get_embedding(model))
            
            kgiotdriver.mergeLink("manufacturer",[], "Organization", [("name", manufacturer),("url", url)], "Product", [("name", model)])
            if(geo!=""):
                kgiotdriver.mergeNode("Country:Searchable", [("name", geo)])
                kgiotdriver.addEmbeddings("Searchable", "name", geo, "embedding", clientOpenAI.get_embedding(geo))
                kgiotdriver.mergeLink("nationality",[], "Organization", [("name", manufacturer),("url", url)], "Country", [("name", geo)])
            if(contactname!=""):
                kgiotdriver.mergeNode("Person:Searchable", [("name", contactname)])
                kgiotdriver.addEmbeddings("Searchable", "name", contactname, "embedding", clientOpenAI.get_embedding(contactname))
                kgiotdriver.mergeLink("WorksFor",[], "Person", [("name", contactname)],"Organization", [("name", manufacturer),("url", url)])
            if(tefcontactname!=""):
                kgiotdriver.mergeNode("Person:Searchable", [("name", tefcontactname)])
                kgiotdriver.addEmbeddings("Searchable", "name", tefcontactname, "embedding", clientOpenAI.get_embedding(tefcontactname))
                kgiotdriver.mergeLink("knowsAbout",[], "Person", [("name", tefcontactname)],"Organization", [("name", manufacturer),("url", url)])
                kgiotdriver.mergeLink("WorksFor",[], "Person", [("name", tefcontactname)],"Organization", [("name", "Telefonica"),("url", "http://www.telefonica.com")])
            print("Inserted:"+manufacturer+":"+url+","+model+","+geo+","+contactname+","+tefcontactname)
            for i in range (firstService,maxServices):
                if fields[i] != "" and headers[i] != "" :
                    kgiotdriver.mergeLink("providesService",[], "Product", [("name", model)],  "Service", [("name", headers[i])])
                    print(manufacturer+" provides "+headers[i]+" service")
            
            
            
def loadSalvaFormat(args, kgiotsynonims, kgiotdriver):
    with open(args.filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        reader.__next__()
        for fields in reader:
            #time.sleep(2);
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
                #model="Generic "+manufacturer+" product"
                continue # This product comes from the Zorzano CVS. Better get it from there
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
            kgiotdriver.mergeNode("Organization:Searchable", [("name", manufacturer),("url", url)])
            kgiotdriver.addEmbeddings("Searchable", "name", manufacturer, "embedding", clientOpenAI.get_embedding(manufacturer))

            if(geo!=""):
                kgiotdriver.mergeNode("Country:Searchable", [("name", geo)])
                kgiotdriver.addEmbeddings("Searchable", "name", geo, "embedding", clientOpenAI.get_embedding(geo))
                kgiotdriver.mergeLink("nationality",[], "Organization", [("name", manufacturer),("url", url)], "Country", [("name", geo)])
            if(model!=""):
                kgiotdriver.mergeNode("Product:Searchable", [("name", model)])
                kgiotdriver.addEmbeddings("Searchable", "name", model, "embedding", clientOpenAI.get_embedding(model))
                kgiotdriver.mergeLink("manufacturer",[], "Organization", [("name", manufacturer),("url", url)], "Product", [("name", model)])
            if(devicemode!=""):
                kgiotdriver.mergeNode("Service:Searchable", [("name", devicemode)])
                kgiotdriver.addEmbeddings("Searchable", "name", devicemode, "embedding", clientOpenAI.get_embedding(devicemode))
                kgiotdriver.mergeLink("providesService",[], "Product", [("name", model)],  "Service", [("name", devicemode)])
            if(devicetype!=""):
                kgiotdriver.mergeNode("Service:Searchable", [("name", devicetype)])
                kgiotdriver.addEmbeddings("Searchable", "name", devicetype, "embedding", clientOpenAI.get_embedding(devicetype))
            if(deviceusecase!=""):
                for x in deviceusecase.split(" "):
                    kgiotdriver.mergeNode("Service:Searchable", [("name", x)])
                    kgiotdriver.addEmbeddings("Searchable", "name", x, "embedding", clientOpenAI.get_embedding(x))
        #            kgiotdriver.mergeLink("USEDIN",[], "Product", [("name", model)],  "UseCase", [("name", deviceusecase)])
                    kgiotdriver.mergeLink("providesService",[], "Product", [("name", model)],  "Service", [("name", x)])
                    if(devicetype!=""):
                        kgiotdriver.mergeLink("serviceType",[], "Service", [("name", x)],  "Service", [("name", devicetype)])
            if(contactname!="" or contactmail!=""):
                kgiotdriver.mergeNode("Person:Searchable", [("name", contactname),("email", contactmail)])
                kgiotdriver.addEmbeddings("Searchable", "name", contactname, "embedding", clientOpenAI.get_embedding(contactname))
                kgiotdriver.mergeLink("WorksFor",[], "Person", [("name", contactname),("email", contactmail)],"Organization", [("name", manufacturer),("url", url)])
            if(tefcontactname!="" or tefcontactmail!=""):
                kgiotdriver.mergeNode("Person:Searchable", [("name", tefcontactname),("email", tefcontactmail)])
                kgiotdriver.addEmbeddings("Searchable", "name", tefcontactname, "embedding", clientOpenAI.get_embedding(tefcontactname))
                kgiotdriver.mergeLink("knowsAbout",[], "Person", [("name", tefcontactname),("email", tefcontactmail)],"Organization", [("name", manufacturer),("url", url)])
                kgiotdriver.mergeLink("WorksFor",[], "Person", [("name", tefcontactname),("email", tefcontactmail)],"Organization", [("name", "Telefonica"),("url", "http://www.telefonica.com")])
            if(ob!=""):
                kgiotdriver.mergeNode("Organization:Searchable", [("name", ob),("url", "http://www.telefonica.com")])
                kgiotdriver.addEmbeddings("Searchable", "name", ob, "embedding", clientOpenAI.get_embedding(ob))
                kgiotdriver.mergeLink("WorksFor",[], "Organization", [("name", manufacturer),("url", url)],"Organization", [("name", ob),("url", "http://www.telefonica.com")])
                kgiotdriver.mergeLink("ISPARTOF",[], "Organization", [("name", ob),("url", "http://www.telefonica.com")],"Organization", [("name", "Telefonica"),("url", "http://www.telefonica.com")])


parser = argparse.ArgumentParser(
                    prog='KG IoT Loader',
                    description='Load KITI base from CSV files',
                    epilog='Knowledge and Things')
                    
parser.add_argument('filename', help="Name of CSV file to load")
parser.add_argument('-d', dest="dictionary", help="Dictionary file")
parser.add_argument('-k', dest="kill", help="Empty database", action="store_true")
parser.add_argument('-f', dest="format", help="File format. s for Salva, z for Zorzano", choices=["s", "z"], default="s")

args = parser.parse_args()

kgiotdriver = KGIoTDriverNeo4j("bolt://localhost:7687", "neo4j", os.getenv('PWDNEO4J'))
kgiotdriver.mergeNode("Organization", [("name", "Telefonica"),("url", "http://www.telefonica.com")])

if args.kill :
    kgiotdriver.nukeBase()

if(args.dictionary != None):
    kgiotsynonims=KGIoTSynonims(args.dictionary)
else:
    kgiotsynonims=KGIoTSynonims("")

if args.format=="s" :
    loadSalvaFormat(args, kgiotsynonims, kgiotdriver)
elif args.format=="z" :
    loadZorzoFormat(args, kgiotsynonims, kgiotdriver)