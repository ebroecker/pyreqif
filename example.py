#!/usr/bin/env python2

import os.path
import pyreqif.reqif
import pyreqif.rif


filename = "/home/edu/Downloads/ReqIFStudio/workspace/reqifTest/Spec.reqif"
basepath = os.path.dirname(filename)


def workOnHierarch(asd, deepth = 0):
    for i in range(0, deepth):
        print "  ",
    print asd["ReqIF.ForeignID"],
    print asd["ReqIF.Text"]
    if "attachments" in asd:
        for attachment in asd["attachments"]:
            absPath = os.path.abspath(attachment)
            print absPath
    for id,child in asd["children"].iteritems():
        workOnHierarch(child, deepth+1)


myDoc = pyreqif.reqif.load(filename)
f = open("bb.xml", "wb")
pyreqif.rif.dump(myDoc,f)


print "Specification Requirements:"
specs = myDoc.asDict()
for spec in specs:
  for req in spec:
      print req["ReqIF.ForeignID"],
      print req["ReqIF.Text"]


print "Specification Requirements (hierarchical):"
hierarchSpec = myDoc.asHierarchDict()
for id,topElement in hierarchSpec[0].iteritems():
    workOnHierarch(topElement)
