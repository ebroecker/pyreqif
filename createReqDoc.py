#!/usr/bin/env python3
from __future__ import absolute_import

import pyreqif.pyreqif
import pyreqif.reqif
import pyreqif.create


xhtmlDatatypeId = "_2"
reqirementTypeId = "_3"
collumn1typeId = "_4"
collumn2typeId = "_5"

document_id = "_1"
doc_type_ref = "_doc_type_ref"

mydoc = pyreqif.create.createDocument(document_id)
pyreqif.create.addDocType(doc_type_ref, mydoc)
pyreqif.create.addDatatype(xhtmlDatatypeId,mydoc)


pyreqif.create.addReqType(reqirementTypeId, "requirement Type",collumn1typeId, "Col1", xhtmlDatatypeId, mydoc)
pyreqif.create.addReqType(reqirementTypeId,"", collumn2typeId, "Col2", xhtmlDatatypeId, mydoc)

pyreqif.create.addReq("_6", reqirementTypeId, "<div>Hallo</div>", collumn1typeId, mydoc)
pyreqif.create.addReq("_6", reqirementTypeId, "<div>Hallo2</div>", collumn2typeId, mydoc)

pyreqif.create.addReq("_7", reqirementTypeId, "<div>Hallo 3</div>", collumn1typeId, mydoc)
pyreqif.create.addReq("_7", reqirementTypeId, "<div>Hallo 4</div>", collumn2typeId, mydoc)


link_type = document_id + "link_type"
pyreqif.create.addRelation("_6","_7", mydoc, id="_self_link", type=link_type)
pyreqif.create.addSpecRelationType(link_type, mydoc, longName="selflink")

myHierarch = pyreqif.create.createHierarchHead("Reqirement Document Name", typeRef=doc_type_ref)
myHierarch.addChild(pyreqif.create.createHierarchElement("_6"))
myHierarch.addChild(pyreqif.create.createHierarchElement("_7"))

mydoc.hierarchy.append(myHierarch)

f = open("aa.reqif", "w")
pyreqif.reqif.dump(mydoc,f)
