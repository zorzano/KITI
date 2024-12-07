from flask import Flask
from flask import request
import json
import re
import logging
import sys
import spacy

sys.path.append('/home/ubuntu/repo/code')

from GordopiloDialog import GordopiloDialog

# Code to create a minibase for tests. No longer useful
#kgiotdriver.mergeNode("Organization", [("name", "Queclink")])
#kgiotdriver.mergeNode("Product", [("name", "GL300W")])
#kgiotdriver.mergeNode("Service", [("name", "Asset Tracker")])
#kgiotdriver.mergeNode("Service", [("name", "Tracking")])
#kgiotdriver.mergeLink("manufacturer",[("name", "theLink")], "Organization", [("name", "Queclink")], "Product", [("name", "GL300W")])
#kgiotdriver.mergeLink("providesService",[("name", "theLink")], "Product", [("name", "GL300W")], "Service", [("name", "Asset Tracker")])
#kgiotdriver.mergeLink("serviceType",[("name", "theLink")], "Service", [("name", "Asset Tracker")], "Service", [("name", "Tracking")])


CLEANR = re.compile('<.*?>')

app = Flask(__name__)
gp=GordopiloDialog()
# punctuation_symbols = string.punctuation

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    
    response=""
    app.logger.warning("Request received."+request.form["text"])
    jsonmsg=json.loads(request.form["text"])
    texto=jsonmsg["content"]
    texto=re.sub(CLEANR, '',texto)
    response=gp.answerText(texto)
    response=response.replace("\n", "<P>")
    return response

if __name__ == "__main__":
  app.run(ssl_context='adhoc')
