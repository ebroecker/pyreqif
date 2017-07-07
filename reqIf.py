#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import json
import sys
import pyreqif.pyreqif
from pprint import pprint
            

def pretty(d, indent=0):
    for key, value in d.iteritems():
        print ('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print ('\t' * (indent+1) + str(value))
  
transLationTable = {"IDENTIFIER": "identifier",
    "COUNTRY-CODE" : "countryCode",
    "CREATION-TIME" : "creationTime",
    "TITLE" : "title",
    "AUTHOR" : "author",
    "LONG-NAME" : "longName",
    "VERSION" : "version",
    "SOURCE-TOOL-ID" : "sourceToolId",
    "LAST-CHANGE" : "lastChange",
    "EMBEDDED":"embedded",
    "TYPE":"type",
    "VALUES":"values",
    "CONTENT-REF":"contentref",
    "CONTENT":"content",
    "DESC":"desc"}

transLationTableReverse = dict(map(reversed, transLationTable.items()))

def py2reqif(myDict):
    for pyname in myDict:
        if pyname in transLationTableReverse:
            reqifname= transLationTableReverse[pyname]
            myDict[reqifname] =  myDict.pop(pyname)
    return myDict


def reqif2py(myDict):
    for reqifname in myDict:
        if reqifname in transLationTable:
            pyname = transLationTable[reqifname]
            myDict[pyname] =  myDict.pop(reqifname)
    return myDict
    
            
def load(f):
    doc = pyreqif.pyreqif.doc()
    tree =  etree.parse(f)
    root = tree.getroot()

    ns = "{" + tree.xpath('namespace-uri(.)') + "}"
    nsp = tree.xpath('namespace-uri(.)')

    def getSubElementValuesByTitle(xmlElement, tagNameArray = []):
        defaultsSubElements = ['IDENTIFIER','LAST-CHANGE','LONG-NAME']
        tagNameArray = list(set(defaultsSubElements + tagNameArray))
        returnDict = {}
        for tag in tagNameArray:
            temp = xmlElement.find('./' + ns +tag)
            if temp is not None:
                    returnDict[tag] = temp.text
#            else:
#                    returnDict[tag] = None
        return returnDict

    headerTags = getSubElementValuesByTitle(root, ['AUTHOR','COUNTRY-CODE','CREATION-TIME','SOURCE-TOOL-ID','TITLE','VERSION'])

    doc.addHeader(reqif2py(headerTags))
    

    datatypesXmlElement = root.find('./' + ns + 'DATATYPES')
    for child in datatypesXmlElement:
            if child.tag == ns + "DATATYPE-DEFINITION-DOCUMENT":
                    datatypeProto = getSubElementValuesByTitle(child, ['EMBEDDED'])
                    datatypeProto['type'] = "document"
                    doc.addDatatype(reqif2py(datatypeProto))

            elif child.tag == ns + "DATATYPE-DEFINITION-ENUMERATION":
                    datatypeProto = getSubElementValuesByTitle(child, ['EMBEDDED'])				
                    datatypeProto['type'] = "enum"
                    specifiedValues = child.find('./' + ns + "SPECIFIED-VALUES")
                    values = {}
                    for valElement in specifiedValues:
                        tempDict = getSubElementValuesByTitle(valElement)
                        properties = valElement.find('./' + ns + "PROPERTIES")
                        embeddedValue = properties.find('./' + ns + "EMBEDDED-VALUE")
                        tempDict['properites']  = reqif2py(getSubElementValuesByTitle(embeddedValue, ['KEY','OTHER-CONTENT']) )
                        values[tempDict['identifier']] = reqif2py(tempDict) 
                    datatypeProto['values'] = values   
                    doc.addDatatype(reqif2py(datatypeProto))
            else:
                    print ("Not supported datatype: ",)
                    print (child.tag)

    
    specTypesXmlElement = root.find('./' + ns + 'SPEC-TYPES')
    for child in specTypesXmlElement:
        if child.tag == ns + "SPEC-TYPE":
            specType = getSubElementValuesByTitle(child, ['DESC'])
#            specType = getSubElementValuesByTitle(child)
            attributesXml = child.find('./' + ns + "SPEC-ATTRIBUTES")
            if attributesXml is not None:
                for attribute in attributesXml:
                    if attribute.tag == ns +"ATTRIBUTE-DEFINITION-COMPLEX":
                        specAttribType = getSubElementValuesByTitle(attribute)
                        specAttribType["type"] = "complex" 
                        typeTag = attribute.find('./' + ns + 'TYPE')
                        if typeTag is not None:
                            reference = typeTag.find('./' + ns + 'DATATYPE-DEFINITION-DOCUMENT-REF')
                            if doc.datatypeById(reference.text):
                                specAttribType['typeRef'] = reference.text
                            else:
                                print ("BEEP unknown Datatype") 
                    elif attribute.tag == ns + "ATTRIBUTE-DEFINITION-ENUMERATION":
                        specAttribType = getSubElementValuesByTitle(attribute)
                        specAttribType["type"] = "enum" 
                        typeRef = attribute.find('./' + ns + 'TYPE/' + ns + 'DATATYPE-DEFINITION-ENUMERATION-REF')
                        if typeRef is not None:
                            specAttribType['typeRef'] = typeRef.text
                        
                    else:
                        print ("Not supported Attribute: ",)
                        print (attribute.tag)
                    specType[specAttribType['identifier']] = reqif2py(specAttribType)
#                    specType[specAttribType['identifier']].pop('identifier')
            doc.addRequirementType(reqif2py(specType))


    specObjectsXmlElement = root.find('./' + ns + 'SPEC-OBJECTS')
    for requirementXml in specObjectsXmlElement:
        if requirementXml.tag == ns + "SPEC-OBJECT":
            requirement = getSubElementValuesByTitle(requirementXml)
            
            typeRefXml = requirementXml.find('./' + ns + 'TYPE/' +ns + 'SPEC-TYPE-REF')
            if typeRefXml is not None:
                requirement["typeRef"] = typeRefXml.text
                
            valuesXml = requirementXml.find('./' +ns + 'VALUES')
            values = {}
            for valueXml in valuesXml:
                value = getSubElementValuesByTitle(valueXml)
                if valueXml.tag == ns + 'ATTRIBUTE-VALUE-EMBEDDED-DOCUMENT':
                    attributeRefXml = valueXml.find('./' + ns + 'DEFINITION/' + ns + 'ATTRIBUTE-DEFINITION-COMPLEX-REF')
                    value['attributeRef'] = attributeRefXml.text
                    contentXml = valueXml.find('./' + ns + 'XHTML-CONTENT/{http://automotive-his.de/200706/rif-xhtml}div')
                    value["content"] = contentXml.text
                    value["type"] = "embeddedDoc"
                    
                elif valueXml.tag == ns + 'ATTRIBUTE-VALUE-ENUMERATION':
                    value["type"] = "enum"
                    attributeRefXml = valueXml.find('./' + ns + 'DEFINITION/' + ns + 'ATTRIBUTE-DEFINITION-ENUMERATION-REF')
                    value['attributeRef'] = attributeRefXml.text
                    contentXml = valueXml.find('./' + ns + 'VALUES/' + ns + 'ENUM-VALUE-REF')                
                    value["contentRef"] = contentXml.text
                else:
                    print ("not supported yet:",)
                    print (valueXml.tag[len(ns):])

                values[value['identifier']] = reqif2py(value)
            requirement["values"] = values
        else:
            print ("Unknown spec object tag:",)
            print (requirementXml.tag)
        doc.addRequirement(reqif2py(requirement))


#    for requirement in doc._requirementList._list:
#        for value in requirement._values:
#            print value._content

    specGroupsXml = root.find('./' + ns + 'SPEC-GROUPS')
    for specGroupXml in specGroupsXml:
        if specGroupXml.tag == ns + "SPEC-GROUP":
            specification = getSubElementValuesByTitle(specGroupXml, ['DESC'])
            spec = pyreqif.pyreqif.specification(**reqif2py(specification))
            
            specObjectsXml = specGroupXml.find('./' + ns + 'SPEC-OBJECTS')
            for specObjectRef in specObjectsXml:
                spec.addReq(specObjectRef.text)
            doc.addSpecification(spec)


    def getHierarchy(hierarchyEle):
        hierarchyDict = getSubElementValuesByTitle(hierarchyEle)
        typeRef = hierarchyEle.find('./' + ns + 'TYPE/' + ns + 'SPEC-TYPE-REF')
        if typeRef is not None:
            hierarchyDict["typeRef"] = typeRef
            
        objectRef = hierarchyEle.find('./' + ns + 'OBJECT/' + ns + 'SPEC-OBJECT-REF')
        if objectRef is not None:
            hierarchyDict["objectRef"] = objectRef
        hierarchy = pyreqif.pyreqif.hierarchy(**reqif2py(hierarchyDict))

        children = hierarchyEle.find('./' + ns + 'CHILDREN')
        if children is not None:
            for child in children:
                hierarchy.addChild(getHierarchy(child))
        return hierarchy

        
    hierarchyRoots = root.find('./' + ns + 'SPEC-HIERARCHY-ROOTS')
    for hierarchyRoot in hierarchyRoots:
        doc._hierarchy.append(getHierarchy(hierarchyRoot))

    relations = {}
    specRelsXml = root.find('./' + ns + 'SPEC-RELATIONS')
    for specRelXml in specRelsXml:
        if specRelXml.tag == ns + "SPEC-RELATION":
            relation = getSubElementValuesByTitle(specRelXml)
            typeRef = specRelXml.find('./' + ns + 'TYPE/' + ns + 'SPEC-TYPE-REF')
            if typeRef is not None:
                relation["typeRef"] = typeRef.text
            sourceRef = specRelXml.find('./' + ns + 'SOURCE/' + ns + 'SPEC-OBJECT-REF')
            if typeRef is not None:
                relation["sourceRef"] = sourceRef.text 
            targetRef = specRelXml.find('./' + ns + 'TARGET/' + ns + 'SPEC-OBJECT-REF')
            if targetRef is not None:
                relation["targetRef"] = targetRef.text

            doc.addRelation(reqif2py(relation))
    return doc


def createSubElements(parent, myDict):
    for key in myDict:
        sn = etree.SubElement(parent, key)
        if myDict[key] is not None:
            sn.text = myDict[key]
        else:
            sn.text = 'None'
                
def createSubElement(parent, tag, text=None):
    sn = etree.SubElement(parent, tag)
    if text is not None:
        sn.text = text
    return sn

def dump(doc, f):
    xsi = 'http://www.w3.org/2001/XMLSchema-instance'
    arVersion = "1"
    root = etree.Element(
        'RIF',
        nsmap={
            None: 'http://automotive-his.de/200706/rif',
            'rif-xhtml' : 'http://automotive-his.de/200706/rif-xhtml',
            'xsi': xsi
            })

    root.attrib['{{{pre}}}schemaLocation'.format(
        pre=xsi)] = 'http://automotive-his.de/200706/rif rif.xsd http://automotive-his.de/200706/rif-xhtml rif-xhtml.xsd'
    
  
    #
    # HEADER
    #

    createSubElements(root, py2reqif(doc._header.toDict())) 


    #
    # DATATYPES
    #
    datatypesXml = createSubElement(root, "DATATYPES")
    for datatype in doc._datatypeList._list:
        if datatype._type == "document":
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-DOCUMENT")
            myDict = py2reqif(datatype.toDict())
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
        if datatype._type == "enum":
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-ENUMERATION")
            myDict = py2reqif(datatype.toDict())
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
            specifiedValuesXml = createSubElement(datatypeXml, "SPECIFIED-VALUES")
            for value,label in datatype._valueTable.iteritems():
                valuesXml = createSubElement(specifiedValuesXml , "ENUM-VALUE")
                createSubElement(valuesXml, "IDENTIFIER", value)
                for element,content in py2reqif(label).iteritems():
                    if element == "properites":
                        props = createSubElement(valuesXml, "PROPERTIES")
                        for tag,val in content.iteritems():
                            createSubElement(props, tag,val)
                    else:
                        createSubElement(valuesXml, element, content)

    
    #
    # SPEC-TYPES
    #
    specTypes = createSubElement(root, "SPEC-TYPES")
    for reqType in doc._requirementTypeList._list:
        specType = createSubElement(specTypes, "SPEC-TYPE")
        specTypeDict = py2reqif(reqType.toDict())
        for value,label in specTypeDict.iteritems():
            createSubElement(specType,value,label)
        
        if len(reqType._myTypes) > 0:
            attributesXml = createSubElement(specType,"SPEC-ATTRIBUTES")

            for mytype,ref in reqType._myTypes.iteritems():
                attribDict = py2reqif(ref.toDict())
                if "TYPE" in attribDict and attribDict["TYPE"] == "enum":
                    attribDict.pop("TYPE")
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-ENUMERATION")
                    for value,label in attribDict.iteritems():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-ENUMERATION-REF",label)
                        else:
                            createSubElement(enumXml,value,label)


                if "TYPE" in attribDict and attribDict["TYPE"] == "complex":
#                    attribDict.pop("TYPE")
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-COMPLEX")
                    for value,label in attribDict.iteritems():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-DOCUMENT-REF",label)
                        else:
                            createSubElement(enumXml,value,label)

    #
    # SPEC-TYPES
    #
    specsXml = createSubElement(root, "SPEC-OBJECTS")
    
    for req in doc._requirementList._list:
        specXml = createSubElement(specsXml , "SPEC-OBJECT")
        requirementDict = py2reqif(req.toDict())
        for value,label in requirementDict.iteritems():
            if value == "VALUES":
                valuesXml = createSubElement(specXml, "VALUES")
                for value in label:
                    if value._type == "enum":
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-ENUMERATION")
                    else:
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-EMBEDDED-DOCUMENT")
                    for val,lab in py2reqif(value.toDict()).iteritems():
                        if val == "contentRef":
                            createSubElement(valuesXml, "ENUM-VALUE-REF",lab)
                        elif val == "attributeRef":
                            if value._type == "enum":
                                createSubElement(valuesXml, "ATTRIBUTE-DEFINITION-ENUMERATION-REF", lab)
                            elif value._type == "embeddedDoc":
                                createSubElement(valuesXml, "ATTRIBUTE-DEFINITION-COMPLEX-REF", lab)
                            else:
                                print "Unknown Type " + value._type
                            
                        elif val == "TYPE":
                            pass
                        elif val == "CONTENT":
                            if lab is not None:
                                createSubElement(valueXml, "XHTML-CONTENT", lab)
                        else:
                            createSubElement(valueXml, val, lab)
            elif value == "typeRef":
                typeXml = createSubElement(specXml, "TYPE")
                createSubElement(typeXml, "SPEC-TYPE-REF", label)
            else:
                createSubElement(specXml , value , label)
            

    #
    # SPEC-RELATIONS
    #
    specsRelXml = createSubElement(root, "SPEC-RELATIONS")
    for relation in doc._relations._list:
        specsRel = createSubElement(specsRelXml  , "SPEC-RELATION")
        for value,label in py2reqif(relation).iteritems():
            if value == "typeRef":
                typeXml = createSubElement(specsRel , "TYPE")
                createSubElement(typeXml , "SPEC-TYPE-REF", label)
            elif value == "sourceRef":
                sourceXml = createSubElement(specsRel , "SOURCE")
                createSubElement(sourceXml, "SPEC-OBJECT-REF", label)
            elif value == "targetRef":
                targetXml = createSubElement(specsRel , "TARGET")
                createSubElement(targetXml, "SPEC-OBJECT-REF", label)
            else:
                createSubElement(specsRel , value, label)

    f.write(etree.tostring(root, pretty_print=True, xml_declaration=True))

    #
    # SPEC-HIERARCHY-ROOTS
    #
    specsRelXml = createSubElement(root, "SPEC-HIERARCHY-ROOTS")
    for hierarch in doc._hierarchy:
        print hierarch._children[0]._objectref
    

myDoc = load("aa.xml")
f = open("bb.xml", "w")
dump(myDoc, f)
exit(0)
#specification = myDoc._specificationList._list[0]
#for req in specification._list:
#    reqObj = myDoc.getReqById(req)
#    print myDoc.flatReq(reqObj)

##req = myDoc.getReqById("_640aba33-6f1e-49b3-bbf5-df798a7786bd")
##req = myDoc.getReqById("_e747a0ca-ea6f-4b8a-b20d-893759701799")
##pprint(vars(req), indent=2)
##print myDoc.flatReq(req)


def printHierarch(asd, deepth=0):
        print deepth,
        print asd._identifier
        for child in asd._children:
            printHierarch(child, deepth+1)

for req in myDoc._hierarchy:    
    printHierarch(req)    

