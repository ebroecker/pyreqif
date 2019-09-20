import sys
sys.path.append('..')
import io
import pyreqif.rif
from lxml import etree
import lxml.html

def load(f):
    return pyreqif.rif.load(f)

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

transLationTableReverse = dict(map(reversed, transLationTable.items()))


def py2reqif(myDict):
    MyNewDict = {}
    for pyname in myDict:
        if pyname in transLationTableReverse:
            reqifname= transLationTableReverse[pyname]
            MyNewDict[reqifname] = myDict[pyname]
        else:
            MyNewDict[pyname] = myDict[pyname]
    return MyNewDict


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
                
def createSubElement(parent, tag, text=None, attributes=None, additionalAttributesForElements = []):
    sn = etree.SubElement(parent, tag)
    if text is not None:
        sn.text = str(text)
    if attributes is not None:
        for attributeName in attributesForElements:
            if attributeName in attributes and attributes[attributeName] is not None and attributeName not in notUsedAttributes:
                sn.attrib[attributeName] = attributes[attributeName]
        for attributeName in additionalAttributesForElements:
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
#            for value,label in datatype.valueTable.iteritems():
            for value,label in datatype.valueTable.items():
                valuesXml = createSubElement(specifiedValuesXml , "ENUM-VALUE", attributes=py2reqif(label) )
                #createSubElement(valuesXml, "IDENTIFIER", value)
#                for element,content in py2reqif(label).iteritems():
                for element, content in py2reqif(label).items():
                    if element == "properites":
                        props = createSubElement(valuesXml, "PROPERTIES")
                        createSubElement(props, "EMBEDDED-VALUE", attributes=py2reqif(content))
                    elif element not in attributesForElements:
                        createSubElement(valuesXml, element, content)

    
    #
    # SPEC-TYPES
    #
    specTypes = createSubElement(reqIfContent, "SPEC-TYPES")
    #SPEC-OBJECT-TYPE
    for reqType in doc.requirementTypeList:
        specType = createSubElement(specTypes, "SPEC-OBJECT-TYPE", attributes=py2reqif(reqType.toDict()))
        createSubElements(specType,py2reqif(reqType.toDict()))
        
        if len(reqType.myTypes) > 0:
            attributesXml = createSubElement(specType,"SPEC-ATTRIBUTES")

#            for mytype,ref in reqType.myTypes.iteritems():
            for mytype,ref in reqType.myTypes.items():
                attribDict = py2reqif(ref.toDict())
                if "TYPE" in attribDict and attribDict["TYPE"] == "enum":
                    attribDict.pop("TYPE")
                    attribDict["MULTI-VALUED"] = "false"
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-ENUMERATION", attributes=attribDict)
#                    for value,label in attribDict.iteritems():
                    for value, label in attribDict.items():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-ENUMERATION-REF",label)
                        elif value not in attributesForElements:
                            createSubElement(enumXml,value,label)

                if "TYPE" in attribDict and attribDict["TYPE"] == "complex":
#                    attribDict.pop("TYPE")
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-XHTML", attributes=attribDict)
                    attribDict.pop("TYPE")
#                    for value,label in attribDict.iteritems():
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
#                    for value,label in attribDict.iteritems():
                    for value,label in attribDict.items():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-STRING-REF",label)
                        elif value not in attributesForElements and value not in notUsedAttributes:
                            createSubElement(enumXml,value,label)
    #SPEC-RELATION-TYPE
    for relationType in doc.specRelationTypeList:
        createSubElement(specTypes, "SPEC-RELATION-TYPE", attributes=py2reqif(relationType.toDict()))

    #RELATION-GROUP-TYPE
    for relationGroup in doc.specRelationGroupList:
        attributes = py2reqif(relationGroup.toDict())
        attributes['IDENTIFIER'] += "_type"
        createSubElement(specTypes, "RELATION-GROUP-TYPE", attributes = attributes)

    #
    # SPEC-OBJECTS
    #
    specsXml = createSubElement(reqIfContent, "SPEC-OBJECTS")
    
    for req in doc.requirementList:
        specXml = createSubElement(specsXml , "SPEC-OBJECT", attributes=py2reqif(req.toDict()))
        requirementDict = py2reqif(req.toDict())
#        for value,label in requirementDict.iteritems():
        for value, label in requirementDict.items():
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
                    elif value.mytype == "string":
                        tempDict["THE-VALUE"] = tempDict['CONTENT']
                        tempDict.pop('CONTENT', None)
                        value._content=None
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-STRING", attributes=tempDict, additionalAttributesForElements=['THE-VALUE'])
                        valuesDefinitionsXml = createSubElement(valueXml, "DEFINITION")
                    elif value.mytype == "embeddedDoc":
                        valueXml = createSubElement(valuesXml, "ATTRIBUTE-VALUE-XHTML", attributes=tempDict)
                        valuesDefinitionsXml = createSubElement(valueXml, "DEFINITION")
                    else:
                        print ("Unknown Type " + value.mytype)                        

#                    for val,lab in py2reqif(value.toDict()).iteritems():
                    for val,lab in py2reqif(value.toDict()).items():
                        if val == "contentRef" and lab is not None:
                            for elem in lab:
                                createSubElement(valuesValuesXml, "ENUM-VALUE-REF",elem)
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
                                if "<" in str(lab):
                                    labtree = lxml.html.fromstring(lab)
#                                        labtree = etree.parse(io.BytesIO(lab))
                                    labroot = labtree #.getroot()
                                    for el in labroot.iter():
                                        if el.tag == "font" or el.tag == "height" or el.tag == "width":
                                            el.drop_tag()
                                            #for key in el.keys:
                                        for attr in ["height", "width", "align"]:
                                            if attr in el.keys():
                                                del (el.attrib[attr])
                                        if el.tag == "a":
                                            el.tag = "object"
                                            el.attrib["data"] = el.attrib["href"].replace(
                                                'mks:///item/field?fieldid=Text Attachments&attachmentname=',
                                                'attachments/')
                                            del (el.attrib["href"])
                                            if el.attrib["data"].endswith(".png"):
                                                el.attrib["type"] = "image/png"
                                            elif el.attrib["data"].endswith(".rtf"):
                                                el.attrib["type"] = "text/x-rtf"

                                        if el.tag == "img":
                                            el.tag = "object"
                                            el.attrib["data"] = el.attrib["src"].replace(
                                                'mks:///item/field?fieldid=Text Attachments&attachmentname=',
                                                'attachments/')

                                            del (el.attrib["src"])
                                            if "alt" in el.keys():
                                                el.text = el.attrib["alt"]
                                                del (el.attrib["alt"])
                                            if el.attrib["data"].endswith(".png"):
                                                el.attrib["type"] = "image/png"
                                            elif el.attrib["data"].endswith(".rtf"):
                                                el.attrib["type"] = "text/x-rtf"
                                        try:
                                            el.tag = '{http://www.w3.org/1999/xhtml}' + el.tag
                                        except:
                                            print ("probably XML Comment found - ignoring")
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
        specsRel = createSubElement(specsRelXml  , "SPEC-RELATION", attributes=py2reqif(relation))
        for value,label in py2reqif(relation).items():
            if value == "typeRef":
                typeXml = createSubElement(specsRel , "TYPE")
                createSubElement(typeXml , "SPEC-RELATION-TYPE-REF", label)
            elif value == "sourceRef":
                sourceXml = createSubElement(specsRel , "SOURCE")
                createSubElement(sourceXml, "SPEC-OBJECT-REF", label)
            elif value == "targetRef":
                targetXml = createSubElement(specsRel , "TARGET")
                createSubElement(targetXml, "SPEC-OBJECT-REF", label)
#            else:
#                createSubElement(specsRel , value, label)
            # RELATION-GROUP-TYPE



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
    def createChildHirachy(parentXmlTag, childrenList):
        childrenXml = createSubElement(parentXmlTag, 'CHILDREN')
        for childObject in childrenList:
            hierarchXml = createSubElement(childrenXml, 'SPEC-HIERARCHY', attributes=py2reqif(childObject.toDict()))
#            for value, label in py2reqif(childObject.toDict()).iteritems():
            for value, label in py2reqif(childObject.toDict()).items():
                if value == 'objectRef':
                    objectXml = createSubElement(hierarchXml, 'OBJECT')
                    createSubElement(objectXml, 'SPEC-OBJECT-REF', label)
                elif value not in attributesForElements:
                    if label is not None:
                        createSubElement(hierarchXml, value, label)

            if len(childObject.children) > 0:
                createChildHirachy(hierarchXml, childObject.children)

        return
    
    specHierarchRootsXml = createSubElement(reqIfContent, "SPECIFICATIONS")
    #SPEC-HIERARCHY-ROOT
    for hierarch in doc.hierarchy:
        specHierarchRootXml = createSubElement(specHierarchRootsXml, "SPECIFICATION", attributes=py2reqif(hierarch.toDict()))
#        for value,label in py2reqif(hierarch.toDict()).iteritems():
        for value, label in py2reqif(hierarch.toDict()).items():
            if value == "typeRef":
                typeXml = createSubElement(specHierarchRootXml, "TYPE")
                createSubElement(typeXml, "SPECIFICATION-TYPE-REF", label)
            elif value not in attributesForElements:
                createSubElement(specHierarchRootXml, value, label)

        
        if len(hierarch.children) > 0:
            createChildHirachy(specHierarchRootXml, hierarch.children)
    

    #
    # SPEC-RELATION-GROUPS
    #
    specsRelGroupsXml = createSubElement(reqIfContent, "SPEC-RELATION-GROUPS")
    for relationGroup in doc.specRelationGroupList:
        tempAttributes =relationGroup.toDict()
        tempAttributes["longName"] = relationGroup.nameOfType
        specRelGroupXML = createSubElement(specsRelGroupsXml, "RELATION-GROUP", attributes=py2reqif(tempAttributes))
        specRelations = createSubElement(specRelGroupXML, "SPEC-RELATIONS")
        for specRel in relationGroup.specRelationRefs:
            createSubElement(specRelations, "SPEC-RELATION-REF",specRel)
        textXml = createSubElement(specRelGroupXML, "TYPE")
        createSubElement(textXml, "RELATION-GROUP-TYPE-REF", text=relationGroup._identifier + "_type" )

        sourceXML = createSubElement(specRelGroupXML, "SOURCE-SPECIFICATION")
        createSubElement(sourceXML, "SPECIFICATION-REF", text=relationGroup.sourceDoc)
        targetXML = createSubElement(specRelGroupXML, "TARGET-SPECIFICATION")
        createSubElement(targetXML, "SPECIFICATION-REF", text=relationGroup.targetDoc)
    
    xmlData = etree.tostring(root, pretty_print=True, xml_declaration=True)
    f.write(xmlData.decode("utf-8"))