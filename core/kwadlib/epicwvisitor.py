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




from . import wk
from .epicbase import TAG_SEP
from kwadlib import xception


ALIAS_BEGIN_CHAR='$['
ALIAS_END_CHAR=']'
ALIAS_ALLOWED_STARTING_CHARS=['a', 'b' ,'c', 'd', 'e', 'f', 'g', 'h', 'i' ,'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u' , 'v', 'x', 'y', 'z']


class Visitor:

    def __init__(self, childFirst = True, treatAncestor=True, recursiveNodes=True):
        self.childFirst = childFirst
        # Imbricated classes Treat the caller ?
        self.treatAncestor=treatAncestor
        # Imbricated classes recursivity ?
        self.recursiveNodes = recursiveNodes        
    
    def visitWideNodes(self, element):       
        pass
        
    def visitWideNode(self, element):
        pass




                                #------------------------------#
                                #  Make Real Nodes from Wides  #
                                #------------------------------#



class WorkMkNode(Visitor):
    
    def __init__(self, clasIsSoftClassNode=False):
        Visitor.__init__(self, childFirst=False, treatAncestor=True, recursiveNodes=True)
        self.foundFirstNode=None
        self.clasIsSoftClassNode = clasIsSoftClassNode

    def visitWideNodes(self, element):
        """Recursivite sur les classes inbriquees."""
        # - childs
        for c in element.listWideNodes:
            c.accept(self)

    def visitWideNode(self, element):        
        element.workMkNode(self)
        
    def visitFirstNode(self, element):       
        pass 
        


                                    #----------------#
                                    #  Eval Express  #
                                    #----------------#




class WorkClone(Visitor):
    """
    A link cannot contain another lnk.
    """

    def __init__(self, firstNode=None, childFirst=False, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)     
        self.__firstNode=firstNode
        
    def visitWideNodes(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listWideNodes:                                       
            c.accept(self)
    
    def visitWideNode(self, element):       
        element.clone(firstNode=self.__firstNode)
        self.__firstNode=None

    
    
class WorkClearClone(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)  
        
    def visitWideNodes(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listWideNodes:                                       
            c.accept(self)
    
    def visitWideNode(self, element):       
        delattr(element, 'workClone')



#M001:20120901
class WorkForeach(Visitor):

    def __init__(self, childFirst = False, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)  
        self.mayHaveMore=False
        
    def visitWideNodes(self, element):
        """Recursivity on imbricated Classes."""
        if self.mayHaveMore:return # stop
        l=element.listWideNodes
        for c in l:                                       
            c.accept(self)
            if self.mayHaveMore:return # stop
    
    def visitWideNode(self, element):
        self_funct='visitWideNode'
        if self.mayHaveMore:return # stop
        if not element.getName()=='__foreach__':return
        
        parent=element.getAggregatParent()
        if not element.hasAttr('tag'):raise xception.kwadXmlSyntaxException(self.__class__.__name__, self_funct, 'This Foreach tag with parent:' + element.getAggregatParent().getName() + ', has no Attribute Tag !')
        
        try:
            targets=parent.getNode(element.getAttr('tag'))
        except Exception as e:
            parent._remove(element)
            return
        
        for target in targets:
            for innernode in element.listWideNodes:
                wrk=WorkClone()
                innernode.accept(wrk)
                clone=innernode.workClone
                wrk=WorkClearClone()
                innernode.accept(wrk)
            
                target.add(clone)

        parent._remove(element)
        if len(targets)>0:self.mayHaveMore=True




class WorkPxQuery(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)  
        
    def visitWideNodes(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listWideNodes:                                       
            c.accept(self)
    
    def visitWideNode(self, element):
        dattrs=element.getdAttrs()
        for attr in dattrs:
            value= dattrs[attr]
            if not isinstance(value, str):continue
            treatPxQuery(element, attr, value)



class WorkAlias(Visitor):

    def __init__(self, aliases=None, childFirst=False, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)  
        self.__aliases=aliases
        
    def visitWideNodes(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listWideNodes:                                       
            c.accept(self)
    
    def visitWideNode(self, element):
        dattrs=element.getdAttrs()
        for attr in dattrs:
            value=dattrs[attr]
            if not isinstance(value, str):continue
            treatAlias(element, value, attr=attr, aliases=self.__aliases)
            
        texts=element._getText()
        if isinstance(texts, list):
            for i in range(len(texts)):
                if not isinstance(texts[i], str):continue
                found, texts[i]=treatAlias(element, texts[i], aliases=self.__aliases)


#M001:20120901
class WorkClearAlias(Visitor):

    def __init__(self, childFirst = True, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)  
        self.__alias=list()
        
    def visitWideNodes(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listWideNodes:                                       
            c.accept(self)
    
    def visitWideNode(self, element):
        if not element.getName()=='__alias__':return        
        self.__alias.append(element)

    def clearAlias(self):
        for node in self.__alias:
            node.getAggregatParent()._remove(node)
            
        self.__alias=None



class WorkOr(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)  
        
    def visitWideNodes(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listWideNodes:                                       
            c.accept(self)
    
    def visitWideNode(self, element):
        dattrs=element.getdAttrs()        
        for attr in list(dattrs.keys()):
            value=dattrs[attr]            
            if not isinstance(value, str):continue
            WorkOr.treatOr(element, attr, value)
            
    def treatOr(node, attr, value):
        """
        Ex: pxo:pxq:bu.member.name|pxq:bu.server.jvm|$jvm
        """
        self_funct='treatOr'

        if value==None:return False
        if not value.startswith('pxo:'):return False
        pxos=value[4:]
        pxos=pxos.split('|')
        
        if len(pxos)<=1:raise xception.kwadXmlSyntaxException('WorkOr', self_funct, 'Bad Format for this pxo exit:' + value + '.\n' +
            'For the Tag/Attribute:' + node.getName() + '/' + attr + '.\n' +
            'A PxQuery exit: must start by : "pxo:" and contain more than one values/expressions separated by "|"' + '.')
            
        for pxo in pxos:
            passed = False
            if pxo.startswith('pxq:'):
                try:
                    passed=treatPxQuery(node, attr, pxo)
                    break
                except:pass
                if passed:break
            elif pxo.find(ALIAS_BEGIN_CHAR)>=0:
                try:
                    passed, value=treatAlias(node, pxo, attr=attr)
                except:pass
                if passed:break
                else:
                    node.setAttr(attr, pxo)
                    passed=True
                    break
            else:
                node.setAttr(attr, pxo)
                passed=True
                break
            
        if not passed:raise xception.kwadXmlSyntaxException('WorkOr', self_funct, 'No value found for this Pxo exit:' + value + '.\n' +
            'For the Tag/Attribute:' + node.getName() + '/' + attr + '.\n' +
            'A PxQuery exit: must start by : "Pxo:" and contain more than one values/expressions separated by "|"' + '. And at least one expression must match.')
            
        return True
    
    treatOr=staticmethod(treatOr)
    


def treatPxQuery(node, attr, value):
    self_funct='treatPxQuery'
    if value==None:return False
    
    parent=node.getAggregatParent()        
    if not value.startswith('pxq:'):return False
        
    spl=value.split('pxq:')
    if len(spl)!=2:
        raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ value + '.\n' +
        'For the Tag/Attribute:' + node.getName() + '/' + attr + '.\n')    
    pxq=spl[1]
    
    if pxq.startswith('tdc.'):
        spl=pxq.split('tdc.')
        if len(spl)!=2:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag/Attribute:' + node.getName() + '/' + attr + '.\n')
            
        pxq=spl[1]        
        node.setAttr(attr, parent.tdc(pxq, checkIsNode=False, checkIsAttr=True, checkIsUnique=True))
        
    elif pxq.startswith('td.'):
        spl=pxq.split('td.')
        if len(spl)!=2:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag/Attribute:' + node.getName() + '/' + attr + '.\n')
        pxq=spl[1]          
        node.setAttr(attr, parent.td(pxq, checkIsNode=False, checkIsAttr=True, checkIsUnique=True))
        
    elif pxq.startswith('bu.'):
        spl=pxq.split('bu.')
        if len(spl)!=2:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag:' + node.getName() + ', Attribute:' + attr + '.\n')
        pxq=spl[1]
        node.setAttr(attr, node.pxq_bu(pxq))
        
    else:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag/Attribute:' + node.getName() + '/' + attr + '.\n'
        'A PxQuery exit: must start by one of : "pxq:tdc." or "pxq:td." or "pxq:bu."' + '.')
        
    return True


def search(node, pattern, aliases=None):
    value=node.getAlias(pattern)
    if value==None and pattern in aliases:value=aliases[pattern]
    return value
    
def replace(value, pos_start, pos_end, node, aliases=None):
    pattern = value[pos_start+2:pos_end]    
    
    alias=search(node, pattern, aliases=aliases)
    if alias==None:return value
    
    value = value[0:pos_start] + alias + value[pos_end+1:]

def treatAlias(node, value, attr=None, aliases=None):
    found=False
    if value==None:return found, value

    fstart=0
    while True:
        pos_start=value.find(ALIAS_BEGIN_CHAR, fstart)
        if pos_start<0:break
        fstart=pos_start+2
        if len(value)>pos_start+2 and value[pos_start+2] not in ALIAS_ALLOWED_STARTING_CHARS:continue
        
        pos_end=value.find(ALIAS_END_CHAR, fstart)
        if pos_end<0:break
        #A001:fstart=pos_end+1
        fstart=pos_end
        value=replace(value, pos_start, pos_end, node, aliases=aliases)
        
        found=True

    if found and attr!=None:node.setAttr(attr, value)
    return found, value
