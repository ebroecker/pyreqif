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
        
    def addDatatype(self, myDatatypeDict):
        self._list.append(datatype(**myDatatypeDict))
    

class requirementType(reqIfObject):
    def __init__(self, **kwargs):
        print kwargs
        sys.exit(0)
        pass


class requirementTypeList(reqIfObject):
    def __init__(self):
        self._list = []
        
    def addRequirementType(self, myReqTypeDict):
        self._list.append(requirementType(**myReqTypeDict))
        s

class reqirement(reqIfObject):
    def __init__(self):
        pass
    
class reqirementList(reqIfObject):
    def __init__(self):
        self._list = []
    
class specification(reqIfObject):
    def __init__(self):
        self._list = []

class specificationList(reqIfObject):
    def __init__(self):
        self._list = []
    
class doc(reqIfObject):
    def __init__(self):
        self._header = None
        self._datatypeList = datatypeList()
        self._requirementTypeList = requirementTypeList()
        
    def addHeader(self, myHeader):
        self._header = header(**myHeader)
        
    def addDatatype(self, myDatatypeDict):
        self._datatypeList.addDatatype(myDatatypeDict)
    
    def addRequirementType(self, myReqTypeDict):
        self._requirementTypeList.addRequirementType(myReqTypeDict)