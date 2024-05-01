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


# 2015/05/21  | 001 | Default value is no longer required !


from . import attrxception
from . import wk
from . import ct
try:
    from .repoztools import _Apb_isinstance
except:from .tools import _Apb_isinstance

import io
import re
ATTRMK_RE=re.compile(r'[\(\)]')
SINGLES={'LoadedPRFiles':dict()}
INTERNAL_VARIABLE_CAR='_'

import threading
import optparse
lock_LoadedPRFile=threading.Lock()  



def getLoadedPRFile(file):
    if 'file' in SINGLES['LoadedPRFiles']:return SINGLES['LoadedPRFiles']['file']
    return None

def setLoadedPRFile(file, value):
    selfMethod='setLoadedPRFile'
    if not isinstance(file, str):raise attrxception.attrmkParameterTypeException('Main', selfMethod, 'file', 'str', str(file))
    if not isinstance(value, dict):raise attrxception.attrmkParameterTypeException('value', 'dict', str(value))
    
    succeed=lock_LoadedPRFile.acquire(0)
    if not succeed:raise attrxception.attrmkSystemException('Main', selfMethod, 'Impossible to acquire lock on single ressource, trying to save characteristics for attribute file:' + str(file) + '.')
    SINGLES['LoadedPRFiles']['file']=value
    lock_LoadedPRFile.release()



class AttrMaker(dict):
    
    def __init__(self, files=None, doCrypt=False, doCoolTyping=False, doAppend=False, doReadOnly=False, doAllowSave=True, doForce=False, doTemplate=False, temp_vars=None, doSingle=False):
        selfMethod='__init__'
        self.attrDescs=dict()
        self.__repoz=None
        
        if files!=None and not isinstance(files, list):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'files', 'list', str(files))                  
        if files!=None:
            for file in files:self.addFile(file, doCrypt=doCrypt, doCoolTyping=doCoolTyping, doAppend=doAppend, doReadOnly=doReadOnly, doAllowSave=doAllowSave, doForce=doForce, doTemplate=doTemplate, temp_vars=temp_vars, doSingle=doSingle)

    def getRepozInfos(self):
        if self.__repoz==None or self.__repoz()==None:return None
        return {'repoz': self.__repoz(), 'alias': self.__alias}
    
    def setRepozInfos(self, repoz, alias):
        import weakref
        self.__repoz=weakref.ref(repoz)   
        self.__alias=alias

    def clearRepozInfos(self):
        self.__repoz=None
        self.__alias=None
           
    def newPR(alias=None, file_desc=None, file_source=None, doCrypt=False, doCoolTyping=False, doAppend=False, doReadOnly=False, doAllowSave=True, doForce=False, doTemplate=False, temp_vars=None, doSingle=False):
        
        pr=AttrMaker()
        pr.addAttrDesc(file_desc, alias=alias)
        pr.addFile(file_source, alias=alias, attrDesc=alias, doCrypt=doCrypt, doCoolTyping=doCoolTyping, doAppend=doAppend, doReadOnly=doReadOnly, doAllowSave=doAllowSave, doForce=doForce, doTemplate=doTemplate, temp_vars=temp_vars, doSingle=doSingle)
        return pr
    
    def addAttrDesc(self, file, alias=None):
        """
        self.attrDescs[alias]['file'] : real file name
        self.attrDescs[alias]['attributes'] : attribute descriptor
        self.attrDescs[alias]['helps'] : attribute help
        """
        selfMethod='addAttrDesc'

        import os
        from .ct import _eval
        if not isinstance(file, str):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'file', 'str', str(file))
        if not os.path.isfile(file):raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(file) + ' Must Exist.')
        if not alias!=None and isinstance(alias, str):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'alias', 'str', str(alias))                  
        if alias==None:alias=(file.split(os.path.sep)).pop()
        if alias in self.attrDescs:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'A File desc with the alias: ' + alias + ' has already been added for file:' + self.attrDescs[alias]['file'] + ', please explicitly specify another one.')                                    

        self.attrDescs[alias]=dict()
        self.attrDescs[alias]['lFile']=file
        self.attrDescs[alias]['file']=file
        ## register the attributes
        self.attrDescs[alias]['attributes']=dict()
        self.attrDescs[alias]['attrHelps']=dict()
        self.attrDescs[alias]['attrOrders']=[]
        ## save the real file name

        f=open(file, 'r')        
        l=f.readlines()            
        f.close()
        
        dct_vars={}
        dct=self.attrDescs[alias]['attributes']
        attrHelps=self.attrDescs[alias]['attrHelps']
        attrOrders=self.attrDescs[alias]['attrOrders']
        passed=False
        for line in l:
            line=line.strip()
            if line.startswith('#') or line.isspace() or line =='' or line =='\n':continue  
            line, contentHelp=self.__extractHelp(line)
            
            i=line.find('=')            
            
            passed=True
            if i < 0:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + file + ', Line: ' +  line + ', key and value have no = separator.')                            
            key=line[0:i].strip()
            content=line[i+1:].strip()

            dct_vars[key]=content
            ## Operate replace variable
            content=self.replaceVar(content, dct_vars)
            if key.startswith(INTERNAL_VARIABLE_CAR):continue
                        
            _wk=content
            if not content.startswith('{') and not content.endswith('}') < 0:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + file + ', Line: ' +  line + ', key value:' + content + ' should be  enclosed by "{" and "}" !')
            if content.find('"')>=0 or content.find("'")>=0:_wk=_eval(_wk)
            else:_wk=ct.dress(_wk)
            wk.isWKDefinition(_wk, class_exit=self.__class__, method_exit=selfMethod)
            # checkDefault Value
            # D001: if not _wk.has_key('*value') or str(_wk['*value'])==None:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File:' + file + ' Attribute:' + key + ', wk should have a Default value. Your wk:' + str(_wk) + '. ')
            _wk.update({'*withCoolTyping':True})
            
            self.__extractHelp(line)
            dct[key]=_wk
            attrHelps[key]=contentHelp
            attrOrders.append(key)
            
        if not passed:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File:' + file + ' seems being empty.')
        
        return alias
        
    def __extractHelp(line):
        """ grab help content """
        selfMethod='addAttrDesc_extractHelp'
        if line.strip().startswith('__help__'):raise attrxception.attrmkSystemException('Main', selfMethod, 'Line: ' +  line + ', an help decorator must be associated with an attribute.', fromClass='AttrMaker', fromMethod=selfMethod)
        spl=line.split('__help__')            
        if len(spl)>2:raise attrxception.attrmkSystemException('Main', selfMethod, 'Line: ' +  line + ', a line allow only one help decorator "__help__".', fromClass='AttrMaker', fromMethod=selfMethod)
        contentHelp=''
        if len(spl)==2:contentHelp=spl[1].strip()
        line=spl[0]
        if contentHelp!='' and not contentHelp.startswith('='):raise attrxception.attrmkSystemException('Main', selfMethod, 'Line: ' +  line + ', the help decorator shape is "__help__=some text to comment this attribute. And more comments. And more comments again."', fromClass='AttrMaker', fromMethod=selfMethod)
        contentHelp=contentHelp[1:]
        return line, contentHelp
        
    def replaceVar(content, dct):
        """ Operate replace variable """
        from .tmplmaker import MARK_SINGLE
        
        for key in dct:
            patern=MARK_SINGLE + key
            if content.find(patern)>=0:
                value=dct[key]
                if isinstance(value, (list, tuple, dict)):value=ct.unDress(value)                      
                else:value=str(value)
                content=content.replace(patern, value)
        return content

    def addFile(self, file, alias=None, except_defs=None, doCreate=False, doCrypt=False, attrDesc=None, doCoolTyping=False, doAppend=False, doReadOnly=False, doAllowSave=True, doForce=False, doTemplate=False, temp_vars=None, doSingle=False):
        """        
        file : The attribute file path.
        alias (Default:None)        : operational alias to operate on this attribute file.
        self[alias]['doCrypt']      : (Default:False) : is this file need to be decrypted on read and crypted on write ?
        self[alias]['attrDesc']     : (Default:None) : alias of the attributes descriptor of this attribute file (if has one).
        self[alias]['doCoolTyping'] : (Default:False) : does CoolTyping need to be applied on read/write for this attribute file ?
        self[alias]['doAppend']     : (Default:False) : must += operator be detected (as = operator is) ?
        self[alias]['doReadOnly']   : (Default:False) : is write allowed on this attribute file ? 
        self[alias]['doTemplate']   : (Default:False) : must template tools be applied on this attribute file.
        self[alias]['doSingle']     : (Default:False) : does this attribute file instance must be unique for the module.
        
        if doSingle is set, doReadOnly will be set to True.

        temp_vars (Default:None) : must be set to a dict of var:value if doTemplate is True.

        if this attribute file as a file descriptor Cooltyping will be set to True (for later use in write method).
        """
        selfMethod='addFile'

        import os
        
        if not os.path.isfile(file):
            if doCreate:
                fd=open(file, 'wb')
                fd.close()
            else:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + file + ' Must Exist.')                                    
        if alias!=None and not isinstance(alias, str):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'alias', 'str', str(alias))                  
        if not isinstance(doCrypt, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doCrypt', 'bool', str(doCrypt))                  

        if alias==None:alias=(file.split(os.path.sep)).pop()
        if alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'A File with the alias: ' + alias + ' has already been added for file:' + self[alias]['file'] + ', please explicitly specify another one.')                                    
        if except_defs!=None and not isinstance(except_defs, (list, tuple)):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'except_defs', 'list/tuple', str(except_defs))
        if attrDesc!=None and not isinstance(attrDesc, str):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attrDesc', 'str', str(attrDesc))
        if attrDesc!=None and not attrDesc in self.attrDescs:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'A File with the attrDesc: ' + attrDesc + ' has not been defined, use addAttrDesc() first.')

                
        if not isinstance(doCoolTyping, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doCoolTyping', 'bool', str(doCoolTyping))
        if not isinstance(doAppend, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doAppend', 'bool', str(doAppend))
        if not isinstance(doReadOnly, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doReadOnly', 'bool', str(doReadOnly))
        if not isinstance(doAllowSave, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doAllowSave', 'bool', str(doAllowSave))
        if not isinstance(doForce, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doForce', 'bool', str(doForce))
        if not isinstance(doTemplate, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doTemplate', 'bool', str(doTemplate))
        if not isinstance(doSingle, bool):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'doSingle', 'bool', str(doSingle))
        if temp_vars!=None and not isinstance(temp_vars, dict):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'temp_vars', 'dict', str(temp_vars))
        if doTemplate and temp_vars==None:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + file + ' If doTemplate is set, temp_vars should be set.')                                    
        if doSingle:doReadOnly=True
        
        self[alias]=dict()
        
        ## Treat single
        if doSingle:
                lpr=getLoadedPRFile(file)
                if lpr!=None:
                    self[alias]=lpr
                    return alias
        
        ## save the real file name
        self[alias]['lFile']=file
        self[alias]['file']=file
        ## register the attributes
        self[alias]['attributes']=dict()
        ## register the attributes descriptor
        self[alias]['nickDesc']=attrDesc
        self[alias]['doCrypt']=doCrypt
        self[alias]['doCoolTyping']=doCoolTyping # ok
        self[alias]['doAppend']=doAppend
        self[alias]['doReadOnly']=doReadOnly # ok
        self[alias]['doAllowSave']=doAllowSave # ok
        self[alias]['doForce']=doForce # ok
        self[alias]['doTemplate']=doTemplate #
        self[alias]['temp_vars']={}
        if temp_vars!=None:self[alias]['temp_vars']=temp_vars
        self[alias]['doSingle']=doSingle # ok
        
        #f814290522f79d1e9e5ae4ae83e967b4
            
        f=open(file, 'r')
        
        if self[alias]['doCrypt']:
            import security
            fs=security.decrypt(_base64=f.read())
            l=fs.split('\n')
        else:l=f.readlines()            
        f.close()
        
        ## Treat doTemplate:
        if self[alias]['doTemplate'] and temp_vars!={}:
            import template
            l=template.replaceVar(listIn=l, vars=temp_vars)
        
        dct=self[alias]['attributes']
        for line in l:
            line=line.strip()
            if line.startswith('\n'):line=line[1:]
            if line.startswith('#') or line ==''  or line.startswith('\n') or line.isspace():continue            
            i=line.find('=')            

            if i < 0:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + file + ', Line: ' +  str(line) + ', key and value have no = separator.')
            key=line[0:i].strip()
            if key.endswith('+') and not self[alias]['doAppend']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + file + ', Line: ' +  str(line) + "+= operator is forbiden if you don't use doAppend=True !")
                
            content=line[i+1:].strip()

            ## Operate replace variable
            content=self.replaceVar(content, dct)
            
            ## Treat CoolTyping:
            if self[alias]['doCoolTyping']:content=ct.dress(content)

            ## Treat Append:
            if self[alias]['doAppend']:
                if key.endswith('+'):
                    key=key[:-1].strip()
                    content=self.__append(content, key, dct)
           
            dct[key]=content

        if attrDesc==None or len(dct)==0:return alias
        ## Treat CoolTyping (for later use in write method):
        self[alias]['doCoolTyping']=True

        ## Erase internal variables
        for key in list(dct.keys()):
            if key.startswith(INTERNAL_VARIABLE_CAR):del dct[key]
  
        try:
            p=self.__checkAttrDesc(alias=attrDesc, attributes=dct, except_defs=except_defs)
            self[alias]['attributes'].clear()
            _l=dir(p)
            for attr in _l:
                if attr.startswith('_'):continue
                self[alias]['attributes'][attr]=getattr(p, attr)            
        except Exception as e:
            raise
            del self[alias]                
            raise e             

        ## Treat single
        if self[alias]['doSingle'] and getLoadedPRFile(self[alias]['file'])==None:setLoadedPRFile(self[alias]['file'], self[alias])
        
        return alias

    def __append(content, key, dct):
        selfMethod='append'
        SUPPORTED_TYPES=('str', 'int', 'tuple', 'list', 'dict')                
        
        if key not in dct:return content
        if type(content)!=type(dct[key]):raise attrxception.attrmkSystemException('Main', selfMethod, 'Attribute:' + str(key) + ' Operator:+=, must keep the same type between appends. Previous value:' + str(type(dct[key])) + '. Actual value:' + str(type(content)) + '.', fromClass='AttrMaker', fromMethod=selfMethod)
        if isinstance(content, str):content+=content
        elif isinstance(content, int):content+=content            
        elif isinstance(content, tuple):
            content=list(content)
            content.extend(dct[key])
            content=tuple(content)
        elif isinstance(content, list):content.extend(dct[key])
        elif isinstance(content, dict):
            content.update(dct[key])
        else:raise attrxception.attrmkSystemException('Main', selfMethod, 'Attribute:' + str(key) + ' Operator:+=, Type:' + str(type(content)) + ' is unsupoorted for this operation. Supported types are:' + str(SUPPORTED_TYPES) + '.', fromClass='AttrMaker', fromMethod=selfMethod)
        
        return content

    def getAttrDesc(self, alias):
        selfMethod='getAttrDesc'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has not been added.')                                    
        attrDesc=self[alias]['nickDesc']        
        if attrDesc==None:return None
        
        dct=self.attrDescs[attrDesc]
        return dct 

    def getFiles(self, alias):
        selfMethod='getFileAttrDesc'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has not been added.')                                    
        return self[alias]['file'], self.getFileDesc(alias)

    def getLogicalFiles(self, alias):
        selfMethod='getLogicalFiles'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has not been added.')                                    
        return self[alias]['lFile'], self.getAttrDesc(alias)['lFile']
        
    def setLogicalFiles(self, alias=None, lFile_source=None, lFile_desc=None):
        """ Only set whith a different value than files if loading an apb resource file. """
        selfMethod='setLogicalFiles'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has not been added.')                                    
        self[alias]['lFile']=lFile_source
        self.getAttrDesc(alias)['lFile']=lFile_desc

    def getFileDesc(self, alias):
        selfMethod='getFileAttrDesc'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has not been added.')                                    
        attrDesc=self[alias]['nickDesc']
        if attrDesc==None:return None
        return self.getAttrDesc(attrDesc)['file']
    
    def __checkAttrDesc(self, alias=None, attributes=None, except_defs=None, isRestraint=False, checkDefault=False):
        selfMethod='__checkAttrDesc'
        if not alias in self.attrDescs:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File desc: ' + alias + ' has not been added.')                                            
        if attributes==None:raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attributes', 'str', str(attributes))
        from kwadlib.repozwkextension import wkExtension

        # Except for: kwad.attrs.descs (a):
        """ The following will only check descriptor attributes with the shape: 'software_<sfw>_' only if they are also 
        present into the kwad.attrs file.
        This will allow the use of the parameter required:True for some software_<sfw>_ entries.
        """
        SOFTWARE_PREFIX = 'software_'
        kattrs_sfw_filters = []
        isKwadAttrs = False
        if alias == 'kwad.attrs.descs':
            isKwadAttrs = True
            import re
            for attr in attributes:
                if not attr.startswith(SOFTWARE_PREFIX):continue
                sfw = re.findall(SOFTWARE_PREFIX + '([a-z0-9]{3})_', attr)
                if not len(sfw)==1:continue
                kattrs_sfw_filters.append(SOFTWARE_PREFIX + sfw[0] + '_')

        
        repoz_infos=self.getRepozInfos()        
        if repoz_infos!=None:wkExtension=wkExtension(repoz_infos['repoz'], repoz_infos['alias'], self)
        else:wkExtension=None

        for attr in attributes:    
            if not attr in self.attrDescs[alias]["attributes"]:raise attrxception.attrmkUnSupportedAttributeException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ': Your attribute:' + str(attr) + ', is unknown, known attributes are:' + str(list(self.attrDescs[alias]["attributes"].keys())) + '. You should check you attributes descriptor file file:' + str(self.attrDescs[alias]["file"]) + '. ')
            
        attrDescs=self.attrDescs[alias]['attributes']
        p=wk.WantedKeywords()
        for attr in attrDescs:
            if isRestraint and attr not in attributes:continue

            # Except for: kwad.attrs.descs (b):
            """ The following will only check descriptor attributes with the shape: 'software_<sfw>_' only if they are also 
            present into the kwad.attrs file.
            This will allow the use of the parameter required:True for some software_<sfw>_ entries.
            """
            if isKwadAttrs and attr.startswith(SOFTWARE_PREFIX):
                sfw = re.findall(SOFTWARE_PREFIX + '([a-z0-9]{3})_', attr)
                if len(sfw)==1 and SOFTWARE_PREFIX + sfw[0] + '_' not in kattrs_sfw_filters:continue

            # D001: if checkDefault and ( '*value' not in attrDescs[attr] or attrDescs[attr]['*value']==None ):raise attrxception.attrmkAttributeException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ': Your attribute:' + str(attr) + ' descriptor should include a default value, your wk:' + str(attrDescs[attr])  + '. ')
            setattr(p, attr, attrDescs[attr])            
        wk.getKeywords(wantedKeywords=p, keywords=attributes, wkExtension=wkExtension, except_defs=except_defs, class_exit=str(self.__class__), method_exit=selfMethod)

        return p

    def getDoCrypt(self, alias):
        return self[alias]['doCrypt']
    
    def getDoCoolTyping(self, alias):
        return self[alias]['doCoolTyping']
    
    def getDoAppend(self, alias):
        return self[alias]['doAppend']

    def getDoReadOnly(self, alias):
        return self[alias]['doReadOnly']
    
    def getDoAllowSave(self, alias):
        return self[alias]['doAllowSave']    
    
    def getDoForce(self, alias):
        return self[alias]['doForce']
    
    def getDoTemplate(self, alias):
        return self[alias]['doTemplate']
    
    def getTemp_vars(self, alias):
        return dict ( self[alias]['temp_vars'] )
    
    def getDoSingle(self, alias):
        return self[alias]['doSingle']
    
    def getDescAttrs(self, alias):
        return dict ( self.getAttrDesc(alias)['attributes'] )

    def getDescAttrOrders(self, alias):
        attrdesc=self.getAttrDesc(alias)
        if attrdesc!=None:return list ( attrdesc['attrOrders'] )
        l=list(self.getAttrs(alias).keys())
        l.sort()
        return l
    
    def getDescAttrHelps(self, alias):
        attrdesc=self.getAttrDesc(alias)
        if attrdesc!=None:return dict ( attrdesc['attrHelps'] )
        return {}

    def getAttrs(self, alias):
        selfMethod='getAttrs'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')

        return dict(self[alias]['attributes'])

    def setAttrs(self, alias, attributes, checkDefault=False, force=False):
        """ Destructive affectation """
        selfMethod='setAttrs'
        if not force and self[alias]['doForce']:force=self[alias]['doForce']
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')                                            
        ## Treat doReadOnly:
        if self[alias]['doReadOnly']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has not been loaded whith doReadOnly=True.')                                    
        if not force and self.attrDesc==None:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has no descriptor file. Advice: Either use the force parameter or add a descriptor file using AttrMk.addAttrDesc and addFile, or the file_desc parameter.')
        self[alias]['attributes'].clear()
        if attributes==None:return
                
        attrDesc=self[alias]['nickDesc']
        if attrDesc==None:
            self[alias]['attributes'].update(attributes)
            return 
    
        p=self.__checkAttrDesc(alias=attrDesc, attributes=attributes, checkDefault=checkDefault)

        _l=dir(p)
        for attr in _l:
            if attr.startswith('_'):continue
            self[alias]['attributes'][attr]=getattr(p, attr)

    def hasAttr(self, alias, attr):        
        selfMethod='getAttr'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')                                            
        if not isinstance(attr, str) or attr=='':raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attr', 'str', str(attr))            

        if attr not in self[alias]['attributes']:return False
        return True

    def getAttr(self, alias, attr):        
        selfMethod='getAttr'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')                                            
        if not isinstance(attr, str) or attr=='':raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attr', 'str', str(attr))            
        if attr not in self[alias]['attributes']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' Attribute:' + attr + ' is unknown.')
        
        return self[alias]['attributes'][attr]

    def getDft(self, alias, attr, force=True):
        selfMethod='getAttr'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')                                            
        if not isinstance(attr, str) or attr=='':raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attr', 'str', str(attr))            
        if attr not in self[alias]['attributes']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' Attribute:' + attr + ' is unknown.')
        value=None
        
        # D001: attrDesc=self[alias]['nickDesc']['attributes']
        # A001: 
        if self[alias]['nickDesc']!=None:
            attrDescs=self.getDescAttrs(alias)
            # D001: if attrDesc==None:return False
            # A001: 
            wks=self.attrDescs[alias]['attributes'][attr]
            
            # D001: if '*value' in attrDesc:return attrDesc['*value']
            # A001: 
            if '*value' in wks:value=wks['*value']
            
        if force and value==None:
            if self[alias]['nickDesc']==None:return attr.upper()
            if '*type' not in wks: type = 'str'
            else:type=wks['*type']
            if type=='str':return attr.upper()
            elif type=='bool':return False
            elif type in ('int', 'long', 'float'):return 0
            elif type=='list':return [attr.upper()]
            elif type=='tuple':return (attr.upper(),)
            else:return attr.upper()
            
    def eqDft(self, alias, attr, value):        
        if self.getDft(alias, attr)==value:return True
        return False

    def setAttr(self, alias, attr, value, checkDefault=False, force=False):        
        selfMethod='setAttr'
        if not force and self[alias]['doForce']:force=self[alias]['doForce']
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')                                            
        ## Treat doReadOnly:
        if self[alias]['doReadOnly']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has been loaded whith doReadOnly=True.')
        if not isinstance(attr, str) or attr=='':raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attr', 'str', str(attr))            
        attrDesc=self[alias]['nickDesc']
        if not force and attrDesc==None:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has no descriptor file. Advice: Either use the force parameter or add a descriptor file using AttrMk.addAttrDesc and addFile, or the file_desc parameter.')

        if attrDesc==None:
            self[alias]['attributes'].update({attr:value})
            return         

        p=self.__checkAttrDesc(alias=attrDesc, attributes={attr:value}, isRestraint=True, checkDefault=checkDefault)

        _l=dir(p)
        for attr in _l:
            if attr.startswith('_'):continue
            self[alias]['attributes'][attr]=getattr(p, attr) 
            
    def delAttr(self, alias, attr, force=False):     
        selfMethod='delAttr'
        if not force and self[alias]['doForce']:force=self[alias]['doForce']
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')
        ## Treat doReadOnly:
        if self[alias]['doReadOnly']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has been loaded whith doReadOnly=True.')
        if not isinstance(attr, str) or attr=='':raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attr', 'str', str(attr))            
        if not self.hasAttr(alias, attr):return

        del self[alias]['attributes'][attr] 
        attrDesc=self[alias]['nickDesc']
        if not force and attrDesc==None:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has no descriptor file. Advice: Either use the force parameter or add a descriptor file using AttrMk.addAttrDesc and addFile, or the file_desc parameter.')
        if attrDesc==None:return
 
        p=self.__checkAttrDesc(alias=attrDesc, attributes={attr:None}, isRestraint=True)
        
    def delAttrs(self, alias, force=False):
        selfMethod='delAttrs'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + str(alias) + ' has not been added.')
        ## Treat doReadOnly:
        if self[alias]['doReadOnly']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has been loaded whith doReadOnly=True.')
        attrDesc=self[alias]['nickDesc']
        if not force and attrDesc==None:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has no descriptor file. Advice: Either use the force parameter or add a descriptor file using AttrMk.addAttrDesc and addFile, or the file_desc parameter.')                                    

        attrs=list(self[alias]['attributes'].keys())
        for attr in attrs:
            del self[alias]['attributes'][attr] 
            if attrDesc!=None:p=self.__checkAttrDesc(alias=attrDesc, attributes={attr:None}, isRestraint=True)
            
    def getView(self, alias=None, view=None, message=None):
        selfMethod='getView'
        try:
             import apy.view as xview
        except:
            raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'This method is supposed to work into AskApy only. Check the AskApy project for more information.')

        if not isinstance(alias, str) or alias=='':raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'alias', 'str', str(alias))
        
        attrDescs=self.getDescAttrs(alias)
        attrOrders=self.getDescAttrOrders(alias)
        attrs  = self.getAttrs(alias)

        p=xview.vw.Page(name='alias')
        view.setPage(p)

        p.add( xview.vw.InputHidden(name='xall', value='True') )
        p.add( xview.vw.InputHidden(name='file_source', value=self.getLogicalFiles(alias)[0] ) )
        p.add( xview.vw.InputHidden(name='file_desc', value=self.getLogicalFiles(alias)[1] ) )
        p.add( xview.vw.InputHidden(name='xdoCrypt', value=self.getDoCrypt(alias)) )
        p.add( xview.vw.InputHidden(name='xdoCoolTyping', value=self.getDoCoolTyping(alias)) )
        p.add( xview.vw.InputHidden(name='xdoAppend', value=self.getDoAppend(alias)) )
        p.add( xview.vw.InputHidden(name='xdoReadOnly', value=self.getDoReadOnly(alias)) )
        p.add( xview.vw.InputHidden(name='xdoTemplate', value=self.getDoTemplate(alias)) )
        p.add( xview.vw.InputHidden(name='xtemp_vars', value=ct.unDress(self.getTemp_vars(alias))) )
        p.add( xview.vw.InputHidden(name='xdoSingle', value=self.getDoSingle(alias)) )

        mtable=xview.vw.Table()
        p.add(mtable)
        tr=xview.vw.Tr()
        mtable.add(tr)
        
        table=xview.vw.Table()
        tr.add(table)
        tr=xview.vw.Tr()
        table.add(tr)
        tdc=xview.vw.Td()
        tr.add(tdc)
        tdhelp=xview.vw.Td()
        tr.add(tdhelp)
    
        #--# Help
        
        table=xview.vw.Table(cellspacing=20, cellpadding=0)
        tdhelp.add(table)
        tr=xview.vw.Tr()
        table.add(tr)
        xview.vw.tmplHelp(view=view, comp=tr, pzheight='80%', pzwidth=100)
        
        #--# Content
        
        table=xview.vw.Table()
        tdc.add(table)
        tr=xview.vw.Tr()
        table.add(tr)
        tr.add(xview.vw.Br())        
        tr=xview.vw.Tr()
        table.add(tr)
        ttitle=xview.vw.Td(align=xview.vw.vw_CENTER)
        tr.add(ttitle)

        tr=xview.vw.Tr()
        table.add(tr)
        tdheader=xview.vw.Tr()
        table.add(tdheader)
        
        tr=xview.vw.Tr()
        table.add(tr)
        tdbody=xview.vw.Td()
        tr.add(tdbody)
        tfooter=xview.vw.Tr()
        table.add(tfooter)

        #----# Title
        
        ttitle.add(xview.vw.Label(self.getLogicalFiles(alias)[0]))

        #----# Header
        
        table=xview.vw.Table(border=1, bgcolor='#95FFF6', cellspacing=20, cellpadding=0)
        tdheader.add(table)

        ## Select
        tr=xview.vw.Tr()
        table.add(tr)
        s=xview.vw.Select(name='xattr', multiple=False, length=1)
        for attr in attrOrders:s.addRow({'value':attr, 'display_value':attr, 'isSelected':False})
        tr.add(s)

        ## Button
        tr.add(xview.vw.Br())
        td=xview.vw.Td()
        tr.add(td)
        sb=xview.vw.SButton('Create', name='xcreate')
        sb.beParameter()
        sb.setTarget(xview.vw.vwSELF)
        td.add(sb)
        sb=xview.vw.SButton('Delete', name='xdelete')
        sb.beParameter()
        sb.setTarget(xview.vw.vwSELF)
        td.add(sb)
        
        #----# Body 

        for attr in attrOrders:

            if attr in attrs:
                # Label
                tdbody.add(xview.vw.Label(attr))
            
                tdbody.add(xview.vw.WKDefinition(name=attr, wk=attrDescs[attr], value=attrs[attr]))
                tdbody.add(xview.vw.Br())                   

        #----# Footer
        
        ## Buttons
        table=xview.vw.Table(border=1, bgcolor='#95FFF6', cellspacing=20, cellpadding=0)
        tfooter.add(table)
        tr=xview.vw.Tr()
        table.add(tr)
        sb=xview.vw.SButton('Update', name='xupdate')
        sb.beParameter()
        sb.setTarget(xview.vw.vwSELF)
        tr.add(sb)
        tr=xview.vw.Tr()
        table.add(tr)
        sb=xview.vw.SButton('Save...', name='xsave')
        sb.beParameter()
        sb.setTarget(xview.vw.vwSELF)
        tr.add(sb)
        tr.add(xview.vw.Br())
        i=xview.vw.InputText(name='xtofile', length=6, value='')
        tr.add(i)
        tfooter.add(xview.vw.Br())

        #--# msg

        if message not in ('', None):p.add(xview.vw.PopUp(name='Alert', pzheight=250, pzwidth=250, value=message, frcolor=xview.vw.vw_RED))

        return view    

#-----#
# aql #
#-----#

    def cde(self, alias, cde, sb=None):
        """ Facade for Repository """
        return self.aql(alias, aqlString=cde, sb=sb) 

    def aql(self, alias, aqlString=None, sb=None):
        """
        Samples are better than spared words.
        
        aql supports four family of orders : 
        
        1 select
        
        select order : select or ccselect:
        
        1.1 description 
        
            select orders return a list of matching tags.
            
            These selects differs by the way they organize the result.

            Let suppose that these two tags match a select request:
            
            select returns a tabbed formatted text of the returned attributes like sql does.
                ex:
                                    attr1       attr3                     

                                    value10     value30               
                                    value11     value31             
                                    value12     value32               
      

            ccselect returns a CoolTyped expression of the returned attribute.
                ex:
                    {ATTR10:value10,ATTR3:value30}

                This tag's CoolTyped expression can be used into xql orders.

        1.2 syntax

            select
            ccselect
            select O_WHAT where F_ATTRS
            See Filter for F_TAGS and F_ATTRS possibly values.
            
            example:
            -------
            select attr2,attr4 where name=georges
            select attr2,attr4 where (name=georges or name=jules) and adresse=toronto

            Note:
                Attributes comparaison operators are : =, <=, >=, <, >, <>, *between, *in.
                Attributes comparaison criterions can be imbricated into parenthesis.
                
            For more information about criterions and F_TAGS or F_ATTRS,
            from a command line type: doc.py afilter.


        2 update
        
        update order : update
        
        2.1 description 
        
            update the given attribute.

        2.2 syntax
        
            update set O_SET
            
            example:
            -------
            update set name=charlie, address=105 breakstreet


        3 delete
        
        delete order : delete
        
        3.1 description 
        
            delete the given attribues.

        3.2 syntax
        
            delete F_ATTRS
            
            example:
            -------
            delete attr1, attr2
        
        
        
        Note :
        aql attributes and values are cases sensitives.
        
        
        Each request have an order part and a filter part.
        In the following samples in the code, these two parts are respectfully signaled by :
        ___________ (Order part)
        ----------- (Filter part)
        """
        selfMethod='aql'
        SUPPORTED_SELECT_ORDERS=('select', 'ccselect')
        SUPPORTED_ORDERS=list(SUPPORTED_SELECT_ORDERS)
        SUPPORTED_ORDERS.extend(['update','delete'])
        SUPPORTED_ORDERS=tuple(SUPPORTED_ORDERS)
        if not isinstance(aqlString, str) or aqlString=='' or len(aqlString)*' '==aqlString:raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'aqlString', 'str', str(aqlString))
        _aqlString=aqlString.strip()
        i=_aqlString.find(' ')
        o_name=_aqlString[:i]
        _aqlString=_aqlString[i:].strip()
        
        if o_name not in (SUPPORTED_ORDERS):raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'aql: The order:' + str(o_name) + ' is not a supported order. Supported orders are:' + str(SUPPORTED_ORDERS) + '. Your request:' + aqlString + '.')
        
        if o_name in SUPPORTED_SELECT_ORDERS:return self.__aql_select(alias, o_name, _aqlString, sb=sb)
        if o_name=='update':return self.__aql_update(alias, o_name, _aqlString, sb=sb)
        if o_name=='delete':return self.__aql_delete(alias, o_name, _aqlString, sb=sb)
        
    def __aql_select(self, alias, o_name, aqlString, sb=None):
        SELECT_ATTR_MAX_LEN=20
        SELECT_MARGE=20
        """
        # =======
        # SYNTAXE:
        # =======
        #
        # select
        # ccselect
        # select O_WHAT at F_TAGS where F_ATTRS
        # See Filter for F_TAGS and F_ATTRS possibly values.
        # example:
        # =======
        # select attr2,attr4 where name=georges
        # select attr2,attr4 where (name=georges or name=jules) and adresse=toronto
        # ___________________ -------------------------------------------------------------------
        ## Tests
        # select at31,at32 where at31=bbbbbbbbb
        """
        selfMethod='__aql_select'
        founds={}
        
        _aqlString=aqlString

        ## ORDER ##
        error_what_not_found=attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'aql:' + o_name + ':The O_WHAT clause is not defined in your request. Supported O_WHAT clauses are: * or ATTR1,ATTR2,...,ATTRN. Your request:' + o_name + ' ' + aqlString + '.')
        message_general='aql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + aqlString + '. SubException is:'

        ## o_what
        o_what=[]
        i=_aqlString.find(' where ')
        if i<=0:
            what=_aqlString.strip()
            _aqlString=''
        else:
            what=_aqlString[:i].strip()
            _aqlString=_aqlString[i+7:].strip()
        
        if what!='*':
            spl=what.split(',')
            for s in spl:
                if s=='' or s==len(s)*' ':continue
                o_what.append(s)
            if o_what==[]:raise error_what_not_found
            o_what=[w for w in o_what]
            
        else:o_what=what
           
            
        ## FILTER ##
        try:
            f_attrs, f_attrs_skel=self.__aql_getFilter(_aqlString)
            filter=Filter(fattrs=f_attrs, fattrs_skel=f_attrs_skel)
            ## See the docstring of class Filter to understand how it works.
            extraAttrs=[]
            if o_what!='*':extraAttrs=o_what
            wrk=WorkFilter(alias, self, filter=filter, extraAttrs=extraAttrs)
            fok=wrk.doFilter()
        except Exception as e: 
            _e=attrxception.attrmkSystemException(str(self.__class__), selfMethod, message_general + str(e))
            _e.setSubException(e)
            raise _e


        ## DO ORDER ##
        # ccselect and rrselect : return a colltyped type and not a listing like the others.

        if o_name=='select' and o_what!='*':self.__whead(o_what, sb)
 
        if not fok:return

        if o_name=='select':
            """
                    select returns a tabbed formatted text of the returned attributes like sql does.
                        ex:
                                            attr1       attr3                     

                                            value10     value30               
                                            value11     value31             
                                            value12     value32               
              
            """

            ## head
            what=o_what
            if o_what=='*':
                sb.write('\n')
                _l=self.getDescAttrOrders(alias)
                what=[ attr for attr in _l if attr in self.getAttrs(alias) ]
                self.__whead(what, sb)
            
            ## body
            fbody=' '*SELECT_MARGE + len(what)* ( ' %-' + str(SELECT_ATTR_MAX_LEN) + 's' )
            l=[]
            for attr in what:
                value=self.getAttr(alias, attr)
                founds[attr]=value
                l.append(ct.unDress(value))
                
            sb.write(fbody % tuple(l))   
            sb.write('\n')
            
            return founds
            
        elif o_name=='ccselect':
            """

        ccselect returns a CoolTyped listing of the returned tags.
            ex:
                {ATTR10:value10,ATTR3:value30}

            These tags dict can be used by ccreate order
            """

            # cselect returns a CoolTyped list of the returned attribute
            # ex: [value10,value30]

            if o_what=='*':
                values=self.getAttrs(alias)
                founds=dict(values)
                sb.write( ct.unDress(values) )
            else:
                # otherwise return the attributes list.
                l=[]
                for attr in o_what:
                    value=self.getAttr(alias, attr)
                    founds[attr]=value
                    l.append(value)
                sb.write(ct.unDress(l))
    
    def __whead(what, sb):
        SELECT_ATTR_MAX_LEN=20
        SELECT_MARGE=20
        fhead=' '*SELECT_MARGE + len(what)* (' %-' + str(SELECT_ATTR_MAX_LEN) + 's' )
        sb.write(fhead % tuple(what))
        sb.write('\n')

    def __aql_update(self, alias, o_name, aqlString, sb=None):
        """
        update set O_SET
        example:
        =======
        update set name=charlie, address=105 breakstreet
        ______ -------------------------------------------------------------------------------
        """
        selfMethod='__aql_update'
        _aqlString=aqlString

        ## ORDER ##
        error_set_not_found=attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'aql:' + o_name + ':The O_SET clause is not defined in your request. Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;...;ATTRN=VALUEN. Your request:' + o_name + ' ' + aqlString + '.')
        message_general='aql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + aqlString + '. SubException is:'

        ## o_set
        i=_aqlString.find('set ')
        if i<0:raise error_set_not_found
        
        try:
            o_set={}
            set=_aqlString[i+4:].strip()
            _aqlString=_aqlString[:i].strip()

            spl=set.split(';')
            for s in spl:
                if s=='' or s==len(s)*' ':continue
                spl=s.split('=')
                if spl[0]=='' or len(spl)!=2:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'aql:' + o_name + ':The portion:' + s + 'of your O_SET clause is incorrect. Your set clause:' + set + 'Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXTS=[TEXT_LINE1,TEXT_LINE2,...,TEXT_LINEN];...;ATTRN=VALUEN.')
                attr=spl[0].strip()
                value=ct.dress(spl[1])
                o_set[attr]=value   
            if o_set=={}:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'aql:' + o_name + ':Your O_SET clause is incorrect. Your set clause:' + set + 'Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXTS=[TEXT_LINE1,TEXT_LINE2,...,TEXT_LINEN];...;ATTRN=VALUEN.')
        except Exception as e:
            _e=attrxception.attrmkSystemException(str(self.__class__), selfMethod, message_general + str(e))
            _e.setSubException(e)
            raise _e


        ## NO FILTER ##

        ## DO ORDER ##

        try:
            for attr in o_set:
                sb.write('Updating attr:' + attr + '\n')
                self.setAttr(alias, attr, o_set[attr])
        except Exception as e:
            _e=attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'aql:' + o_name + ':Error updating attribute:' + attr + '. SubException is:' + str(e))
            _e.setSubException(e)
            raise _e
        
        sb.write('\n')

    def __aql_delete(self, alias, o_name, aqlString, sb=None):
        """
        delete F_ATTRS
        example:
        =======
        delete attr1, attr2
        ______ --------------------------------------------------------------
        """
        selfMethod='__aql_delete'
        _aqlString=aqlString
        
        ## ORDER ##
        message_general='aql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + aqlString + '. SubException is:'

        try:
            what=aqlString
            _l=self.getDescAttrOrders(alias)
            if what=='*':what=[ attr for attr in _l if attr in self.getAttrs(alias) ]            
            else:
                _l=what.split(',')
                what=[attr.strip() for attr in _l]
        
            ## DO ORDER ##
            sb=io.StringIO()
            
            for attr in what:
                sb.write(' '*4 + 'Deleting attr:' + attr + '.\n')           
                self.delAttr(alias, attr)
                sb.write('\n')
        except Exception as e:
            _e=attrxception.attrmkSystemException(str(self.__class__), selfMethod, message_general + str(e))
            _e.setSubException(e)
            raise _e

    def __aql_getFilter(self, aqlString):
        selfMethod='__aql_getFilter'
        _aqlString=aqlString        
 
        ## f_attrs
        f_attrs=[]
        if _aqlString!='':
            f_attrs_skel=_aqlString

            # Get pair-values
            s=f_attrs_skel.replace(' and ', ')')
            s=s.replace(' or ', ')')
            pv=ATTRMK_RE.split(s)
            
            for s in pv:
                if s=='' or s==len(s)*' ':continue
                
                f_attrs_skel=f_attrs_skel.replace(s, str(len(f_attrs)), 1)
                f_attrs.append(s)
        else:f_attrs_skel='True'
   
        return f_attrs, f_attrs_skel
    
    def show(self, alias, sb=None, doSpaceWrapEq=False, noDft=True, noDftRaise=False, noNone=True):
        """ Facade for Repository """        
        selfMethod='save'
        if not alias in self:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has not been added.')                                    
        spc=''
        if doSpaceWrapEq:spc=' '

        attrOrders=self.getDescAttrOrders(alias)
        attrHelps=self.getDescAttrHelps(alias)
        attrs=self.getAttrs(alias)

        if sb==None:sb=io.StringIO()
        
        for attr in attrOrders:
            value=self.getAttr(alias, attr)
            
            if (noDft and self.eqDft(alias, attr, value)) or (noNone and value==None):continue
            
            if attr not in attrs:continue
            if attr in attrHelps:
                spl= attrHelps[attr].split('\\')
                for line in spl:sb.write('# ' + line + '\n')
            sb.write( attr + spc + '=' + spc + ct.unDress(self.getAttr(alias, attr)) + '\n')
            sb.write('\n')

        if self.getDoCrypt(alias):
            import security
            value=security.encrypt(_base64=sb.getvalue())
            sb.buf=''
            sb.write(value)
        
        return sb

    def save(self, alias, sb=None, toFile=None, **prt_keywords):
        selfMethod='save'
        if self.getDoReadOnly(alias):raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'File: ' + alias + ' has been opened with doReadOnly=True. File cannot been saved.')                                    
        if not self[alias]['doAllowSave']:raise attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'This maker is not allowed to save !')
        file_source, file_desc=self.getFiles(alias)
        file=file_source
        if toFile!=None:file=toFile
        
        fd=open(file, 'wb')
        fd.write(bytes(self.show(alias, sb=sb, **prt_keywords).getvalue(), 'utf-8'))
        fd.close()

    newPR=staticmethod(newPR)
    replaceVar=staticmethod(replaceVar)
    __extractHelp=staticmethod(__extractHelp)
    __append=staticmethod(__append)
    __whead=staticmethod(__whead)



class Filter(_Apb_isinstance):
    _apb_isinstance_Filter='Filter'  

    def __init__(self, fattrs=None, fattrs_skel=None):
        """
        fattrs  a lis of attribute name<OPERATOR>value.
                There are three types of attribute name:
                
                basic attribute name: ATTR_NAME=ATTR_VALUE all tags returned by the ftags check are tested.
                ex: address=tiny street
  
        fattrs_skel
                Skeleton : a numbered conditional String.
                This string have the exact shape of the if clause except that
                it just keep parenthesis and or/and operators.
                Conditions are replaced by numbers in their order of apparition.
                Note this number is their index in precedent fattrs parameter.
                ex: (0 and (1 or 2)) and (3 ) or  4
        """ 
        
        selfMethod='__init__'
        class FAttr:
            OPERATORS={'=':'*eq','<=':'*le','>=':'*ge','<':'*lt','>':'*gt','<>':'*ne','*between':'*between', '*in':'*checkIn'}
            
            def __init__(self, skeleton=None):  
                self.basics=[]
                self.skeleton=skeleton

        if fattrs!=None and not isinstance(fattrs, (list,tuple)):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'fattrs', 'list/tuple', str(fattrs))                            
        if fattrs_skel!=None and not isinstance(fattrs_skel, (str)):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'fattrs_skel', 'str', str(fattrs_skel))                            

        if fattrs==None:fattrs=()
        self.fattr=FAttr(skeleton=fattrs_skel)
        idx=0
        for fattr in fattrs:
            fattr=str(fattr).strip()
            error_unkattr=attrxception.attrmkSystemException(str(self.__class__), selfMethod, 'Unknown Attribute Filter. An attribute filter must be shaped like this: ATTR_NAME <OPERATOR> ATTR_VALUE. Operator must be in:' + str(FAttr.OPERATORS) + '. Your entry: ' +str(fattr) + '.'+ '. Your Attribute Filter string: ' + str(fattrs) + '.')
            
            i=0
            for op in FAttr.OPERATORS:
                i=fattr.find(op)
                if i>0:break
            if i<=0:raise error_unkattr
            
            spl=fattr.strip().split(op)
            if len(spl)!=2 or spl[0]=='':raise error_unkattr
            name=spl[0].strip()
            value=spl[1].strip()
            
            # D001: attrdesc={FAttr.OPERATORS[op]:ct.dress(value), '*required':True}
            # A001: 
            attrdesc={FAttr.OPERATORS[op]:ct.dress(value)}
            wk.isWKDefinition(attrdesc, class_exit=str(self.__class__), method_exit=selfMethod)

            self.fattr.basics.append([name, attrdesc, idx])
            idx+=1



class WorkFilter:
    """ See the docstring of class Filter to understand how it works. """

    def __init__(self, alias, attributeReader, filter=None, extraAttrs=[]):
        selfMethod='__init__'
        if not isinstance(alias, str) or alias=='':raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'alias', 'str', str(alias))
        if not isinstance(attributeReader, AttrMaker):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'attributeReader', 'AttrMaker', str(attributeReader))                        
        if filter==None or not hasattr(filter, 'isinstance') and not filter.isinstance('Filter'):raise attrxception.attrmkParameterTypeException(str(self.__class__), selfMethod, 'filter', 'Filter', str(filter))                        
        self.alias=alias
        self.attributeReader=attributeReader
        self.filter=filter
        self.extraAttrs=extraAttrs
        
    def doFilter(self): 

        alias=self.alias
        atrdr=self.attributeReader
        
        ## Extra Attrs presence prereqsuiste check
        for attr in self.extraAttrs:
            if not atrdr.hasAttr(alias, attr):
                return False

        fattrs_passe=True
        
        skeleton=self.filter.fattr.skeleton
        
        ## basic test
        for attrdefs in self.filter.fattr.basics:
            attr     = attrdefs[0]
            attrdesc  = attrdefs[1]
            skelidx   = attrdefs[2]
            
            fattrs_passe=self.__checkAttr(atrdr, alias, attrdesc, attr)

            skeleton=skeleton.replace(str(skelidx), str(fattrs_passe))

        from .ct import _eval

        fattrs_passe=_eval(skeleton)
        try:
            fattrs_passe=_eval(skeleton)
        except:
            pass
        if not fattrs_passe:return False
        
        return True

    ## fattrs test      ##
    def __checkAttr(self, atrdr, alias, attrdesc, attr): 
        selfMethod='__checkAttr'
        try:
            value=atrdr.getAttr(alias, attr)
        except:
            raise
            return False
        
        passe=False
        try:
            p=wk.WantedKeywords()
            setattr(p, attr, attrdesc)
            wk.getKeywords(wantedKeywords=p, keywords={attr:value,}, class_exit=self.__class__, method_exit=selfMethod)                    
            passe=True
        except:
            pass
        
        return passe
    
    
    
    
#--------------------#
# Processor Commands #
#--------------------#


##=== xpath ===##

def xpath_options(parser):

    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option("-H", "--HELP", dest="HELP", action="store_true", default=False, help="Shows the processor extended options.")
    parser.add_option("-s", "--attr_separator", dest="attr_separator", default=' ', help="Separator when multiple Attributes are returned  (default: space).\nOption --attr_separator (-s) is allowed when not using: --console (-o), --update  (-u), --create (-n) and --remove (-e) options.")    
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False, help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")
    
def save_and_show_options(parser):

    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option('--indent', dest="indent", default=0, type=int, help="Margin for the whole text block.")
    parser.add_option("--space_wrap_eq", dest="space_wrap_eq", action="store_true", default=False, help='(default False) If used, one blank space is writen on the left and rigth of the "=" symbol.')
    parser.add_option('-n', "--show_dft", dest="show_dft", action="store_true", default=False,  help="(default False) If used, Attributes whose match their default values are not shown.")
    parser.add_option("--dft_raise", dest="dft_raise", action="store_true", default=False,  help="(default False, advanced) If used and an exception is encountered trying to retreive the default value for one Attribute, the exception is raised.")
    parser.add_option('-N', "--show_none", dest="show_none", action="store_true", default=False, help="(default False) If used, Attributes whose value is None are not shown.")
    parser.add_option('-a', "--all", dest="all", action="store_true", default=False, help="(default False) If used, save all processors.")
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False, help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")

def xpath_usage():
    return """
    Supported xpath commands are: ls, set, rm, save, show

    For help on command type: 
        h (or help) <command>
    """
    
def save_and_show_usage():
    return """
    Save the current mounted  processor,
    or the whole precessor with the --all (-a) option.
    The best practice is to use --all.

    Syntax:
    -------
    save [--all]
    """

def xpath_command(am, command, pcInfo, fct_save=None, verbose=0, sb=None):
    self_funct='xpath_command'
    ALLOWED_COMMANDS=('show', 'save', 'ls', 'set', 'rm')
    SET_SYNTAX='set ATTR = VALUE'
    import shlex
    
    args=shlex.split(command)
    command=args[0]
    del args[0]
    
    if command not in ALLOWED_COMMANDS:raise attrxception.attrmkSystemException('Main', self_funct, 'UnSupported command:' + command.split()[0] + '. Supported commands are:' + str(ALLOWED_COMMANDS)[1:-1].replace("'", '') + ' !')
    
    parser = optparse.OptionParser(xpath_usage())
    if command in ('save', 'show'):save_and_show_options(parser)    
    else:xpath_options(parser)

    try:(options, xpaths) = parser.parse_args(args)    
    except:raise attrxception.attrmkOptionException('Main', self_funct) 

    if verbose==0:verbose=options.verbose

    if command in ('show', 'save'):
        print_keywords={'doSpaceWrapEq':options.space_wrap_eq, 'noDft':options.show_dft==False, 'noDftRaise':options.dft_raise==False, 'noNone':options.show_none==False}
        
        if command=='show':

            if len(xpaths)!=0:raise attrxception.attrmkSystemException('Main', self_funct, 'No arguments is allowed with the show command !')
            am.show(sb=sb, **print_keywords)
            return

        print_keywords['all']=options.all 
        fct_save(alias=pcInfo.getAlias(), sb=sb, force=options.xforce, **print_keywords)
        return
    

    ## Checks args
    if command!='ls' and len(xpaths)==0:
        print(xpath_usage())
        print('At least one picpath argument is required!')
        return
    if options.HELP:
        parser = optparse.OptionParser(xpath_usage())
        xpath_options(parser)
        parser.print_help()
        return
    if '-h' in args:
        parser.print_help()
        return

    ## Run
    attrs = am.getAttrs()
    if command=='ls':
        firstime=True
        founds={}

        if len(xpaths)==0:xpaths=am.getDescAttrOrders()
        else:        
            for attr in xpaths:
                if attr not in attrs:raise attrxception.attrmkSystemException('Main', self_funct, 'Unknown Attribute:' + attr + ' ! Known attributes are:' + str(list(attrs.keys()))[1:-1].replace("'", '') + '.')

        for attr in xpaths:
            if attr not in attrs:continue
            if not firstime:sb.write(options.attr_separator)
            else:firstime=False

            value=attrs[attr]
            founds[attr]=value
            sb.write(attr + ':' + ct.unDress(value))

        return founds

    if command=='rm':
        for attr in xpaths:
            if attr not in attrs:raise attrxception.attrmkSystemException('Main', self_funct, 'Unknown Attribute:' + attr + ' ! Known attributes are:' + str(list(attrs.keys()))[1:-1].replace("'", '') + '.')
            am.delAttr(attr)

    elif command=='set':
        if len(xpaths)!=3 or xpaths[1]!='=':
            raise attrxception.attrmkSystemException('Main', self_funct, 'set requires two arguments separated by:= ! Received:' + str(xpaths)[1:-1].replace("'", '') + '.')
        founds={}
        attr=xpaths[0]
        value=ct.dress(xpaths[2])

        am.setAttr(attr, value, force=options.xforce)

        founds={attr:am.getAttr(attr)}
        return founds


##=== aql ===##

def aql_command(am, command, pcInfo, verbose=0, sb=None):
    
    return am.aql(aqlString=command, sb=sb)


    

#  MainTest ===================================================================/
if __name__ == '__main__':
    pass