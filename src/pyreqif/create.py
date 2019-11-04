#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import pyreqif.pyreqif
import pyreqif.rif
import uuid

def createDocument(id, title="title", comment="created by pyreqif"):
    mydoc = pyreqif.pyreqif.doc()
    mydoc.addHeader({"identifier":id,"sourceToolId":"pyreqif", "comment": comment, "title":title, "creationTime": str(datetime.date.today())})
    return mydoc

def addDatatype(id, mydoc, type="document", lastChange=datetime.datetime.today().isoformat(), longName="xhtml", values = None):
    if values is None:
        mydoc.addDatatype({"identifier":id, "type":type, "lastChange": lastChange, "longName":longName})
    else:
        mydoc.addDatatype({"identifier":id, "type":type, "lastChange": lastChange, "longName":longName, "values" : values})


def addSpecRelationType(id, mydoc, longName, lastChange=datetime.datetime.today().isoformat()):
    mydoc.addSpecRelationType({"identifier":id, "longName" : longName, "lastChange": lastChange})

def addSpecRelationGroup(mydoc, id, sourceDoc, targetDoc,  longName, longNameOfType, specRelationRefs, lastChange=datetime.datetime.today().isoformat()):
    mydoc.addSpecRelationGroup({"identifier":id, "longName": longName, "sourceDoc" : sourceDoc,
                                "targetDoc": targetDoc, "lastChange": lastChange,
                                "longNameOfType": longNameOfType, "specRelationRefs" : specRelationRefs})

def addReqType(specObjId, specObjLongName, specAttribId, collumName, typeRef, mydoc, type="complex", lastChange=datetime.datetime.today().isoformat()):
    mydoc.addRequirementType({"identifier":specObjId,  "longName": specObjLongName, "lastChange": lastChange, specAttribId : {"identifier":specAttribId, "typeRef":typeRef,"type":type, "lastChange": lastChange, "longName": collumName}})

def addReq(id, specType,  content, reqTypeRef, mydoc, lastChange=datetime.datetime.today().isoformat()):
    mydoc.addRequirement({"typeRef" : specType, "identifier" : id, "lastChange": lastChange, "values" : {id : {"content" :content, "attributeRef":reqTypeRef, "type": "embeddedDoc"}}})

def addRelation(sourceId, targetId, mydoc, id, type, longName=None, lastChange=datetime.datetime.today().isoformat()):
    relation = {"identifier" : id, "lastChange": lastChange}
    relation ["sourceRef"] = sourceId
    relation["targetRef"] = targetId
    relation["typeRef"] = type
    if longName is not None:
        relation["longName"] = longName
    mydoc.addRelation(relation)

def creatUUID(itemId = None):
    if itemId is not None:
        return "_" + str(uuid.uuid1(int(itemId)))
    else:
        return "_" + str(uuid.uuid1())

def createHierarchHead(longName, id=None, lastChange=datetime.datetime.today().isoformat()):
    if id is None:
        id = creatUUID()
    return pyreqif.pyreqif.hierarchy(**pyreqif.rif.reqif2py({"identifier": id, "longName": longName, "lastChange": lastChange}))

def createHierarchElement(reqid, id=None, lastChange=datetime.datetime.today().isoformat()):
    if id is None:
        id = creatUUID()
    return pyreqif.pyreqif.hierarchy(**pyreqif.rif.reqif2py({"identifier": id, "lastChange": lastChange, "objectRef": reqid}))

