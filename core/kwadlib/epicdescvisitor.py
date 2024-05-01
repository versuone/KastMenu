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


# 20220829 | 001: Python 2 to 3 Conversion
# 20220918 | 002 accept a full wk for text.
# 20221121 | 003 XFormat (yaml, hcl, json) support. Mark instance tag.
#202230901 | 004 WorkText Correction stab: apimenu

from . import epicxception

TEXTDESCS_ROLES_AUTZ_DFT={'*anyone': '-allow;-display'} 
TEXTDESCS_ROLES_AUTZ_ALLOW_ALL={'*anyone': '+all'}



class Visitor:

    def __init__(self, childFirst = True, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        self.childFirst = childFirst
        # Imbricated classes Treat the caller ?
        self.treatAncestor=treatAncestor
        # Imbricated classes recursivity ?
        self.recursiveImbricatedNodeBase = recursiveImbricatedNodeBase
        self.recursiveTagdesc = recursiveTagdesc        
        # End Imbricated classes recursivity.

    def visitNodeBase(self, element):
        pass
    
    def visitLnk(self, element): 
        pass
    
    def visitTagdesc(self, element):
        pass
        
    def visitFirstNode(self, element):           
        pass      



class WorkTestParent(Visitor):
    """ Has to be called ChildFirst=False
    """
    
    def __init__(self, childFirst = False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc)                             
        self.space=""
    
    def visitNodeBase(self, element): 
        if not element.isFirstNode():
            print(self.space + "Element:" + str(element)  + "::Parent:" + str(element.getAggregatParent()))    
            print(self.space + "_Name:" + str(element.name))            
            if hasattr(element, 'attrDescs'):print(self.space + "_Attributes:" + str(element.attrDescs))
            if hasattr(element, 'tagdescs'):print(self.space + "_Nodes childs:" + str(element.tagdescs))
            if hasattr(element, 'textDesc'):print(self.space + "_Text desc:" + str(element.textDesc))          
                   
    def visitLnk(self, element): 
            print(self.space + "Tpye:***LNK")
            print(self.space + "Element:" + str(element)  + "::Parent:" + str(element.getAggregatParent()))    
            print(self.space + "_Name:" + str(element.name))   

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        self.space=self.space + "      "
        for c in element.listNodeBases:                                       
            c.accept(self)
        self.space=self.space[0:len(self.space) - 6]            
    
    def visitTagdesc(self, element):       
        pass
        
    def visitFirstNode(self, element):           
        pass      
    


class WorkSwitchRefToWeak(Visitor):
    """ 
    Python Garbadge Concern :
    Real references to their parent for the child must
    be converted to Weak to be garbadge collected.
    """
    
    def __init__(self):
        Visitor.__init__(self)                             
    
    def visitNodeBase(self, element): 
        import weakref
        # M001: if element.aggregatParent==None or str(type(element.aggregatParent))=="<type 'weakref'>":return
        if element.aggregatParent==None or str(type(element.aggregatParent))=="<class 'weakref'>":return
        element.aggregatParent=weakref.ref(element.aggregatParent)

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)



class WorkSwitchWeakToRef(Visitor):
    """ 
    Python Pickle Concern :
    Pickle do not know how to garbadge Weak references.
    Note: that object stored in session are Pickled.
    """
    
    def __init__(self):
        Visitor.__init__(self)                             
    
    def visitNodeBase(self, element): 
        # D001: import weakref
        # M001: if not str(type(element.aggregatParent)) == "<type 'weakref'>": return
        if not str(type(element.aggregatParent))=="<class 'weakref'>":return
        element.aggregatParent=element.aggregatParent()

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)   

      
class WorkClone(Visitor):
    """
    A link cannot contains another lnk.
    """
    def __init__(self, firstDescNode=None, doCloneLink=False, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)
        self.__firstDescNode=firstDescNode
        self.__doCloneLink=doCloneLink

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNodeBase(self, element):
        element.clone(firstDescNode=self.__firstDescNode, doCloneLink=self.__doCloneLink)
        self.__firstDescNode = None

    def visitLnk(self, element):
        pass

    def visitTagdesc(self, element):
        pass

    def visitFirstNode(self, element):
        pass



class WorkClearClone(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNodeBase(self, element):
        delattr(element, 'workClone')

    def visitLnk(self, element):
        pass

    def visitTagdesc(self, element):
        pass

    def visitFirstNode(self, element):
        pass


class WorkupdQuickTun(Visitor):
    
    def __init__(self, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNodeBase(self, element):
        if element.isinstance('Lnk'):return
        element.updQuickTun()

    def visitLnk(self, element):
        pass

    def visitTagdesc(self, element):
        pass

    def visitFirstNode(self, element):
        pass


# A003: Adding XFormtat support
class WorkText(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)
    
    def visitNodeBase(self, element):
        """
        Text expected:
        - a full wk:
            __wk__={*type:list,*ltype:{*type:str},*raw:True,*help:abcd,*lhelp:%lang/softclass.jss.en/ssl.lhelp} : usefull for CDATA
        - or a part type:
            {*type:int}
            a direct wk content is taken for *ltype.
        - or a direct value:
        aaa
        bbb
        ccc
        - or if Text is <![CDATA[ we force: force_str:
            <![CDATA[
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
            ]]>
        """
        if element.isinstance('Lnk'): return
        descs = element._getText()
        if descs != None:descs = descs.strip().split('\n')
        else:descs = []

        if len(descs) == 1 and ((descs[0].startswith('{') and descs[0].endswith('}')) or (descs[0].startswith('__wk__') and descs[0].endswith('}'))):
            # A002:
            if descs[0].startswith('__wk__='):
                _desc = descs[0][7:]
            elif descs[0].startswith('__wk__ ='):
                _desc = descs[0][8:]
            else:
                _desc = descs[0]
            desc = treatWk(_desc, element.getFiliation())
            textDesc = desc


            """
            M004:
            # Retreive as wk:
            if descs[0].startswith('__wk__'):
                textDesc = desc  # A002
            # Retreive as ltype:
            elif not ('*type' in desc and desc['*type'] == 'list'):
                if '*withCoolTyping' in desc: del desc['*withCoolTyping']
                textDesc = {'*type': 'list', '*ltype': desc, '*withCoolTyping': True}
            else:
                if '*ltype' not in desc: desc['*ltype'] = {'*type': 'str'}
                desc['*withCoolTyping'] = True
                textDesc = desc
            """
            # Retreive as wk:
            if descs[0].startswith('__wk__'):
                textDesc = desc  # A002
            else:
                if not '*type' in desc:
                    if '*withCoolTyping' in desc: del desc['*withCoolTyping']
                    textDesc = {'*type': 'list', '*ltype': desc, '*withCoolTyping': True}

                if '*type' in desc and desc['*type'] == 'list':
                    if '*ltype' not in desc: desc['*ltype'] = {'*type': 'str'}
                    desc['*withCoolTyping'] = True
                    textDesc = desc

            textDesc['*rolesAutz'] = dict(TEXTDESCS_ROLES_AUTZ_ALLOW_ALL)

        # Retreive as value:
        elif len(descs) > 0:
            textDesc = {'*type': 'list', '*ltype': {'*type': 'str'}, '*withCoolTyping': True, '*value': list(descs)}
            textDesc['*rolesAutz'] = dict(TEXTDESCS_ROLES_AUTZ_ALLOW_ALL)

        else:
            textDesc = {'*type': 'list', '*ltype': {'*type': 'str'}, '*withCoolTyping': True, '*rolesAutz': dict(TEXTDESCS_ROLES_AUTZ_DFT)}

        if '*rolesAutzDft' not in textDesc: textDesc['*rolesAutzDft'] = dict(TEXTDESCS_ROLES_AUTZ_DFT)

        element.setText(textDesc)
        
    def visitLnk(self, element): 
        pass
        
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        from .epicdesc import YAML_AND_HCL_MARK_NEWTAG

        for c in element.listNodeBases:                                       
            c.accept(self)

        # A003:
        parent = element.getAggregatParent()
        if parent==None:return
        tagDesc = element.tagDesc
        # If node is multiple and this node is the sole child for its parent.
        if not (('*le' in tagDesc and tagDesc['*le'] == 1) or ('*eq' in tagDesc and tagDesc['*eq'] == 1))\
                and len(parent.listNodeBases) == 1:
                tagDesc.update({YAML_AND_HCL_MARK_NEWTAG: True})
    
    def visitNode(self, element):       
        pass      
        
    def visitFirstNode(self, element):           
        pass



def treatWk(desc, fil):
    """ Eval or CoolTyping and Wk over an expression. """
    self_funct='treatWk'
    from . import ct
    from .ct import _eval
    from . import wk
    
    ## -- eval
    if desc.find('"')>0 or  desc.find("'")>0:
        try:
            desc=_eval(desc)
        except Exception as e:
            raise epicxception.epicxmlDescriptorCheckException('Main', self_funct, 'Tag: ' + fil + ', Text, Uncorrect Python literal expression ! SubException is:' + str(e))

    ## -- CoolTyping
    else:
        try:
            desc=ct.dress(desc)
        except Exception as e:
            raise epicxception.epicxmlDescriptorCheckException('Main', self_funct, 'Tag: ' + fil + ', Text, Uncorrect Cooltyped expression ! SubException is:' + str(e))
    try:
        if not wk.isWKDefinition(desc, class_exit='Main', method_exit='visitNodeBase'):
            raise Exception('The expression:' + str(desc) + ', is not a wk expression ! Info: a value enclosed between {} must be a wk expression !')
    except Exception as e:
        raise epicxception.epicxmlDescriptorCheckException('Main', self_funct, 'Tag: ' + fil + ', Text, Error encountred evaluating the Text: ' + str(desc) + ' as a wk expression ! SubException is:' + e.__class__.__name__ + ' ' + str(e))
    
    return desc



class WorkPluginInfo(Visitor):
    """ Has to be called ChildFirst=False
    """
    
    def __init__(self, childFirst = False, isDescriptor=True, toHtml=False, temp_dir=None, verbose=0, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc)
        self.__space=""
        self.__isDescriptor=isDescriptor
        from .multilangue import MULTILANG
        from io import StringIO
        from . import tools
        MULTILANG.init(verbose=verbose)
        self.__MULTILANG=MULTILANG

        self.web_descriptor_helps={}
        self.__toHtml= toHtml
        self.__tag_format= '%-47s %-10s %-7s %s'
        self.__format= '%-15s %-15s %-15s %-10s %-7s %s'
        self.__headers= ('Name', 'Default', 'Type', 'Required', 'Denied', 'Help')
        self.__output = StringIO()

    def visitNodeBase(self, element): 
        if element.isinstance('Lnk'):return
        if not element.isFirstNode():
            
            # Print Tag
            if self.__isDescriptor:tagdescs=element.tagDesc
            else:tagdescs=element.attrRests['tagdescs']
            chars=getCharacteristics(tagdescs)
            type, help, lhelp, rolesAutz, default, required = chars['type'], chars['help'], chars['lhelp'], chars['rolesAutz'], chars['default'], chars['required']
            if 'display' in chars and chars['display']:display=True
            else:display = False

            if display==False:return
            if self.__toHtml:
                self.__output.write('<br/>' + '\n')
                end='&gt;'
            else:
                self.__output.write('\n' + '\n')
                end='>'
                
            path=element.getFiliation()
            printCharacteristics(self.__MULTILANG, self.__tag_format, path + end, None, None, required, rolesAutz, None, help, lhelp, path, isTag=True, toHtml=self.__toHtml, sb=self.__output, web_descriptor_helps=self.web_descriptor_helps)
            
            # Attrs
            if self.__isDescriptor:
                attrdescs=element.attrDescs
                oattrs=element.orderedAttrDescs
            else:
                attrdescs=element.attrRests['attrdescs']
                oattrs=element.attrRests['attrorders']

            # Text
            if self.__isDescriptor:textdescs=element.textDesc
            else:textdescs=element.attrRests['textdescs']                
            
            if len(oattrs)!=0 or '*value' in textdescs:
                if self.__toHtml:
                    self.__output.write("<table BORDER='1' CELLPADDING='3' CELLSPACING='0' style='border-width:1;border-style:ridge'>" + '\n')
                    self.__output.write("<tr>" + '\n')
                    for header in self.__headers:
                        self.__output.write("<td>" + '\n')
                        self.__output.write('<b>' + header + '</b>' + '\n')
                        self.__output.write("</td>" + '\n')
                    self.__output.write("</tr>" + '\n')

                else:

                    self.__output.write(len(self.__format % self.__headers)*'_' + '\n')
                    self.__output.write(self.__format % self.__headers + '\n')
                    self.__output.write(len(self.__format % self.__headers)*'_' + '\n')


            #> Attrs
            for attr in oattrs:
                chars=getCharacteristics(attrdescs[attr])
                type, help, lhelp, rolesAutz, default, required = chars['type'], chars['help'], chars['lhelp'], chars['rolesAutz'], chars['default'], chars['required']
                if display==False:continue

                printCharacteristics(self.__MULTILANG, self.__format, attr, default, type, required, rolesAutz, None, help, lhelp, element.getFiliation() + '/' + attr, toHtml=self.__toHtml, sb=self.__output, web_descriptor_helps=self.web_descriptor_helps)

            #> Text
            if '*value' in textdescs:
                texts=textdescs['*value']
                if self.__toHtml:
                    self.__output.write('<tr>' + '\n')
                    self.__output.write('<td>' + '\n')
                    self.__output.write("<font color='blue'><b>*Text</b></font>" + '\n')
                    self.__output.write('</td>' + '\n')
                    self.__output.write('<td>' + '\n')
                    for text in texts:self.__output.write(text + '<br/>' + '\n')
                    self.__output.write('</td>' + '\n')
                    for i in range(len(self.__headers) - 2):self.__output.write('<td>&nbsp</td>')
                    self.__output.write('</tr>' + '\n')
                else:
                    self.__output.write('*Text:')
                    for text in texts:self.__output.write('%-15s %-15s' % (' ', text) + '\n')
                
            if self.__toHtml and (len(oattrs)!=0 or '*value' in textdescs):
                self.__output.write('</table>' + '\n')

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""

        for c in element.listNodeBases:
            if element.isinstance('Lnk'):continue
            if not element.isFirstNode():
                if not self.__isDescriptor:
                    if not element.hasRestrictor():continue
                    if '*display' in element.attrRests['tagdescs'] and not element.attrRests['tagdescs']['*display']:continue
                elif '*display' in element.tagDesc and not element.tagDesc['*display']:continue

            c.accept(self)
    
    def visitTagdesc(self, element):       
        pass
        
    def visitFirstNode(self, element):           
        pass     
        
    def output(self):
        return self.__output.getvalue()

def getCharacteristics(wks):
    type=None
    help=None
    lhelp=None
    rolesAutz=None
    default=None
    required=False
    if '*rolesAutz' in wks:rolesAutz=wks['*rolesAutz']
    else:rolesAutz=None
    if '*rolesAutzDft' in wks:rolesAutzDft=wks['*rolesAutzDft']
    else:rolesAutzDft=None
    
    if '*type' in wks:type=wks['*type']
    if '*checkIn' in wks:type=str(wks['*checkIn']).replace("'", '')
    if '*help' in wks:help=wks['*help']
    if '*lhelp' in wks:lhelp=wks['*lhelp']
        
    if '*value' in wks:default=wks['*value']
    if '*required' in wks:required=wks['*required']
    if '*eq' in wks and wks['*eq']==1:required=True
    if '*between' in wks and wks['*between'][0]>=1:required=True
    
    return {'type': type, 'help':help, 'lhelp':lhelp, 'rolesAutz': rolesAutz, 'rolesAutzDft': rolesAutzDft, 'default': default, 'required': required}

def printCharacteristics(MULTILANG, format, name, default, type, required, rolesAutz, rolesAutzDft, help, lhelp, path, isTag=False, toHtml=False, sb=None, web_descriptor_helps=None):
    if default==None:default=''
    else:default=str(default)
    if type==None:type=''
    if required!=True:required=''
    else:required='True'
    if rolesAutz==None:rolesAutz=''
    if rolesAutzDft==None:rolesAutzDft=''
    rolesAutz=str(rolesAutz)
    rolesAutzDft=str(rolesAutzDft)

    # help
    if help==None:help=''
    else:help=MULTILANG.convert(help)
    if lhelp!=None and help!=None:
        web_descriptor_helps[path]=MULTILANG.convert(lhelp).replace('<', '&lt;').replace('>', '&gt;')
        if toHtml:help='<a ' + 'href="' + "javascript:wiki_showDescHelp('" + path + "')" + '">' + help + '</a>'
        else:help+='\n'
    
    if not isTag:l = (name, default, type, required, rolesAutz, rolesAutzDft, help)
    else:
        if toHtml: d = {'name': name, 'required': required, 'rolesAutz': rolesAutz, 'rolesAutzDft': rolesAutzDft, 'help': help}
        else:l = (name, required, rolesAutz, rolesAutzDft, help)

    if toHtml:
        
        if isTag:
            sb.write('<b>' + d['name'] + '</b>&nbsp&nbsp ' + d['help'] + '\n')
            sb.write('<br/>' + '\n')
            if d['required']!='': sb.write('Required:' + d['required'] + '<br/>' + '\n')
            
        else:
            firstime=True
            sb.write('<tr>' + '\n')
            for td in l:
                sb.write('<td>' + '\n')
                
                if td == '':sb.write('&nbsp' + '\n')
                else:
                    if firstime:
                        firstime=False
                        td="<font color='blue'><b>" + td + "</b></font>"
                    sb.write(td + '\n')
                sb.write('</td>' + '\n')
            sb.write('</tr>' + '\n')
            
    else:sb.write(format % l + '\n')



class WorkCheckRestrictor(Visitor):

    def __init__(self, descriptor=None, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)

        self.descriptor=descriptor
        self.prefix='[RestrictorCheck]'
    
    def visitNodeBase(self, element):
        selfMethod = 'visitNodeBase'
        if element.isinstance('Lnk'):return      
        if element.isFirstNode():return
        
        try:
            peerTagdesc=self.descriptor.getPeerTagdesc(element.getFiliation())
        except:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, self.prefix + 'The Restrictor Tag:' + str(element.getFiliation()) + ' is not defined into the Descriptor file !' ) 
        
        for attr in element.attrDescs:
            if attr not in peerTagdesc.attrDescs:
                raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, self.prefix + 'Tag:' + str(element.getFiliation()) + ', the Restrictor Attribute:' + attr + 'is not defined into the Descriptor file, for this tag !' ) 
        
    def visitLnk(self, element): 
        pass
        
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)
    
    def visitNode(self, element):       
        pass      
        
    def visitFirstNode(self, element):           
        pass


class WorkrmvQuickTun(Visitor):

    def __init__(self, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)
        self.__top = None

    def visitNodeBase(self, element):
        if self.__top == None:self.__top = element.getTopParent()

        self.__top._delQuickTun(element.getTun())
        element.isDead = True

    def visitLnk(self, element):
        pass

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:
            c.accept(self)

    def visitNode(self, element):
        pass

    def visitFirstNode(self, element):
        pass




class WorkQuickTun(Visitor):
    def __init__(self, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)
        self.__topd = None

    def visitImbricatedNodeBase(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listNodeBases:
            c.accept(self)

    def visitNodeBase(self, element):
        self_funct='visitNode'

        if self.__topd == None:
            self.__topd = element.getTopParent()

        # Node:
        # -----
        # Topd QuickTun:
        element.filiation = None #  # force tun generation only for tagDesc wich is based on filiation (and may change with: setAggregatParent)
        if not self.__topd._hasQuickTun(element.getTun()):self.__topd._setQuickTun(element.getTun(), element)
