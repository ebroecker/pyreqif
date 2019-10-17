#!/usr/bin/env python
from __future__ import print_function
import os.path
import pyreqif.reqif
import pyreqif.rif
import sys

#
# command line parsing
#
if len(sys.argv) < 2:
    print("Usage {} some_reqif_file.reqif\n".format(sys.argv[0]))
    print("prints Text and Chapter Information and also exports a RIF file")
    sys.exit()

filename = sys.argv[1]

#
# calculate base path of reqif-document for extracting attachments
#
basepath = os.path.dirname(filename)


#
# load reqif/rif file
#
myDoc = pyreqif.reqif.load(filename)


#
#  example rif export:
#
f = open(os.path.splitext(filename)[0] + "_pyreqif_export.xml", "wb")
pyreqif.rif.dump(myDoc,f)

#
# example ascii console 'flat' dump, without hierarchie
#
print ("Specification Requirements (flat):")
specs = myDoc.asDict()
for spec in specs:
  for req in spec:
      print (req["ReqIF.ChapterName"], end="")
      print (req["ReqIF.Text"])



#
# example ascii console 'hierarchy' dump, using hierach_iterator
#
print ("Specification Requirements (hierarchical):")
cols = myDoc.fields
for spec in specs:
    for child in myDoc.hierarchy:
        for item, depth in  myDoc.hierach_iterator(child, cols):
            #
            # iterator gives every element and its hierachical depth
            # do some ascii printing of Text and Chapter
            print("  " * depth, end="")
            print (item["ReqIF.ChapterName"], end="")
            print (item["ReqIF.Text"])

            #
            # print some info, if attachement is found
            #
            if "attachments" in item:
                for attachment in item["attachments"]:
                    absPath = os.path.abspath(attachment)
                    print (absPath)

