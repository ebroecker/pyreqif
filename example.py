#!/usr/bin/env python2

import os.path
import pyreqif.reqif

filename = "aa.xml"
basepath = os.path.dirname(filename)


def workOnHierarch(asd, deepth = 0):
    for i in range(0, deepth):
        print "  ",
    print asd["Object ID"]
    if "attachments" in asd:
        for attachment in asd["attachments"]:
            absPath = os.path.abspath(attachment)
            print absPath
    for id,child in asd["children"].iteritems():
        workOnHierarch(child, deepth+1)


myDoc = pyreqif.reqif.load(filename)


print "Specification Requirements:"
specs = myDoc.asDict()
for spec in specs:
  for req in spec:
      print req["Object ID"]

print "Specification Requirements (hierarchical):"
hierarchSpec = myDoc.asHierarchDict()
for id,topElement in hierarchSpec[0].iteritems():
    workOnHierarch(topElement)
