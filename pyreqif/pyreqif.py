# -*- coding: utf-8 -*-
import sys


class reqIfObject(object):
    def __init__(self):
        self._identifier = None
        self._lastChanged = 0
        self._logName = ""

    def setValues(self, **kwargs):
        args = [
            ('identifier', '_identifier', str, None),
            ('lastChange', '_lastChanged', str, None),
            ('longName', '_longname', str, None),
            ('longname', '_longname', str, None),
        ]
        for arg_name, destination, function, default in args:
            try:
                value = kwargs[arg_name]
            except KeyError:
                value = default
            else:
                kwargs.pop(arg_name)
            setattr(self, destination, value)
        return kwargs
        
class header(reqIfObject):
    def __init__(self, **kwargs):
        args = [
            ('author', '_author', str, None),
            ('countrycode', '_countrycode', str, None),
            ('creationtime', '_creationtime', str, None),
            ('sourceToolId', '_sourceToolId', str, None),
            ('title', '_title', str, None),
            ('version', '_version', str, None),
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
            
        if len(kwargs) > 0:
            raise TypeError('{}() got unexpected argument{} {}'.format(
                self.__class__.__name__,
                's' if len(kwargs) > 1 else '',
                ', '.join(kwargs.keys())
            ))

         

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
        if "typeref" in kwargs:
            self._typeref = kwargs["typeref"]
            kwargs.pop("typeref")
        else:
            self._typeref = None
            
    
class requirementType(reqIfObject):
    def __init__(self, **kwargs):
        self._myTypes = {}
        kwargs = reqIfObject.setValues(self, **kwargs)
        for myType in kwargs:
            self._myTypes[myType] = reqTypeRefs(**kwargs[myType])


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
            ('contentref', '_contentref', str, None),
            ('content', '_content', None, None),
            ('attributeref', '_attributeref', str, None),
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
 
class reqirement(reqIfObject):
    def __init__(self, **kwargs):
        self._values = []
        kwargs = reqIfObject.setValues(self, **kwargs)
        if "typeref" in kwargs:
            self._typeref = kwargs["typeref"]
            kwargs.pop("typeref")
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
    def addReq(self, reqId):
        self._list.append(reqId)

class specificationList(reqIfObject):
    def __init__(self):
        self._list = []
    def add(self, mySpec):
        self._list.append(mySpec)
        
    
class doc(reqIfObject):
    def __init__(self):
        self._header = None
        self._datatypeList = datatypeList()
        self._requirementTypeList = requirementTypeList()
        self._requirementList = reqirementList()
        self._specificationList = specificationList()
        
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
            
    def flatReq(self, reqirement):
        reqType = self._requirementTypeList.byId(reqirement._typeref) 
        print(vars (reqType))
        