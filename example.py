#!/usr/bin/env python2
import pyreqif.pyreqif
import pyreqif.reqif

myDoc = pyreqif.reqif.load("aa.xml")
f = open("bb.xml", "w")
pyreqif.reqif.dump(myDoc, f)

#for specification in myDoc.specificationList:
#    for req in specification._list:
#        reqObj = myDoc.getReqById(req)
#        print myDoc.flatReq(reqObj)
##req = myDoc.getReqById("_640aba33-6f1e-49b3-bbf5-df798a7786bd")
##req = myDoc.getReqById("_e747a0ca-ea6f-4b8a-b20d-893759701799")
##pprint(vars(req), indent=2)
##print myDoc.flatReq(req)


def printHierarch(asd, deepth=0):
        print deepth,
        print asd._identifier
        for child in asd._children:
            printHierarch(child, deepth+1)

#for req in myDoc._hierarchy:    
#    printHierarch(req)    
