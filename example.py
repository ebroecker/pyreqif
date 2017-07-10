#!/usr/bin/env python2

import pyreqif.reqif
import io
import os.path
from lxml import etree
import pyreqif.extractOleData

filename = "aa.xml"
basepath = os.path.dirname(filename)


myDoc = pyreqif.reqif.load(filename)
for specification in myDoc.specificationList:
    row = 0
    cols = []
    for req in specification:
        reqObj = myDoc.getReqById(req)
        for col in myDoc.flatReq(reqObj, html=True):
            if col  not in cols:
                cols.append(col)

    colNr = 0        
    for req in specification:
        row += 1
        reqObj = myDoc.getReqById(req)
        for col,value in myDoc.flatReq(reqObj, html=True).iteritems():
            if value is not None:
                if "<" in value:
                    try:
                        tree = etree.parse(io.BytesIO(value))
                        root = tree.getroot()
                        for element in root.iter("object"):
                            print value

                            rtfFilename = os.path.join(basepath, element.attrib["data"])
                            files = extractOleData(rtfFilename)
#                            for file in files:
#                                print os.path.splitext(file)[1]

                            name = element.attrib["name"]

                            for key in element.attrib:
                                del element.attrib[key]
#                            root.remove(element)
                            element.tag = "a"
                            element.set("href", "mks:///item/field?fieldid=Attachments&attachmentname=" + name)

                            value = etree.tostring(root)

                            print value
                            print "\n\n"

                    except:
                        pass

#def printHierarch(asd, deepth=0):
#        print deepth,
#        print asd._identifier
#        for child in asd._children:
#            printHierarch(child, deepth+1)

#for req in myDoc._hierarchy:    
#    printHierarch(req)    
