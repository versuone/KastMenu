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



# 2012/03/06:001
# 2014/06/27:002: export do not retreive label no more.
# 20200830: 003: Treat Aliases moved to tools.
# 2022/12/03  | G001 | (G for Global) Support for outputs. Now SoftClasses of sub_type: configuration, control and datasrouce support the return of:
#                      structured values as output.
#                      The tag <output> must be defined into the SoftClass's descriptor file.
# 2023/03/22: 004: Add support for Combined SoftClass File: Global descriptor check.
# A Combined SoftClass File's descriptor can be defined like this:
# <anytag blabla ...>
#     <softclass1 type='softclass'  bsl=''/>
#     <someothertag blabla ...>
#         <softclass2 type='softclass' bsl=''/>
#     </someothertag>
# </anytag blabla ...>
# 2023/06/19 | 030 | Replacing pixmlp by epicxmlp. _getPArent replaced by getAggreagatParent everywhere. ._isFirstNode() Replaced by .isFirstNode() EveryWhere.
# 2023/10/05 | 031 | Add the ability to set default tag wks to Non SoftClass Node (usefull to lock trivail tag creation into kupd).

from .jython_aptitude import *
from . import xception
# D003: ALIAS_BEGIN_CHAR='$['
# D003: ALIAS_END_CHAR=']'
ALIAS_ALLOWED_STARTING_CHARS=['a', 'b' ,'c', 'd', 'e', 'f', 'g', 'h', 'i' ,'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u' , 'v', 'x', 'y', 'z']

from kwadlib.default import ACTION_OUTPUT_MARK


class Visitor:

    def __init__(self, childFirst=True, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        self.childFirst = childFirst
        # Imbricated classes Treat the caller ?
        self.treatAncestor = treatAncestor
        # Imbricated classes recursivity ?
        self.recursiveImbricatedNodeBase = recursiveImbricatedNodeBase
        self.recursiveNode = recursiveNode
        # End Imbricated classes recursivity.

    def visitNodeBase(self, element):
        pass

    def visitNode(self, element):
        pass

    def visitFirstNode(self, element):
        pass



class WorkPrt(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.space=""
        self.__logFile=logFile

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        self.space=self.space + "      "

        for c in element.listNodeBases:
            c.accept(self)
        self.space=self.space[0:len(self.space) - 6]

    def visitNode(self, element):
        from . import tools
        tools.verbose("Tag:" + str(element.getTag()), level=10, ifLevel=10, indent=self.space, logFile=self.__logFile)
        tools.verbose("Attributes:" + str(element.getdAttrs()), level=10, ifLevel=10, indent=self.space, logFile=self.__logFile)
        tools.verbose("Text:" + str(element.getText()), level=10, ifLevel=10, indent=self.space, logFile=self.__logFile)



#M001:20120901
class WorkForeach(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.mayHaveMore=False

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        if self.mayHaveMore:return # stop
        l=element.listNodeBases
        for c in l:
            c.accept(self)
            if self.mayHaveMore:return # stop

    def visitNode(self, element):
        self_funct='visitNode'
        from kwadlib.epicvisitor import WorkClone, WorkClearClone
        if self.mayHaveMore:return # stop
        if not element.getTag()=='__foreach__':return

        parent=element.getAggregatParent()
        if not element.hasAttr('tag'):raise xception.kwadXmlSyntaxException(self.__class__.__name__, self_funct, 'This Foreach tag with parent:' + element.getAggregatParent().getTag() + ', has no Attribute Tag !')

        try:
            targets=parent.getNode(element.getAttr('tag'))
        except Exception as e:
            parent.remove(element)
            return

        for target in targets:
            for innernode in element.listNodeBases:
                wk=WorkClone(firstNode=target, doCloneLink=False)
                innernode.accept(wk)
                clone=innernode.workClone
                wk=WorkClearClone()
                innernode.accept(wk)

        parent.remove(element)
        if len(targets)>0:self.mayHaveMore=True



class WorkPxQuery(Visitor):

    def __init__(self, doCheck=True, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.__doCheck=doCheck

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        dattrs=element.getdAttrs()
        for attr in dattrs:
            value= dattrs[attr]
            if not isinstance(value, str):continue
            treatPxQuery(element, attr, value, doCheck=self.__doCheck)

def treatPxQuery(node, attr, value, doCheck=True):
    self_funct='treatPxQuery'
    if value==None:return False

    parent=node.getAggregatParent()
    if not value.startswith('pxq:'):return False

    spl=value.split('pxq:')
    if len(spl)!=2:
        raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit.\n' +
        'For the Tag/Attribute:' + node.getTag() + '/' + attr + '.\n')
    pxq=spl[1]

    if pxq.startswith('tdc.'):
        spl=pxq.split('tdc.')
        if len(spl)!=2:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag/Attribute:' + node.getTag() + '/' + attr + '.\n')

        pxq=spl[1]
        node.setAttr(attr, parent.tdc(pxq, checkIsNode=False, checkIsAttr=True, checkIsUnique=True), doCheck=doCheck)

    elif pxq.startswith('td.'):
        spl=pxq.split('td.')
        if len(spl)!=2:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag/Attribute:' + node.getTag() + '/' + attr + '.\n')
        pxq=spl[1]
        node.setAttr(attr, parent.td(pxq, checkIsNode=False, checkIsAttr=True, checkIsUnique=True), doCheck=doCheck)

    elif pxq.startswith('bu.'):
        spl=pxq.split('bu.')
        if len(spl)!=2:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag:' + node.getTag() + ', Attribute:' + attr + '.\n')
        pxq=spl[1]
        node.setAttr(attr, node.pxq_bu(pxq), doCheck=doCheck)

    else:raise xception.kwadXmlSyntaxException('WorkPxQuery', self_funct, 'Bad Format for this PxQuery exit:'+ pxq + '.\n' +
        'For the Tag/Attribute:' + node.getTag() + '/' + attr + '.\n'
        'A PxQuery exit: must start by one of : "pxq:tdc." or "pxq:td." or "pxq:bu."' + '.')

    return True

# Jython do not support staticmethod : treatPxQuery=staticmethod(treatPxQuery)



class WorkAlias(Visitor):

    def __init__(self, aliases=None, doCheck=True, childFirst=False, treatAncestor=True, recursiveNodes=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveNodes)  
        self.__aliases=aliases
        self.__doCheck = doCheck
        
    def visitImbricatedNodeBase(self, element):
        for c in element.listNodeBases:                                       
            c.accept(self)
    
    def visitNode(self, element):
        dattrs=element.getdAttrs()
        for attr in dattrs:
            value=dattrs[attr]
            if not isinstance(value, str):continue
            treatAlias(element, value, attr=attr, aliases=self.__aliases, doCheck=self.__doCheck)
            
        text=element.getText()
        text = treatAlias(element, text, aliases=self.__aliases, doCheck=self.__doCheck)

def treatAlias(node, value, attr=None, aliases=None, doCheck=False):
    from kwadlib.tools import ALIAS_BEGIN_CHAR, ALIAS_END_CHAR
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
    
    if found and attr!=None:node.setAttr(attr, value, doCheck=doCheck)
    return found, value


def replace(value, pos_start, pos_end, node, aliases=None):
    pattern = value[pos_start+2:pos_end]

    alias=search(node, pattern, aliases=aliases)
    if alias==None:return value
    value = value[0:pos_start] + alias + value[pos_end+1:]
    return value

def search(node, pattern, aliases=None):
    value=node.getAlias(pattern)
    if value==None and pattern in aliases:value=aliases[pattern]
    return value

class WorkClearAlias(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.__alias=list()

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        if not element.getTag()=='__alias__':return
        self.__alias.append(element)

    def clearAlias(self):
        for node in self.__alias:
            node.getAggregatParent().remove(node)

        self.__alias=None



class WorkOr(Visitor):

    def __init__(self, doCheck=True, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.__doCheck=doCheck

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        dattrs=element.getdAttrs()
        for attr in list(dattrs.keys()):
            value= dattrs[attr]
            if not isinstance(value, str):continue
            treatOr(element, attr, value, doCheck=self.__doCheck)

def treatOr(node, attr, value, doCheck=False):
    """
    Ex: pxo:pxq:bu.member.name|pxq:bu.server.jvm|$jvm
    """
    self_funct='treatOr'

    if value==None:return False
    if not value.startswith('pxo:'):return False
    pxos=value[4:]
    pxos=pxos.split('|')

    if len(pxos)<=1:raise xception.kwadXmlSyntaxException('WorkOr', self_funct, 'Bad Format for this pxo exit:' + value + '.\n' +
        'For the Tag/Attribute:' + node.getTag() + '/' + attr + '.\n' +
        'A PxQuery exit: must start by : "pxo:" and contain more than one values/expressions separated by "|"' + '.')

    for pxo in pxos:
        passed = False
        if pxo.startswith('pxq:'):
            try:
                passed=treatPxQuery(node, attr, pxo, doCheck=doCheck)
                break
            except:pass
            if passed:break
            """ D003:
        elif pxo.find(ALIAS_BEGIN_CHAR)>=0:
            try:
                passed, value=treatAlias(node, pxo, attr=attr)
            except:pass
            if passed:break
            else:
                node.setAttr(attr, pxo)
                passed=True
                break
        """
        else:
            node.setAttr(attr, pxo, doCheck=doCheck)
            passed=True
            break

    if not passed:raise xception.kwadXmlSyntaxException('WorkOr', self_funct, 'No value found for this Pxo exit:' + value + '.\n' +
        'For the Tag/Attribute:' + node.getTag() + '/' + attr + '.\n' +
        'A PxQuery exit: must start by : "Pxo:" and contain more than one values/expressions separated by "|"' + '. And at least one expression must match.')

    return True

# Jython do not support staticmethod : treatOr=staticmethod(treatOr)



class WorkSoftClasses(Visitor):
    """
    Sample SoftClass Tag:
        <confjvm type='softclass' name='srv_invoices_uat_01' node='axaneUatNode01'>
            ...
        </confjvm>
    """

    # A031: nonsoftclass_tag_wks
    def __init__(self, nonsoftclass_tag_wks = None, nonsoftclass_text_wks = None, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        ## ++
        self.__nonsoftclass_tag_wks = nonsoftclass_tag_wks
        self.__nonsoftclass_text_wks = nonsoftclass_text_wks
        self.__doSetTagWks = True
        self.softclass_nodes=list()

    def visitImbricatedNodeBase(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listNodeBases:
            c.accept(self)
        if element.isSoftClass(): self.__doSetTagWks = True

    def visitNode(self, element):
        self_funct='visitNode'
        if element.isSoftClass(): self.__doSetTagWks = False

        if self.__doSetTagWks:
            if self.__nonsoftclass_tag_wks != None:
                tag_descs = element.peerTagdesc.getTagDescWk()
                tag_descs.update(dict(self.__nonsoftclass_tag_wks))
            if self.__nonsoftclass_text_wks != None:
                text_descs = element.peerTagdesc.getTextDescWk()
                text_descs.update(dict(self.__nonsoftclass_text_wks))

        if element.isSoftClass():
            self.softclass_nodes.append(element)


class WorkCSoftClasses(Visitor):
    """
    Sample SoftClass Tag:
        <anything type='csoftclass' cal='somepath'>
            ...
        </anything>
    """

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)

        self.csoftclass_nodes=list()

    def visitImbricatedNodeBase(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        self_funct='visitNode'

        if element.hasAttr('type') and element.getAttr('type') == 'csoftclass' and element.hasAttr('cal'):
            self.csoftclass_nodes.append(element)


class WorkOptStructOpereation(Visitor):
    """
    For SoftClass of type OptStruct:
    Grab the first operation found:
    """
    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.operation=None
        self.__break = False

    def visitImbricatedNodeBase(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listNodeBases:
            if self.__break:continue
            p = c.getAggregatParent()
            if p!=None and p.getName() == 'operations':continue
            c.accept(self)

    def visitNode(self, element):
        self_funct='visitNode'
        if element.getName()!='operations':return
        l = element.getNodes()
        if len(l) == 0:return
        self.operation = l[0].getName()
        self.__break = True


# A004:
class WorkCustomCheck(Visitor):
    """

    """

    def __init__(self, checkDescriptor=True, descriptors=None, restrictors=None, file_desc=None, childFirst=False, treatAncestor=True, recursiveNode=True):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.checkDescriptor = checkDescriptor
        self.restrictors = restrictors
        self.descriptors = descriptors
        self.__file_desc = file_desc

    def visitImbricatedNodeBase(self, element):
        self_funct='visitNodes'
        """Recursivity on imbricated Classes."""

        # - check max occurences per tag
        if self.checkDescriptor:method='Desc'
        else:method='Rest'

        l=getattr(element, 'get' + method + 'TagChilds')()
        for tag in l:
            if element.hasNode(tag):ll=element.getNode(tag)
            else:ll=[]
            getattr(element, 'check' + method + 'Tag')(tag, len(ll))

        nodes=list(element.listNodeBases)
        for c in nodes:
            # Dont check SoftClassNodes:
            if c.isSoftClass():
                # bsl  is required and must be equal:
                if not c.hasAttr('bsl'): raise xception.kwadSystemException('Main', self_funct, 'The SoftClass: ' + c.getTag() + ' defined into the Combined SoftClass File, Should support required Attribute: bsl')
                continue

            c.accept(self)

    def visitNode(self, element):
        self_funct = 'visitNode'
        fil = element.getFiliationSA()
        from . import wk

        if self.checkDescriptor:
            gdescs = self.descriptors
            err_class = 'kwadSoftClassDescriptorCheckException'
            prefix = ' -- Descriptor Check (%s): -- ' % self.__file_desc
        else:
            gdescs = self.restrictors
            err_class = 'kwadSoftClassRestrictorCheckException'
            prefix = ' -- Restrictor Check: -- '

        # -- descriptor attributes

        if fil not in gdescs:
            raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'Tag: ' + fil + ', Do not Exist into the descriptor file !')
        descs = gdescs[fil]
        attrdescs = descs['attrdescs']
        textdescs = descs['textdescs']
        tagdescs = descs['tagdescs']
        # -- element attributes
        dattrs = element.getdAttrs()
        text = element.getText()

        # -----------------#
        # Check Attribute #
        # -----------------#

        ## 1/
        for attr in list(dattrs.keys()):
            value = dattrs[attr]
            if value == 'None': value = None

            if attr not in list(attrdescs.keys()):
                if self.checkDescriptor: raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Unknown Attribute:' + attr + ' !' + ' Known Attributes are: ' + str(list(attrdescs.keys())) + ' !')

            # AG001:
            """
            Syntax:
            @koutref-<name>/<tdc> (Prefered)
            e.g.: @koutref-myact1/tag1/tag2@attr1=val1,@attr2 or
            <attr> = @koutref-<id>/<tdc>
            e.g.: @koutref-middleware§jss.ssl.by.kwad_tmp-mystore/tag1/tag2@attr1=val1,@attr2

            Corresponding SoftClass/output would be:
            <output>
               <softclass id=middleware§jss.ssl.by.kwad_tmp-mystore name=mystore>
                      <keystore created='False' path='/tmp/kwad/my_srv_keystore.jks'/>
                      <p12 created='True' path='/tmp/kwad/my_clt_keystore.p12'/>
               </softclass>
            </output>
            """
            if attr not in list(attrdescs.keys()):
                if value != element.getDft(attr): raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Attribute:' + attr + ' is denied !')
                continue

            if (('*deny' in tagdescs and tagdescs['*deny'] == True) or \
                    ('*deny' in attrdescs[attr] and attrdescs[attr]['*deny'] == True)):

                if value != element.getDft(attr):
                    raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Attribute:' + attr + ' is denied !')
                else:
                    continue

            try:
                p = wk.WantedKeywords()
                setattr(p, attr, attrdescs[attr])
                wk.getKeywords(wantedKeywords=p, keywords={attr: value}, class_exit=self.__class__, method_exit=self_funct)
            except Exception as e:
                raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Uncorrect value for attribute:' + attr + ' ! SubException is:' + str(e))

            element.setAttr(attr, getattr(p, attr))

        ## 2/ (reverse)

        for attr in list(attrdescs.keys()):
            if attr in dattrs: continue

            try:
                p = wk.WantedKeywords()
                setattr(p, attr, attrdescs[attr])
                wk.getKeywords(wantedKeywords=p, keywords={}, class_exit=self.__class__, method_exit=self_funct)
            except Exception as e:
                raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Uncorrect value for omitted attribute:' + attr + ' ! SubException is:' + str(e))

            element.setAttr(attr, getattr(p, attr))

        # ------------#
        # Check Text #
        # ------------#
        if text != None:
            if (('*deny' in tagdescs and tagdescs['*deny'] == True) or \
                    ('*deny' in textdescs and textdescs['*deny'] == True)):
                if value != element.getTextDft():
                    raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Text is denied !')
                else:
                    return

            try:
                p = wk.WantedKeywords()
                p.text = textdescs
                wk.getKeywords(wantedKeywords=p, keywords={'text': value}, class_exit=self.__class__, method_exit=self_funct)
            except Exception as e:
                raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Uncorrect value for Text ! SubException is:' + str(e))

            element.setText(p.text)

class WorkSoftClassCheck(Visitor):

    def __init__(self, checkDescriptor=True, descriptors=None, restrictors=None, topSA=None, file_desc=None, file_rest=None, childFirst=False, skipOutputMark=False, treatAncestor=True, recursiveNode=True):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.checkDescriptor = checkDescriptor
        self.restrictors = restrictors
        self.descriptors = descriptors
        self.__topSA=topSA
        self.__skipOutputMark = skipOutputMark
        self.__file_desc =file_desc
        self.__file_rest =file_rest

    def visitImbricatedNodeBase(self, element):
        self_funct='visitNodes'
        """Recursivity on imbricated Classes."""

        # - check max occurences per tag
        if self.checkDescriptor:method='Desc'
        else:method='Rest'

        l=getattr(element, 'get' + method + 'TagChilds')()
        for tag in l:
            if element.hasNode(tag):ll=element.getNode(tag)
            else:ll=[]
            getattr(element, 'check' + method + 'Tag')(tag, len(ll))

        nodes=list(element.listNodeBases)
        for c in nodes:

            """ Doing an operation here also avoid to do it twice. """
            fil = c.getFiliationSA()

            if not c.isSoftClassChild():
                #-- Only in custom xml (c.getTopSA()==c.getTop()): Allows custom trivial tags at root level only.
                if c.getTopSA()!=c.getTop() and c.getTopSA()==c.getAggregatParent():continue
                else:raiseTrivial(xception.kwadSoftClassDescriptorCheckException, self.__class__.__name__, self_funct, c.getTopSA().getTag(), c.getAggregatParent().getTag(), self.__topSA.getTag(), fil)

            if not fil in list(self.descriptors.keys()):
                #-- Disallows non root trivial tags. This trap SoftClassNode trivial tags.
                if c.isSoftClass():
                    if c!=self.__topSA and c.getAggregatParent()==self.__topSA:continue
                    else:raiseTrivial(xception.kwadSoftClassDescriptorCheckException, self.__class__.__name__, self_funct, c.getTopSA().getTag(), c.getAggregatParent().getTag(), self.__topSA.getTag(), fil)

            c.accept(self)

    def visitNode(self, element):
        self_funct='visitNode'
        fil = element.getFiliationSA()
        from . import wk

        if self.checkDescriptor:
            gdescs = self.descriptors
            err_class='kwadSoftClassDescriptorCheckException'
            prefix = ' -- Descriptor Check (%s): -- ' % self.__file_desc
        else:
            gdescs = self.restrictors
            err_class='kwadSoftClassRestrictorCheckException'
            prefix = ' -- Restrictor Check (%s): -- ' % self.__file_rest

        #-- descriptor attributes
        descs=gdescs[fil]
        attrdescs = descs['attrdescs']
        textdescs = descs['textdescs']
        tagdescs = descs['tagdescs']
        #-- element attributes
        dattrs=element.getdAttrs()
        text=element.getText()

        #-----------------#
        # Check Attribute #
        #-----------------#

        ## 1/
        for attr in list(dattrs.keys()):
            value=dattrs[attr]
            if value=='None':value=None

            if attr not in list(attrdescs.keys()):
                if self.checkDescriptor:raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Unknown Attribute:' + attr + ' !' + ' Known Attributes are: ' + str(list(attrdescs.keys())) + ' !')

            # AG001:
            """
            Syntax:
            @koutref-<name>/<tdc> (Prefered)
            e.g.: @koutref-myact1/tag1/tag2@attr1=val1,@attr2 or
            <attr> = @koutref-<id>/<tdc>
            e.g.: @koutref-middleware§jss.ssl.by.kwad_tmp-mystore/tag1/tag2@attr1=val1,@attr2
            
            Corresponding SoftClass/output would be:
            <output>
               <softclass id=middleware§jss.ssl.by.kwad_tmp-mystore name=mystore>
                      <keystore created='False' path='/tmp/kwad/my_srv_keystore.jks'/>
                      <p12 created='True' path='/tmp/kwad/my_clt_keystore.p12'/>
               </softclass>
            </output>
            """
            if self.__skipOutputMark and isinstance(value, str) and value.startswith(ACTION_OUTPUT_MARK):continue

            if attr not in list(attrdescs.keys()):
                if value!=element.getDft(attr):raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Attribute:' + attr + ' is denied !')
                continue

            if (('*deny' in tagdescs and tagdescs['*deny']==True) or \
                ('*deny' in attrdescs[attr] and attrdescs[attr]['*deny']==True)):

                if value!=element.getDft(attr):raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Attribute:' + attr + ' is denied !')
                else:continue

            try:
                p=wk.WantedKeywords()
                setattr(p, attr, attrdescs[attr])
                wk.getKeywords(wantedKeywords=p, keywords={attr:value}, class_exit=self.__class__, method_exit=self_funct)
            except Exception as e:
                raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Uncorrect value for attribute:' + attr + ' ! SubException is:' + str(e))

            element.setAttr(attr, getattr(p, attr))

        ## 2/ (reverse)

        for attr in list(attrdescs.keys()):
            if attr in dattrs:continue

            try:
                p=wk.WantedKeywords()
                setattr(p, attr, attrdescs[attr])
                wk.getKeywords(wantedKeywords=p, keywords={}, class_exit=self.__class__, method_exit=self_funct)
            except Exception as e:
                raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Uncorrect value for omitted attribute:' + attr + ' ! SubException is:' + str(e))

            element.setAttr(attr, getattr(p, attr))


        #------------#
        # Check Text #
        #------------#
        if text!=None:
            if (('*deny' in tagdescs and tagdescs['*deny']==True) or \
                ('*deny' in textdescs and textdescs['*deny']==True)):
                if value!=element.getTextDft():raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Text is denied !')
                else:return


            try:
                p=wk.WantedKeywords()
                p.text=textdescs
                wk.getKeywords(wantedKeywords=p, keywords={'text':value}, class_exit=self.__class__, method_exit=self_funct)
            except Exception as e:
                raise getattr(xception, err_class)(self.__class__.__name__, self_funct, prefix + 'SoftClass: ' + element.getTopSA().getTag() + ', Tag: ' + element.getTag() + ', Uncorrect value for Text ! SubException is:' + str(e))

            element.setText(p.text)

def raiseTrivial(exception, clsname, funct, tag, parent_tag, topSATag, fil):
    raise exception(clsname, funct, 'SoftClass: ' + tag  + ', Unknown Tag: ' + fil + '!' + \
    ' Advice: Custom tags are not accepted at this level:/' + parent_tag + '.' + \
    ' Custom Tags included in SoftClass Tags are only accepted for Combined SoftClass File and only directly under the root SoftClass node:/' + topSATag + '. Correct your combined softclass file.')


class WorkWaitingFromOutput(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)

    def visitImbricatedNodeBase(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        self_funct='visitNode'
        dattrs=element.getdAttrs()

        #-----------------#
        # Check Attribute #
        #-----------------#

        ## 1/
        for attr in list(dattrs.keys()):
            value=dattrs[attr]

            if  isinstance(value, str) and value.startswith(ACTION_OUTPUT_MARK):
                element.getTopSA().addAttrWaitingFromOutput(element, attr)


class WorkSoftClassUpdateCustomTree(Visitor):
    """
    After an operation read or update, this affect returned nodes to the Custom tree at the rigth positions.
    """

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, softclass_node_by_ids=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.softclass_node_by_ids = softclass_node_by_ids

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        l=tuple(element.listNodeBases) # Allows modifiying the table.

        #-- Retreiving the og Custome xml tag order !
        # D030: element._wrkTagOrders=element._guessTagOrders()
        element._wrkTagOrders=element.getTagOrders()

        for c in l:c.accept(self)

    def visitNode(self, element):
        self_funct='visitNode'
        from kwadlib.epicvisitor import WorkClone
        if not element.isSoftClass():return
        parent_node=element.getAggregatParent()

        id=element.getCEKId()

        if id not in self.softclass_node_by_ids: # Should never happen.
            parent_node.remove(element)
            return

        nodes=self.softclass_node_by_ids[id]
        if len(nodes)==0 or not nodes[0]._getExtractIsFilled():
            parent_node._remove(element)
            return

        # Only retreives trivial nodes.
        trivial_nodes=[]
        l=element.listNodeBases
        for c in l:
            if not c.isSoftClassChild():trivial_nodes.append(c)

        # Kills og SoftClass Nodes.
        parent_node._remove(element)

        # Replaces it by x found SoftClass Nodes.
        for node in nodes:
            wrk=WorkClone(firstTag=parent_node)
            node.accept(wrk)
            cnode=node.workClone


            # Add trivials node to root SoftClass node.
            for trivial_node in trivial_nodes:
                wrk=WorkClone(firstTag=cnode)
                trivial_node.accept(wrk)


class WorkSoftClassMatchDescForCustomTree(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, restrictor_dir=None, kwad_attrs=None, verbose=False, temp_dir = None, doCheck=True, doEVEX=False):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.__restrictor_dir=restrictor_dir
        self.__kwad_attrs=kwad_attrs
        self.__verbose=verbose
        self.__temp_dir = temp_dir
        self.__doCheck=doCheck
        self.__doEVEX=doEVEX

        self.softclass_nodes=list()

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        self_funct='visitNode'

        #-- Retreiving the og Custome xml tag order !
        if hasattr(element, '_wrkTagOrders'):
            element._setTagOrders(element._wrkTagOrders)
            del element._wrkTagOrders



class WorkSoftClassToDir(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveNode=True, softclass_dir=None, noDft=None, noDftRaise=None, verbose=None, logFile=None):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveNode=recursiveNode)
        self.__softclass_dir=softclass_dir
        self.__noDft=noDft
        self.__noDftRaise=noDftRaise
        self.__uniq_names={}
        self.__verbose=verbose
        self.__logFile=logFile

    def visitImbricatedNodeBase(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        self_funct='visitNode'
        from os import path, rename
        from . import tools
        
        if element.isSoftClass():
            content=element.printXml(noDft=self.__noDft, noDftRaise=self.__noDftRaise, fct_omit=element.isThisSoftClassChild).getvalue()
            
            if self.__softclass_dir==None:print(content)
            else:
                #D002: if element.getBalLabel()!=None:label='.$' + element.getBalLabel()
                #D002: else:label=''
                #D002: fname=element.getBalOg() + label
                #A002:
                fname=element.getBalOg().replace('/', '.')
                if fname not in self.__uniq_names:self.__uniq_names[fname]=-1
                else:
                    self.__uniq_names[fname]=self.__uniq_names[fname] + 1
                    fname=fname + '.%' + str(self.__uniq_names[fname])
                    
                file=path.normpath(self.__softclass_dir + '/' + fname + '.xml')
                if path.isfile(file):rename(file, file.split('.xml')[0] + '.' + tools.getTimeStamp())

                fd=open(file, 'wb')
                fd.write(bytes(content, 'utf-8'))
                fd.close()
                tools.verbose('file: ' + file + ' created !', level=self.__verbose, ifLevel=5, logFile=self.__logFile)

