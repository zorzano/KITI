from flask import Flask
from flask import request
from collections import defaultdict
import json
import re
import logging
import string
import sys
import os
import spacy
from openai import OpenAI
import datetime
from KGIoTDriverNeo4j import KGIoTDriverNeo4j

logger = logging.getLogger(__name__)

def singleton(cls, *args, **kw):
     instances = {}
     def _singleton(*args, **kw):
        if cls not in instances:
             instances[cls] = cls(*args, **kw)
        return instances[cls]
     return _singleton

@singleton
class GordopiloDialog(object):
     def __init__(self):
         self.client = OpenAI()
         self.nlp = spacy.load("es_core_news_sm")
         sys.path.append('/home/ubuntu/repo/code')
         self.kgiotdriver = KGIoTDriverNeo4j("bolt://localhost:7687", "neo4j", os.getenv('PWDNEO4J'))
         logger.info("GordopiloDialog Initialized")
         

     def close(self):
        self.kgiotdriver.close()
        
     def get_embedding(self, text, model="text-embedding-ada-002"):
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input = [text], model=model).data[0].embedding
   
     def chatgptify(self, text, explain, question=""):

        voiceRoles=[#"Eres un sargento brutal con un gran conocimiento de telecomunicaciones, gritando a un recluta.", 
                    #"Eres Yoda, con un gran conocimiento de telecomunicaciones.", 
                    #"Eres un poeta escribiendo en verso.",
                    #"Eres un un siervo humilde y miserable de un cuento oriental, con un gran conocimiento de telecomunicaciones.",
                    #"Eres un pijo",
                    #"Eres un ingeniero de telecomunicaciones.",
                    "normal"
                    ]
        if explain :
            response = self.client.chat.completions.create(
                #model="gpt-3.5-turbo-1106",
                model="chatgpt-4o-latest",
                response_format={ "type": "text" },
                messages=[
                    {"role": "system", "content": voiceRoles[datetime.datetime.today().day % len(voiceRoles)]},
                    {"role": "user", "content": "Tienes que responder a la siguiente pregunta:"+question+"\n Para ello debes usar solo los siguientes datos que son la ficha de un elemento de una base de datos de fabricantes de dispositivos IoT. Por favor, genera un texto que de toda la información de una manera explicada. No hagas suposiciones que no estén aquí indicadas ni añadas otra información.\n"+text}
                ])
        else:
            response = self.client.chat.completions.create(
                model="chatgpt-4o-latest",
                response_format={ "type": "text" },
                messages=[
                    {"role": "system", "content": voiceRoles[datetime.datetime.today().day % len(voiceRoles)]},
                    {"role": "user", "content": text}
                ])
        return(response.choices[0].message.content)

     def formatNodeResult(self, theEntity, res):
            # Identify node type
            for i in res[0][0].labels:
                nodeType=str(i)
            response="Name: "+theEntity+"\n Type:"+nodeType+".\n" 
            if "text" in res[0][0]:
              response+=res[0][0]["text"]+"\n"
        
            # Define relationsSet as an empty dictionary
            relationsSet=defaultdict(list)
            
            
            for item in res:
                # POR AQUI. RELLENAR VALOR
                # item[0, el sujeto, 1, el link, 2, el objeto]["name"]
                # item[0].labels[0]?
                #response+=str(item[0]["name"])+"-"+"-"+str(item[1].type)+"-"+str(item[2]["name"])
                # But, if the object flies alone, it has no link nor object
                if item[1]:
                    relationsSet[str(item[1].type)].append(str(item[2]["name"]))
            
            # Print result of the kind "Tiene 5 pais: Albania, Alemania, España, Rumania, Francia,.
            for key in relationsSet:
                response+=key+":"
                for target in relationsSet[key]:
                    response+=target+","
                response+=".\n"
            
            if nodeType=="Organization":
               #app.logger.info("["+theEntity+"] is an Organization. Looking for delivered services.") 
               services=self.kgiotdriver.searchLinkChain("Organization", [("name", theEntity)], [("manufacturer",1),("serviceType|providesService", 1)], "Service")
               response+="Services offered:"
               for item in services :
                   response+=item[0]["name"]+","
               response+="\n."
               
            return response

         
     def answerText(self, texto):                            
         
        #return "Gordopilo está en parada de mantenimiento"
        
        response=""
        
        # Gordopilo is too chatty, and people sometimes discuss on the same thread
        if ("?" not in texto) and ("ordopilo" not in texto):
            return response
        #texto=texto.split("ordopilo:", 1)[-1].strip()
        texto=texto.strip("?")
        logger.warning(texto)
        doc=self.nlp(texto)
        
        if "[off]" in texto:
            return ""
                
        logger.info("Analyzing:["+texto+"]in base embeddings")
        vector=self.get_embedding(texto)
        res=self.kgiotdriver.searchByEmbeddings("allembeddings", 5, vector, "name")
        if len(res)>=1:
           logger.info("Located through embeddings "+str(len(res))+" elements")
           for i in range(len(res)):
               logger.info("Located through embeddings Node <<"+res[i][0]["name"]+">> with score "+str(res[i][1]))
               if res[i][1] > 0.9 :
                  #possibleServiceName=res[0][0]["name"]
                  res2=self.kgiotdriver.readNodeAndLinked("%", [("name", res[i][0]["name"])], partial=False) #% means any type
                  response+=self.formatNodeResult(res[i][0]["name"], res2)

        if response== "" :
            logger.warning("Response NULL")
            response="[*]"+self.chatgptify(texto, True)
        else :
            logger.warning("Response: "+response)
            response=self.chatgptify(response, True, texto)
        
        return response



       # for token in doc:
            # #app.logger.info(token.text+"-"+token.pos_)

            # if token.pos_ == "NOUN" or token.pos_ == "PROPN":
              # responseitem=""
              # logger.info("Analyzing:["+token.text+"]")
              
              
              # # Check through embeddings if I have a better name
              # possibleServiceName=token.text
              # logger.info("Analyzing:["+possibleServiceName+"] in Services embeddings")
              # vector=self.get_embedding(possibleServiceName)
              # res=self.kgiotdriver.searchByEmbeddings("service-embeddings", 1, vector, "name")
              # if len(res)>=1:
                  # logger.info("Located through embeddings "+str(len(res))+" elements")
                  # for i in range(len(res)):
                    # logger.info("Located through embeddings Service <<"+res[i][0]["name"]+">> with score "+str(res[i][1]))
                  # if res[0][1] > 0.93 :
                     # possibleServiceName=res[0][0]["name"]
                       
              # # Check if it is a Service
              # res=self.kgiotdriver.searchLinkChain("Service", [("name", possibleServiceName)], [("serviceType|providesService", 2), ("manufacturer",2)], "Organization")
              # count=0
              # logger.info("Database response:"+str(res))
              # for item in res:
                  # responseitem+=item[0]["name"]+","
                  # count+=1
              # if count > 0:
                  # response=response+"Conocemos "+str(count)+" proveedores del servicio "+possibleServiceName+": "+responseitem[:-1]+"\n"
                  
              # # Check for any other thing, but only if it is not a service
              # if response == "":
                # #app.logger.info("Analyzing:["+token.text+"] in readNodeAndLinked. Type:%, name:"+token.text)
                # res=self.kgiotdriver.readNodeAndLinked("%", [("name", token.text)], partial=False) #% means any type
                # if len(res) >0:
                    # response+=self.formatNodeResult(token.text, res)
                    
         # # If I find nothing yet, try with the wiki
        # #if response == "":
        # if True:
            # subject=re.search("se hace para (.*)\?", texto)
            # if not subject:
                # subject=re.search("proceso de (.*)\?", texto)
            # if not subject:
                # subject=re.search("proceso para (.*)\?", texto)
            # if not subject:
                # subject=re.search("u.l es (.*)\?", texto)
            # if not subject:
                # subject=re.search("mo se hace para (.*)\?", texto)
            # if not subject:
                # subject=re.search("mo se hace (.*)\?", texto)
            # if not subject:
                # subject=re.search("mo se hacen (.*)\?", texto)            
            # if not subject:
                # subject=re.search("rocedimiento para (.*)\?", texto)   
            # if not subject:
                # subject=re.search("manera de (.*)\?", texto)      
            # if not subject:
                # subject=re.search("nde est.n l.s (.*)\?", texto) 
            # if not subject:
                # subject=re.search("nde est. .. (.*)\?", texto) 
            # if not subject:
                # subject=re.search("en caso de (.*)\?", texto) 
            # if not subject:
                # subject=re.search("mo (.*)\?", texto)
            # if subject:
                # logger.info("Analyzing:["+subject.group(1).strip()+"] in Processes")
                # vector=self.get_embedding(texto)
                # res=self.kgiotdriver.searchByEmbeddings("process-embeddings", 1, vector, "name")
                # if len(res)>=1:
                    # logger.info("Located through embeddings "+str(len(res))+" elements")
                    # logger.info("Located through embeddings Process <<"+res[0][0]["name"]+">> with score "+str(res[0][1]))
                    # # res=kgiotdriver.readNode("Process", [("name", subject.group(1).strip())], partial=False) #% means any type
                    # if res[0][1] > 0.9 :
                       # response+="Process name:"+res[0][0]["name"]+"\n Process description:"+res[0][0]["text"]
