## Copyright (c) 2007-2024, Patrick Germain Placidoux
## All rights reserved.
##
## This file is part of KastMenu (Unixes Operating System's Menus Broadkasting).
##
## KastMenu is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## KastMenu is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with KastMenu.  If not, see <http://www.gnu.org/licenses/>.
##
## Home: http://www.kastmenu.org
## Contact: kastmenu@kastmenu.org


## BEWARE: repoztools is imported into the repoz interprater, so as a context where tools is already imported as: import * from tools
# 20120306:A001


from . import wk
from .ct import _eval
from . import ct
from . import repozxception
import  warnings
from kwadlib import tools

HARD_SERIALIZED=False


def getModule(newMod):
    selfMethod='getModule'
    
    if  __debug__ and isinstance(newMod, (str))==False:        
        raise repozxception.repozParameterTypeException("Main", "getModule", 'newMod', 'str', str(newMod))
      
    mod=newMod

    try:
        mod=__import__(mod, None, None, [mod])
    except ImportError as e:
        raise ImportError(repozxception.repozSystemException("Main", selfMethod, 'Error in trying to load module:' + newMod + '. SubException is:' + str(e) + '. '))
   
    return mod  


def getAttrType(obj, attr):
    return getType(getattr(obj,attr)) 

def getType(value):
    t=str(type(value)).split("'")[1]
    
    if t=='instance':        
        # Class Name
        className=value.__class__.__name__
        t=className          
    return t    

#M001:
def getSignature(value, temp_dir=None):
    selfMethod='getSignature'

    try:
        from hashlib import md5

        m=md5()
        m.update(bytes(value, 'utf-8'))
        return str(m.hexdigest())

    except:
        if tools.getOsType()!='unix':raise
        
    if temp_dir==None or not isinstance(temp_dir, str):raise repozxception.repoParameterTypeException('Main', selfMethod, 'temp_dir', 'str', str(temp_dir))
    import os
    
    fpath=os.path.normpath(os.path.realpath(temp_dir + '/getSignature_' + tools.genUid() + '.dat'))
    fd=open(fpath, 'wb')
    fd.write(bytes(value, 'utf-8'))
    fd.close()
    
    ret, sig, stderr=tools.subprocess2(['cksum', fpath])
    if ret!=0:raise repozxception.repozSystemException('Main', selfMethod, 'Error running system command:cksum ' + fpath + ' !')

    return sig.split()[0]

#M001:
def getFileSignature(fpath):
    selfMethod = 'getFileSignature'
    import os   
    
    fpath=os.path.normpath(os.path.realpath(fpath))
    if not os.access(fpath, os.F_OK):return None
    
    try:
        from hashlib import md5
        
        fd=open(fpath, 'rb')
        value=fd.read().decode("utf-8")
        fd.close()
        
        m=md5()
        m.update(bytes(value, 'utf-8'))
        return str(m.hexdigest())

    except:
        if tools.getOsType()!='unix':raise
        
    ret, sig, stderr=tools.subprocess2(['cksum', fpath])
    if ret!=0:raise repozxception.repozSystemException('Main', selfMethod, 'Error running system command:cksum ' + fpath + ' !')

    return sig.split()[0]

def getFilesSignature(fpaths):
    import io
    
    sb=io.StringIO()
    for fpath in fpaths:
        fd=open(fpath, 'rb')
        sb.write(fd.read().decode("utf-8"))
        fd.close()
        
    return getSignature(sb.getvalue())




#####################
## _Apb_isinstance ##
#####################

class _Apb_isinstance:
    """ Sometimes Python isinstance seems not to work! """

    def isinstance(self, typ): 

        if not isinstance(typ, str):
            raise repozxception.repozParameterTypeException('Main', "_apb_isinstance"'typ', 'str', str(typ))

        typs=[]
        attrs=dir(self)
        for attr in attrs:
            if attr.startswith('_apb_isinstance'):typs.append(getattr(self, attr))

        return (typ in typs)



   
##################
## Serializable ##
##################

class StructSerializable(_Apb_isinstance):    
    _apb_isinstance_StructSerializable='StructSerializable'
    
    """ The frameWork is supposed to be used not only with Python langage
    So we want a readable serialized form for returned objects.
    [{'attrName':'className', 'type':'string', 'value':'TaskCtx'}, {'attrName':'boot', 'type':'int', 'value':'linux1.freezestoem.com'}...]    
    
    A subclass can implement deSerialize(),
    this method willb called after the class has been desrialized.
    A subclass can implement serialize(),
    this method will called befor the class be desrialized.    
    
    """
    # For use of the deSerialize() methods upon the TheRealClass, we will need to obtain 
    # an empty object first by obj=TheRealClass().
    # So since we want to be able to do an __init()__,  StructSerializable must be the only one implementing 
    # the __init__ method, in order to bypass standards __inits__ controls of its childs. 
            
    def __init__(self,   *args, **keywords): 
        selfMethod='__init__'
        p=wk.WantedKeywords()
        p.forDeSerial={'*value':False,}
        wk.getKeywords(wantedKeywords=p, keywords=keywords, class_exit=str(self.__class__), method_exit=selfMethod)
        
        self.dontSerialize=None
        self.doSerialize=None        
              
        if not p.forDeSerial:
            wk.setKeywords({}, keywords)

            getattr(self, '_init')(*args, **keywords)
            
    def _init(self, *args, **keywords):
        pass

    def serializeToXml(self, dontSerialize=None, doSerialize=None, className=None):
        return tools.serialize(dontSerialize=dontSerialize, doSerialize=doSerialize, className=className, toXml=True)
    
    def serialize(self, *args, **keyworfs):
        """ inbound method """
        return self._serialize(self, *args, **keyworfs)

    def _serialize(self, dontSerialize=None, doSerialize=None, className=None, toXml=False):
        """ static method """
        selfMethod='_serialize'
        if doSerialize!=None and not isinstance(doSerialize, (tuple, list)):raise repozxception.repozParameterTypeException(str(self.__class__), selfMethod, 'doSerialize', '(tuple, list)', str(doSerialize))
        if dontSerialize!=None and not isinstance(dontSerialize, (tuple, list)):raise repozxception.repozParameterTypeException(str(self.__class__), selfMethod, 'dontSerialize', '(tuple, list)', str(dontSerialize))                       
        if self.doSerialize!=None and not isinstance(self.doSerialize, (tuple, list)):raise repozxception.repozParameterTypeException(str(self.__class__), selfMethod, 'doSerialize', '(tuple, list)', str(self.doSerialize))               
        if self.dontSerialize!=None and not isinstance(self.dontSerialize, (tuple, list)):raise repozxception.repozParameterTypeException(str(self.__class__), selfMethod, 'dontSerialize', '(tuple, list)', str(self.dontSerialize))                       
                
        serList=[]
                
        # Attribute Class Name
        if not isinstance(className, str):
            className=str(self.__class__).split()[0]                    
            if className.startswith('__main__.'):className=className[9:]
        
        if not toXml:serList.append({'attrName':'className', 'type':'string', 'value':repr(className)})
        else:serList.append({'className':str(className)})

        ## Concordentes behaviours after serial/deserial...
        if self.doSerialize!=None:
            if 'doSerialize' not in self.doSerialize:
                if isinstance(self.doSerialize, tuple):self.doSerialize=self.doSerialize + ('doSerialize',)
                else:self.doSerialize=self.doSerialize + ['doSerialize',]
            if self.dontSerialize!=None and 'dontSerialize' not in self.doSerialize:
                if isinstance(self.doSerialize, tuple):self.doSerialize=self.doSerialize + ('dontSerialize',)
                else:self.doSerialize=self.doSerialize + ['dontSerialize',]
        
        # Other Attributes
        attrs=dir(self)
        for attr in attrs:
            if attr[0]=='_':continue                                    
            if (doSerialize!=None) and (attr not in doSerialize):continue            
            if doSerialize==None and self.getDoSerialize()!=None and (attr not in self.getDoSerialize()):continue                                                            
            if (dontSerialize!=None) and (attr in dontSerialize):continue            
            if dontSerialize==None and self.getDontSerialize()!=None and (attr in self.getDontSerialize()):continue
            typ=getAttrType(self, attr)
            if typ=='instancemethod' or typ=='function':continue
            v=getattr(self, attr)
            
            # Begin:Recursive serialization
            if isinstance(v, (tuple, list)):
                l=list(v)
                for i in range(len(l)):
                    self.__deepSerialize(list=l, index=i)                                                             
                if isinstance(v, tuple):v=tuple(l)
                else:v=l
            elif isinstance(v, dict):
                v=dict(v)
                for k in v:
                    self.__deepSerialize(list=v, index=k)
            # End:Recursive serialization
            typ=getType(v)
            
            ## StructSerializable
            if hasattr(v, 'isinstance') and v.isinstance('StructSerializable'):
                value=v.serialize()                                                    
                
            ## Base type
            elif typ in wk.supportedTypes or typ=='NoneType':
                value=v                       
            else:
                ## Trivial type, try dump
                if not HARD_SERIALIZED:raise repozxception.repozSystemException(str(self.__class__), selfMethod, 'Hard serializable is forbidden. You are trying to Hard serialize attribute:' + str(attr) + '. You have two choices:' + ' either extend class StructSerializableYou or set the preference attribute HARD_SERIALIZED to True for this apbserver.')                    
                try:
                    import  pickle
                    value='__HardSerialized:' + pickle.dumps(v)
                except:
                    import sys
                    raise repozxception.repozSystemException(str(self.__class__), selfMethod, "Non Hard serializable attribute:" + str(attr) + ':' + str(v)  + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) )

            if not toXml:serList.append({'attrName':attr, 'type':typ, 'value':repr(value)})
            else:serList.append({attr:value})

        if not toXml:return repr(serList)
        else:return serList
        
    def __deepSerialize(self, list=None, index=None):
        selfMethod='__deepSerialize'
        typ=type(list[index])  

        if hasattr(list[index], 'isinstance') and list[index].isinstance('StructSerializable'):
            list[index]=list[index].serialize()                
        ## Not Base type
        elif str(typ).split("'")[1] not in wk.supportedTypes and typ!=type(None):    
            ## Trivial type, try dump
            if not HARD_SERIALIZED:raise repozxception.repozSystemException(str(self.__class__), selfMethod, 'Hard serializable is forbidden. You are trying to Hard serialize attribute:' + str(typ) + '. You have two choices:' + ' either extend class StructSerializable or set the preference attribute HARD_SERIALIZED to True for this apbserver.')
            try:                    
                import  pickle
                list[index]='__HardSerialized:' + pickle.dumps(list[index])
            except:
                import sys
                raise repozxception.repozSystemException(str(self.__class__), selfMethod, "Non Hard serializable attribute:" + str(list[index])  + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]))
 
    def pyDeSerializeToBasic(serStr=None, d='a'):
        selfMethod='pyDeSerializeToBasic'                    
        """ Python programs can use this to make a StructSerializable class
        """
        
        if not StructSerializable._isSerialized(serStr):raise repozxception.repozSystemException(str(serStr) + '_(is not serialized) !', fromClass='Main', fromMethod=selfMethod)                                
            
        ret=StructSerializable()
        serList=_eval(serStr)       
        attr0=serList.pop(0)
        setattr(ret, attr0['attrName'], _eval(attr0['value']))                
        for attr in serList:

            # Basic type
            v=_eval(attr['value'])

            # Begin:Recursive serialization                                        
            if isinstance(v, (tuple, list)):
                for i in range(len(v)):
                    StructSerializable.__deepDeSerialize(list=v, index=i)                        
                        
            elif isinstance(v, dict):
                for k in v:
                    StructSerializable.__deepDeSerialize(list=v, index=k)
            # End:Recursive serialization
            
            elif StructSerializable._isSerialized(v):v=StructSerializable._pyDeSerializeToOg(v)                                                        
            elif StructSerializable.__isHardSerialized(v):                        
                try:
                    ## Trivial type, try load                    
                    if not HARD_SERIALIZED:raise repozxception.repozSystemException('Main', selfMethod, 'Hard serializable is forbidden. You are trying to Hard serialize attribute:' + str(attr) + '. You have two choices:' + ' either extend class StructSerializableYou or set the preference attribute HARD_SERIALIZED to True for this apbserver.')
                    import pickle      
                    v=pickle.loads(v[17:])                                  
                except:
                    import sys
                    raise repozxception.repozSystemException('Main', selfMethod, "Non Hard Unserializable attribute:" + str(attr)  + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) )
                                                        
            setattr(ret, attr['attrName'], v) 
            
        return ret            

    def __deepDeSerialize(list=None, index=None):
        selfMethod='__deepDeSerialize'
        if StructSerializable._isSerialized(list[index]):
            list[index]=StructSerializable._pyDeSerializeToOg(list[index])
        elif StructSerializable.__isHardSerialized(list[index]):
            try:
                ## Trivial type, try load
                if not HARD_SERIALIZED:raise repozxception.repozSystemException('Main', selfMethod, 'Hard serializable is forbidden. You are trying to Hard serialize attribute. You have two choices: either extend class StructSerializableYou or set the preference attribute HARD_SERIALIZED to True for this apbserver.')
                import pickle      
                list[index]=pickle.loads(list[index][17:])                                  
            except:
                import sys
                raise repozxception.repozSystemException('Main', selfMethod, "Non Hard Unserializable attribute:" + str(list[index])  + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) )

    def pyDeSerializeToOg(serStr=None):
        selfMethod='pyDeSerializeToOg'            
        """Python programs can use this to make an Original class.
        """
        if not StructSerializable._isSerialized(serStr):raise repozxception.repozSystemException(str(serStr) + '_(is not serialized) !', fromClass='Main', fromMethod=selfMethod)                        
    
        ser=StructSerializable._pyDeSerializeToBasic(serStr)   
        # Create instance            
        strMod=ser.className.split('.')
        strMod.pop()
        strMod=".".join(strMod)              
        
        try:
            if strMod=='main':raise('Unable to serialize/deserialize from module main!')
            mod=getModule(strMod)            
        except:
            raise
            #return ser
        
        ret=getattr(mod, ser.className.split('.').pop())(forDeSerial=True)
        delattr(ser, 'className')
   
        # Implements attributes
        attrs=dir(ser)
        for attr in attrs:
            if attr[0]=='_':continue            
            if attr[:3]=='get':continue  
            
            typ=getAttrType(ser, attr)
            if typ!='instancemethod':                            
                setattr(ret, attr, getattr(ser, attr))
                
        if hasattr(ret, 'deSerialize'):ret.deSerialize()                
        
        return ret

    def isSerialized(st):
        if  not isinstance(st, (str)): 
            return False
        
        if st.startswith("[{'attrName': 'className',") or st.startswith("[{\'attrName\': \'className\',"):
            return True
        
        return False
    
    def _isHardSerialized(st):
        if  not isinstance(st, (str)): 
            return False
        
        if st.startswith("__HardSerialized:"):
            return True
        return False
    
    def getDontSerialize(self):
        if  hasattr(self, 'dontSerialize'):return self.dontSerialize
        return None

    def getDoSerialize(self):
        if  hasattr(self, 'doSerialize'):return self.doSerialize
        return None

    _serialize=staticmethod(_serialize)
    _pyDeSerializeToBasic=staticmethod(pyDeSerializeToBasic)
    _pyDeSerializeToOg=staticmethod(pyDeSerializeToOg)
    __deepDeSerialize=staticmethod(__deepDeSerialize)
    _isSerialized=staticmethod(isSerialized)
    __isHardSerialized=staticmethod(_isHardSerialized)