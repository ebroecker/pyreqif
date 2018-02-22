import sys
sys.path.append('..')
import rif

def load(f):
    return rif.load(f)

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
        if datatype.mytype == "enum":
            datatypeXml = createSubElement(datatypesXml, "DATATYPE-DEFINITION-ENUMERATION", attributes=py2reqif(datatype.toDict()))
            myDict = py2reqif(datatype.toDict())
            del myDict["TYPE"]
            createSubElements(datatypeXml, myDict)
            specifiedValuesXml = createSubElement(datatypeXml, "SPECIFIED-VALUES")
            for value,label in datatype.valueTable.iteritems():
                valuesXml = createSubElement(specifiedValuesXml , "ENUM-VALUE", attributes=py2reqif(label) )
                #createSubElement(valuesXml, "IDENTIFIER", value)
                for element,content in py2reqif(label).iteritems():
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

            for mytype,ref in reqType.myTypes.iteritems():
                attribDict = py2reqif(ref.toDict())
                if "TYPE" in attribDict and attribDict["TYPE"] == "enum":
                    attribDict.pop("TYPE")
                    attribDict["MULTI-VALUED"] = "false"
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-ENUMERATION", attributes=attribDict)
                    for value,label in attribDict.iteritems():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-ENUMERATION-REF",label)
                        elif value not in attributesForElements:
                            createSubElement(enumXml,value,label)


                if "TYPE" in attribDict and attribDict["TYPE"] == "complex":
#                    attribDict.pop("TYPE")
                    enumXml = createSubElement(attributesXml,"ATTRIBUTE-DEFINITION-XHTML", attributes=attribDict)
                    attribDict.pop("TYPE")
                    for value,label in attribDict.iteritems():
                        if value == "typeRef":
                            typeXml = createSubElement(enumXml,"TYPE")
                            createSubElement(typeXml,"DATATYPE-DEFINITION-XHTML-REF",label)
                        elif value not in attributesForElements and value not in notUsedAttributes:
                            createSubElement(enumXml,value,label)

    #
    # SPEC-OBJECTS
    #
    specsXml = createSubElement(reqIfContent, "SPEC-OBJECTS")
    
    for req in doc.requirementList:
        specXml = createSubElement(specsXml , "SPEC-OBJECT", attributes=py2reqif(req.toDict()))
        requirementDict = py2reqif(req.toDict())
        for value,label in requirementDict.iteritems():
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
                    for val,lab in py2reqif(value.toDict()).iteritems():
                        if val == "contentRef" and lab is not None:
                            createSubElement(valuesValuesXml, "ENUM-VALUE-REF",lab)
                        elif val == "attributeRef":
                            if value.mytype == "enum":
                                createSubElement(valuesDefinitionsXml, "ATTRIBUTE-DEFINITION-ENUMERATION-REF", lab)
                            elif value.mytype == "embeddedDoc":
                                createSubElement(valuesDefinitionsXml, "ATTRIBUTE-DEFINITION-XHTML-REF", lab)
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
            elif element not in attributesForElements:
                createSubElement(specXml , value , label)
            

    #
    # SPEC-RELATIONS
    #
    specsRelXml = createSubElement(reqIfContent, "SPEC-RELATIONS")
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
        for value,label in py2reqif(childObject.toDict()).iteritems():
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
        for value,label in py2reqif(hierarch.toDict()).iteritems():
            if value == "typeRef":
                typeXml = createSubElement(specHierarchRootXml, "TYPE")
                createSubElement(typeXml, "SPECIFICATION-TYPE-REF", label)
            elif value not in attributesForElements:
                createSubElement(specHierarchRootXml, value, label)

        
        for child in hierarch.children:
            createChildHirachy(specHierarchRootXml, child)
    

    f.write(etree.tostring(root, pretty_print=True, xml_declaration=True))

