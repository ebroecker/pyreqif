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
                        defaultValue = attribute.find('./' + ns + 'DEFAULT-VALUE/' + ns + 'ATTRIBUTE-VALUE-ENUMERATION/' + ns + 'VALUES/'+ ns + 'ENUM-VALUE-REF')
                        if defaultValue is not None:
                            specAttribType['defaultValue'] = defaultValue.text

                    else:
                        print ("Not supported Attribute: ",)
                        print (attribute.tag)
                    specType[specAttribType['identifier']] = reqif2py(specAttribType)
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

        xslt_doc = etree.parse(io.BytesIO(xslt))
        transform = etree.XSLT(xslt_doc)
        ret = transform(thedoc)
        return ret

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

#                    value["content"] = "".join(contentXml.itertext())
                    value["content"] = etree.tostring(remove_namespaces(contentXml))
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
            hierarchyDict["typeRef"] = typeRef.text
            
        objectRef = hierarchyEle.find('./' + ns + 'OBJECT/' + ns + 'SPEC-OBJECT-REF')
        if objectRef is not None:
            hierarchyDict["objectRef"] = objectRef.text
        hierarchy = pyreqif.pyreqif.hierarchy(**reqif2py(hierarchyDict))

        children = hierarchyEle.find('./' + ns + 'CHILDREN')
        if children is not None:
            for child in children:
                hierarchy.addChild(getHierarchy(child))
        return hierarchy

        
    hierarchyRoots = root.find('./' + ns + 'SPEC-HIERARCHY-ROOTS')
    for hierarchyRoot in hierarchyRoots:
        doc.hierarchy.append(getHierarchy(hierarchyRoot))

    relations = {}
    specRelsXml = root.find('./' + ns + 'SPEC-RELATIONS')
    if specRelsXml is not None:
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

    createSubElements(root, py2reqif(doc.header)) 


    #
    # DATATYPES
    #
    datatypesXml = createSubElement(root, "DATATYPES")
    for datatype in doc.datatypeList:
        if datatype.mytype == "document":
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-DOCUMENT")
            myDict = py2reqif(datatype.toDict())
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
        if datatype.mytype == "enum":
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-ENUMERATION")
            myDict = py2reqif(datatype.toDict())
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
            specifiedValuesXml = createSubElement(datatypeXml, "SPECIFIED-VALUES")
            for value,label in datatype.valueTable.iteritems():
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
    for reqType in doc.requirementTypeList:
        specType = createSubElement(specTypes, "SPEC-TYPE")
        specTypeDict = py2reqif(reqType.toDict())
        for value,label in specTypeDict.iteritems():
            createSubElement(specType,value,label)
        
        if len(reqType.myTypes) > 0:
            attributesXml = createSubElement(specType,"SPEC-ATTRIBUTES")

            for mytype,ref in reqType.myTypes.iteritems():
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
    # SPEC-OBJECTS
    #
    specsXml = createSubElement(root, "SPEC-OBJECTS")
    
    for req in doc.requirementList:
        specXml = createSubElement(specsXml , "SPEC-OBJECT")
        requirementDict = py2reqif(req.toDict())
        for value,label in requirementDict.iteritems():
            if value == "VALUES":
                valuesXml = createSubElement(specXml, "VALUES")
                for value in label:
                    if value.mytype == "enum":
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-ENUMERATION")
                    else:
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-EMBEDDED-DOCUMENT")
                    for val,lab in py2reqif(value.toDict()).iteritems():
                        if val == "contentRef":
                            createSubElement(valuesXml, "ENUM-VALUE-REF",lab)
                        elif val == "attributeRef":
                            if value.mytype == "enum":
                                createSubElement(valuesXml, "ATTRIBUTE-DEFINITION-ENUMERATION-REF", lab)
                            elif value.mytype == "embeddedDoc":
                                createSubElement(valuesXml, "ATTRIBUTE-DEFINITION-COMPLEX-REF", lab)
                            else:
                                print "Unknown Type " + value.mytype
                            
                        elif val == "TYPE":
                            pass
                        elif val == "CONTENT":
                            if lab is not None:
                                if "<" in lab:
                                    labtree = etree.parse(io.BytesIO(lab))
                                    labroot = labtree.getroot()
                                    for el in labroot.iter():
                                        el.tag = '{http://automotive-his.de/200706/rif-xhtml}' + el.tag
                                    contentXml = createSubElement(valueXml, "XHTML-CONTENT")
                                    contentXml.append(labroot)
                                else:
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
    for relation in doc.relations:
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

    #
    # SPEC-GROUPS
    #
    specGroupsXml = createSubElement(root, "SPEC-GROUPS")
    for specification in doc.specificationList:
        specGroupXml = createSubElement(specGroupsXml, "SPEC-GROUP")
        for value,label in py2reqif(specification.toDict()).iteritems():
            createSubElement(specGroupXml,value,label)
        specObjectsXml = createSubElement(specGroupXml,"SPEC-OBJECTS")
        for req in specification:
            createSubElement(specObjectsXml ,"SPEC-OBJECT-REF", req)


    #
    # SPEC-HIERARCHY-ROOTS
    #
    def createChildHirachy(parentXmlTag, childObject):
        childrenXml = createSubElement(parentXmlTag, "CHILDREN")

        for value,label in py2reqif(childObject.toDict()).iteritems():
            if value == "objectRef":
                objectXml = createSubElement(childrenXml , "OBJECT")
                createSubElement(objectXml, "SPEC-OBJECT-REF", label)
            else:
                if label is not None:
                    createSubElement(childrenXml , value, label)

        for child in childObject.children:
            createChildHirachy(childrenXml, child)
    
    
    specHierarchRootsXml = createSubElement(root, "SPEC-HIERARCHY-ROOTS")
    #SPEC-HIERARCHY-ROOT
    for hierarch in doc.hierarchy:
        specHierarchRootXml = createSubElement(specHierarchRootsXml, "SPEC-HIERARCHY-ROOT")
        for value,label in py2reqif(hierarch.toDict()).iteritems():
            if value == "typeRef":
                typeXml = createSubElement(specHierarchRootXml, "TYPE")
                createSubElement(typeXml, "SPEC-TYPE-REF", label)
            else:
                createSubElement(specHierarchRootXml, value, label)

        
        for child in hierarch.children:
            createChildHirachy(specHierarchRootXml, child)
    

    f.write(etree.tostring(root, pretty_print=True, xml_declaration=True))

