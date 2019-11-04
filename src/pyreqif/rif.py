#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import io
from builtins import *

from lxml import etree
from lxml import objectify
import json
import sys
sys.path.append('..')
import pyreqif.pyreqif
from pprint import pprint
import re

def pretty(d, indent=0):
    for key, value in d.items():
        print ('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print ('\t' * (indent+1) + str(value))
  
transLationTable = {"IDENTIFIER": "identifier",
    "COUNTRY-CODE" : "countryCode",
    "CREATION-TIME" : "creationTime",
    "TITLE" : "title",
    "COMMENT" : "comment",
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

mapReqifAttributeValue = {"default": "embeddedDoc",
                          "ATTRIBUTE-VALUE-EMBEDDED-DOCUMENT":"embeddedDoc",
                          "ATTRIBUTE-VALUE-STRING":"string",
                          "ATTRIBUTE-VALUE-XHTML":"embeddedDoc",
                          "ATTRIBUTE-VALUE-BOOLEAN":"embeddedDoc",
                          "ATTRIBUTE-VALUE-INTEGER":"embeddedDoc"}

mapReqifAttributeDefinition = {"default": "complex",
                          "ATTRIBUTE-DEFINITION-COMPLEX":"complex",
                          "ATTRIBUTE-DEFINITION-STRING":"string",
                          "ATTRIBUTE-DEFINITION-XHTML":"complex",
                          "ATTRIBUTE-DEFINITION-BOOLEAN":"complex",
                          "ATTRIBUTE-DEFINITION-INTEGER":"complex"}

mapReqifDatatypeDefinition = {"default": "document",
                          "DATATYPE-DEFINITION-DOCUMENT":"document",
                          "DATATYPE-DEFINITION-STRING":"string",
                          "DATATYPE-DEFINITION-XHTML":"document",
                          "DATATYPE-DEFINITION-BOOLEAN":"document",
                          "DATATYPE-DEFINITION-INTEGER":"document"}

transLationTableReverse = dict(map(reversed, transLationTable.items()))

mapReqifAttributeValueReversed = dict(map(reversed, mapReqifAttributeValue.items()))
mapReqifAttributeDefinitionReversed = dict(map(reversed, mapReqifAttributeDefinition.items()))
mapReqifDatatypeDefinitionReversed = dict(map(reversed, mapReqifDatatypeDefinition.items()))

def mapReqifAttributeValue2Py(elem:str):
    if elem in mapReqifAttributeValue:
        return mapReqifAttributeValue[elem]
    else:
        print ("Not supported datatype: ")
        print (elem)
    return mapReqifAttributeValue['default']

def mapPy2ReqifAttributeValue(elem:str):
    if elem in mapReqifAttributeValueReversed:
        return mapReqifAttributeValueReversed[elem]
    else:
        print ("Not supported datatype: ")
        print (elem)
    return mapReqifAttributeValueReversed['default']

def mapReqifAttributeDefinition2Py(elem:str):
    if elem in mapReqifAttributeDefinition:
        return mapReqifAttributeDefinition[elem]
    else:
        print ("Not supported attribute definition: ")
        print (elem)
    return mapReqifAttributeDefinition['default']

def mapPy2ReqifAttributeDefinition(elem:str):
    if elem in mapReqifAttributeDefinitionReversed:
        return mapReqifAttributeDefinitionReversed[elem]
    else:
        print ("Not supported attribute definition: ")
        print (elem)
    return mapReqifAttributeDefinitionReversed['default']

def mapReqifDatatypeDefinition2Py(elem:str):
    if elem in mapReqifDatatypeDefinition:
        return mapReqifDatatypeDefinition[elem]
    else:
        print ("Not supported datatype definition: ")
        print (elem)
    return mapReqifDatatypeDefinition['default']

def mapPy2ReqifDatatypeDefinition(elem:str):
    if elem in mapReqifDatatypeDefinitionReversed:
        return mapReqifDatatypeDefinitionReversed[elem]
    else:
        print ("Not supported datatype datatype: ")
        print (elem)
    return mapReqifDatatypeDefinitionReversed['default']

def py2reqif(myDict):
    MyNewDict = {}
    for pyname in myDict:
        if pyname in transLationTableReverse:
            reqifname= transLationTableReverse[pyname]
            MyNewDict[reqifname] = myDict[pyname]
        else:
            MyNewDict[pyname] = myDict[pyname]
    return MyNewDict


def reqif2py(myDict):
    MyNewDict = {}
    for reqifname in myDict:
        if reqifname in transLationTable:
            pyname = transLationTable[reqifname]
            MyNewDict[pyname] = myDict[reqifname]
        else:
            MyNewDict[reqifname] = myDict[reqifname]
    return MyNewDict
    
            
def load(f):
    inputType = "RIF"
    doc = pyreqif.pyreqif.doc()
    tree =  etree.parse(f)
    root = tree.getroot()

    ns = "{" + tree.xpath('namespace-uri(.)') + "}"
    nsp = tree.xpath('namespace-uri(.)')

    def getSubElementValuesByTitle(xmlElement, tagNameArray = []):
        defaultsSubElements = ['IDENTIFIER','LAST-CHANGE','LONG-NAME']
        # ALTERNATIVE-ID ?
        tagNameArray = list(set(defaultsSubElements + tagNameArray))
        returnDict = {}
        for tag in tagNameArray:
            if tag in xmlElement.attrib:
                returnDict[tag] = xmlElement.attrib[tag]
            else:
                temp = xmlElement.find('./' + ns +tag)
                if temp is not None:
                        returnDict[tag] = temp.text
        return returnDict

    if root.tag ==  ns + "REQ-IF":
        inputType = "REQIF"
        headerRoot = root.find('./' + ns + 'THE-HEADER/' + ns + 'REQ-IF-HEADER')
        contentRoot = root.find('./' + ns + 'CORE-CONTENT/' + ns + 'REQ-IF-CONTENT')

    else:
        headerRoot = root
        contentRoot = root

    headerTags = getSubElementValuesByTitle(headerRoot, ['AUTHOR', 'COMMENT','COUNTRY-CODE','CREATION-TIME','SOURCE-TOOL-ID','TITLE','VERSION'])
    #header missing:
    #COMMENT, REPOSITORY-ID, REQ-IF-TOOL-ID, REQ-IF-VERSION
    doc.addHeader(reqif2py(headerTags))
    


    datatypesXmlElement = contentRoot.find('./' + ns + 'DATATYPES')
    for child in datatypesXmlElement:
            if child.tag == ns + "DATATYPE-DEFINITION-DOCUMENT" or child.tag == ns + 'DATATYPE-DEFINITION-STRING' or child.tag == ns + 'DATATYPE-DEFINITION-XHTML'\
                    or child.tag == ns + 'DATATYPE-DEFINITION-BOOLEAN' or child.tag == ns + "DATATYPE-DEFINITION-INTEGER":
                    datatypeProto = getSubElementValuesByTitle(child, ['EMBEDDED'])
                    tagWithoutNamespace = re.sub('{[\S]*}', '', child.tag)
                    datatypeProto['type'] = mapReqifDatatypeDefinition2Py(tagWithoutNamespace)
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
                        tempDict = reqif2py(tempDict)
                        values[tempDict['identifier']] = tempDict
                    datatypeProto['values'] = values   
                    doc.addDatatype(reqif2py(datatypeProto))
            else:
                    # missing: 
                    #DATATYPE-DEFINITION-BOOLEAN
                    #DATATYPE-DEFINITION-DATE
                    #DATATYPE-DEFINITION-INTEGER
                    #DATATYPE-DEFINITION-REAL
                    print ("Not supported datatype: ",)
                    print (child.tag)

    
    specTypesXmlElement = contentRoot.find('./' + ns + 'SPEC-TYPES')
    for child in specTypesXmlElement:
        if child.tag == ns + "SPEC-TYPE" or child.tag == ns + "SPEC-OBJECT-TYPE":
            specType = getSubElementValuesByTitle(child, ['DESC'])
#            specType = getSubElementValuesByTitle(child)
            attributesXml = child.find('./' + ns + "SPEC-ATTRIBUTES")
            if attributesXml is not None:
                for attribute in attributesXml:
                    if attribute.tag == ns +"ATTRIBUTE-DEFINITION-COMPLEX" or attribute.tag == ns +"ATTRIBUTE-DEFINITION-STRING" or attribute.tag == ns +"ATTRIBUTE-DEFINITION-XHTML"\
                            or attribute.tag == ns + "ATTRIBUTE-DEFINITION-BOOLEAN" or attribute.tag == ns + "ATTRIBUTE-DEFINITION-INTEGER" :
                        specAttribType = getSubElementValuesByTitle(attribute)
                        tagWithoutNamespace = re.sub('{[\S]*}', '', attribute.tag)
                        specAttribType["type"] = mapReqifAttributeDefinition2Py(tagWithoutNamespace)
                        typeTag = attribute.find('./' + ns + 'TYPE')
                        if typeTag is not None:
                            reference = typeTag.getchildren()[0]
#                            reference = typeTag.find('./' + ns + 'DATATYPE-DEFINITION-DOCUMENT-REF')
                            reference = typeTag.getchildren()[0]
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
                        defaultValue = attribute.find('./' + ns + 'DEFAULT-VALUE/' + ns + 'ATTRIBUTE-VALUE-ENUMERATION/' + ns + 'VALUES/'+ ns + 'ENUM-VALUE-REF')
                        if defaultValue is not None:
                            specAttribType['defaultValue'] = defaultValue.text

                    else:
                        print ("Not supported Attribute: ",)
                        print (attribute.tag)
                        
                    specAttribType = reqif2py(specAttribType)
                    specType[specAttribType['identifier']] = specAttribType

#                    specType[specAttribType['identifier']].pop('identifier')
            doc.addRequirementType(reqif2py(specType))

    def remove_namespaces(thedoc):
        # http://wiki.tei-c.org/index.php/Remove-Namespaces.xsl
        xslt = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:output method="xml" indent="no"/>
    
        <xsl:template match="/|comment()|processing-instruction()">
            <xsl:copy>
              <xsl:apply-templates/>
            </xsl:copy>
        </xsl:template>
    
        <xsl:template match="*">
            <xsl:element name="{local-name()}">
              <xsl:apply-templates select="@*|node()"/>
            </xsl:element>
        </xsl:template>
    
        <xsl:template match="@*">
            <xsl:attribute name="{local-name()}">
              <xsl:value-of select="."/>
            </xsl:attribute>
        </xsl:template>
        </xsl:stylesheet>
        '''

#        xslt_doc = etree.parse(io.BytesIO(xslt))
        xslt_doc = etree.parse(io.BytesIO(bytes(xslt, "utf8")))
        transform = etree.XSLT(xslt_doc)
        ret = transform(thedoc)
        return ret

    specObjectsXmlElement = contentRoot.find('./' + ns + 'SPEC-OBJECTS')
    for requirementXml in specObjectsXmlElement:
        requirement=None

        if requirementXml.tag == ns + "SPEC-OBJECT":
            requirement = getSubElementValuesByTitle(requirementXml)
            
            typeRefXml = requirementXml.find('./' + ns + 'TYPE/' +ns + 'SPEC-TYPE-REF')
            if typeRefXml is None:
                typeRefXml = requirementXml.find('./' + ns + 'TYPE/' +ns + 'SPEC-OBJECT-TYPE-REF')
            if typeRefXml is not None:
                requirement["typeRef"] = typeRefXml.text
                
            valuesXml = requirementXml.find('./' +ns + 'VALUES')
            values = {}
            for valueXml in valuesXml:
                value = getSubElementValuesByTitle(valueXml)
                #TODO : Support other types
                if valueXml.tag == ns + 'ATTRIBUTE-VALUE-EMBEDDED-DOCUMENT' or valueXml.tag == ns + 'ATTRIBUTE-VALUE-STRING' or valueXml.tag == ns + 'ATTRIBUTE-VALUE-XHTML'\
                        or valueXml.tag == ns + 'ATTRIBUTE-VALUE-BOOLEAN' or valueXml.tag == ns + 'ATTRIBUTE-VALUE-INTEGER':
                    attributeRefXml = valueXml.find('./' + ns + 'DEFINITION').getchildren()[0]
                    value['attributeRef'] = attributeRefXml.text
                    if 'THE-VALUE' in valueXml.attrib:
                        value["content"] = valueXml.attrib['THE-VALUE']
                    else:
                        contentXml = valueXml.find('./' + ns + 'XHTML-CONTENT/{http://automotive-his.de/200706/rif-xhtml}div')
                        if contentXml is None:
                            contentXml = valueXml.find("./" + ns + 'THE-VALUE/{http://www.w3.org/1999/xhtml}div')

                        value["content"] = etree.tostring(remove_namespaces(contentXml))

#                    value["content"] = "".join(contentXml.itertext())

                    tagWithoutNamespace = re.sub('{[\S]*}', '', valueXml.tag)
                    value["type"] = mapReqifAttributeValue2Py(tagWithoutNamespace)
                    
                elif valueXml.tag == ns + 'ATTRIBUTE-VALUE-ENUMERATION':
                    value["type"] = "enum"
                    attributeRefXml = valueXml.find('./' + ns + 'DEFINITION/' + ns + 'ATTRIBUTE-DEFINITION-ENUMERATION-REF')
                    value['attributeRef'] = attributeRefXml.text
                    contentXml = valueXml.findall('./' + ns + 'VALUES/' + ns + 'ENUM-VALUE-REF')
                    if contentXml is not None:
                        value["contentRef"] = []
                        for content in contentXml:
                            value["contentRef"].append(content.text)
                        a=1
                    else:
                        value["contentRef"] = None
                else:
                    print ("valueType not supported yet:",)
                    print (valueXml.tag[len(ns):])

                values[value['attributeRef']] = reqif2py(value)
            requirement["values"] = values
        else:
            print ("Unknown spec object tag:",)
            print (requirementXml.tag)

        if requirement != None:   
            doc.addRequirement(reqif2py(requirement))


    specGroupsXml = contentRoot.find('./' + ns + 'SPEC-GROUPS')
    if specGroupsXml is not None:
        for specGroupXml in specGroupsXml:
            if specGroupXml.tag == ns + "SPEC-GROUP":
                specification = getSubElementValuesByTitle(specGroupXml, ['DESC'])
                spec = pyreqif.pyreqif.specification(**reqif2py(specification))

                specObjectsXml = specGroupXml.find('./' + ns + 'SPEC-OBJECTS')
                for specObjectRef in specObjectsXml:
                    spec.addReq(specObjectRef.text)
                doc.addSpecification(spec)


    def getHierarchy(hierarchyEle, inputType):
        hierarchyDict = getSubElementValuesByTitle(hierarchyEle)
        typeRef = hierarchyEle.find('./' + ns + 'TYPE/' + ns + 'SPEC-TYPE-REF')
        if typeRef is not None:
            hierarchyDict["typeRef"] = typeRef.text
            
        objectRef = hierarchyEle.find('./' + ns + 'OBJECT/' + ns + 'SPEC-OBJECT-REF')
        if objectRef is not None:
            hierarchyDict["objectRef"] = objectRef.text
        hierarchy = pyreqif.pyreqif.hierarchy(**reqif2py(hierarchyDict))

        children = hierarchyEle.find('./' + ns + 'CHILDREN')
        if children is not None:
            for child in children:
                hierarchy.addChild(getHierarchy(child, inputType))
        return hierarchy

        
    if inputType == "RIF":
        hierarchyRoots = contentRoot.find('./' + ns + 'SPEC-HIERARCHY-ROOTS')
    elif inputType == "REQIF":
        hierarchyRoots = contentRoot.find('./' + ns + 'SPECIFICATIONS')


    for hierarchyRoot in hierarchyRoots:
        doc.hierarchy.append(getHierarchy(hierarchyRoot, inputType))

    # SPEC-HIERARCHY
    relations = {}
    specRelsXml = contentRoot.find('./' + ns + 'SPEC-RELATIONS')
    if specRelsXml is not None:
        for specRelXml in specRelsXml:
            if specRelXml.tag == ns + "SPEC-RELATION":
                relation = getSubElementValuesByTitle(specRelXml)
                typeRef = specRelXml.find('./' + ns + 'TYPE')
                if typeRef is not None:
                    relation["typeRef"] = typeRef.getchildren()[0].text
                sourceRef = specRelXml.find('./' + ns + 'SOURCE/' + ns + 'SPEC-OBJECT-REF')
                if sourceRef is not None:
                    relation["sourceRef"] = sourceRef.text
                targetRef = specRelXml.find('./' + ns + 'TARGET/' + ns + 'SPEC-OBJECT-REF')
                if targetRef is not None:
                    relation["targetRef"] = targetRef.text

                doc.addRelation(reqif2py(relation))
    return doc

attributesForElements = ["IDENTIFIER", "LAST-CHANGE", "LONG-NAME", "MAX-LENGTH", "MAX", "MIN", "ACCURACY", "OTHER-CONTENT", "KEY", "MULTI-VALUED"]
notUsedAttributes = ["COUNTRY-CODE","EMBEDDED", "AUTHOR", "VERSION", "DESC", "contentRef"]

def createSubElements(parent, myDict):
    for key in myDict:
        if key in attributesForElements or key in notUsedAttributes:
            continue
        sn = etree.SubElement(parent, key)
        if myDict[key] is not None:
            sn.text = myDict[key]
        else:
            sn.text = 'None'
                
def createSubElement(parent, tag, text=None, attributes=None):
    sn = etree.SubElement(parent, tag)
    if text is not None:
        sn.text = text
    if attributes is not None:
        for attributeName in attributesForElements:
            if attributeName in attributes and attributes[attributeName] is not None and attributeName not in notUsedAttributes:
                sn.attrib[attributeName] = attributes[attributeName]
    return sn

def dump(doc, f):
    xsi = 'http://www.w3.org/2001/XMLSchema-instance'
    arVersion = "1"
    root = etree.Element(
        'REQ-IF',
        nsmap={
            None: 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd',
            'xhtml': "http://www.w3.org/1999/xhtml",
            'id': "http://pror.org/presentation/id",
            "configuration": "http://eclipse.org/rmf/pror/toolextensions/1.0",
            })

  
    #
    # HEADER
    #
    theheader = createSubElement(root, "THE-HEADER")
    headerXML = createSubElement(theheader, "REQ-IF-HEADER", attributes = py2reqif(doc.header))
    tempDict = py2reqif(doc.header)
    tempDict["REQ-IF-TOOL-ID"] = tempDict["SOURCE-TOOL-ID"]
    tempDict["REQ-IF-VERSION"] = "1.0"
    tempDict["SOURCE-TOOL-ID"] = "pyreqif"
    for tagName in ["COMMENT", "CREATION-TIME", "REQ-IF-TOOL-ID", "REQ-IF-VERSION", "SOURCE-TOOL-ID", "TITLE"]:
        createSubElement(headerXML, tagName, tempDict[tagName])
    coreContent = createSubElement(root, "CORE-CONTENT")
    reqIfContent = createSubElement(coreContent, "REQ-IF-CONTENT")

    #
    # DATATYPES
    #
    datatypesXml = createSubElement(reqIfContent, "DATATYPES")
    for datatype in doc.datatypeList:
        if datatype.mytype == "document":
            myDict = py2reqif(datatype.toDict())
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-XHTML", attributes=myDict)
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
        if datatype.mytype == "string":
            myDict = py2reqif(datatype.toDict())
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-STRING", attributes=myDict)
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
        if datatype.mytype == "enum":
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-ENUMERATION", attributes=py2reqif(datatype.toDict()))
            myDict = py2reqif(datatype.toDict())
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
            specifiedValuesXml = createSubElement(datatypeXml, "SPECIFIED-VALUES")
            for value,label in datatype.valueTable.items():
                valuesXml = createSubElement(specifiedValuesXml , "ENUM-VALUE", attributes=py2reqif(label) )
                #createSubElement(valuesXml, "IDENTIFIER", value)
                for element,content in py2reqif(label).items():
                    if element == "properites":
                        props = createSubElement(valuesXml, "PROPERTIES")
                        createSubElement(props, "EMBEDDED-VALUE", attributes=py2reqif(content))
                    elif element not in attributesForElements:
                        createSubElement(valuesXml, element, content)

    
    #
    # SPEC-TYPES
    #
    specTypes = createSubElement(reqIfContent, "SPEC-TYPES")
    for reqType in doc.requirementTypeList:
        specType = createSubElement(specTypes, "SPEC-OBJECT-TYPE", attributes=py2reqif(reqType.toDict()))
        createSubElements(specType,py2reqif(reqType.toDict()))
        
        if len(reqType.myTypes) > 0:
            attributesXml = createSubElement(specType,"SPEC-ATTRIBUTES")

            for mytype,ref in reqType.myTypes.items():
                attribDict = py2reqif(ref.toDict())
                if "TYPE" in attribDict and attribDict["TYPE"] == "enum":
                    attribDict.pop("TYPE")
                    attribDict["MULTI-VALUED"] = "false"
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-ENUMERATION", attributes=attribDict)
                    for value,label in attribDict.items():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-ENUMERATION-REF",label)
                        elif value not in attributesForElements:
                            createSubElement(enumXml,value,label)


                if "TYPE" in attribDict and attribDict["TYPE"] == "complex":
#                    attribDict.pop("TYPE")
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-XHTML", attributes=attribDict)
                    attribDict.pop("TYPE")
                    for value,label in attribDict.items():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-XHTML-REF",label)
                        elif value not in attributesForElements and value not in notUsedAttributes:
                            createSubElement(enumXml,value,label)

                if "TYPE" in attribDict and attribDict["TYPE"] == "string":
#                    attribDict.pop("TYPE")
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-STRING", attributes=attribDict)
                    attribDict.pop("TYPE")
                    for value,label in attribDict.items():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-STRING-REF",label)
                        elif value not in attributesForElements and value not in notUsedAttributes:
                            createSubElement(enumXml,value,label)

    #
    # SPEC-OBJECTS
    #
    specsXml = createSubElement(reqIfContent, "SPEC-OBJECTS")
    
    for req in doc.requirementList:
        specXml = createSubElement(specsXml , "SPEC-OBJECT", attributes=py2reqif(req.toDict()))
        requirementDict = py2reqif(req.toDict())
        for value,label in requirementDict.items():
            if value == "VALUES":
                valuesXml = createSubElement(specXml, "VALUES")
                for value in label:
                    tempDict = py2reqif(value.toDict())
                    if "LONG-NAME" in tempDict:
                        tempDict.pop("LONG-NAME")
                    if "LAST-CHANGE" in tempDict:
                        tempDict.pop("LAST-CHANGE")
                    if "IDENTIFIER" in tempDict:
                            tempDict.pop("IDENTIFIER")
                    if value.mytype == "enum":
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-ENUMERATION", attributes=tempDict)
                        valuesValuesXml = createSubElement(valueXml, "VALUES")
                        valuesDefinitionsXml = createSubElement(valueXml, "DEFINITION")
                    else:
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-XHTML", attributes=tempDict)
                        valuesDefinitionsXml = createSubElement(valueXml, "DEFINITION")
                    for val,lab in py2reqif(value.toDict()).items():
                        if val == "contentRef" and lab is not None:
                            createSubElement(valuesValuesXml, "ENUM-VALUE-REF",lab[0])
                        elif val == "attributeRef":
                            if value.mytype == "enum":
                                createSubElement(valuesDefinitionsXml, "ATTRIBUTE-DEFINITION-ENUMERATION-REF", lab)
                            elif value.mytype == "embeddedDoc":
                                createSubElement(valuesDefinitionsXml, "ATTRIBUTE-DEFINITION-XHTML-REF", lab)
                            elif value.mytype == "string":
                                createSubElement(valuesDefinitionsXml, "ATTRIBUTE-DEFINITION-STRING-REF", lab)
                            else:
                                print ("Unknown Type " + value.mytype)
                            
                        elif val == "TYPE":
                            pass
                        elif val == "CONTENT":
                            if lab is not None:
                                if '<' in str(lab):
                                    labtree = etree.parse(io.BytesIO(lab))
                                    labroot = labtree.getroot()
                                    for el in labroot.iter():
                                        el.tag = '{http://www.w3.org/1999/xhtml}' + el.tag
                                    contentXml = createSubElement(valueXml, "THE-VALUE")
                                    contentXml.append(labroot)
                                else:
                                    createSubElement(valueXml, "THE-VALUE", lab)
                        elif val not in attributesForElements and val not in notUsedAttributes:
                            createSubElement(valueXml, val, lab)
            elif value == "typeRef":
                typeXml = createSubElement(specXml, "TYPE")
                createSubElement(typeXml, "SPEC-OBJECT-TYPE-REF", label)
            elif value not in attributesForElements:
                createSubElement(specXml , value , label)
            

    #
    # SPEC-RELATIONS
    #
    specsRelXml = createSubElement(reqIfContent, "SPEC-RELATIONS")
    for relation in doc.relations:
        specsRel = createSubElement(specsRelXml  , "SPEC-RELATION")
        for value,label in py2reqif(relation).items():
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

    #
    # SPEC-GROUPS
    #
    #specGroupsXml = createSubElement(reqIfContent, "SPEC-GROUPS")
    #for specification in doc.specificationList:
    #    specGroupXml = createSubElement(specGroupsXml, "SPEC-GROUP")
    #    for value,label in py2reqif(specification.toDict()).iteritems():
    #        createSubElement(specGroupXml,value,label)
    #    specObjectsXml = createSubElement(specGroupXml,"SPEC-OBJECTS")
    #    for req in specification:
    #        createSubElement(specObjectsXml ,"SPEC-OBJECT-REF", req)


    #
    # SPEC-HIERARCHY-ROOTS
    #
    def createChildHirachy(parentXmlTag, childObject):
        childrenXml = createSubElement(parentXmlTag, "CHILDREN")
        hierarchXml = createSubElement(childrenXml, "SPEC-HIERARCHY", attributes=py2reqif(childObject.toDict()))
        for value,label in py2reqif(childObject.toDict()).items():
            if value == "objectRef":
                objectXml = createSubElement(hierarchXml , "OBJECT")
                createSubElement(objectXml, "SPEC-OBJECT-REF", label)
            elif value not in attributesForElements:
                if label is not None:
                    createSubElement(hierarchXml , value, label)

        for child in childObject.children:
            createChildHirachy(hierarchXml, child)
    
    
    specHierarchRootsXml = createSubElement(reqIfContent, "SPECIFICATIONS")
    #SPEC-HIERARCHY-ROOT
    for hierarch in doc.hierarchy:
        specHierarchRootXml = createSubElement(specHierarchRootsXml, "SPECIFICATION", attributes=py2reqif(hierarch.toDict()))
        for value,label in py2reqif(hierarch.toDict()).items():
            if value == "typeRef":
                typeXml = createSubElement(specHierarchRootXml, "TYPE")
                createSubElement(typeXml, "SPECIFICATION-TYPE-REF", label)
            elif value not in attributesForElements:
                createSubElement(specHierarchRootXml, value, label)

        
        for child in hierarch.children:
            createChildHirachy(specHierarchRootXml, child)
    

    f.write(etree.tostring(root, pretty_print=True, xml_declaration=True))

