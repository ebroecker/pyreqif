# -*- coding: utf-8 -*-
import sys


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
        args = [
            ('type', '_type', str, None),
            ('embedded', '_embedded', str, None),
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

class reqTypeRefs(reqIfObject):
    def __init__(self, **kwargs):
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "typeRef" in kwargs:
            self._typeref = kwargs["typeRef"]
            kwargs.pop("typeRef")
        else:
            self._typeref = None
    
class requirementType(reqIfObject):
    def __init__(self, **kwargs):
        self._myTypes = {}
        kwargs = reqIfObject.setValues(self, **kwargs)
        for myType in kwargs:
            self._myTypes[myType] = reqTypeRefs(**kwargs[myType])
    def attribById(self, attribId):
        for attrib in self._myTypes:
            if attrib == attribId:
                return self._myTypes[attrib]




class requirementTypeList(reqIfObject):
    def __init__(self):
        self._list = []
        
    def add(self, myReqTypeDict):
        self._list.append(requirementType(**myReqTypeDict))
        
    def byId(self, identifier):
        for reqType in self._list:
            if reqType._identifier == identifier:
                return reqType

class reqirementItem(reqIfObject):
    def __init__(self, **kwargs):
        kwargs = reqIfObject.setValues(self, **kwargs)
        args = [
            ('contentRef', '_contentref', str, None),
            ('content', '_content', None, None),
            ('attributeRef', '_attributeref', str, None),
            ('type', '_type', str, None),            
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
 
class reqirement(reqIfObject):
    def __init__(self, **kwargs):
        self._values = []
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "typeRef" in kwargs:
            self._typeref = kwargs["typeRef"]
            kwargs.pop("typeRef")
        for ident, value in kwargs["values"].iteritems():
            self._values.append(reqirementItem(**value))
        
class reqirementList(reqIfObject):
    def __init__(self):
        self._list = []
    def add(self, myReqDict):
        self._list.append(reqirement(**myReqDict))
    
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
    def addReq(self, reqId):
        self._list.append(reqId)

class specificationList(reqIfObject):
    def __init__(self):
        self._list = []
    def add(self, mySpec):
        self._list.append(mySpec)

class hierarchy(reqIfObject):
    def __init__(self, **kwargs):
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "typeRef" in kwargs:
            self._typeref = kwargs["typeRef"]
            kwargs.pop("typeRef")
        if "objectRef" in kwargs:
            self._objectref = kwargs["objectRef"]
            kwargs.pop("objectRef")

        self._children = []
    def addChild(self, child):        
        self._children.append(child)
        
    
class doc(reqIfObject):
    def __init__(self):
        self._header = None
        self._datatypeList = datatypeList()
        self._requirementTypeList = requirementTypeList()
        self._requirementList = reqirementList()
        self._specificationList = specificationList()
        self._hierarchy = []
        
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
            
    def flatReq(self, requirement):
        reqDict = {}
        reqType = self._requirementTypeList.byId(requirement._typeref)
        for value in requirement._values:
            valueType = reqType.attribById(value._attributeref)
            dataType = self._datatypeList.byId(valueType._typeref)

            if value._contentref is not None:
                reqDict[valueType._longname] = dataType._valueTable[value._contentref]["longName"]
            else:
                reqDict[valueType._longname] = value._content
        return reqDict