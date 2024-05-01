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


# 20220918 | 002 accept a full wk for text.

from .jython_aptitude import *
from . import xception

ALLOWED_TAG_DESCS_KEYS=('*lt', '*le', '*gt', '*ge', '*eq', '*help', '*lhelp', '*rolesAutzDft', '*rolesAutz')
ROLES_AUTZ_DFT={'*anyone': '+all'}
TEXTDESCS_ROLES_AUTZ_DFT={'*anyone': '-allow;-display'}
TEXTDESCS_ROLES_AUTZ_ALLOW_ALL={'*anyone': '+all'}

class Visitor:

    def __init__(self, childFirst=True, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True):
        self.childFirst = childFirst
        # Imbricated classes Treat the caller ?
        self.treatAncestor = treatAncestor
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

class WorkDesc(Visitor):
    
    def __init__(self, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveTagdesc=True, isDescriptor=False):
        Visitor.__init__(self, childFirst=childFirst, treatAncestor=treatAncestor, recursiveImbricatedNodeBase=recursiveImbricatedNodeBase, recursiveTagdesc=recursiveTagdesc)
        self.isDescriptor=isDescriptor
        self.descs = dict()
        self.descs['orderedFiliations']=[]

    def visitImbricatedNodeBase(self, element):
        """Recursivity on imbricated Classes."""
        
        for c in element.listNodeBases:
            c.accept(self)
    
    def visitNodeBase(self, element):       
        self_funct='visitNodeBase'
        if self.isDescriptor:
            err_class='kwadSoftClassDescriptorSyntaxException'
        else:
            err_class='kwadSoftClassRestrictorSyntaxException'

        """ D030: 
        top=element.getTop()
        topname=top.getName()

        # role support
        if topname in self.descs:
            if '*rolesAutzDft' in self.descs[topname]['tagdescs']:
                rolesAutzDft=self.descs[topname]['tagdescs']['*rolesAutzDft']
            else:rolesAutzDft=dict(ROLES_AUTZ_DFT)
            if '*rolesAutzDft' in self.descs[topname]['textdescs']:textdescs_rolesAutzDft=self.descs[topname]['textdescs']['*rolesAutzDft']
            else:textdescs_rolesAutzDft=dict(TEXTDESCS_ROLES_AUTZ_DFT)
        else:
            rolesAutzDft=dict(ROLES_AUTZ_DFT)
            textdescs_rolesAutzDft=dict(TEXTDESCS_ROLES_AUTZ_DFT)
            
        if '*anyone' in rolesAutzDft and '+all' in rolesAutzDft['*anyone'].split(';'):optimistic='+*optimistic'
        else:optimistic='-*optimistic'
        if '*anyone' not in rolesAutzDft:rolesAutzDft['*anyone']=optimistic
        elif rolesAutzDft['*anyone'].find('*optimistic')<0:rolesAutzDft['*anyone']+=';' + optimistic
        """
        dattrs=dict(element.attrDescs)
        attrdescs=dict()
        tagdescs=dict()

        #-----------------#
        # Check Attribute #
        #-----------------#
        
        als=list(dattrs.keys())
        als.sort()
        for attr in als:

            if attr=='__wk__':
                # - treats tag wk = #
                tagdescs=dattrs[attr]
                l=list(tagdescs.keys())
                # role support
                ## D030: if '*rolesAutzDft' not in tagdescs:tagdescs['*rolesAutzDft']=dict(rolesAutzDft)
                ## D030: if '*rolesAutz' not in tagdescs:tagdescs['*rolesAutz']=tagdescs['*rolesAutzDft']
        
                for key in  l:
                    if key not in ALLOWED_TAG_DESCS_KEYS:raise getattr(xception, err_class)(self.__class__.__name__, self_funct, "For tag:" + element.getName() + "/attribute:"  + attr + ', Unsupported key:' + key + ', for tag wk. A tag wk only supports these keys:' + str(ALLOWED_TAG_DESCS_KEYS) + '.')
                element.delAttr(attr)
                continue

            # - treats attr wk = #
            desc=dattrs[attr]

            # role support
            ## D030: if '*rolesAutzDft' not in desc:desc['*rolesAutzDft']=dict(rolesAutzDft)
            ## D030: if '*rolesAutz' not in desc:desc['*rolesAutz']=desc['*rolesAutzDft']
            
            attrdescs[attr]=desc


        #------------#
        # Check Text #
        #------------#

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

        textdescs = element.textDesc

        # role support
        ## D030:  if '*rolesAutzDft' not in textdescs:textdescs['*rolesAutzDft']=dict(textdescs_rolesAutzDft)
        ## D030:  if '*rolesAutz' not in textdescs:textdescs['*rolesAutz']=textdescs['*rolesAutzDft']


        attr_orders=list(element.orderedAttrDescs)
        attrdescs_keys=list(attrdescs.keys())
        self.descs[element.getFiliation()[1:]]={'attrdescs': attrdescs, 'attrorders': [key for key in attr_orders if key in attrdescs_keys], 'textdescs': textdescs, 'tagdescs': tagdescs, 'tagorders': element.getTagOrders()}
        self.descs['orderedFiliations'].append(element.getFiliation()[1:])

