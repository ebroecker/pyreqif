#!/usr/bin/env python2

import pyreqif.reqif
import io
import os.path
from lxml import etree
import pyreqif.extractOleData

filename = "../DDA_Appl_Grundfunktion_0024e5ba.xml"
basepath = os.path.dirname(filename)

def req2dict(req, cols):
    reqObj = myDoc.getReqById(req)
    tempReq = {}
    for col in cols:
        tempReq[col] = ""
    for col, value in myDoc.flatReq(reqObj, html=True).iteritems():
        if value is not None:
            if "<" in value:
#                try:
                    tree = etree.parse(io.BytesIO(value))
                    root = tree.getroot()
                    for element in root.iter("object"):
                        rtfFilename = os.path.join(basepath, element.attrib["data"])
                        name = element.attrib["name"]

                        files = pyreqif.extractOleData.extractOleData(rtfFilename)
                        if len(files) > 0:
                            for key in element.attrib:
                                del element.attrib[key]
                            element.tag = "a"
                            element.set("href", "mks:///item/field?fieldid=Attachments&attachmentname=" + name)

                            element.append(etree.XML("<img src='mks:///item/field?fieldid=Attachmentsa.png'/>"))
                        else:
                            root.remove(element)

                        value = etree.tostring(root)
#                except:
                    pass
        tempReq[col] = value
        tempReq["reqifId"] = req
    return tempReq

def reqif2dict(myDoc):
    cols = myDoc.fields
    specs = []

    for specification in myDoc.specificationList:
        spec = []
        for req in specification:
            tempReq = req2dict(req, cols)
            spec.append(tempReq)
        specs.append(spec)
    return specs


def hierarchDict(element, cols):
    retDict = {}
    for child in element.children:
        retDict[child._objectref] = req2dict(child._objectref, cols)
        retDict[child._objectref]["children"] = hierarchDict(child, cols)
    return retDict

def reqif2hierarchDict(myDoc):
    cols = myDoc.fields
    spec = []

    for child in myDoc.hierarchy:
        spec.append(hierarchDict(child, cols))
    return spec

def printHierarch(asd, deepth= 0):
    for i in range(0, deepth):
        print "  ",
    print asd["Object Text"],

    if len(asd["children"]) > 0:
        print "CHILDREN"
    else:
        print ""
    for id,child in asd["children"].iteritems():
        printHierarch(child, deepth +1)


myDoc = pyreqif.reqif.load(filename)
specs = reqif2dict(myDoc)
hierarchSpec = reqif2hierarchDict(myDoc)
for id,topElement in hierarchSpec[0].iteritems():
    printHierarch(topElement)

#for spec in specs:
#  for req in spec:
#      print req["reqifId"]

#def printHierarch(asd, deepth=0):
#        print deepth,
#        for child in asd._children:
#            print "Parent: " + asd._identifier + " child " + child._identifier
#        for child in asd._children:
#            printHierarch(child, deepth+1)

#for req in myDoc.hierarchy:
#    printHierarch(req)
