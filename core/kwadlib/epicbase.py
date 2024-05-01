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
# 2012/12/12  | 004 | Support of * on f_tags and support of __all__ for * in select.
# 2013/01/10  | 007 | Change Link support model.
# 2023/03/23  | 008 | Add noParentWeakRef. Previously and currently if not set at the top level: if the top node reference is lost by the program, the underlaying childs loose their aggregatParent becoming None.
# 2023/10/02  | 009 | newNode.replace(oldNode): newNodewill replace oldNode at same position inside the parent.

from . import epicxception
try:
    from .repoztools import _Apb_isinstance, StructSerializable
except:from .tools import _Apb_isinstance, StructSerializable
from .xmlsuckerscraper import Node
from . import wk
from . import ct
import weakref
class dummy:pass
WEAKREF_TYPE = type(weakref.ref(dummy))
TAG_SEP='/'
PICPATH_ATTR_SEP=','
PICPATH_TEXT_SEP=';'
ATTR_SEP=' '
NODE_SEP=','
TEXT_SEP=';'
VW_STORED_PARAMETERS=('xhelp', 'xtree', 'xgrid', 'xrepoz')
ALHPANUMS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


class Filter(_Apb_isinstance):
    _apb_isinstance_Filter='Filter'  

    def __init__(self, ftags=None, fattrs=None, fattrs_skel=None, first=False, capSensitive=True):
        """
        ftags   a list of tags names.
                There are three types of tag name:
        
                basic tag name: TAGNAME all tags named TAGNAME are returned.
                ex : tag3
                
                hierarchical tag name: TAGNAME1.TAGNAME2.TAGNAME3
                all tags named TAGNAME3 are returned if their parent's is named TAGNAME2,
                and if their parent's parent is named TAGNAME3.
                ex : tag2.tag3.tag4
                
                hierarchical tag name from the top : .TAGNAME1.TAGNAME2.TAGNAME3
                the same than previous but starting from the top tag.
                ex : .tag1.tag2.tag3
                
                tun: *tun=TAG_UNIQUE_NAME this tag unique id is checked (equivalent to the the database *rrn).
                ex : *tun=I7
                
                complete ex: tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7
                
                If a tag match one type of the list, it is returned.
                If nothing is given for ftags, all tags are returned.
                All returned tags go througth the next fattrs test.
                
                
        fattrs  a lis of attribute name<OPERATOR>value.
                There are three types of attribute name:
                
                basic attribute name: ATTR_NAME=ATTR_VALUE all tags returned by the ftags check are tested.
                ex: address=tiny street
                
                hierarchical attribute name: TAGNAME1.TAGNAME2.TAGNAME3.ATTR_NAME=ATTR_VALUE
                Only tags returned by the ftags that passe the hierarchical test TAGNAME1.TAGNAME2.TAGNAME3
                are tested.
                ex : tag2.tag3.tag4.address=tiny street
                
                hierarchical attribute name from the top: .TAGNAME1.TAGNAME2.TAGNAME3.ATTR_NAME=ATTR_VALUE
                Only tags returned by the ftags that passe the hierarchical test from the top .TAGNAME1.TAGNAME2.TAGNAME3
                are tested.
                ex : .tag1.tag2.tag3.address=tiny street
                
                complete ex: address=tiny street,tag2.tag3.tag4.address=tiny street,.tag1.tag2.tag3.address=tiny street
                
                All tags must passe the fattrs test to be returned.
                
        fattrs_skel
                Skeleton : a numbered conditional String.
                This string have the exact shape of the where clause except that
                it just keep parenthesis and or/and operators.
                Conditions are replaced by numbers in their order of apparition.
                Note this number is their index in precedent fattrs parameter.
                ex: (0 and (1 or 2)) and (3 ) or  4
        """ 
        selfMethod='__init__'
        HIERAR_ATTRS_SHAPE='tag[' + TAG_SEP + 'tag]@attr'
        self.capSensitive=capSensitive
        
        class FTag:
            def __init__(self):
##                self.all=False # A004
                self.hierarTags=[]
                self.tun=None
                self.basics=[]
        class FAttr:
            OPERATORS={'=':'*eq','<=':'*le','>=':'*ge','<':'*lt','>':'*gt','<>':'*ne','*between':'*between', '*in':'*checkIn'}
            
            def __init__(self, skeleton=None):  
                self.hierarAttrs=[]
                self.basics=[]
                self.skeleton=skeleton

        # D004: if ftags!=None and not isinstance(ftags, (list,tuple)):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'ftags', 'list/tuple', str(ftags))
        if ftags not in (None, '*') and not isinstance(ftags, (list,tuple)):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'ftags', 'list/tuple', str(ftags))                            
        if fattrs!=None and not isinstance(fattrs, (list,tuple)):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'fattrs', 'list/tuple', str(fattrs))                            
        if fattrs_skel!=None and not isinstance(fattrs_skel, (str)):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'fattrs_skel', 'str', str(fattrs_skel))                            
        if ftags==None:ftags=()
        self.ftag=FTag()
        
        # ftags:
        if ftags!='*':
            for ftag in ftags:
                ftag=str(ftag)
                
                if ftag.find(TAG_SEP)>=0:
                    spl=ftag.strip().split(TAG_SEP)
                    if len(spl)==1 or spl[-1]=='':raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unknown Tag Filter. A hierarchical tag filter should at least contains one tag name an cannot end by ".". Your value: ' +str(ftag) + '.'+ '. Your Filter string: ' + str(ftags).replace("'", '')[1:-1] + '.')
                    if ftag.find('=')>=0:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unknown Tag Filter. A hierarchical tag filter should not contains "=". Your value: ' +str(ftag) + '.'+ '. Your Filter string: ' + str(ftags).replace("'", '')[1:-1] + '.')           
                    spl=ftag.strip().split(TAG_SEP)

                    if self.isCapSensitive():ftag=TAG_SEP.join( [l for l in spl] )
                    else:ftag=TAG_SEP.join( [l.capitalize() for l in spl] )

                    self.ftag.hierarTags.append(ftag)
                elif ftag.startswith('*tun'):
                    try:
                        spl=ftag.strip().split('=')
                        if len(spl)!=2:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unknown Tag Filter. A basic tag filter should not contains "=", or "*tun". Your entry: ' +str(ftag) + '.'+ '. Your Tag Filter string: ' + str(ftags) + '.')           
                        if spl[0].strip()!='*tun':raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unknown Tag Filter. A basic tag filter should not contains "=", or "*tun". Your entry: ' +str(ftag) + '.'+ '. Your Tag Filter string: ' + str(ftags) + '.')           
                        if self.isCapSensitive():self.ftag.tun=spl[1].strip()
                        else:self.ftag.tun=spl[1].strip().upper()
                    except Exception as e:
                        raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unknown Tag Filter. A *tun filter must be shaped like this: *tun=TAG_UNIQUE_ID. Your value: ' +str(ftag) + '.'+ '. Your Filter string: ' + str(ftags).replace("'", '')[1:-1] + '.')
                else:
                    if ftag.find('*tun')>=0 or ftag.find('=')>=0:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unknown Tag Filter. A basic tag filter should not contains "=", or "*tun". Your entry: ' +str(ftag) + '.'+ '. Your Tag Filter string: ' + str(ftags) + '.')
                    if self.isCapSensitive():self.ftag.basics.append(ftag)
                    else:self.ftag.basics.append(ftag.capitalize())

        # fattrs:
        if fattrs==None:fattrs=()
        self.fattr=FAttr(skeleton=fattrs_skel)
        idx=0
        for fattr in fattrs:
            fattr=str(fattr).strip()
            error_unkattr=epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Unknown Attribute Filter. An attribute filter must be shaped like this: ATTR_NAME <OPERATOR> ATTR_VALUE. Operator must be in:' + str(FAttr.OPERATORS) + '. Your entry: ' +str(fattr) + '.'+ '. Your Attribute Filter string: ' + str(fattrs).replace("'", '')[1:-1] + '.')
            
            i=0
            for op in FAttr.OPERATORS:
                i=fattr.find(op)
                if i>0:break
            if i<=0:raise error_unkattr
            
            spl=fattr.strip().split(op)
            if len(spl)!=2 or spl[0]=='':raise error_unkattr
            name=spl[0].strip()
            value=spl[1].strip()
            value=ct.dress(value)
            
            # - if value is compared with None allow no required !
            if value==None:attrdesc={FAttr.OPERATORS[op]:value}
            else:attrdesc={FAttr.OPERATORS[op]:value, '*required':True}
            wk.isWKDefinition(attrdesc, class_exit=str(self.__class__), method_exit=selfMethod)
        
            if name.find(TAG_SEP)>=0 or name.find('@')>=0:
                spl=name.strip().split('@')
                if len(spl)!=2:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Uncorrect Hierarchical Attribute:' + name + '! The Hierarchical Attribute shape is:' + HIERAR_ATTRS_SHAPE+ '. Your Attribute Filter string: ' + str(fattrs).replace("'", '')[1:-1] + '.') 
                attr=spl[-1]
                if not self.isCapSensitive():attr=attr.upper()
                if attr.find(TAG_SEP)>=0:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Uncorrect Hierarchical Attribute:' + name + '! The Hierarchical Attribute shape is:' + HIERAR_ATTRS_SHAPE+ '. Your Attribute Filter string: ' + str(fattrs).replace("'", '')[1:-1] + '.') 
                
                spl=spl[0].split(TAG_SEP)
                if not self.isCapSensitive():
                    spl=[tag.capitalize() for tag in spl]

                name=TAG_SEP.join(spl) + TAG_SEP + attr
                self.fattr.hierarAttrs.append([name, attrdesc, idx])
            else:
                if self.isCapSensitive():self.fattr.basics.append([name, attrdesc, idx])
                else:self.fattr.basics.append([name.upper(), attrdesc, idx])
            idx+=1

    def isCapSensitive(self):
        return self.capSensitive



# D003: class NodeBase(_Apb_isinstance, Node):
class NodeBase:
    _apb_isinstance_NodeBase='NodeBase'  

    def init(self, **keywords):
        self.dontSerialize=('allowedAttributesValue', 'allowedChilds')
        self.aggregatParent=None

    def isFirstNode(self):  
        return False 
        
    def setName(self, p_name=None):
        if   isinstance(p_name, str)!=True:
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, 'setName', 'p_name', 'str', str(p_name))
            
        self.name=p_name
       
    def getName(self):            
       return self.name

    def getFiliation(self, asList=False):
        if self.isFirstNode():return ''
        
        filiation=[o.getName() for o in self.getAggregatFiliation([])]        
        filiation.insert(0, self.getName())
        filiation.reverse()
        if asList:return filiation  
        return TAG_SEP + TAG_SEP.join(filiation)
   
    def initFrom_xmlNode(self, xmlSucker):     
        pass
        
    def clone(self, concreteObj):
        self.workClone=concreteObj
                
    def accept(self, p_visitor):
        p_visitor.visitNodeBase(self)      

    def getAggregatParent(self):
        if self.aggregatParent!=None:
            if type(self.aggregatParent) == WEAKREF_TYPE: return self.aggregatParent()
            else:return self.aggregatParent
        else:return None
       
    def setAggregatParent(self, p_nodeBase):
        if  __debug__ and not hasattr(p_nodeBase, 'isinstance') and not p_nodeBase.isinstance('NodeBase'):
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, 'setAggregatParent', 'p_nodeBase', 'NodeBase', str(p_nodeBase))

        # A008:
        if hasattr(p_nodeBase, 'noParentWeakRef') and p_nodeBase.noParentWeakRef():self.aggregatParent=p_nodeBase
        else:self.aggregatParent=weakref.ref(p_nodeBase)

    def removeAggregatParent(self):
        self.aggregatParent=None

    def getAggregatFiliation(self, p_aggFiliation):            
        if  __debug__ and not isinstance(p_aggFiliation, list):
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, 'getAggregatFiliation', 'p_aggFiliation', 'list', str(list))

        if  self.getAggregatParent()!=None and not self.getAggregatParent().isFirstNode():
            p_aggFiliation.append(self.getAggregatParent())
            self.getAggregatParent().getAggregatFiliation(p_aggFiliation)
        
        return p_aggFiliation

    def getTopParent(self):
        if not (self.isFirstNode() or self.getAggregatParent()==None):
            return self.getAggregatParent().getTopParent()
        return self

    def getTop(self):
        return self.getTopParent()


    def getTop2(self):
        top = self.getTopParent()
        nodes = top.getNodes()
        if len(nodes) == 0:return None
        return nodes[0]
    
    def checkIntegrity(self):
        if  self.aggregatParent==None:
            raise epicxception.AppComponentIntegrityError(str(self.__class__), id(self),  "self.aggregatParent=None")    

        if  self.name==None:
            raise epicxception.AppComponentIntegrityError(str(self.__class__), id(self),  "self.name=None")

    # D003:
##    def clearTrivialRef(self):
##        if hasattr(self, 'xmlNodeLnk'):delattr(self, 'xmlNodeLnk')

class ImbricatedNodeBase(NodeBase):
    _apb_isinstance_ImbricatedNodeBase='ImbricatedNodeBase'       

    def init(self, **keywords):           
        NodeBase.init(self, **keywords)
        self.listNodeBases = []
        self.__tagOrders = [] # A009
        self.__quickTags = {}
        self.__quickTagAndLinks = {}

    def accept(self, p_visitor, p_specificRecursive):                        
        if  __debug__ and isinstance(p_specificRecursive, bool)!=True:
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, 'accept','p_specificRecursive', 'bool', str(p_specificRecursive))
    
        if p_visitor.recursiveImbricatedNodeBase == True and p_specificRecursive == True:
            p_visitor.visitImbricatedNodeBase(self)

    # M007
    def add(self, p_nodeBase, doCheckKey=True, doAddToQuickTun=True, force=False):
        selfMethod='add'
        self.isAllowedChilds(p_nodeBase, force=force, createDescForRecursiveLink=True)
        p_nodeBase.setAggregatParent(self)
        if hasattr(p_nodeBase, 'filiation'): p_nodeBase.filiation = None # force tun generation only for tagDesc wich is based on filiation (and may change with: setAggregatParent)
        if  p_nodeBase in self.listNodeBases:raise epicxception.AppPreexistingObjectError(str(self.__class__), p_nodeBase.__class__, id(p_nodeBase))
        if  doCheckKey and p_nodeBase.getTun() in [o.getTun() for o in self.listNodeBases if not o.isinstance('Lnk')]:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'This Tag Unique Id:' + str(p_nodeBase.getTun()) + ' already exist at this level. Existing Tags Unique Ids are:' + str([o.getTun() for o in self.listNodeBases]) + '.')

        self.listNodeBases.append(p_nodeBase)

        
        if not (hasattr(p_nodeBase, 'isinstance') and p_nodeBase.isinstance('Lnk')):
            if p_nodeBase.getName() not in self.__quickTags:self.__quickTags[p_nodeBase.getName()]=[]
            if p_nodeBase.getName() not in self.__quickTagAndLinks:self.__quickTagAndLinks[p_nodeBase.getName()]=[]
            self.__quickTags[p_nodeBase.getName()].append(p_nodeBase)
            self.__quickTagAndLinks[p_nodeBase.getName()].append(p_nodeBase)
            if doAddToQuickTun:self.getTopParent()._setQuickTun(p_nodeBase.getTun(), p_nodeBase)
        else:
            if p_nodeBase.getName() not in self.__quickTagAndLinks:self.__quickTagAndLinks[p_nodeBase.getName()]=[]
            self.__quickTagAndLinks[p_nodeBase.getName()].append(p_nodeBase)

    def isAllowedChilds(self, p_nodeBase, force=False, createDescForRecursiveLink=False):
        selfMethod = 'isAllowedChilds'
        if  not hasattr(p_nodeBase, 'isinstance') and not p_nodeBase.isinstance(self.allowedChilds):          
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "Not allowed child:" + p_nodeBase.getName() + ' for Node:' + self.getName() + '. Allowed children are:' + self.allowedChilds + ', or use force.')
        return True

    # M007
    def remove(self, p_nodeBase, doRemoveFromQuickTun=True):  
        """        
        Removes this guiven node from its parent (self).
        topic: Utility methods
        """
        if  p_nodeBase not in self.listNodeBases:raise epicxception.AppNonPreexistingObjectError(str(self.__class__), p_nodeBase.__class__,str(p_nodeBase))
        from kwadlib import epicvisitor
        if doRemoveFromQuickTun:
            self.getTopParent()._delQuickTun(p_nodeBase.getTun())
        p_nodeBase.removeAggregatParent()
        del self.listNodeBases[self.listNodeBases.index(p_nodeBase)]

        del self.__quickTags[p_nodeBase.getName()][self.__quickTags[p_nodeBase.getName()].index(p_nodeBase)]
        del self.__quickTagAndLinks[p_nodeBase.getName()][self.__quickTagAndLinks[p_nodeBase.getName()].index(p_nodeBase)]

    def replace(self, p_old_nodeBase, p_new_nodeBase):
        if (p_old_nodeBase.__class__.__name__ != 'SoftClassNode' or p_new_nodeBase.__class__.__name__ != 'SoftClassNode') and \
            (p_old_nodeBase.__class__.__name__ != 'Tagdesc' or p_new_nodeBase.__class__.__name__ != 'Tagdesc'):raise epicxception.epicxmlParameterException(self.__class__.__name__, 'replace', 'Must be called for p_old_nodeBase as SoftClassNode or Tagdesc !')

        # Destroy old:
        index = self.listNodeBases.index(p_old_nodeBase)
        self.remove(p_old_nodeBase)

        # Top QuickTun:
        self.getTopParent()._setQuickTun(p_new_nodeBase.getTun(), p_new_nodeBase)

        # childs:
        self.listNodeBases.insert(index, p_new_nodeBase)

        # __quickTags:
        if p_old_nodeBase.getName() in self.__quickTags and p_old_nodeBase in self.__quickTags[p_old_nodeBase.getName()]:
            del self.__quickTags[p_old_nodeBase.getName()][self.__quickTags[p_old_nodeBase.getName()].index(p_old_nodeBase)]

        if p_new_nodeBase.getName() not in self.__quickTags: self.__quickTags[p_new_nodeBase.getName()] = []
        self.__quickTags[p_new_nodeBase.getName()].append(p_new_nodeBase)

        # __quickTagAndLinks:
        if  p_old_nodeBase.getName() in self.__quickTagAndLinks and p_old_nodeBase in self.__quickTagAndLinks[p_old_nodeBase.getName()]:
            del self.__quickTagAndLinks[p_old_nodeBase.getName()][self.__quickTagAndLinks[p_old_nodeBase.getName()].index(p_old_nodeBase)]

        if p_new_nodeBase.getName() not in self.__quickTagAndLinks: self.__quickTagAndLinks[p_new_nodeBase.getName()] = []
        self.__quickTagAndLinks[p_new_nodeBase.getName()].append(p_new_nodeBase)

        p_new_nodeBase.setAggregatParent(self)
        p_old_nodeBase.removeAggregatParent()

    def getChilds(self):
        return list(self.listNodeBases)

    def getChildByNames(self, name):
        founds = []
        for c in self.listNodeBases:
            if c.name == name:
                founds.append(c)

        return founds

    def hasChild(self, name):
        if len(self.getChildByNames(name)) > 0 : return True
        return False

    def hasAnyChild(self):
        return len(self.listNodeBases) > 0

    def getTagOrders(self):
        return list(self.__tagOrders)

    def getQuickTagKeys(self):
        return list(self.__quickTags.keys())    
    
    def getQuickTagAndLinkKeys(self):
        return list(self.__quickTagAndLinks.keys())
    
    def getQuickTagNodes(self, tag):
        return self.__quickTags[tag]    
    
    def getQuickTagAndLinkNodes(self, tag):
        return self.__quickTagAndLinks[tag]



class rImbricatedNodeBase(ImbricatedNodeBase, StructSerializable):
    _apb_isinstance_rImbricatedNodeBase='rImbricatedNodeBase' 

class rImbricatedDescNodeBase(ImbricatedNodeBase, Node):
    _apb_isinstance_rImbricatedDescNodeBase='rImbricatedDescNodeBase' 
        
    def clearTrivialRef(self):
        if hasattr(self, 'xmlNodeLnk'):delattr(self, 'xmlNodeLnk')



class Garbadge:

    def __init__(self, p_nodeBase):
        if  __debug__ and isinstance(p_nodeBase, NodeBase)!=True:
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, '__init__', 'p_nodeBase', 'NodeBase', str(p_nodeBase))
        
        self.lnkNodeBase=p_nodeBase
        self.garbadges = []
        
    def throw(self, object):
        object.throwed_garbadge = self
        object.throwed = True
        self.garbadges.Append(object)



def convertTerra(name, doTerraNames=False, terra_names=None):
    """
    This function would convert to Terraform expected names:
    lowercase alphanumeric characters (a-z, 0-9) and underscores (_),
    And feed and equivalent table.
    """
    if not doTerraNames: return name

    l=[]
    for c in name:
        if not c in ALHPANUMS: c = '_'
        elif c.isupper():c='_' + c.lower()
        l.append(c)
    new_name = ''.join(l).lstrip('_')

    terra_names[new_name] = name
    return new_name