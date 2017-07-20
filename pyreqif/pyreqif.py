#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import io
from lxml import etree
import collections

class reqIfObject(object):
    def __init__(self):
        self._identifier = None
        self._lastChanged = 0
        self._logName = ""

    def setValues(self, **kwargs):
        self._reqIfObjargs = [
            ('identifier', '_identifier', str, None),
            ('lastChange', '_lastChanged', str, None),
            ('longName', '_longname', str, None),
        ]
        for arg_name, destination, function, default in self._reqIfObjargs:
            try:
                value = kwargs[arg_name]
            except KeyError:
                value = default
            else:
                kwargs.pop(arg_name)
#            if value is not None:
            setattr(self, destination, value)
        return kwargs
        
    def toDict(self):
        myDict = {}
        for arg_name, attrib, function, default in self._reqIfObjargs:
            myDict[arg_name] = getattr(self, attrib)
        return myDict
            
        
        
class header(reqIfObject):
    def __init__(self, **kwargs):
        self._args = [
            ('author', '_author', str, None),
            ('countryCode', '_countrycode', str, None),
            ('creationTime', '_creationtime', str, None),
            ('sourceToolId', '_sourceToolId', str, None),
            ('title', '_title', str, None),
            ('version', '_version', str, None),
        ]


        for arg_name, destination, function, default in self._args:
            try:
                value = kwargs[arg_name]
            except KeyError:
                value = default
            else:
                kwargs.pop(arg_name)
            if function is not None and value is not None:
                value = function(value)
            setattr(self, destination, value)

        kwargs = reqIfObject.setValues(self, **kwargs)
            
        if len(kwargs) > 0:
            raise TypeError('{}() got unexpected argument{} {}'.format(
                self.__class__.__name__,
                's' if len(kwargs) > 1 else '',
                ', '.join(kwargs.keys())
            ))
        
    def toDict(self):
        myDict = reqIfObject.toDict(self)
        for arg_name, attrib, function, default in self._args:
            myDict[arg_name] = getattr(self, attrib)
        return myDict
         

class datatype(reqIfObject):
    def __init__(self, **kwargs):
        self.datatypeArgs = [
            ('type', '_type', str, None),
            ('embedded', '_embedded', str, None),
        ]


        for arg_name, destination, function, default in self.datatypeArgs:
            try:
                value = kwargs[arg_name]
            except KeyError:
                value = default
            else:
                kwargs.pop(arg_name)
            if function is not None and value is not None:
                value = function(value)
            setattr(self, destination, value)

        kwargs = reqIfObject.setValues(self, **kwargs)
            
        if "values" in kwargs:
            self._isValueTable = True
            self._valueTable = {}
            for valId, value in kwargs["values"].iteritems(): 
                self._valueTable[valId] = value
            kwargs.pop("values")

        if len(kwargs) > 0:
            raise TypeError('{}() got unexpected argument{} {}'.format(
                self.__class__.__name__,
                's' if len(kwargs) > 1 else '',
                ', '.join(kwargs.keys())
            ))
        
    @property
    def mytype(self):
        return self._type
    
    @property
    def valueTable(self):
        return self._valueTable
    
    def toDict(self):
        myDict = reqIfObject.toDict(self)
        for arg_name, attrib, function, default in self.datatypeArgs:
            myDict[arg_name] = getattr(self, attrib)
        return myDict
        
class datatypeList(reqIfObject):
    def __init__(self):
        self._list = []
        
    def add(self, myDatatypeDict):
        self._list.append(datatype(**myDatatypeDict))
    
    def byId(self, datatypeId):
        for dt in self._list:
            if datatypeId == dt._identifier:
                return dt
        return None

    def __iter__(self):
        return iter(self._list)


class reqTypeRefs(reqIfObject):
    def __init__(self, **kwargs):
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "typeRef" in kwargs:
            self._typeref = kwargs["typeRef"]
            kwargs.pop("typeRef")            
        else:
            self._typeref = None

        if "defaultValue" in kwargs:
            self._defaultValue = kwargs["defaultValue"]
            kwargs.pop("defaultValue")
        else:
            self._defaultValue = None


        if "type" in kwargs:
            self._type = kwargs["type"]
            kwargs.pop("type")            
        else:
            self._typeref = None
            
    def toDict(self):
        myDict = reqIfObject.toDict(self)
        if self._typeref is not None:
            myDict["typeRef"] = self._typeref
        if self._type is not None:
            myDict["type"] = self._type
            
        return myDict
        
class requirementType(reqIfObject):
    def __init__(self, **kwargs):
        self._myTypes = {}
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "desc" in kwargs:
            self._desc = kwargs["desc"]
            kwargs.pop("desc")
        for myType in kwargs:
            self._myTypes[myType] = reqTypeRefs(**kwargs[myType])


    @property
    def myTypes(self):
        return self._myTypes

    @property
    def fields(self):
        fields = []
        for type,typeObj in self._myTypes.iteritems():
            fields.append(typeObj._longname)
        return fields

    def attribById(self, attribId):
        for attrib in self._myTypes:
            if attrib == attribId:
                return self._myTypes[attrib]

    def toDict(self):
        myDict = reqIfObject.toDict(self)
        if self._desc:
            myDict["desc"] = self._desc
        return myDict

class requirementTypeList(reqIfObject):
    def __init__(self):
        self._list = []
        
    def add(self, myReqTypeDict):
        self._list.append(requirementType(**myReqTypeDict))
        
    def byId(self, identifier):
        for reqType in self._list:
            if reqType._identifier == identifier:
                return reqType

    @property
    def fields(self):
        fields = []
        for reqType in self._list:
            fields += reqType.fields
        return fields

    def __iter__(self):
        return iter(self._list)



class reqirementItem(reqIfObject):
    def __init__(self, **kwargs):
        kwargs = reqIfObject.setValues(self, **kwargs)
        self.reqItem_args = [
            ('contentRef', '_contentref', str, None),
            ('content', '_content', None, None),
            ('attributeRef', '_attributeref', str, None),
            ('type', '_type', str, None),            
        ]


        for arg_name, destination, function, default in self.reqItem_args:
            try:
                value = kwargs[arg_name]
            except KeyError:
                value = default
            else:
                kwargs.pop(arg_name)
            if function is not None and value is not None:
                value = function(value)
            setattr(self, destination, value)
            
        if len(kwargs) > 0:
            raise TypeError('{}() got unexpected argument{} {}'.format(
                self.__class__.__name__,
                's' if len(kwargs) > 1 else '',
                ', '.join(kwargs.keys())
            ))
    
    @property
    def mytype(self):
        return self._type
    
    def toDict(self):
        myDict = reqIfObject.toDict(self)
        
        for arg_name, attrib, function, default in self.reqItem_args:
            myDict[arg_name] = getattr(self, attrib)

        return myDict

 
class reqirement(reqIfObject):
    def __init__(self, **kwargs):
        self._values = []
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "typeRef" in kwargs:
            self._typeref = kwargs["typeRef"]
            kwargs.pop("typeRef")
        else:
            self._typeref = None
        for ident, value in kwargs["values"].iteritems():
            self._values.append(reqirementItem(**value))
    
    @property 
    def values(self):
        return self._values

    @property
    def values_text(self):
        textValues = []
        for value in self._values:
            newVal = value
#            print value._content
            if value._contentref is None and value._content is not None and len(value._content) > 0 and value._content[0] == "<":
                try:
                    tree = etree.parse(io.BytesIO(value._content))
                    root = tree.getroot()
                    test = "".join(root.itertext())
                    newVal._content = test
                except:
                    pass
            textValues.append(newVal)
        return textValues

    def toDict(self):
        myDict = reqIfObject.toDict(self)
        if self._typeref is not None:
            myDict["typeRef"] = self._typeref
        myDict["values"] = self._values
        return myDict

        
class reqirementList(reqIfObject):
    def __init__(self):
        self._list = []
    def add(self, myReqDict):
        self._list.append(reqirement(**myReqDict))
    def __iter__(self):
        return iter(self._list)
    
class specification(reqIfObject):
    def __init__(self, **mySpecDict):
        mySpecDict = reqIfObject.setValues(self, **mySpecDict)
        if "desc" in mySpecDict:
            self._desc = mySpecDict["desc"]
            mySpecDict.pop("desc")
        else:
            self._desc = None
        self._list = []
        if len(mySpecDict) > 0:
            raise TypeError('{}() got unexpected argument{} {}'.format(
                self.__class__.__name__,
                's' if len(mySpecDict) > 1 else '',
                ', '.join(mySpecDict.keys())
            ))
    def __iter__(self):
        return iter(self._list)
    @property
    def name(self):
        return self._longname
    @property
    def desc(self):
        return self._desc
    
    def toDict(self):
        myDict = reqIfObject.toDict(self)
        if self._desc is not None:
            myDict["desc"] = self._desc
        return myDict
        
    def addReq(self, reqId):
        self._list.append(reqId)

class specificationList(reqIfObject):
    def __init__(self):
        self._list = []
    def add(self, mySpec):
        self._list.append(mySpec)
    def __iter__(self):
        return iter(self._list)

class hierarchy(reqIfObject):
    def __init__(self, **kwargs):
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "typeRef" in kwargs:
            self._typeref = kwargs["typeRef"]
            kwargs.pop("typeRef")
        else:
            self._typeref = None
        if "objectRef" in kwargs:
            self._objectref = kwargs["objectRef"]
            kwargs.pop("objectRef")
        else:
            self._objectref = None

        self._children = []
        
    @property
    def children(self):
        return self._children
    
    def toDict(self):
        myDict = reqIfObject.toDict(self)
        if self._typeref is not None:
            myDict["typeRef"] = self._typeref
        if self._objectref is not None:
            myDict["objectRef"] = self._objectref
        return myDict

    def addChild(self, child):        
        self._children.append(child)
    

class relation(reqIfObject):
    def __init__(self, **kwargs):
        kwargs = reqIfObject.setValues(self, **kwargs)
        args = [
            ('typeRef', '_typeref', str, None),
            ('desc', '_desc', None, None),
            ('sourceRef', '_sourceref', str, None),
            ('targetRef', '_targetref', str, None),            
        ]


        for arg_name, destination, function, default in args:
            try:
                value = kwargs[arg_name]
            except KeyError:
                value = default
            else:
                kwargs.pop(arg_name)
            if function is not None and value is not None:
                value = function(value)
            setattr(self, destination, value)
            
        if len(kwargs) > 0:
            raise TypeError('{}() got unexpected argument{} {}'.format(
                self.__class__.__name__,
                's' if len(kwargs) > 1 else '',
                ', '.join(kwargs.keys())
            ))
        

class relationList(reqIfObject):
    def __init__(self):
        self._list = []
    def add(self, relation):
        self._list.append(relation)
        
    def __iter__(self):
        return iter(self._list)


    
    
class doc(reqIfObject):
    def __init__(self):
        self._header = None
        self._datatypeList = datatypeList()
        self._requirementTypeList = requirementTypeList()
        self._requirementList = reqirementList()
        self._specificationList = specificationList()
        self._hierarchy = []
        self._relations = relationList()
    
    @property 
    def header(self):
        return self._header.toDict()

    @property 
    def datatypeList(self):
        return self._datatypeList

    @property 
    def requirementTypeList(self):
        return self._requirementTypeList 
    
    @property
    def requirementList(self):
        return self._requirementList
    
    @property
    def relations(self):
        return self._relations
    
    @property
    def hierarchy(self):
        return self._hierarchy
    
    @property
    def specificationList(self):
        return self._specificationList

    @property
    def fields(self):
        return self._requirementTypeList.fields

    def addHeader(self, myHeader):
        self._header = header(**myHeader)
        
    def addDatatype(self, myDatatypeDict):
        self._datatypeList.add(myDatatypeDict)
    
    def datatypeById(self, datatypeId):
        return self._datatypeList.byId(datatypeId)
    
    def addRequirementType(self, myReqTypeDict):
        self._requirementTypeList.add(myReqTypeDict)
        
    def addRequirement(self, myReqDict):
        self._requirementList.add(myReqDict)
    
    def addSpecification(self, mySpec):
        self._specificationList.add(mySpec)
    
    def getReqById(self, reqId):
        for req in self._requirementList._list:
            if req._identifier == reqId:
                return req
            
    def flatReq(self, requirement, **kwargs):
        reqDict = {}
        reqType = self.requirementTypeList.byId(requirement._typeref)

        for myTypeId,myType in reqType.myTypes.iteritems():
            if myType._defaultValue is not None:
                dataType = self.datatypeById(myType._typeref)
                reqDict[myType._longname] = dataType._valueTable[myType._defaultValue]["longName"]

        if "html" in kwargs and kwargs["html"]:
            valueArray = requirement.values
        else:
            valueArray = requirement.values_text
        for value in valueArray:
            valueType = reqType.attribById(value._attributeref)
            dataType = self.datatypeById(valueType._typeref)

            if value._contentref is not None:
                if "longName" in dataType._valueTable[value._contentref]:
                    reqDict[valueType._longname] = dataType._valueTable[value._contentref]["longName"]
            else:
                reqDict[valueType._longname] = value._content
        return reqDict
    
    def addRelation(self, relation):
        self._relations.add(relation)

    def asDict(self):
        cols = self.fields
        specs = []

        for specification in self.specificationList:
            spec = []
            for req in specification:
                tempReq = self.req2dict(req, cols)
                spec.append(tempReq)
            specs.append(spec)
        return specs

    def req2dict(self, req, cols):
        reqObj = self.getReqById(req)
        tempReq = collections.OrderedDict()
        for col in cols:
            tempReq[col] = ""
        for col, value in self.flatReq(reqObj, html=True).iteritems():
            tempReq[col] = value
            tempReq["reqifId"] = req
        return tempReq

    def asHierarchDict(self):
        cols = self.fields
        spec = []

        for child in self.hierarchy:
            spec.append(self._hierarchDict(child, cols))
        return spec

    def _hierarchDict(self, element, cols):
        retDict = collections.OrderedDict()
        for child in element.children:
            retDict[child._objectref] = self.req2dict(child._objectref, cols)
            retDict[child._objectref]["children"] = self._hierarchDict(child, cols)
        return retDict
