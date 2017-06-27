#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import json
import sys
import pyreqif.pyreqif

            

def pretty(d, indent=0):
    for key, value in d.iteritems():
        print ('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print ('\t' * (indent+1) + str(value))
  
def reqif2py(myDict):    
    for reqifname in myDict:
        pyname = reqifname.title().replace('-','')
        pyname = pyname[0].lower() + pyname[1:]
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
            else:
                    returnDict[tag] = None
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
            specType = getSubElementValuesByTitle(child)
            attributesXml = child.find('./' + ns + "SPEC-ATTRIBUTES")
            if attributesXml is not None:
                for attribute in attributesXml:
                    if attribute.tag == ns +"ATTRIBUTE-DEFINITION-COMPLEX":
                        specAttribType = getSubElementValuesByTitle(attribute)
                        typeTag = attribute.find('./' + ns + 'TYPE')
                        if typeTag is not None:
                            reference = typeTag.find('./' + ns + 'DATATYPE-DEFINITION-DOCUMENT-REF')
                            if doc.datatypeById(reference.text):
                                specAttribType['typeRef'] = reference.text
                            else:
                                print ("BEEP unknown Datatype") 
                    elif attribute.tag == ns + "ATTRIBUTE-DEFINITION-ENUMERATION":
                        specAttribType = getSubElementValuesByTitle(attribute)
                        typeRef = attribute.find('./' + ns + 'TYPE/' + ns + 'DATATYPE-DEFINITION-ENUMERATION-REF')
                        if typeRef is not None:
                            specAttribType['typeRef'] = typeRef.text
                        
                    else:
                        print ("Not supported Attribute: ",)
                        print (attribute.tag)
                    specType[specAttribType['identifier']] = reqif2py(specAttribType)
                    specType[specAttribType['identifier']].pop('identifier')
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


    for requirement in doc._requirementList._list:
        for value in requirement._values:
            print value._content

#load("aa.xml")