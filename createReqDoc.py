#!/usr/bin/env python2
from __future__ import absolute_import

import pyreqif.pyreqif
import pyreqif.reqif
import datetime
import uuid

def createDocument(id, title="title", comment="created by pyreqif"):
    mydoc = pyreqif.pyreqif.doc()
    mydoc.addHeader({"identifier":id,"sourceToolId":"pyreqif", "comment": comment, "title":title, "creationTime": str(datetime.date.today())})
    return mydoc

def addDatatype(id, mydoc, type="document", lastChange=datetime.datetime.today().isoformat(), longName="xhtml"):
    mydoc.addDatatype({"identifier":id, "type":type, "lastChange": lastChange, "longName":longName})

def addReqType(specObjId, specObjLongName, specAttribId, collumName, typeRef, mydoc, type="complex", lastChange=datetime.datetime.today().isoformat()):
    mydoc.addRequirementType({"identifier":specObjId,  "longName": specObjLongName, "lastChange": lastChange, specAttribId : {"identifier":specAttribId, "typeRef":typeRef,"type":type, "lastChange": lastChange, "longName": collumName}})

def addReq(id, specType,  content, reqTypeRef, mydoc, lastChange=datetime.datetime.today().isoformat()):
    mydoc.addRequirement({"typeRef" : specType, "identifier" : id, "lastChange": lastChange, "values" : {id : {"content" :content, "attributeRef":reqTypeRef, "type": "embeddedDoc"}}})

def addRelation(sourceId, targetId, mydoc):
    relation = {}
    relation ["sourceRef"] = sourceId
    relation["targetRef"] = targetId

    mydoc.addRelation(pyreqif.rif.reqif2py(relation))

def creatUUID(itemId = None):
    if itemId is not None:
        return str(uuid.uuid1(int(itemId)))
    else:
        return str(uuid.uuid1())

def createHierarchHead(longName, id=None, lastChange=datetime.datetime.today().isoformat()):
    if id is None:
        id = creatUUID()
    return pyreqif.pyreqif.hierarchy(**pyreqif.rif.reqif2py({"identifier": id, "longName": longName, "lastChange": lastChange}))

def createHierarchElement(reqid, id=None, lastChange=datetime.datetime.today().isoformat()):
    if id is None:
        id = creatUUID()
    return pyreqif.pyreqif.hierarchy(**pyreqif.rif.reqif2py({"identifier": id, "lastChange": lastChange, "objectRef": reqid}))

xhtmlDatatypeId = "2"
reqirementTypeId = "3"
collumn1typeId = "4"
collumn2typeId = "5"

mydoc = createDocument("1")

addDatatype(xhtmlDatatypeId,mydoc)


addReqType(reqirementTypeId, "requirement Type",collumn1typeId, "Col1", xhtmlDatatypeId, mydoc)
addReqType(reqirementTypeId,"", collumn2typeId, "Col2", xhtmlDatatypeId, mydoc)

addReq("6", reqirementTypeId, "Hallo", collumn1typeId, mydoc)
addReq("6", reqirementTypeId, "Hallo2", collumn2typeId, mydoc)


addRelation("6","12", mydoc)

myHierarch = createHierarchHead("Reqirement Document Name")
myHierarch.addChild(createHierarchElement("6"))
myHierarch.addChild(createHierarchElement("7"))

mydoc.hierarchy.append(myHierarch)

f = open("aa.reqif", "w")
pyreqif.reqif.dump(mydoc,f)
