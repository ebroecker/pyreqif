#!/usr/bin/env python
from __future__ import print_function
import os.path
import pyreqif.reqif
import pyreqif.rif
import sys



def workOnHierarch(asd, deepth = 0):
    for i in range(0, deepth):
        print ("  ", end="")
    print (asd["ReqIF.ChapterName"], end="")
    print (asd["ReqIF.Text"])
    if "attachments" in asd:
        for attachment in asd["attachments"]:
            absPath = os.path.abspath(attachment)
            print (absPath)
    for id,child in asd["children"].items():
        workOnHierarch(child, deepth+1)


if len(sys.argv) < 2:
    print("Usage {} some_reqif_file.reqif\n".format(sys.argv[0]))
    print("prints Text and Chapter Information and also exports a RIF file")
    sys.exit()

filename = sys.argv[1]
basepath = os.path.dirname(filename)
myDoc = pyreqif.reqif.load(filename)
f = open(os.path.splitext(filename)[0] + "_pyreqif_export.xml", "wb")
pyreqif.rif.dump(myDoc,f)


print ("Specification Requirements:")
specs = myDoc.asDict()
for spec in specs:
  for req in spec:
      print (req["ReqIF.ChapterName"], end="")
      print (req["ReqIF.Text"])


print ("Specification Requirements (hierarchical):")
hierarchSpec = myDoc.asHierarchDict()
for id,topElement in hierarchSpec[0].items():
    workOnHierarch(topElement)
