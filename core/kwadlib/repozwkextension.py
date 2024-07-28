###############################################################################
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
###############################################################################




#=============#
# wkExtension #
#=============#

import re
from kwadlib import repozwkexception
QUERY_QL_RE=re.compile('\[([^\]]*)\]', re.IGNORECASE)  
QUERY_LQ_RE=re.compile('\$\(([^)]*)\)', re.IGNORECASE)    
QUERY_PATTERN_SYNTAX=""" e.g:
<repoz_alias>[<query_langage>]<query_string>
e.g.:global|groupes.xml[xpath]groups/group,@name

<repoz_alias>: is the alias for a file already loaded as a repoz processor (pc) within the repository.

<query_langage>: is the langage you want to use to query this file 
(ex: the xml processor (xpc) supports two query langages askapy xpath and askapy xql).
Note: the brackets "[" and "]" are requiered and are part of the syntax.

<query_string>: is the query string of the previously quoted langage.

e.g.:
a/ global|groupes.xml[xpath]groups/group,@name
This will retreive the value of the xml attribute: name, from the node at xpath groups/group within the xml file
managed by the repoz (xpc) processor with alias: global|groupes.xml.

b/ template|kwad.attrs[xql]verbose
This will retreive the value of the attribute: verbose, from the attrs file
managed by the repoz (apc) processor with alias: template|kwad.attrs.

More advanced features:
-----------------------
c/ global|groupes.xml[xpath]groups/group@active=true,@name
The same as a/.
Plus will only match node groups with the "active" attribute equal to "true".

d/ global|groupes.xml[xpath]groups/group@active=$(@active),@name
The same as a/.
Plus will only match node groups with the "active" attribute equal to the value of the "active" attribute
of the source node.            

e/ global|groupes.xml[xpath]groups/group@active=$(tag1/tag2/tag3@active),@name
The same as a/.
Plus will only match node groups with the "active" attribute equal to the value of the "active" attribute
of not the source node but at its parent's level at tag1/tag2/tag3 (tag1 is the top tag).
"""
XPC_SUPPORTED_QUERY_LANGAGES=('xpath',)
APC_SUPPORTED_QUERY_LANGAGES=('apath',)


class wkExtension:
    SUPPORTED_KEY_ORDERS=('*@checkUid', '*@genUid', '*@value', '*@checkIn')
    SUPPORTED_PC_TYPES=('apc', 'xpc')
    
    def __init__(self, repoz, alias_source=None, item=None, doCheck=False):
        selfMethod='__init__'
        import weakref
        
        self.__repoz=weakref.ref(repoz)
        self.__alias_source=alias_source
        self.__item=item
        self.__doCheck=doCheck
        
        if self.__alias_source!=None:
            self.__pc_infos=self.__getRepoz().mkPcInfo(self.__alias_source)
            if self.__pc_infos.getPcType()=='xpc':more='/Tag:' + self.__item.getTag()
            else:more=''
            if self.__alias_source!=None: more=', from alias:' + self.__alias_source + more
            msufix=''
            
            if self.__pc_infos.getPcType() not in wkExtension.SUPPORTED_PC_TYPES:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix + ' wkExtension is not supported on this PC Type:' + self.__pc_infos.getPcType() + ' ! Supported PC Types are:' + str(wkExtension.SUPPORTED_PC_TYPES).replace("'", '')[1:-1] + '.')
        
    def __getRepoz(self):
        return self.__repoz()        
        
    def __getPcInfos(self, alias):
        return self.__getRepoz().mkPcInfo(alias)
    
    def getKeywords(self, attr, wks, value, keywords=None, class_exit=None, method_exit=None):
        selfMethod='getKeywords'
        
        for key in wkExtension.SUPPORTED_KEY_ORDERS:
            if key in wks:value=self.resolve(attr, wks, value, key, keywords=keywords, class_exit=class_exit, method_exit=method_exit)

        return wks, value

    def resolve(self, attr, wks, value, key, keywords=None, class_exit=None, method_exit=None):
        selfMethod='resolve'
        if self.__alias_source!=None and self.__pc_infos.getPcType()=='xpc':more='/Tag:' + self.__item.getTag() + '/attr:' + attr
        else:more='/Attr:' + attr
        if self.__alias_source!=None: more=', from alias:' + self.__alias_source + more
        
        mprefix='This Definition:' + str(wks) + more + ', is not a WKDefinition. For key:' + key + '.'
        mconstraint='This Definition:' + str(wks) + more + ', Failed constraint. For key:' + key + '.'
        if (class_exit, method_exit)!=(None, None):msufix=" SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit)
        else:msufix=''
        
        # if check:self.isWKDefinition(attr, wks, key=key, class_exit=class_exit, method_exit=method_exit)

        item = self.__item
        if key=='*@checkUid':
            """ e.g: unique key (if value is not None)
            *@checkUid: True|False ==> raise
            """
            if not isinstance(wks[key], bool):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Expected: *@checkUid: True|False. Received:' + str(wks[key]) + ' !')            
            if self.__alias_source==None or not self.__pc_infos.getPCType()=='xpc':raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' wkExtension Attribute: "*@checkUid" is only supported on xpc Repository Processor !')
            
            if not wks[key] or value==None or item.isFirstNode() or item.getAggregatParent()==None:pass
            else:
                parent=item.getAggregatParent()
                nodes=parent.getNodes()
                l=[node.getAttr(attr) for node in nodes]
                
                if value in l:raise repozwkexception.repozCheckUidException(self.__class__.__name__, selfMethod + mconstraint, mprefix + ' Reject this preexisting key:' + value + ' on alias:' + self.__alias_source + more + ' at filiation:' + item.getFiliation() + ' !')
            
        elif key=='*@genUid':
            """ e.g: generates unique key (if value is None)
            *@genUid: <idprefix> ==> generates uid on this item
            """
            if not isinstance(wks[key], str) or wks[key].isspace():raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, attr, wks, value, key, mprefix + ' Expected: *@genUid: <id_prefix>. Received:' + str(wks[key]) + ' !')
            if self.__alias_source==None or not self.__pc_infos.getPCType()=='xpc':raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' wkExtension Attribute: "*@genkUid" is only supported on xpc Repository Processor !')
            
            if value==None:
                if wks[key]!=None:
                    if item.isFirstNode() or item.getAggregatParent()==None:id='00000'
                    else:
                        parent=item.getAggregatParent()
                        nodes=parent.getNodes()
                        l=[node.getAttr(attr) for node in nodes]
                        l=[val for val in l if isinstance(val, str) and val.startswith(wks[key]) and val.split(wks[key])[-1].isdigit()]
                        if len(l)==0:id='00000'
                        else:
                            l.sort()
                            last=l[-1]
                            last.split(wks[key])[-1]
                            last=int(last)
                            
                            last=str(last + 1)
                            i=len(last) - 5
                            if i>0:
                                for j in range(i):
                                    last='0' + last

                            id=wks[key] + last

                value=id

        elif key=='*@value':
            """ e.g:
            '*@value': 'global|groupes.xml[xpath]groups/group,@name' ==> '*value': 1'
            '*@value': 'template|kwad.attrs//verbose' ==> '*value': 1'
            '*@value': 'global|groupes.xml[xpath]groups/group@name=$(tag1/tag2@attr2=val2)/user@name=$(@attr2),@user
            """
            
            value, query=self.grabQuery(wks[key], attr, value, keywords=keywords, infos={'key': key, 'wks' :dict(wks)}, mprefix=mprefix, msufix=msufix)
            
        elif key=='*@checkIn':
            """ e.g:
            '*@checkIn': 'global|groupes.xml[xpath]groups/group@name' ==> '*@checkIn': ('aaa', 'bbb')
            """
            values, wks[key]=self.grabQuery(wks[key], attr, value, keywords=keywords, infos={'key': key, 'wks' :dict(wks)}, mprefix=mprefix, msufix=msufix)
            if values==None or len(values)==0:raise repozwkexception.repozWkCheckInException(self.__class__.__name__, selfMethod + msufix, mconstraint + ' wkExtension Attribute: "*@CheckIn" No values retreived !', attr=attr, value=value, key=key, wks=wks)

            if not isinstance(values, list):values=[values]
            wks['*checkIn']=values
            
            if self.__doCheck and value not in values:raise repozwkexception.repozWkCheckInException(self.__class__.__name__, selfMethod + msufix, mconstraint + ' wkExtension Attribute: "*@CheckIn" value:' + str(value) + ', not found in:' + str(values)[1:-1] + ' !', attr=attr, value=value, key=key, wks=wks)

            return value            
        
        elif key=='*@checkXIn':
            """ e.g:
            '*@checkXIn': 'global|groupes.xml[xpath]groups/group@name' ==> '*@checkIn': ('aaa', 'bbb')
            """
            values, wks[key]=self.grabQuery(wks[key], attr, value, keywords=keywords, infos={'key': key, 'wks' :dict(wks)}, mprefix=mprefix, msufix=msufix)
            if values==None or len(values)==0:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' wkExtension Attribute: "*@CheckIn" No values retreived !')

            if not isinstance(values, list):values=[values]
            wks['*checkXIn']=values
            
            if self.__doCheck:
                if not isinstance(value, (list, tuple)):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' *value:' + str(value) + ' should be a list or a tuple !')
                for val in value:
                    if value not in values:
                        raise repozwkexception.repozWkCheckXInException(self.__class__.__name__, selfMethod + msufix, mconstraint + ' value:' + str(value) + ' from key *value:' + str(values) + ' not found in:' + str(values)[1:-1] + ' !', attr=attr, value=value, key=key, wks=wks)

            return value
    
    def grabQuery(self, query, attr, value, keywords=None, infos=None, mprefix='', msufix=''):
        """
        <repoz_alias>[<query_langage>]<query_string>
        """
        selfMethod='isQueryPattern'

        # Query Langage:
        founds=QUERY_QL_RE.findall(query)
        if len(founds)!=1:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Incorect query expression:' + str(query) + ' ! The query syntax is:\n' + QUERY_PATTERN_SYNTAX + '.')
        query_langage=founds[0]
        
        # Alias Destination:
        alias_dest, query=query.split('[' + query_langage + ']')
        if not self.__getRepoz().hasAlias(alias_dest):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' The Alias:' + alias_dest + ' is not loaded into the repository !')
        dest_pc_infos=self.__getPcInfos(alias_dest)
        if dest_pc_infos.getPcType() not in wkExtension.SUPPORTED_PC_TYPES:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' wkExtension Query is not supported on this Target PC Type:' + dest_pc_infos.getPcType() + ' ! Supported PC Types are:' + str(wkExtension.SUPPORTED_PC_TYPES).replace("'", '')[1:-1] + '.')

        # Query:
        local_queries=QUERY_LQ_RE.findall(query)
        
        for local_query in local_queries:
            query=query.replace('$(' + local_query + ')', self.grabLocalQuery(local_query, attr, value, keywords=keywords, mprefix=mprefix + ' Incorect query expression:' + str(query), msufix=msufix))
        if dest_pc_infos.getPcType()=='xpc':
            if query_langage!='xpath':raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Incorect query_langage:' +  query_langage + '. Supported query_langage for repoz type "xpc" are:' + str(XPC_SUPPORTED_QUERY_LANGAGES)[1:-1] + ' !')
            try:
                topNode=dest_pc_infos.getPc()
                value, nodes=topNode.tdc(query, checkIsNode=False, checkIsAttr=True, doRetNodeIfIsAttr=True, checkIsUnique=False)
                # dft:  tdc(self, pxq, checkIsNode=True, checkIsAttr=False, doRetNodeIfIsAttr=False, checkIsUnique=False,
                
                qattr=query.split('@')[-1]
                if not isinstance(nodes, list):return nodes.getAttr(qattr), alias_dest + '[' + query_langage + ']' + query
                else:return [node.getAttr(qattr) for node in nodes], alias_dest + '[' + query_langage + ']' + query
            
            except Exception as e:
                raise repozwkexception.repozWkCheckException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Incorect query expression:' + str(query) + ' ! SubException is:' + str(e) + ' !', attr=attr, value=value, key=infos['key'], wks=infos['wks'])

        elif dest_pc_infos.getPcType()=='apc':
            if query_langage!='apath':raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Incorect query_langage:' +  query_langage + '. Supported query_langage for repoz type "apc" are:' + str(APC_SUPPORTED_QUERY_LANGAGES)[1:-1] + ' !')
            if not query.startswith('@'):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Incorect query expression:' + str(query) + ' ! This query should start with "@" !')
            if query.find('/')>=0:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Incorect query expression:' + str(query) + ' ! This query should not contain "/" after "@" !')
            attr=local_query[1:]
            
            if not dest_pc_infos.hasAttr(attr):raise repozwkexception.repozWkCheckException(self.__class__.__name__, selfMethod + msufix, mprefix + ' Incorect query expression:' + str(query) + ', Attribute:' + attr + ' incorrect ! Supported attributes are:' + str([attr for attr in self.__item.getAttrDesc()]).replace("'", '')[1:-1] + ' !', attr=attr, value=value, key=infos['key'], wks=infos['wks'])
            
            return dest_pc_infos.getPc().getAttr(attr), alias_dest + '[' + query_langage + ']' + query

    def grabLocalQuery(self, local_query, wkattr, wkvalue, keywords=None, mprefix='', msufix=''):
        """
        <repoz_alias>[<query_langage>]<query_string>
        """
        selfMethod='grabLocalQuery'
        
        if not local_query.find('/')>=0:
            if not local_query.startswith('@'):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ' should start with: @ !')
            attr=local_query[1:]
            
            if self.__item==None and not attr in keywords:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ', Attribute:' + attr + ' incorrect ! Supported attributes are:' + str(list(keywords.keys())).replace("'", '')[1:-1] + ' !')
            if self.__item==None:
                if attr==wkattr:value=wkvalue
                else:value=keywords[attr]
            else:
                if not self.__item.hasAttr(attr):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ', Attribute:' + attr + ' incorrect ! Supported attributes are:' + str([attr for attr in self.__item.getAttrDesc()]).replace("'", '')[1:-1] + ' !')
                if attr==wkattr:value=wkvalue
                else:value=self.__item.getAttr(attr)
                
            if value!=None and isinstance(value, (list, tuple, dict)):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' *value:' + str(value) + ' should not be list, a tuple or a dict !')

            return value
            
        if self.__alias_source==None or not self.__pc_infos.getPCType()=='xpc':
            if self.__alias_source!=None:more=' ' + self.__pc_infos.getPCType()
            else:more=' NO PC'
            raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ' should not contains "/", that are not supported by:' + more + ' Repository Processor !')
        
        spl=local_query.split('@')
        if len(spl)!=2:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ' should end with: @<attr> !')
        lq_filstr, attr=spl
        
        if not lq_filstr.find('/')>=0:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ' should be shaped like: /<tag1[/tag2]@<attr> !')
        if attr.find('/')>=0:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ' should end with: @<attr> and not contain any "/" after "@" !')
        
        filiations=[o.getName() for o in self.getAggregatFiliation([])]                
        filiations.insert(0, self.__item)
        filiations.reverse()
        filstr='/' + '/'.join([o.getName() for o in filiations])
        
        if not filstr.startswith(lq_filstr):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + " tag's chain:" + lq_filstr + ' is not comprised within this tag filiation:' + filstr + ' !')
        lq_filstrs=lq_filstr.split('/')
        
        o=filiations[len(lq_filstrs)-1]
        if o.getName()!=lq_filstrs[len(lq_filstrs)-1]:raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + " tag's chain:" + lq_filstr + ' is not comprised within this tag filiation:' + filstr + ' !')
        if not o.hasAttr(attr):raise repozwkexception.repozWkSystemException(self.__class__.__name__, selfMethod + msufix, mprefix + ' This Local Query:' + local_query + ', Attribute:' + attr + ' incorrect ! Supported attributes are:' + str([attr for attr in self.__item.getAttrDesc()]).replace("'", '')[1:-1] + ' !')
        
        return str(o.getAttr(attr))