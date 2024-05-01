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



# 2012/05/26  | 003 | Postpone Descriptor Check from initFrom_xmlNode to visitor to allow support of Special Tags like SoftClassNodes does.
# 2013/01/10  | 007 | Change Link support model.
# 2022/09/20  | 010 | Force support of capSensitive on MakeDefaultNode/newTagdesc
# 2022/10/14  | 011 | Bug Correction
# 2023/05/30  | 012 | Ajout CLone
# 2023/07/04  | 013 | Bug Correction
# 2023/07/18  | 014 | Text dfault type is now: raw
# 2023/07/18  | 015 | Bug Correction
# 2023/07/21 | 035 | EveryWhere replacement of Node.texts as list by Node.text.
# 2023/09/19 | 036 | Bug correction

"""
/opt/kwad-base/current/bin/convert -f /opt/kwad-base/current/plugins/softclasses/category/middleware/software/tom/softclass/crtcluster/by/kwad/middleware§tom.crtcluster.by.kwad.xml  -D /opt/kwad-base/current/plugins/categories/middleware/softclasses/tom/crtcluster/by/kwad/ACT_INF/softclass.xml -v300 --toyaml
/opt/kwad-base/current/bin/convert -D /opt/kwad-base/current/plugins/softclasses/category/middleware/software/tom/softclass/crtcluster/by/kwad/ACT_INF/softclass.json --desconly -v300 tojson
"""

from . import epicbase
from .epicdescvisitor import *
from . import epicxception
from . import wk
from . import ct
from .ct import _eval


XMLSUCKER_NODE_EQUIV=   {  
                        '__link__':'Lnk',
                        '*':'Tagdesc',                              
                        '#text':'Xml_Text',
                        }  
ALLOWED_TAG_DESCS_KEYS=('*lt', '*le', '*gt', '*ge', '*eq', '*between', '*shortcut', '*help', '*lhelp', '*roles', '*rolesAutzDft', '*rolesAutz')

ROLES_AUTZ_DFT={'*anyone': '+all;+*optimistic'}
XFORMAT_TAG_PREFIX='tag_'
YAML_AND_HCL_MARK_NEWTAG = '*@YAML_AND_HCL_NEWTAG'


def checkFirstNode(obj):
    """
        Check for authorized first Node.
    """
    
    if  isinstance(obj, (FirstNode)):
        return True
    return False

def firstNode(parms):
    return FirstNode(**parms)



class Xml_Text:       
    def __init__(self, xmlNode=None, xmlSucker=None):
        """ later workText run on text """
        selfMethod='__init__'
        node=xmlNode

        p_xmlSucker=xmlSucker            

        #==> for xmlsuckerscraper who brings texts by block:Use only for xml with no <br>
        # M035:
        """
        texts=[]
        l=str(node.nodeValue).split('\n')        
        for line in l:
            line=line.strip()
            if line=='\n' or line=='':continue
            texts.append(line)
        
        l=node.getParentNode().instanceLnk._getText()
        l.extend(texts)
        """
        text = node.getParentNode().instanceLnk._getText()
        text = text if text!=None else '' + node.nodeValue
        node.getParentNode().instanceLnk._setText(text)



class Autz:

    #+roles support
    def getRoles(self):
        top_descs=self.getTopParent().getTagDescWk()
        
        if '*roles' in top_descs and top_descs['*roles']!=None:return top_descs['*roles'] + ['*anyone']
        else:return ['*anyone']
    
    #+roles support
    def checkAutz(self, autz, attr):
        self_funct='checkAutz'
        roles=self.getRoles()
        rolesAutz=None
        rolesAutzDft=ROLES_AUTZ_DFT
        passed=False

        descs=[]
        wks=self.getRestWk(attr)
        if wks!=None and '*rolesAutz' in wks:
            rolesAutz=wks['*rolesAutz']
            # M011:
            if '*rolesAutzDft' not in wks: wks['*rolesAutzDft'] = dict(wks['*rolesAutz'])
            rolesAutzDft=wks['*rolesAutzDft']
            excptCls='epicxmlRestrictorCheckException'
        else:
            excptCls='epicxmlDescriptorCheckException'        
            wks=self.getDescWk(attr)
            if wks!=None and '*rolesAutz' in wks:
                rolesAutz=wks['*rolesAutz']
                # M011:
                if '*rolesAutzDft' not in wks: wks['*rolesAutzDft'] = dict(wks['*rolesAutz'])
                if rolesAutz==None:rolesAutzDft=wks['*rolesAutzDft']
        if rolesAutz==None:rolesAutz=rolesAutzDft
        if '+*optimistic' in rolesAutzDft['*anyone'].split(';'):optimistic=True
        else:optimistic=False

        for role in roles:
            if role not in rolesAutz:continue
            autzs=rolesAutz[role].split(';')
            if '-' + autz in autzs:continue
            if '+all' in autzs or '+' + autz in autzs:
                passed=True
                break
            if optimistic:
                passed=True
                break

        return passed, excptCls
        
    #+roles support
    def checkTextAutz(self, autz):
        self_funct='checkTextAutz'
        roles=self.getRoles()
        rolesAutz=None
        rolesAutzDft=ROLES_AUTZ_DFT
        passed=False
            
        descs=[]
        wks=self.getTextRestWk()
        
        if wks!=None and '*rolesAutz' in wks:
            rolesAutz=wks['*rolesAutz']
            # M011:
            if '*rolesAutzDft' not in wks: wks['*rolesAutzDft'] = dict(wks['*rolesAutz'])
            rolesAutzDft=wks['*rolesAutzDft']
            excptCls='epicxmlRestrictorCheckException'
        else:
            excptCls='epicxmlDescriptorCheckException'        
            wks=self.getTextDescWk()
            if wks!=None and '*rolesAutz' in wks:
                rolesAutz=wks['*rolesAutz']
                # M011:
                if '*rolesAutzDft' not in wks: wks['*rolesAutzDft'] = dict(wks['*rolesAutz'])
                rolesAutzDft=wks['*rolesAutzDft']
        
        if rolesAutz==None:rolesAutz=rolesAutzDft
        if '+*optimistic' in rolesAutzDft['*anyone'].split(';'):optimistic=True
        else:optimistic=False
        
        for role in roles:
            if role not in rolesAutz:continue
            autzs=rolesAutz[role].split(';')
            if '-' + autz in autzs:continue
            if '+all' in autzs or '+' + autz in autzs:
                passed=True
                break
            if optimistic:
                passed=True
                break
            
        return passed, excptCls

    #+roles support
    def checkTagAutz(self, autz):
        self_funct='checkAutz'
        roles=self.getRoles()
        rolesAutz=None
        rolesAutzDft=ROLES_AUTZ_DFT
        passed=False
            
        descs=[]
        wks=self.getTagRestWk()
        if wks!=None and '*rolesAutz' in wks:
            rolesAutz=wks['*rolesAutz']
            # M011:
            if '*rolesAutzDft' not in wks: wks['*rolesAutzDft'] = dict(wks['*rolesAutz'])
            rolesAutzDft=wks['*rolesAutzDft']
            excptCls='epicxmlRestrictorCheckException'
        else:
            excptCls='epicxmlDescriptorCheckException'        
            wks=self.getTagDescWk()
            if wks!=None and '*rolesAutz' in wks:
                rolesAutz=wks['*rolesAutz']
                # M011:
                if '*rolesAutzDft' not in wks:wks['*rolesAutzDft'] = dict(wks['*rolesAutz'])
                rolesAutzDft=wks['*rolesAutzDft']
        if rolesAutz==None:rolesAutz=rolesAutzDft
        if '+*optimistic' in rolesAutzDft['*anyone'].split(';'):optimistic=True
        else:optimistic=False

        for role in roles:
            if role not in rolesAutz:continue
            autzs=rolesAutz[role].split(';')
            if '-' + autz in autzs:continue
            if '+all' in autzs or '+' + autz in autzs:
                passed=True
                break
            if optimistic:
                passed=True
                break

        return passed, excptCls
    
    #-roles support
    def isDenied(self, attr, doExcptCls=False, doRaise=False):
        self_funct='isDenied'
        passed, error_class=self.checkAutz('allow', attr)

        if not passed:
            if doExcptCls:return True, error_class
            if doRaise:raise getattr(epicxception, error_class)(self.__class__.__name__, self_funct, 'Tag:' + self.getName() + '/Attribute:' + attr + ' is Denied !')
            return True
            
        if doExcptCls:return False, None
        return False
    
    #-roles support
    def isTextDenied(self, doExcptCls=False, doRaise=False):
        self_funct='isTextDenied'
        passed, error_class=self.checkTextAutz('allow')

        if not passed:
            if doExcptCls:return True, error_class
            if doRaise:raise getattr(epicxception, error_class)(self.__class__.__name__, self_funct, 'Tag:' + self.getName() + '/Text: is Denied !')
            return True
        

            
        if doExcptCls:return False, None
        return False
    
    #-roles support
    def isTagDenied(self, doExcptCls=False, doRaise=False):
        self_funct='isTagDenied'
        passed, error_class=self.checkTagAutz('allow')

        if not passed:
            if doExcptCls:return True, error_class
            if doRaise:raise getattr(epicxception, error_class)(self.__class__.__name__, self_funct, 'Tag:' + self.getName() + ' is Denied !')
            return True
            
        if doExcptCls:
            return False, None
        return False
    
    #-roles support
    def isDisplayable(self, attr):
        self_funct='isDisplayable'
        passed, error_class=self.checkAutz('display', attr)

        return passed
        
    #-roles support
    def isTextDisplayable(self):
        self_funct='isTextDisplayable'
        passed, error_class=self.checkTextAutz('display')

        return passed
    
    #-roles support
    def isTagDisplayable(self):    
        self_funct='isTagDisplayable'
        passed, error_class=self.checkTagAutz('display')

        return passed
    
    #-roles support
    def isUpdatable(self, attr):
        self_funct='isUpdatable'
        passed, error_class=self.checkAutz('update', attr)

        return passed
    
    #-roles support
    def isTextUpdatable(self):
        self_funct='isTextUpdatable'
        passed, error_class=self.checkTextAutz('update')

        return passed
    
    #-roles support
    def isTagUpdatable(self):
        self_funct='isTagUpdatable'
        passed, error_class=self.checkTagAutz('update')

        return passed
    
    def isSoftClassNewDisplayable(self):
        self_funct='isSoftClassNewDisplayable'
        passed, error_class=self.checkTagAutz('displaySoftClassNew')
        
        return passed

    def isNewDisplayable(self):
        self_funct='isNewDisplayable'
        passed, error_class=self.checkTagAutz('displayNew')
        
        return passed



class  Tagdesc(epicbase.rImbricatedDescNodeBase, Autz):    
    """
    User are allow to describe they xml description as __partial__="True".
    In this case file_source.xml trival tag are allowed even if not exists into file_desc.xml.
    
    Tech:
    The firstNode is marked as self.__isPartial True.
    For each non existaing Tag, a regular Tagdesc is created with newTagdesc() and add to the tagdesc tree.
    The only difference with standard other child if that self.__isPartialTag is True.    
    """
    _apb_isinstance_Tagdesc='Tagdesc'  
    DEFAULT_MAX_NODES=999999     

    def init(self, name=None, **keywords):      
        self.allowedChilds=(Tagdesc, Lnk)
        epicbase.rImbricatedDescNodeBase.init(self, **keywords)
        if name!=None:self.setName(name)
        self.__isStrict=False
        self.__isPartial=False
        self.partialAttrDescs=[] # If partial list all non described Attrs.
        self.orderedAttrDescs=[]
        self.attrDescs={}        
        self.attrRests=None
        self.widgets={}        
        # D035: self.textDesc=[]
        self.textDesc=None
        self._hasText = False
        self.tagDesc={}
        self.filiation=None
        # todo: This is not managed anymore has been replaced by self.help. This good start must be propagated.
        self.attrHelps={}
        self.recursiveLink=False

    def hasText(self):
        return self._hasText

    def _setHasText(self):
        self._hasText = True
        
    def _setRecursiveLink(self):
        self.recursiveLink=True        
        
    def isRecursiveLink(self):
        return self.recursiveLink

    def isStrict(self):
        """  Works with partial desc but requieres this node desc and its tree. """
        return self.__isStrict

    def _setIsStrict(self, value=True):
        selfMethod='_setIsStrict'
        self.__isStrict=value
        
    def _setIsPartial(self):  
        self.__isPartial=True
    
    def isPartial(self):  
        return self.__isPartial
        
    def _isBlank(self):
        if self.getMaxTagNodes()==1 and \
            self.isTextDenied() and \
            len(list(self.attrDescs.keys()))==0:return True
        return False
            
    def _isBlankFiliation(self, stopAtNode):
        if self==stopAtNode:return True
        if not self._isBlank():return False
        return self.getAggregatParent()._isBlankFiliation(stopAtNode)
    
    
                                                                # ------------------------- #

    def isSoftClass(self):
        if 'type' in self.attrDescs:
            if '*eq' in self.attrDescs['type'] and self.attrDescs['type']['*eq']=='softclass':return True
        return False
    
    
                                # ------------------------------- Descriptor/Restrictor facilities (BEGIN) -------------------------------#         


    def hasRestrictor(self):
        if self.attrRests==None:return False
        return True

    # - getDesc

    def getDescs(self):
        return self.attrDescs

    def delDescWk(self, attr):
        self_funct='delDescWk'
        wks=self.attrDescs
        if attr not in list(wks.keys()):return False

        del wks[attr]

        return True

    def getDescWk(self, attr):
        """
        This return the value of this attr alike getAttr.
        But the value is the guiven Attribute's descriptor.
        """
        self_funct='getDescWk'
        wks=self.attrDescs
        if attr not in list(wks.keys()):raise epicxception.epicxmlSystemException(self.__class__.__name__, self_funct, 'Unknown Attribute:' + str(attr) + ' for Tag:' + self.getName() + ', known Attributes are:' + str(list(wks.keys())) + ' !')

        return wks[attr]

    def getTextDescWk(self):
        return self.textDesc
    
    def getTagDescWk(self):
        return self.tagDesc

    def getRests(self):
        self_funct='getRests'
        if not self.hasRestrictor():return None
        
        return self.attrRests
    
    def getRestWk(self, attr):
        if not self.hasRestrictor():return None
        wks=self.attrRests['attrdescs']
        if attr not in list(wks.keys()):return None
        
        return wks[attr]

    def delRestWk(self, attr):
        if not self.hasRestrictor(): return False
        wks = self.attrRests['attrdescs']
        if attr not in list(wks.keys()): return False

        del wks[attr]

        return True

    def getTextRestWk(self):
        if not self.hasRestrictor():return None
        return self.attrRests['textdescs']    
    
    def getTagRestWk(self):
        if not self.hasRestrictor():return None
        return self.attrRests['tagdescs']
    
    # - getDft

    def getDescDft(self, attr):
        self_funct = 'getDescDft'
        wks=self.attrDescs
        if attr not in list(wks.keys()):raise epicxception.epicxmlRestrictorCheckException(self.__class__.__name__, self_funct, 'Unsupported Attribute:' + str(attr) + ' for Tag:' + self.getName() + ', SupportedAttributes are:' + str(list(wks.keys())) + ' !')        
        
        if not isinstance(wks[attr], dict):return wks[attr]        
        if '*value' not in list(wks[attr].keys()):return None
        return wks[attr]['*value']            
    
    def getTextDescDft(self):
        wks=self.textDesc
        
        if not isinstance(wks, dict):return wks        
        if '*value' not in wks:return None
        return wks['*value']
       
    def getRestDft(self, attr):
        self_funct='getRestDft'
        if not self.hasRestrictor():return None
        wks=self.attrRests['attrdescs']
        if attr not in list(wks.keys()):return None

        if not isinstance(wks[attr], dict):return wks[attr]
        if '*value' not in list(wks[attr].keys()):return None
        return wks[attr]['*value']            
    
    def getTextRestDft(self):
        self_funct='getTextRestDft'
        if not self.hasRestrictor():return None
        wks=self.attrRests
        if 'textdescs' not in list(wks.keys()):return None

        if not isinstance(wks['textdescs'], dict):return wks['textdescs']
        if '*value' not in list(wks['textdescs'].keys()):return None
        return wks['textdescs']['*value']     

    def getDft(self, attr):
        """
        If this configuration has a restrictor :
        this method will return the Attributes value retreived from the softclass's resctrictor.
        Otherwise :
        this method will return  the Attributes value retreived from the softclass's descriptor.
        """
        # f814290522f79d1e9e5ae4ae83e967b4
        self_funct='getDft'
        if self.hasRestrictor():
            ret=self.getRestDft(attr)
            if ret!=None:return ret
        return self.getDescDft(attr)
    
    def getTextDft(self):
        self_funct='getTextDft'
        if self.hasRestrictor():
            ret=self.getTextRestDft()
            if ret!=None:return ret
        return self.getTextDescDft()

    # - eqDft
    
    def eqDescDft(self, attr, value):
        self_funct = 'eqDescDft'
        wks=self.attrDescs
        if attr not in list(wks.keys()):raise epicxception.epicxmlRestrictorCheckException(self.__class__.__name__, self_funct, 'Unsupported Attribute:' + str(attr) + ' for Tag:' + self.getName() + ', SupportedAttributes are:' + str(list(wks.keys())) + ' !')        
        
        # -- less likely but old implementation support.
        if not isinstance(wks[attr], dict):
            default=wks[attr]        
            if value==default:return True
            else:return False
        
        if '*value' not in list(wks[attr].keys()):default=None
        else:default=wks[attr]['*value']         

        try:
            p=wk.WantedKeywords()
            setattr(p, 'default', wks[attr])
            wk.getKeywords(wantedKeywords=p, keywords={'default':value})
            
            if p.default==default:return True
        except:
            return False
        
        return False
    
    def eqTextDescDft(self, value):
        wks=self.textDesc
        
        # -- less likely but old implementation support.
        if not isinstance(wks, dict):
            default=wks        
            if value==default:return True
            else:return False
        
        if '*value' not in wks:default=None
        else:default=wks['*value']
        
        try:
            p=wk.WantedKeywords()
            setattr(p, 'default', wks)
            wk.getKeywords(wantedKeywords=p, keywords={'default':value})
            
            if p.default==default:return True
        except:
            return False
        
        return False
       
    def eqRestDft(self, attr, value):
        self_funct='getRestDft'
        if not self.hasRestrictor():return False
        wks=self.attrRests['attrdescs']
        if attr not in list(wks.keys()):return False

        # -- less likely but old implementation support.
        if not isinstance(wks[attr], dict):
            default=wks[attr]
            if value==default:return True
            else:return False

        if '*value' not in list(wks[attr].keys()):default=None
        else:default=wks[attr]['*value']            
        
        try:
            p=wk.WantedKeywords()
            setattr(p, 'default', wks[attr])
            wk.getKeywords(wantedKeywords=p, keywords={'default':value})

            if p.default==default:return True
            raise epicxception.epicxmlSystemException(self.__class__.__name__, self_funct, 'Do not match explict Restrictor Default')
        except:pass
            
        return False
        
    def eqTextRestDft(self, value):
        self_funct='getTextRestDft'
        if not self.hasRestrictor():return False
        wks=self.attrRests
        if 'textdescs' not in list(wks.keys()):return False

        # -- less likely but old implementation support.
        if not isinstance(wks['textdescs'], dict):
            default=wks['textdescs']
            if value==default:return True
            else:return False

        if '*value' not in list(wks['textdescs'].keys()):default=None
        else:default=wks['textdescs']['*value']     
        
        try:
            p=wk.WantedKeywords()
            setattr(p, 'default', wks)
            wk.getKeywords(wantedKeywords=p, keywords={'default':value})
            if p.default==default:return True

            raise epicxception.epicxmlSystemException(self.__class__.__name__, self_funct, 'Do not match explict Restrictor Default')
        except:pass
            
        return False

    def eqDft(self, attr, value):
        try:
            if self.hasRestrictor() and self.eqRestDft(attr, value):return True
        except:return False
        return self.eqDescDft(attr, value)
    
    def eqTextDft(self, value):
        try:
            if self.hasRestrictor() and self.eqTextRestDft(value):return True
        except:return False
        return self.eqTextDescDft(value)


                                # ------------------------------- Descriptor/Restrictor facilities (END) -------------------------------# 



                                # ------------------------------- Wk aliens facilities (BEGIN) -------------------------------# 


    def checkTag(self, tag, max):
        selfMethod = 'checkTag'
        self_funct='checkTag'
        if tag not in self.getQuickTagKeys():raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unsupported Tag:' + tag + ' !' )
        child=self.getQuickTagNodes(tag)[0]
        
        try:
            if child.isTagDenied():
                isd, error_class=child.isTagDenied(doExcptCls=True)
                child.isTagDenied(doRaise=True)

            descs=[]
            rwks=child.getTagRestWk()
            if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
            descs.append((child.getTagDescWk(), 'epicxmlDescriptorCheckException'))

            for wks in descs:
                error_class=wks[1]
                wks=wks[0]

                try:
                    p=wk.WantedKeywords()            
                    setattr(p, 'occurrence', wks)
                    wk.getKeywords(wantedKeywords=p, keywords={'occurrence':max}, class_exit=self.__class__, method_exit=self_funct)
                except Exception as e:
                    raise getattr(epicxception, error_class)(self.__class__.__name__, self_funct, 'A Limit for number of ocurrences of child node:' + child.getFiliation() + ' is exceeded with:' + str(max) + ' occurences !  The tag desc is:' + str(wks) + ' !' )

        except Exception as e:
            _e=getattr(epicxception, error_class)(self.__class__.__name__, self_funct, 'Tag:' + self.getFiliation() + ' ! SubException is:' + str(e))
            _e.setSubException(e)
            raise _e
        
        return True

    def checkMaxTagNodes(self, tag, max):
        selfMethod='checkMaxTagNodes'
        if tag not in self.getQuickTagKeys():raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Not supported Tag:' + tag + ' !' )
        child=self.getQuickTagNodes(tag)[0]
        
        wks=child.getTagRestWk()
        if wks==None:_max=Tagdesc.DEFAULT_MAX_NODES
        else:_max=getMax(wks)
        
        if max >= _max:raise epicxception.epicxmlRestrictorCheckException(self.__class__.__name__, selfMethod, 'Node:' + self.getFiliation() + ', Occurences limit:' + str(_max) + ' for child node:' + tag + ', reached, node not added!')
        
        wks=child.getTagDescWk()
        _max=getMax(wks)
        if max >= _max:raise epicxception.epicxmlDescriptorCheckException(self.__class__.__name__, selfMethod, 'Node:' + self.getFiliation() + ', Occurences limit:' + str(_max) + ' for child node:' + tag + ', reached, node not added!')
        
        return True
    
    def getMaxTagNodes(self):
        wks=self.getTagRestWk()
        if wks==None:max1=Tagdesc.DEFAULT_MAX_NODES
        else:max1=getMax(wks)

        wks=self.getTagDescWk()
        max2=getMax(wks)
        
        if max1<max2:return max1
        else:return max2
     
    def showShortCut(self):
        descs=[]
        rwks=self.getTagRestWk()
        if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
        descs.append((self.getTagDescWk(), 'epicxmlDescriptorCheckException'))

        for wks in descs:
            error_class=wks[1]
            wks=wks[0]
            
            if '*shortcut' in wks and wks['*shortcut']!=True:return False
            
        return True

    def getHelp(self, attr):
        descs=[]
        rwks=self.getRestWk(attr)
        if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
        descs.append((self.getDescWk(attr), 'epicxmlDescriptorCheckException'))

        for wks in descs:
            error_class=wks[1]
            wks=wks[0]
            
            if '*help' in wks and wks['*help']!=None:return wks['*help']
            
        return None
    
    def getLHelp(self, attr):
        descs=[]
        rwks=self.getRestWk(attr)
        if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
        descs.append((self.getDescWk(attr), 'epicxmlDescriptorCheckException'))

        for wks in descs:
            error_class=wks[1]
            wks=wks[0]
            
            if '*lhelp' in wks and wks['*lhelp']!=None:return wks['*lhelp']
            
        return None
    
    def getTextHelp(self):
        descs=[]
        rwks=self.getTextRestWk()
        if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
        descs.append((self.getTextDescWk(), 'epicxmlDescriptorCheckException'))

        for wks in descs:
            error_class=wks[1]
            wks=wks[0]
            
            if '*help' in wks and wks['*help']!=None:return wks['*help']
            
        return None
    
    def getTextLHelp(self):
        descs=[]
        rwks=self.getTextRestWk()
        if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
        descs.append((self.getTextDescWk(), 'epicxmlDescriptorCheckException'))

        for wks in descs:
            error_class=wks[1]
            wks=wks[0]
            
            if '*lhelp' in wks and wks['*lhelp']!=None:return wks['*lhelp']
            
        return None

    def getTagHelp(self):
        descs=[]
        rwks=self.getTagRestWk()
        if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
        descs.append((self.getTagDescWk(), 'epicxmlDescriptorCheckException'))

        for wks in descs:
            error_class=wks[1]
            wks=wks[0]
            
            if '*help' in wks and wks['*help']!=None:return wks['*help']
            
        return None
    
    def getTagLHelp(self):
        descs=[]
        rwks=self.getTagRestWk()
        if rwks!=None:descs.append((rwks, 'epicxmlRestrictorCheckException'))
        descs.append((self.getTagDescWk(), 'epicxmlDescriptorCheckException'))

        for wks in descs:
            error_class=wks[1]
            wks=wks[0]
            
            if '*lhelp' in wks and wks['*lhelp']!=None:return wks['*lhelp']
            
        return None
    
                                # ------------------------------- Wk aliens facilities (END) -------------------------------#     
    
    

    @staticmethod
    def newTagdesc(newtag, parent=None, attrDescs=None, textDesc=None, tagDesc=None, attrRests=None, orderedAttrs=None, isPartial=True, capSensitive=False):
        """ Create a new Tagdesc child when __partial__"True" on top node. """
        selfMethod='newTagdesc'
        if isPartial and (attrDescs, attrRests)!=(None, None):raise epicxception.epicxmlParameterException('Main', selfMethod, 'When isPartial is True, attrDescs and attrRests must be None !')

        child=Tagdesc()
        # M010: child.capSensitive=False
        child.capSensitive=capSensitive
        if parent!=None:child.capSensitive=parent.isCapSensitive()
        if child.isCapSensitive():newtag=newtag.strip()
        else:newtag=newtag.strip().capitalize()
        child.setName(newtag)
        child.orderedAttrDescs=orderedAttrs
        if isPartial:
            child._setIsPartial()
            child.partialAttrDescs=list(orderedAttrs)
        
        # - desc
        if attrDescs!=None:child.attrDescs=attrDescs
        else:child.attrDescs={}
        if textDesc!=None:
            child.textDesc=textDesc
            child._setHasText() # set only if the original descriptor file hasText !
        else:
            # M014: child.textDesc={'*type': 'list', '*ltype': {'*type': 'str'}, '*withCoolTyping':True}
            child.textDesc={'*force_str': True, '*type': 'str', '*raw': True}
        if tagDesc!=None:child.tagDesc=tagDesc
        else:child.tagDesc={}
        # - rest
        if attrRests!=None:child.attrRests=attrRests
        else:child.attrRests=None
        
        child.widgets={}        
        child.attrHelps={}
        child.filiation=None

        if isPartial:
            for attr in orderedAttrs:
                if not child.isCapSensitive():attr=attr.upper()
                child.attrDescs[attr]={'*type':'str'}
            
        if parent!=None:parent.add(child)
        
        return child

    def getFirstNode(self, parms):
        return firstNode(parms)        

    def getTun(self):    
        if self.filiation==None:self.filiation=self.getFiliation()
        return self.filiation
    
    def updQuickTun(self):
        self.filiation=None
        self.getTopParent()._setQuickTun(self.getTun(), self)

    def _getText(self):
        return self.textDesc

    def _setText(self, value):
        self.textDesc=value

    def getText(self):
        return self.textDesc

    def setText(self, value):
        self.textDesc=value

    def initFrom_xmlNode(self, xmlSucker):    
        selfMethod='initFrom_xmlNode'
        node=self.xmlNodeLnk
                
        if  node==None or (node!=None and node.nodeType not in (node.ELEMENT_NODE)):
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "Class:" + str(self.__class__) + " received Incorect value received for node:" + str(node)) 

        if self.isCapSensitive():nodeName=str(node.nodeName).strip()
        else:nodeName=str(node.nodeName).strip().capitalize()

        # Check Attribute and Attribute value
        if node.nodeType==node.ELEMENT_NODE:
            lstNodeAttr=xmlSucker.getAttributes(node)
            for attr in lstNodeAttr.getOrderedAttrs():
                
                try:
                    widget=None
                    value=lstNodeAttr[attr].strip()

                    if attr.lower() == '__partial__':
                        if not (not hasattr(node.getParentNode(), 'instanceLnk') and xmlSucker.foundFirstNode!=None):raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:" + nodeName + "/attribute:" + attr + ", not allowed Attribute. Attribute __partial__ is allowed on the top Node only !")                        
                        xmlSucker.foundFirstNode._setIsPartial()
                        continue
                    
                    elif attr.lower() == '__strict__':
                        self._setIsStrict()
                        continue

                    else:

                        # - widget
                        if value.find('},__widget__={')>=0:
                            spl=value.split('},__widget__={')
                            value=spl[0] + '}'
                            widget='{' + spl[1]
                            widget=ct.dress(widget)

                        # - allow arbitrary default value
                        if not value.find('{')>=0:
                            if value=='':
                                value={'*type':'str', '*value': None}
                            else:
                                value={'*type':'str', '*force_str':True, '*value': value}

                        # - literal python expression
                        elif value.find('"')>=0 or value.find("'")>=0:value=_eval(value)
                        # - ct expression
                        else:value=ct.dress(value)
                        
                        # - because of explicite eval outsite  wk, reapply force_str.
                        if '*force_str' in value and '*value' in value:value['*value']=str(value['*value'])
                               
                    
                except (NameError, Exception) as e:

                    import sys     
                    _e=epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:" + nodeName + "/attribute:" + attr + ", not allowed value:" + lstNodeAttr[attr] + ";  Allowed values are WKDefinition only." + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) )                        
                    _e.setSubException(e)
                    raise _e
                
                if not wk.isWKDefinition(value, class_exit=self.__class__, method_exit=selfMethod):
                    raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:" + nodeName + "/attribute:" + attr + ", not allowed value:" + lstNodeAttr[attr] + ";  Allowed values are WKDefinition only.")                        
                
                # Tag wk:
                if attr.lower() == '__wk__':
                    l=list(value.keys())
                    for key in  l:
                        if key.startswith('*@'):continue
                        if key not in ALLOWED_TAG_DESCS_KEYS:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:" + nodeName + "/attribute:"  + attr + ', Unsupported key:' + key + ', for tag wk. A tag wk only supports these keys:' + str(ALLOWED_TAG_DESCS_KEYS) + '.')
                    self.tagDesc=value
                    
                    # Not needed anymore !
                    # if hasattr(node.getParentNode(), 'instanceLnk'):
                    #     # -- treats maxtagnodes
                    #     max=None
                    #     if self.tagDesc.has_key('*gt'):max=self.tagDesc['*gt']
                    #     if self.tagDesc.has_key('*ge'):max=self.tagDesc['*ge'] + 1
                    #     if self.tagDesc.has_key('*eq'):max=self.tagDesc['*eq'] + 1
                    #     if self.tagDesc.has_key('*between'):max=self.tagDesc['*between'][1] + 1
                    #     if max!=None:node.getParentNode().instanceLnk._setMaxTagNodes(nodeName, max)

                    continue

                # Attr wk:
                value.update({'*withCoolTyping':True})
                if '*type' not in value:value['*type']='str' # Force str if no type (this would desable CT.)
                
                self.orderedAttrDescs.append(attr)
                self.attrDescs[attr]=value
                self.widgets[attr]=widget
                
                 
        self.xmlNodeLnk=node
        self.setName(nodeName)
        node.instanceLnk=self   
        if hasattr(node.getParentNode(), 'instanceLnk'):                     
            node.getParentNode().instanceLnk.add(self)        
        else:
            if xmlSucker.foundFirstNode==None:xmlSucker.foundFirstNode=FirstNode()
            xmlSucker.foundFirstNode.add(self)
           
        # - propaging partial clause strictness.
        if self.getAggregatParent().isStrict():self._setIsStrict()
            
        self.clearTrivialRef()
    
    def add(self, p_tagDesc, doAddToQuickTun=True, doCheckKey=True):
        selfMethod = 'add'
        if  not isinstance(p_tagDesc, (Tagdesc, Lnk)):
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'p_tagDesc', 'Tagdesc', str(p_tagDesc))
        
        epicbase.ImbricatedNodeBase.add(self, p_tagDesc, doAddToQuickTun=doAddToQuickTun, doCheckKey=doCheckKey)
        if doAddToQuickTun:self.getTopParent()._getOrderedFiliations().append(p_tagDesc.getFiliation())

    def remove(self, p_nodeBase, doRemoveFromQuickTun=True):
        """
        Removes this guiven node from its parent (self).
        topic: Utility methods
        """
        if  p_nodeBase not in self.listNodeBases:raise epicxception.AppNonPreexistingObjectError(str(self.__class__), p_nodeBase.__class__,str(p_nodeBase))
        from kwadlib import epicdescvisitor
        # Remove childs first from QuickTun:
        wrk = epicdescvisitor.WorkrmvQuickTun()
        p_nodeBase.accept(wrk)
        # Then remove iself:
        epicbase.ImbricatedNodeBase.remove(self, p_nodeBase, doRemoveFromQuickTun=doRemoveFromQuickTun)

    def replace(self, p_old_nodeBase, p_new_nodeBase):
        epicbase.ImbricatedNodeBase.replace(self, p_old_nodeBase, p_new_nodeBase)
        top = self.getTopParent()
        topofils = top._getOrderedFiliations()

        if p_old_nodeBase.getTun() in topofils:
            del topofils[topofils.index(p_old_nodeBase.getTun())]

        descfil = p_new_nodeBase.getTun()
        if descfil in topofils:
            start = topofils.index(descfil)
            descpfil = epicbase.TAG_SEP.join( descfil.split(epicbase.TAG_SEP)[:-1] )
            # Get Parent:
            parentd = top.getQuickTunNode(descpfil)
            # Get New index:
            # go to the last item at this level:
            for i in range(start+1, len(topofils)):
                fil = topofils[i][len(descpfil)+1:].strip() # +1 to skip slash (epicbase.TAG_SEP='/')
                if fil.find(epicbase.TAG_SEP) > 0:break

            topofils.insert(i+1, descfil) # insert always before
        else:
            topofils.append(descfil)

    def accept(self, p_visitor):

        epicbase.NodeBase.accept(self, p_visitor)
        if (p_visitor.childFirst):
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveTagdesc)
            if p_visitor.treatAncestor:
                p_visitor.visitTagdesc(self) 
            else:
                p_visitor.treatAncestor=True
        else:
            if p_visitor.treatAncestor:
                p_visitor.visitTagdesc(self)
            else:
                p_visitor.treatAncestor=True
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveTagdesc)

    def setFiles(self, file_desc=None, file_rest=None):
        self.__file_desc=file_desc
        self.__file_rest=file_rest
        
    def getFileDesc(self):
        return self.__file_desc

    def setFileDesc(self, file_desc):
        self.__file_desc=file_desc       
        
    def getFileRest(self):
        return self.__file_rest

    def setFileRest(self, file_rest):
        self.__file_rest=file_rest

    # A012:
    def Clone(self):
        # - clone
        v = WorkClone()
        self.accept(v)
        clone = self.workClone
        # -- cleanup
        v = WorkClearClone()
        self.accept(v)
        ## v = WorkClone()
        ## self.accept(v)

        return clone

    def clone(self, firstDescNode=None, doStandAlone=False, doCloneLink=False):
        """ Only used by Link """
        selfMethod='clone'
        
        concreteObj=Tagdesc(name=self.getName())
        concreteObj.capSensitive=self.isCapSensitive()
        concreteObj._setIsStrict(value=self.isStrict())
        epicbase.NodeBase.clone(self, concreteObj)  
        concreteObj.orderedAttrDescs=list(self.orderedAttrDescs)        
        concreteObj.attrDescs=dict(self.attrDescs)        
        concreteObj.tagDesc=dict(self.tagDesc)        
        concreteObj.widgets=dict(self.widgets)        
        concreteObj.recursiveLink=self.recursiveLink
        
        if self.textDesc!=None:
            # D035: if isinstance(self.textDesc, list):concreteObj.textDesc=list(self.textDesc)
            # D035: elif isinstance(self.textDesc, dict):concreteObj.textDesc=dict(self.textDesc)
            concreteObj.textDesc=dict(self.textDesc)
        # D035: else:concreteObj.textDesc=[]
        else:concreteObj.textDesc={}
        concreteObj._hasText = self._hasText # set only if the original descriptor file hasText !
        concreteObj.attrHelps=dict(self.attrHelps)

        if not doStandAlone:
            parentDescNode=None
            if firstDescNode!=None:parentDescNode=firstDescNode            
            elif hasattr(self.getAggregatParent(), 'workClone'):parentDescNode=self.getAggregatParent().workClone        
            self.workClone=concreteObj
            if parentDescNode!=None:
                concreteObj._setIsStrict(value=parentDescNode.isStrict())
                parentDescNode.add(concreteObj, doAddToQuickTun=False)

        return concreteObj                        
    
    def checkIntegrity(self):
        pass

    def makeDefaultNode(self, parentNode, checkDefault=False, clasIsSoftClassNode=False):
        selfMethod='makeDefaultNode'
        if  not hasattr(parentNode, 'isinstance') and not parentNode.isinstance('Node'):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'parentNode', Node, str(parentNode))

        if clasIsSoftClassNode:
            raise Exception('clasIsSoftClassNode is not Supported by KastMenu (DKwad only) !' )
        else:
            from . import epicxmlp
            node=epicxmlp.Node(name=self.getName())

        node.capSensitive=self.isCapSensitive()
        parentNode.add(node)                
        node.peerTagdesc=self        
        attrs=node._getdAttrs()
        text=node._getText()

        # attrss:
        for attr in self.attrDescs:
            value=None
            if checkDefault and ( '*value' not in self.attrDescs[attr] or self.attrDescs[attr]['*value']==None ):raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Attribute:' + str(attr) + ' descriptor should include a default value, your wk:' + str(self.attrDescs[attr])  + '. ')
            if '*value' in self.attrDescs[attr]:value=self.attrDescs[attr]['*value']
            attrs[attr]=value

            """ D015:
            # tesxts:
            if '*value' in self.textDesc:texts.append(self.textDesc['*value'])
            elif checkDefault and ( '*value' not in self.textDesc or self.textDesc['*value']==None ):
                raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Attribute:Text: descriptor should include a default value, your wk:' + str(self.textDesc)  + '. ')
            """

        # M015:
        # tesxt:
        if '*value' in self.textDesc:text = self.textDesc['*value']
        elif checkDefault and ( '*value' not in self.textDesc or self.textDesc['*value']==None ):
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Attribute:Text: descriptor should include a default value, your wk:' + str(self.textDesc)  + '. ')

        return node

    def hasYHSingleListedChild(self):
        childs = self.getChilds()
        if len(childs) != 1: return False
        child = childs[0]
        tag_wk = child.getTagDescWk()

        if YAML_AND_HCL_MARK_NEWTAG in tag_wk and tag_wk[YAML_AND_HCL_MARK_NEWTAG]:
            return True

        return False

    def printXml(self, doChild=True, indent='', step=4, doSpaceWrapEq=False, doLBAfterTag=True, _nbstep=0, _sb=None):
        """
        Print an xml represention of this node and its children if doChild is True (default).

        indent (integer) : if indent is given text is printed respecting this margin.
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        doSpaceWrapEq (bool) : if doSpaceWrapEq is True a space will wrap the sign equal in the output, likewise: ATTR_NAME = 'ATTR_VALUE'.
            if doSpaceWrapEq is False no space will wrap the sign equal in the output, likewise: ATTR_NAME='ATTR_VALUE'.
        step (integer) : width between each tree node when doChild is True.
        _nbstep : internal use only.
        _sb : internal use only.
        """
        from io import StringIO
        self_funct = 'printXml'
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,self_funct,'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(doChild) + '. Type:' + str(type(doChild)) + '.')
        if not isinstance(indent, str) and not indent.isspace(): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,'Bad type for parameter: indent. Expected type is: a blank str ! Received:' + str(indent) + '. Type:' + str(type(indent)) + '.')
        if not isinstance(step, int): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,'Bad type for parameter: step. Expected type is: int ! Received:' + str(step) + '. Type:' + str(type(step)) + '.')
        if not isinstance(doSpaceWrapEq, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,self_funct,'Bad type for parameter: doSpaceWrapEq. Expected type is: bool ! Received:' + str(doSpaceWrapEq) + '. Type:' + str(type(doSpaceWrapEq)) + '.')
        if not isinstance(doLBAfterTag, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,self_funct,'Bad type for parameter: doLBAfterTag. Expected type is: bool ! Received:' + str(doLBAfterTag) + '. Type:' + str(type(doLBAfterTag)) + '.')

        def printValue(_sb, attr, value, margin):
            spl = value[1:-1].split(',')
            _sb.write('\n' + margin + attr + equalspc + '=' + equalspc + "'{")
            for i in range(len(spl)):
                l = spl[i]
                _sb.write('\n' + margin + step*' ' + l)
                if i+1 != len(spl) : _sb.write(',')

            return _sb.write('\n' + margin + "}'")

        def filterWk(wk):
            _wk = dict(wk)
            if '*withCoolTyping' in _wk: del _wk['*withCoolTyping']
            return _wk

        if _sb == None: _sb = StringIO()
        if doSpaceWrapEq:
            equalspc = ' '
        else:
            equalspc = ''
        pos = indent + _nbstep * step * ' '

        # if do_lb_befor_tag: _sb.write('\n')
        _sb.write(pos + '<' + self.name)

        # attrs order
        attrs = self.attrDescs
        keys = list(attrs.keys())
        textwk = self.textDesc
        tagwk = self.tagDesc

        # attrs:
        for attr in keys:
            margin = pos + step * ' '

            value = ct.unDress(filterWk(attrs[attr]))
            printValue(_sb, attr, value, margin)

        # tagwk:
        value = ct.unDress(filterWk(tagwk)).strip()
        margin = pos + step * ' '
        if value!='{}':printValue(_sb, '__wk__', value, margin)

        # Detect if not has default text:
        hasText = textwk != None and ('*rolesAutz' not in textwk or textwk['*rolesAutz'] != {'*anyone': '-allow;-display'})

        # text:
        if self.hasAnyChild() or hasText:
            _sb.write('\n' + pos + '>\n')
        else:
            _sb.write('/>\n')
        if doLBAfterTag: _sb.write('\n')

        # M036: if self.hasText():_sb.write(pos + step * ' ' + str(ct.unDress(filterWk(textwk))) + '" \n')
        # *rolesAutz:{*anyone:-allow;-display}: is the default when no Text Desc is set.
        if hasText :
            textwk = dict(textwk)
            if '*help' in textwk and (textwk['*help'] == None or textwk['*help'].strip() == ''): del textwk['*help']
            if '*lhelp' in textwk and (textwk['*lhelp'] == None or textwk['*lhelp'].strip() == ''): del textwk['*lhelp']
            _sb.write(pos + step * ' ' + str(ct.unDress(filterWk(textwk))) + '\n')

        if doChild:
            for node in self.listNodeBases:
                node.printXml(doChild=doChild, indent=indent, step=step, doSpaceWrapEq=doSpaceWrapEq, _nbstep=_nbstep + 1, _sb=_sb)

        if self.hasAnyChild() or hasText:
            _sb.write(pos + '</' + self.name + '>\n')
            if doLBAfterTag: _sb.write('\n')

        return _sb


    # A008:
    def printJSON(self, doChild=True, doCT = False, to_yaml_or_hcl = False, doTerraNames=False):

        js_attrs = {}
        founds = {self.name: js_attrs}
        # Will return terra_names only if doTerraNames:terra_names if an equiv table Terraform names <-> real names
        terra_names = self._printJSON(isFirst=True, doChild=doChild, js_attrs=js_attrs, doCT = doCT, to_yaml_or_hcl = to_yaml_or_hcl, doTerraNames=doTerraNames)

        if doTerraNames:return founds, terra_names
        else:return founds

    # A008:
    def _printJSON(self, isFirst=False, doChild=True, parent_js_attrs = None, js_attrs=None, doCT=False, to_yaml_or_hcl = False, doTerraNames=False, _terra_names=None):
        """
        Print an JSON represention of this node and its children if doChild is True (default).
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        """
        ## doCT = True
        self_funct = 'printJSON'
        # doTerraNames: if True will convert all tag names to lower cases with only digits and underscore allowed.
        if doTerraNames and _terra_names == None:_terra_names = {}
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(doChild) + '. Type:' + str(type(doChild)) + '.')
        if js_attrs==None:js_attrs={}

        def treat(child_tag, js_attrs, new_js_attrs):
            if epicbase.convertTerra(child_tag, doTerraNames=doTerraNames, terra_names=_terra_names) in js_attrs:
                parent_childs = js_attrs[XFORMAT_TAG_PREFIX + epicbase.convertTerra(child_tag, doTerraNames=doTerraNames, terra_names=_terra_names)]
                parent_childs.append(new_js_attrs)
            else:
                parent_childs = []
                js_attrs[XFORMAT_TAG_PREFIX + epicbase.convertTerra(child_tag, doTerraNames=doTerraNames, terra_names=_terra_names)] = parent_childs
                parent_childs.append(new_js_attrs)

        def filterWk(wk):
            _wk = dict(wk)
            if '*withCoolTyping' in _wk: del _wk['*withCoolTyping']
            return _wk

        # attrs order;
        attrs = self.getDescs()
        attr_keys=list(self.orderedAttrDescs)
        for attr in attr_keys:
            if attrs[attr]!=None:js_attrs[epicbase.convertTerra(attr, doTerraNames=doTerraNames, terra_names=_terra_names)] = attrs[attr] if not doCT else ct.unDress(filterWk(attrs[attr]))

        # tag:
        dvalue = self.getTagDescWk() if not doCT else filterWk(self.getTagDescWk())
        if dvalue!=None:
            if '__tag__' in js_attrs:
                js_attrs['__tag__'].update(dvalue)
                dvalue = js_attrs['__tag__']
            js_attrs['__tag__'] = dvalue if not doCT else ct.unDress(filterWk(dvalue))
        else:js_attrs['__tag__'] = None

        if doChild:
            childs = self.getChilds()
            for node in childs:
                tag_desc_childsOfChild = node.getChilds()
                new_js_attrs = {}

                child_tag = node.name
                tag_wk = node.getTagDescWk()

                text_wk = None if not node.hasText() else node.getTextDescWk()
                if text_wk!=None:
                    """
                    if text_wk.__contains__('*raw') and text_wk['*raw'] and len(tag_desc_childsOfChild)==0:
                        new_js_attrs[child_tag] = text_wk if not doCT else ct.unDress(filterWk(text_wk))
                        continue
                    else:
                    """
                    new_js_attrs['__text__'] = text_wk if not doCT else ct.unDress(filterWk(text_wk))

                if ('*le' in tag_wk and tag_wk['*le'] == 1) or ('*eq' in tag_wk and tag_wk['*eq'] == 1):
                    js_attrs[XFORMAT_TAG_PREFIX + epicbase.convertTerra(child_tag, doTerraNames=doTerraNames, terra_names=_terra_names)] = new_js_attrs
                else:
                    # if parent has just one child (here node) and this node is multiple:
                    if len(childs) == 1 and not isFirst and not to_yaml_or_hcl:
                        new_js_attrs['__tag__'] = {YAML_AND_HCL_MARK_NEWTAG: True}

                    if len(childs) == 1 and not isFirst and to_yaml_or_hcl:
                        parent_js_attrs[XFORMAT_TAG_PREFIX + epicbase.convertTerra(self.name, doTerraNames=doTerraNames, terra_names=_terra_names)] = [new_js_attrs]

                    else:treat(child_tag, js_attrs, new_js_attrs)

                node._printJSON(doChild=doChild, parent_js_attrs = js_attrs, js_attrs = new_js_attrs, doCT=doCT, to_yaml_or_hcl = to_yaml_or_hcl, doTerraNames=doTerraNames, _terra_names=_terra_names)

        return _terra_names

    def printYAML(self, doChild=True, step=4):
        from io import StringIO
        if step == None:step = 4
        sb = StringIO()
        import yaml

        json = self.printJSON(doChild=doChild, doCT = True, to_yaml_or_hcl = True)

        # See: https://stackoverflow.com/questions/8651095/controlling-yaml-serialization-order-in-python
        sb.write(yaml.dump(json, indent=step, allow_unicode=True, default_flow_style=False, sort_keys=False))

        return sb

    def printHCL(self, doChild=True, indent='', step=4):
        self_funct = 'printHCL'
        from io import StringIO
        js_attrs = {}
        self._printJSON(isFirst=True, doChild=doChild, js_attrs=js_attrs, doCT = True, to_yaml_or_hcl = True)
        _sb = StringIO()

        Tagdesc._printHCL(self.name, isFirstNode=True, indent=indent, step=step, js_attrs=js_attrs, _sb=_sb)

        return _sb

    @staticmethod
    def _printHCL(tag, isFirstNode=False, isInList=False, indent='', step=4, js_attrs=None, isTagList=None, tag_list_name=None, tag_list_parent=None, _nbstep=1, _sb=None):
        self_funct = 'printHCL'
        if not isinstance(indent, str) and not indent.isspace(): raise epicxception.epicxmlParameterException('Main', self_funct,'Bad type for parameter: indent. Expected type is: a blank str ! Received:' + str(indent) + '. Type:' + str(type(indent)) + '.')
        if not isinstance(step, int): raise epicxception.epicxmlParameterException('Main', self_funct,'Bad type for parameter: step. Expected type is: int ! Received:' + str(step) + '. Type:' + str(type(step)) + '.')
        if js_attrs == None: js_attrs = {}

        postag = indent + (_nbstep - 1) * step * ' '
        posattr = indent + _nbstep * step * ' '

        if isTagList:
            posinlist = posattr
            posattr = indent + _nbstep * step * ' ' + step * ' '
            _nbstep+=1
            _sb.write('\n' + postag + tag + ' = [' + '\n' + posinlist + '{')
            doEnd = '\n' + posinlist + '}' + '\n' + postag + "]"
        else:
            _sb.write('\n' + postag + tag + ' = {')
            doEnd = '\n' + postag + "}"

        # attrs:
        attr_keys = list(js_attrs.keys())
        if '__tag__' in attr_keys:
            attr_keys.remove('__tag__')
            attr_keys.append('__tag__')
        if '__text__' in attr_keys:
            attr_keys.remove('__text__')
            attr_keys.append('__text__')
        for attr in attr_keys:
            if attr.startswith(XFORMAT_TAG_PREFIX):continue
            value = js_attrs[attr]

            # attr:
            _sb.write('\n' + posattr)
            _sb.write(attr + ' = "' + str(value) + '"')

        # Treat tag dict only:
        for attr in attr_keys:
            if not attr.startswith(XFORMAT_TAG_PREFIX): continue
            dvalue = js_attrs[attr]
            if not (isinstance(dvalue, dict)):continue

            Tagdesc._printHCL(attr, isInList=False, indent=indent, step=step, js_attrs=dvalue, isTagList=False, tag_list_name=tag_list_name,
                tag_list_parent=tag_list_parent,_nbstep=_nbstep + 1, _sb=_sb)

        # Treat tag list only/and hcl long Name representation (isTagList = True):
        firstime = True
        for ltag in attr_keys:
            if not ltag.startswith(XFORMAT_TAG_PREFIX): continue
            lvalue = js_attrs[ltag]
            if not (isinstance(lvalue, list)):continue

            # hasParentDictWithAttr and isTagList: List Normal JSON representation:
            if len(lvalue) > 0:
                for i in range(len(lvalue)):
                    if isTagList and not firstime: _sb.write(',')
                    firstime = False
                    dvalue = lvalue[i]

                    Tagdesc._printHCL(ltag, isInList=isInList, indent=indent, step=step,
                        js_attrs=dvalue, isTagList=True, tag_list_name=tag_list_name, tag_list_parent=tag_list_parent, _nbstep=_nbstep + 1, _sb=_sb)

        if doEnd: _sb.write(doEnd)

    def parseJSON(self, tag, json, force=False, from_yaml=False, from_hcl=False):
        selfMethod = 'parseJSON'
        prefix = 'At tag: %s>' % '.'.join(self.getFiliation().split('/')[1:])
        if from_yaml and from_hcl: raise epicxception.epicxmlParameterException('Node', selfMethod, prefix + 'from_yaml and from_hcl cannot be True together !')
        if not isinstance(json, dict): raise epicxception.epicxmlParameterException('Node', selfMethod, prefix + 'At this step: %s, value must be a dict !' % self.getTag())
        keys = list(json.keys())
        dchilds = {}  # dict means unique
        lchilds = {}  # list means multiple

        # Dispatch Attrs:
        # ---------------
        attrDescs = {}
        textDesc = None
        tagDesc = None
        orderedAttrs = []
        fil = self.getFiliation() + epicbase.TAG_SEP + str(tag)

        tags = []
        for key in keys:
            if key.startswith(XFORMAT_TAG_PREFIX):
                tags.append(key)
                continue
            if key not in ('__text__', '__tag__'):orderedAttrs.append(key)
            value = json[key]

            """
            if key == '__text__': textDesc = None if value == None else ct.dress(value)
            elif key == '__tag__': tagDesc = None if value == None else ct.dress(value)
            else:attrDescs[key] = None if value == None else ct.dress(value)
            """

            if key == '__text__': textDesc = None if value == None else ct.dress(value)
            elif key == '__tag__': tagDesc = None if value == None else ct.dress(value)
            else:attrDescs[key] = None if value == None else ct.dress(value)

        # newTagdesc(newtag, parent=None, attrDescs=None, textDesc=None, tagDesc=None, attrRests=None, orderedAttrs=None, isPartial=True, capSensitive=False):
        nn = Tagdesc.newTagdesc(tag, parent=self, attrDescs=attrDescs, textDesc=textDesc, tagDesc=tagDesc, orderedAttrs=orderedAttrs, isPartial=False)

        # Dispatch dict/list:
        # -------------------
        for key in tags:
            value = json[key]

            # dchilds:
            if isinstance(value, dict):
                dchilds[key[4:]] = dict(value)
                continue
            # attrs:
            if isinstance(value, list):
                if key in lchilds:
                    lchilds[key[4:]].extend(value)
                else:
                    lchilds[key[4:]] = list(value)
                continue

        newkeys = list(dchilds.keys())  # dict means unique
        for newtag in newkeys:
            nn.parseJSON(newtag, dchilds[newtag], force=force, from_yaml=from_yaml, from_hcl=from_hcl)

        newkeys = list(lchilds.keys())  # list means multiple instances for same tag
        for newtag in newkeys:
            ll = lchilds[newtag]
            # nn2 = nn.newNode(newtag, checkDefault=False, force=force)
            attrDescs = {}
            textDesc = None
            tagDesc = None
            orderedAttrs = []
            nn2 = Tagdesc.newTagdesc(newtag, parent=nn, attrDescs=attrDescs, textDesc=textDesc, tagDesc=tagDesc, orderedAttrs=orderedAttrs, isPartial=False)
            ## else:nn2 = nn
            if len(ll)>1:raise
            if newtag.endswith('s'):tag_instance = newtag[:-1]
            else: tag_instance = newtag + 'i'
            attrs = ll[0]
            attrs['__tag__']= ct.unDress({YAML_AND_HCL_MARK_NEWTAG: True})
            nn2.parseJSON(tag_instance, attrs, force=force, from_yaml=from_yaml, from_hcl=from_hcl)




# M003:
from .xmlsuckerscraper import Node
class Lnk(epicbase.NodeBase, Node):   
    _apb_isinstance_Lnk='Lnk'       

    def init(self, **keywords):      
        epicbase.NodeBase.init(self, **keywords)
        self.filiation=None
        self.__fixed=False
        
    def setFixed(self):      
        self.__fixed=True  

    def isFixed(self):      
        return self.__fixed

    def getTun(self):    
        if self.filiation==None:self.filiation=self.getFiliation()
        return self.filiation        
        
    def setText(self, value):
        selfMethod = 'setText'
        raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:Lnk Text is not allowed")

    def clone(self, firstDescNode=None, doStandAlone=False, doCloneLink=False):
        """ Only used by Link """
        selfMethod='clone'
        if not doCloneLink:return
        
        concreteObj=Lnk()
        concreteObj.setName(self.getName())

        if not doStandAlone:
            parentDescNode=None
            if firstDescNode!=None:parentDescNode=firstDescNode            
            elif hasattr(self.getAggregatParent(), 'workClone'):parentDescNode=self.getAggregatParent().workClone        
            self.workClone=concreteObj
            if parentDescNode!=None:
                parentDescNode.add(concreteObj, doAddToQuickTun=False)

        return concreteObj                            

    def initFrom_xmlNode(self, xmlSucker):    
        selfMethod='initFrom_xmlNode'
        node=self.xmlNodeLnk
                
        if  node==None or (node!=None and node.nodeType not in (node.ELEMENT_NODE)):
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "Class:"+ str(self.__class__) + " received Incorect value received for node:" + str(node)) 
        
        self.capSensitive=xmlSucker.isCapSensitive()
        
        if self.isCapSensitive():nodeName=str(node.nodeName).strip()
        else:nodeName=str(node.nodeName).strip().capitalize()

        # Check Attribute and Attribute value
        if node.nodeType==node.ELEMENT_NODE:
            lstNodeAttr=xmlSucker.getAttributes(node)
        
        if 'name' not in lstNodeAttr and 'name'.upper() not in lstNodeAttr:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:" + nodeName + "/attribute:name" + ", must be defined and its value must be an existing tag!")                        
        if self.isCapSensitive():self.setName(lstNodeAttr['name'].strip())
        else:self.setName(lstNodeAttr['name'.upper()].strip().capitalize())
        self.xmlNodeLnk=node
        node.instanceLnk=self   
        if not hasattr(node.getParentNode(), 'instanceLnk'):raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:" + nodeName + ", must have a parent node!")                        

        # M007:
        node.getParentNode().instanceLnk.add(self)   

        self.clearTrivialRef()

    def accept(self, p_visitor):
        epicbase.NodeBase.accept(self, p_visitor)
        p_visitor.visitLnk(self)
        
    # A007:
    def add(self, p_nodeBase, doCheckKey=True, doAddToQuickTun=True, force=False):
        selfMethod='add'

        raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "For tag:" + self.name + ", a Link cannot contain child tag(s) !")



class FirstNode(Tagdesc):    
    _apb_isinstance_FirstNode='FirstNode'       
    
    def init(self, name=None, isPartial=False, comment_recorders=None):
        self.__isPartial=isPartial
        self.__orderedFiliations=[]
        self.__quickTuns={}
        self.__uniqueTags={}
        self.__comment_recorders=comment_recorders
        Tagdesc.init(self, name='FIRSTNODE')

    def getCommentRecorders(self):
        return self.__comment_recorders

    def isFirstNode(self):  
        return True

    def _setIsPartial(self):  
        self.__isPartial=True
    
    def isPartial(self):  
        return self.__isPartial
    
    def _getOrderedFiliations(self):
        return self.__orderedFiliations    
    
    def getOrderedFiliations(self):
        return list(self.__orderedFiliations)
    
    def getQuickTunKeys(self):
        return list(self.__quickTuns.keys())
    
    def getQuickTunNode(self, tun):
        selfMethod='getQuickTunNode'
        if not tun in self.__quickTuns:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'This tun (Node Unique Name):' +str(tun) + ' , is unknown. Known tun are: ' + str(list(self.__quickTuns.keys())) + '.')             
        return self.__quickTuns[tun]

    def _hasQuickTun(self, tun):
        return tun in self.__quickTuns

    def _getQuickTuns(self):
        return self.__quickTuns

    def _setQuickTun(self, tun, p_nodeBase):
        self.__quickTuns[tun]=p_nodeBase

    def _delQuickTun(self, tun):
        if tun in self.__quickTuns: del self.__quickTuns[tun]

    def getUniqueTags(self):
        if self.__uniqueTags=={}:
            for child in list(self.__quickTuns.values()):
                self.__uniqueTags[child.getName()]=child
        return dict(self.__uniqueTags)
    
    def isPeerTagdesc(self, filiation):
        selfMethod='isPeerTagdesc'
        if  not isinstance(filiation, str) or len(filiation)==0:raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'filiation', 'str', str(filiation))
        if filiation not in self.__quickTuns:return False

        return True
        
    def getPeerTagdesc(self, filiation):
        selfMethod='getPeerTagdesc'
        if  not isinstance(filiation, str) or len(filiation)==0:raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'filiation', 'str', str(filiation))
        # A013:
        if not filiation.startswith('/'):filiation = '/' + filiation
        if filiation not in self.__quickTuns:raise epicxception.epicxmlUnSupportedTagException(self.__class__.__name__, selfMethod, 'The Tag:' + filiation + ' is not described into your xml descriptor file ! Described tags are: ' + str(list(self.__quickTuns.keys())) + '.')

        return self.__quickTuns[filiation]
    
    def accept(self, p_visitor):

        epicbase.NodeBase.accept(self, p_visitor)
        if (p_visitor.childFirst):
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveTagdesc)
            if p_visitor.treatAncestor:
                p_visitor.visitFirstNode(self) 
            else:
                p_visitor.treatAncestor=True
        else:
            if p_visitor.treatAncestor:
                p_visitor.visitFirstNode(self)
            else:
                p_visitor.treatAncestor=True
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveTagdesc)

def getMax(wks):
    max=None
    if '*lt' in wks:max=wks['*lt'] - 1
    if '*le' in wks:max=wks['*le']
    if '*eq' in wks:max=wks['*eq']
    if '*between' in wks:max=wks['*between'][1]
    if max==None:max=Tagdesc.DEFAULT_MAX_NODES

    return max





# ############## #
#                #
# DescsGenerator #
#                #
# ############## #



class SrcApb:    
        
    def printHeadImportSrc(file):        
        file.write('"""\nBasic Apb file to use the xmlmk tools box straightforward.\n\nYou can include this directly in the code of your Apb.\nex : in mycube/mypackage1/mypackage2/mymodule.py.\n"""\n\n' ) 
        file.write('from task.xmlmktools import XmlMk\n' ) 

    def printHeadClassSrc(file, apbName):
        file.write('\n')
        file.write("class " + apbName + ':\n')
        file.write('\n')        
                
    def printMainMethodSrc(file, taskName):        
        file.write("    def " + taskName + "(self, *args, **keywords):\n")
        file.write("        return XmlMk.main(*args, **keywords)\n")                  
        file.write('\n')        
        
    def printAll(file, apbName, taskName):
        SrcApb.printHeadImportSrc(file)
        SrcApb.printHeadClassSrc(file, apbName)        
        SrcApb.printMainMethodSrc(file, taskName)           
        
    printHeadImportSrc=staticmethod(printHeadImportSrc)
    printHeadClassSrc=staticmethod(printHeadClassSrc)
    printMainMethodSrc=staticmethod(printMainMethodSrc)
    printAll=staticmethod(printAll)    

class SrcParameter:

    def printHeadImportSrc(file):        
        file.write('"""\nBasic parameter descriptor' + "'" + 's file to use the xmlmk tools box straightforward.\n\nYou can include this directly in the code of your parameter descriptor' + "'" + 's file.\nex : in mycube/mypackage1/mypackage2/mymodule-desc/parameter.py.\n"""\n\n' ) 
        file.write('from task.xmlmk.xmlmk_desc import parameter as xparameter\n' ) 

    def printHeadClassSrc(file, apbName):
        file.write('\n')
        file.write("class " + apbName + ':\n')
        file.write('\n')    

    def printMainMethodSrc(file, taskName):
        file.write("    def " + taskName + "(self, optBib, keywords=None):\n")   
        file.write("        xparameter.XmlMk.parameter(optBib, keywords=keywords)\n")  

    def printAll(file, apbName, taskName):
        SrcParameter.printHeadImportSrc(file)
        SrcParameter.printHeadClassSrc(file, apbName)        
        SrcParameter.printMainMethodSrc(file, taskName)      
 
    printHeadImportSrc=staticmethod(printHeadImportSrc)
    printHeadClassSrc=staticmethod(printHeadClassSrc)
    printMainMethodSrc=staticmethod(printMainMethodSrc)
    printAll=staticmethod(printAll)
            
class SrcCall:    
        
    def printHeadImportSrc(file):        
        file.write('"""\nBasic View call descriptor' + "'" + 's file to use the xmlmk tools box straightforward.\n\nYou can include this directly in the code of your View call descriptor' + "'" + 's file.\nex : in mycube/mypackage1/mypackage2/mymodule-desc/view/view.call.py.\n"""\n\n' ) 
        file.write('from task.xmlmk.xmlmk_desc.view import call as xcall\n' ) 

    def printHeadClassSrc(file, apbName):
        file.write('\n')
        file.write("class " + apbName + ':\n')
        file.write('\n')        
        
    def printMainMethodSrc(file, taskName):        
        file.write("    def " + taskName + "(self, view=None, keywords=None, message=None):\n")          
        file.write("        xcall.XmlMk.vwCall(view=view, keywords=keywords, message=message)\n")          
                
    def printAll(file, apbName, taskName):
        SrcCall.printHeadImportSrc(file)
        SrcCall.printHeadClassSrc(file, apbName)        
        SrcCall.printMainMethodSrc(file, taskName)
        
    printHeadImportSrc=staticmethod(printHeadImportSrc)
    printHeadClassSrc=staticmethod(printHeadClassSrc)
    printMainMethodSrc=staticmethod(printMainMethodSrc)
    printAll=staticmethod(printAll)

class SrcRetrn:    
        
    def printHeadImportSrc(file):        
        file.write('"""\nBasic View retrn descriptor' + "'" + 's file to use the xmlmk tools box straightforward.\n\nYou can include this directly in the code of your View retrn descriptor' + "'" + 's file.\nex : in mycube/mypackage1/mypackage2/mymodule-desc/view/view.retrn.py.\n"""\n\n' ) 
        file.write('from task.xmlmk.xmlmk_desc.view import retrn as xretrn\n' ) 

    def printHeadClassSrc(file, apbName):
        file.write('\n')
        file.write("class " + apbName + ':\n')
        file.write('\n')        
        
    def printMainMethodSrc(file, taskName):        
        file.write("    def " + taskName + "(self, view=None, keywords=None, returned=None):\n")         
        file.write("        xretrn.XmlMk.vwRetrn(view=view, keywords=keywords, returned=returned)\n")
                
    def printAll(file, apbName, taskName):
        SrcRetrn.printHeadImportSrc(file)
        SrcRetrn.printHeadClassSrc(file, apbName)        
        SrcRetrn.printMainMethodSrc(file, taskName)
        
    printHeadImportSrc=staticmethod(printHeadImportSrc)
    printHeadClassSrc=staticmethod(printHeadClassSrc)
    printMainMethodSrc=staticmethod(printMainMethodSrc)
    printAll=staticmethod(printAll)



class DescsGenerator:
    
    def __init__(self, apbName=None, taskName=None):
        selfMethod='__init__'                                    
        if not isinstance(apbName, str) or apbName=='':raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'apbName', 'str', str(apbName))                        
        if not isinstance(taskName, str) or taskName=='':raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'taskName', 'str', str(taskName))                             
        self.taskName=taskName
        from io import StringIO
        self.file_apb=StringIO()
        self.file_parameter=StringIO()
        self.file_call=StringIO()
        self.file_retrn=StringIO()        

        SrcApb.printAll(self.file_apb, apbName, taskName)
        SrcParameter.printAll(self.file_parameter, apbName, taskName)
        SrcCall.printAll(self.file_call, apbName, taskName)
        SrcRetrn.printAll(self.file_retrn, apbName, taskName)

    def getApb(self):
        return self.file_apb.getvalue()    
    
    def getParameter(self):
        return self.file_parameter.getvalue()
    
    def getCall(self):
        return self.file_call.getvalue()

    def getRetrn(self):
        return self.file_retrn.getvalue()


def digest(file, capSensitive=True, temp_dir=None, keep_temp_dir=None, verbose=0):
    selfMethod='digest'

    from os import path
    from os import path
    file = path.abspath(path.normpath(file))
    fbase, desc_suffix = path.splitext(file)
    desc_suffix = desc_suffix[1:]
    # Search for any suffix:
    for desc_suffix in ('xml', 'json', 'yaml', 'hcl'):
        if path.isfile(fbase + '.' + desc_suffix):
            file = path.normpath(fbase + '.' + desc_suffix)
            break

    if not path.isfile(file): raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(
        file) + ' should exist or with any suffix: .xml, .json, .yaml or .hcl !')

    desc_suffix = file.split('.')[-1]
    file = path.abspath(path.normpath(file))
    if not path.isfile(file): raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(
        file) + ' should exist !')

    fd = open(file, 'rb')
    docstring = fd.read().decode("utf-8")
    fd.close()

    return getXmlDesc(docstring, desc_suffix, file=file, capSensitive=capSensitive, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir, verbose=verbose)

def getXmlDesc(docString, type, file = None, capSensitive=True, doXMLDescIncludes=None, temp_dir=None, keep_temp_dir=None, verbose=0):
    selfMethod = 'selfMethod'
    """ get descriptors tree """
    from kwadlib import tools
    from os import path
    if file.endswith('.mako'): raise epicxception.epicxmlSystemException('Main', selfMethod, 'Descriptor file cannot end with .mako !')
    if file.endswith('.jinja'): raise epicxception.epicxmlSystemException('Main', selfMethod, 'Descriptor file cannot end with .jinja !')

    fdhelp=None
    if type in ('json', 'yaml', 'hcl', 'swagger'):
        if type in ('json', 'yaml', 'hcl'):
            # A010: This will convert the file to xml or json:
            docString = tools.Convert.convertSource(docString, file, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir)

            from_yaml = False
            from_hcl = False
            if type == 'yaml':
                from_yaml = True
            elif type == 'hcl':
                from_hcl = True

            try:
                import json as jsonmod
                json = jsonmod.loads(docString)
            except Exception as e:
                raise epicxception.epicxmlSystemException('Main', selfMethod, 'Unable to parse to JSON, File:' + str(file) + '!')

            desc = FirstNode(isPartial=False)
            desc.capSensitive = capSensitive
            keys = list(json.keys())
            tag = keys[0]
            value = json[tag]

            desc.parseJSON(tag, value, force=True, from_yaml=from_yaml, from_hcl=from_hcl)
            docString = desc.getChilds()[0].printXml().getvalue() # :A012

        """ todo: do not polluate:
        xml_file = path.splitext(file)[0] + '.xml'
        if not path.isfile(xml_file):
            # D012: docString = desc.getChilds()[0].printXml()
            fd = open(xml_file, 'w')
            fd.write(docString)
            fd.close()
        """

        return desc


    from . import epicdescvisitor
    from . import xmlsuckerscraper

    file_source, docstring_source, docstring_node = None, None, None

    try:
        # epicdesc dont want CDATA as it just expect a wk => dotreatCDATA=False
        s = xmlsuckerscraper.XmlSuckerScraper(modName='kwadlib.epicdesc', docString=docString, capSensitive=capSensitive, dotreatCDATA=False, verbose=verbose)
    except Exception as e:
        raise epicxception.epicxmlSystemException('Main', selfMethod, 'Error trying to Parse xml desc file: %s ! SubException is:\n %s' % (file, str(e)))
    t = s.foundFirstNode

    # - text and XFormat support:
    v = epicdescvisitor.WorkText()
    t.accept(v)

    return t



