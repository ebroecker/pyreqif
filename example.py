#!/usr/bin/env python2

import pyreqif.reqif
import io
import os.path
from lxml import etree
import pyreqif.extractOleData

filename = "aa.xml"
basepath = os.path.dirname(filename)



def reqif2dict(myDoc):
    cols = myDoc.fields
    specs = []

    for specification in myDoc.specificationList:
        spec = []
        for req in specification:
            reqObj = myDoc.getReqById(req)
            tempReq = {}
            for col in cols:
                tempReq[col] = ""
            for col,value in myDoc.flatReq(reqObj, html=True).iteritems():
                if value is not None:
                    if "<" in value:
                        try:
                            tree = etree.parse(io.BytesIO(value))
                            root = tree.getroot()
                            for element in root.iter("object"):
                                rtfFilename = os.path.join(basepath, element.attrib["data"])
                                name = element.attrib["name"]

                                files = pyreqif.extractOleData.extractOleData(rtfFilename)
                                if len(files > 0):
                                    for key in element.attrib:
                                        del element.attrib[key]
                                    element.tag = "a"
                                    element.set("href", "mks:///item/field?fieldid=Attachments&attachmentname=" + name)
                                else:
                                    root.remove(element)

                                value = etree.tostring(root)
                        except:
                            pass
                tempReq[col] = value
            spec.append(tempReq)
        specs.append(spec)
    return specs

myDoc = pyreqif.reqif.load(filename)

specs = reqif2dict(myDoc)
#for spec in specs:
#    for req in spec:
#        print req


def printHierarch(asd, deepth=0):
        print deepth,
        print asd._identifier
        for child in asd._children:
            printHierarch(child, deepth+1)

for req in myDoc._hierarchy:
    printHierarch(req)
