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
# 2015/05/25  | 006 | Epicxmlp Cache support
# 2022/09/18  | 007 | Modify TreatCDATA to Support b64

from . import epicxception
from . import xmlscraper
from . import wk
try:
    from . import repoztools as tools
except:from . import tools
import weakref

import re
RE_SUP=re.compile('<[^/]', re.IGNORECASE)

# 007: Deprecated:
NEW_CDATA_BEGIN='$&lt;![CDATA['
NEW_CDATA_END=']]$&gt;'
ALTER_SUP='$&gt;'
ALTER_INF='$&lt;'
# A007:
CDATA_BEGIN='<![CDATA['
CDATA_END=']]>'
B64FLAG = "[[KIK-CDATA-BASE64-FLAG:]]"


class Node(tools.StructSerializable):
    _apb_isinstance_Node='Node'

    def _init(self, xmlNode=None, xmlSucker=None, **keywords):
        self.errorPrefix=''
        self.dontSerialize=('allowedAttributesValue', 'allowedChilds', 'xmlNodeLnk')
        self.xmlNodeLnk=xmlNode
        
        if xmlSucker!=None:
            if xmlSucker.foundFirstNode==None:xmlSucker.foundFirstNode=self.getFirstNode(xmlSucker.trivialParmToFirstNode)
            xmlSucker.foundFirstNode.capSensitive=xmlSucker.isCapSensitive()
            self.capSensitive=xmlSucker.isCapSensitive()
            self.xmlNodeLnk.foundFirstNode=xmlSucker.foundFirstNode
        if xmlNode!=None and xmlNode.nodeType==xmlNode.ELEMENT_NODE:self.xmlNodeLnk.attrs=xmlSucker.getAttributes(xmlNode)
        
        self.init(**keywords)

        if self.xmlNodeLnk!=None and xmlSucker!=None:self.initFrom_xmlNode(xmlSucker)  

    def initFrom_xmlNode(self, xmlSucker):     
        selfMethod='initFrom_xmlNode'
        node=self.xmlNodeLnk
        if  node==None or (node!=None and node.nodeType not in (node.ELEMENT_NODE, node.TEXT_NODE)):
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, self.errorPrefix + "Received Incorect value received for node:" + str(node)) 

        nodeName=str(node.nodeName).strip()

        if node.nodeType==node.ELEMENT_NODE:
            lstNodeAttr=self.xmlNodeLnk.attrs

            kws=dict()
            for attr in lstNodeAttr:
                if self.isCapSensitive():atr=attr
                else:atr=attr.lower()
                    
                if hasattr(self, 'allowedAttributesValue'):
                    if atr not in  self.allowedAttributesValue:
                        raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, self.errorPrefix + "For tag:" + nodeName + ", Not allowed attribute:" + atr + ";  Allowed attributes are:" + str(list(self.allowedAttributesValue.keys())))                        
                kws[atr]=lstNodeAttr[attr]
                if kws[atr]=='':kws[atr]=None
                
            if hasattr(self, 'allowedAttributesValue'):               
                p=wk.WantedKeywords()
                for attr in self.allowedAttributesValue:
                    setattr(p, attr, self.allowedAttributesValue[attr])
                wk.getKeywords(wantedKeywords=p, keywords=kws, class_exit=str(self.__class__), method_exit=selfMethod)
                wk.setp1top(p, self)                        
 
        node.instanceLnk=self   
        if hasattr(node.getParentNode(), 'instanceLnk'):                     
            node.getParentNode().instanceLnk.xml_addChild(self)        
        else:xmlSucker.foundFirstNode.xml_addChild(self)
        
        # A003:
        self.clearTrivialRef()

    def isCapSensitive(self):
        return self.capSensitive

    # A003:
    def clearTrivialRef(self):
        if hasattr(self, 'xmlNodeLnk'):delattr(self, 'xmlNodeLnk')

class XmlSuckerScraper(xmlscraper.Scraper):

    def __init__(self, modName = "", docPath="", docString=None, exceptTags=(), doRun=True, trivialParmToFirstNode={}, capSensitive=False, vars=None, beStrict=True, dotreatCDATA=True, verbose=0):
    # D006: def __init__(self, modName = "", docPath="", docString=None, exceptTags=(), doRun=True, trivialParmToFirstNode={}, capSensitive=False, vars=None, beStrict=True, temp_dir=None, tmpl_kws={}, showResultingSourceOnly=False, verbose=0):
        selfMethod='__init__'
        self.errorPrefix=''
        if docPath not in (None, ''):
            from os import path
            docPath=path.normpath(docPath)
            self.errorPrefix='Xml File:' + str(docPath) + ' '
        
        if modName=="" or not isinstance(modName, str):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, self.errorPrefix + ', modName', 'str', str(modName))                
        if docPath!=None and not isinstance(docPath, str):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, self.errorPrefix + ', docPath', 'str', str(docPath))                
        if docString!=None and not isinstance(docString, str):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, self.errorPrefix + ', docString', 'str', str(docString))                
        if docPath==None and docString==None:raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, self.errorPrefix + "One of docPath or docStringNot must be set") 
        if not isinstance(exceptTags, tuple):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'exceptTags', 'tuple', str(exceptTags))                
        if not isinstance(capSensitive, bool):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'capSensitive', 'bool', str(capSensitive))                
        if vars!=None and not isinstance(vars, dict):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'vars', 'dict', str(vars))                
        if not isinstance(beStrict, bool):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'beStrict', 'bool', str(beStrict))
        if not isinstance(dotreatCDATA, bool):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'dotreatCDATA', 'bool', str(dotreatCDATA))

        if verbose>=3 and docPath not in (None, ''):print('XmlSuckerScraper: reading file:' + str(docPath) + '.', docPath=='.')
        
        # Dynamic import for plugable sub-layer.
        self.mod = tools.getModule(modName)

        xmlscraper.Scraper.__init__(self) 
        self.exceptTags=exceptTags
        self.__beStrict=beStrict
        self.__strictTags=[]
        self.firstTime=True
        self.nodeAttributes={}
        self.nodeIndex=0
        self.parentNode=[]
        self.doTreatChilds=True
        self.__docString=docString
        self.__docPath=docPath        
        self.__vars=vars        
        self.trivialParmToFirstNode=trivialParmToFirstNode        
        self.foundFirstNode=None
        self.capSensitive=capSensitive
        self.__dotreatCDATA = dotreatCDATA
        
        if doRun:
            source=self.run()
## D006:
##            if self.__showResultingSourceOnly:
##                self.source=source
##                return
        
        #f814290522f79d1e9e5ae4ae83e967b4

    def isCapSensitive(self):
        return self.capSensitive
    
    def getModule(self):
        return self.mod
    

    def run(self):
        if self.__docString!=None:src=self.__docString
        else:
## D006:
##            if self.__docPath.endswith('.mako'):
##                src=self.mako() # A005
##                if self.__showResultingSourceOnly:return src
##            else:
                fd=open(self.__docPath, 'rb')
                src=fd.read().decode("utf-8")
                fd.close()
            
        if self.__vars!=None:
            for var in self.__vars:src=src.replace(var, self.__vars[var])

        # epicdesc dont want CDATA as it just expect a wk: ==> dont b64:
        src=XmlSuckerScraper.treatCDATA(src, self.errorPrefix, doB64=self.__dotreatCDATA)

        src, self.trivialParmToFirstNode['comment_recorders']=XmlSuckerScraper.treatBackSlash(src, errorPrefix=self.errorPrefix)
        
        self.feed(src)
        
        # clear that mess
        self.__docString=None
        self.__docPath=None
        self.__vars=None
        
    def pdata(self, inchunk):
        """Called when we encounter a new tag. All the unprocessed data since the last tag is passed to this method.
        Dummy method to override. Just returns the data unchanged."""
        if inchunk.startswith('!--'):self.doTreatChilds=False
        
        nodeName='#text'
        if self.doTreatChilds==True:        
            if  str(inchunk).strip()!="" and self.parentNode!=[]:
                class_name= self.mod.XMLSUCKER_NODE_EQUIV[nodeName]
                self.nodeIndex+=1
                nod=node(name=nodeName, id=self.nodeIndex, nodeType=node.TEXT_NODE, nodeValue=str(inchunk), parentNode=self.parentNode[-1:][0])
                nod2=getattr(self.mod, class_name)(xmlNode=nod, xmlSucker=self)
                nod2.errorPrefix=self.errorPrefix
                
        if inchunk.rstrip().endswith('-->'):
            self.doTreatChilds=True
        return inchunk    

    def pdecl(self):
        """Called when we encounter the *start* of a declaration or comment. <!....
        It uses self.index and isn't passed anything.
        Dummy method to override. Just returns."""
        return '<'
    
    def ppi(self):
        """Called when we encounter the *start* of a processing instruction. <?....
        It uses self.index and isn't passed anything.
        Dummy method to override. Just returns."""
        return '<'

    def endtag(self, thetag):
        """Called when we encounter a close tag. </....
        It is passed the tag contents (including leading '/') and just returns it."""
        selfMethod='endtag'
        if self.doTreatChilds==True:        
            if self.parentNode!=[]:self.parentNode.pop()
        
        # Begin/End Tag detection
        if self.__beStrict:
            nodeName=thetag.split('/')[1].strip()
            if not self.isCapSensitive():nodeName=nodeName.lower()

            if len(self.__strictTags)==0:raise epicxception.epicxmlXmlSyntaxException(self.__class__.__name__, selfMethod, self.errorPrefix + 'Found End Tag:' + nodeName + ', with no begining !')
            if len(self.__strictTags)>0:
                parentTag=self.__strictTags[-1]
                
                if nodeName!=parentTag:raise epicxception.epicxmlXmlSyntaxException(self.__class__.__name__, selfMethod, self.errorPrefix + 'End Tag:' + nodeName + ' do not match parent Tag:' + parentTag + '.')

            del self.__strictTags[-1]
        
        return '<' + thetag + '>'

    def emptytag(self, thetag):
        """Called when we encounter a tag that we can't extract any valid name or attributes from.
        It is passed the tag contents and just returns it."""
        return '<' + thetag + '>'  

    def handletag(self, name, attrs, thetag):        
        selfMethod='handletag'
        
        # Begin/End Tag detection
        if self.__beStrict and not thetag.strip().endswith('/'):self.__strictTags.append(name.split('/')[0].strip())
        
        # Do the job
        if self.doTreatChilds==True:
       
            if self.isCapSensitive():nodeName=name.split('/')[0].strip('')
            else:nodeName=name.split('/')[0].strip('').capitalize()

            if nodeName in self.exceptTags:return '<' + thetag + '>'
            if nodeName not in self.mod.XMLSUCKER_NODE_EQUIV and '*' not in self.mod.XMLSUCKER_NODE_EQUIV:
                raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, self.errorPrefix + "Not allowed tag:" + nodeName + ";  Allowed tags are: " + str(list(self.mod.XMLSUCKER_NODE_EQUIV.keys()))) 
    
            if nodeName not in self.mod.XMLSUCKER_NODE_EQUIV and '*' in self.mod.XMLSUCKER_NODE_EQUIV:
                class_name= self.mod.XMLSUCKER_NODE_EQUIV['*']
            else:class_name= self.mod.XMLSUCKER_NODE_EQUIV[nodeName]
    
            self.nodeIndex+=1
            dictKeys=DictKeys()
            listKeys=[]
            for attr in attrs:
                if self.isCapSensitive():
                    dictKeys[attr[0]]=attr[1]
                    listKeys.append(attr[0])            
                else:
                    dictKeys[attr[0].upper()]=attr[1]
                    listKeys.append(attr[0].upper())
                
            dictKeys.setOrderedAttrs(listKeys)
            self.nodeAttributes[self.nodeIndex]=dictKeys
        
            if self.parentNode==[]:parentNode=None
            else:parentNode=self.parentNode[-1:][0]
                
            nod=node(name=nodeName, id=self.nodeIndex, nodeType=node.ELEMENT_NODE, nodeValue='', parentNode=parentNode)
            class_instance=getattr(self.mod, class_name)(xmlNode=nod, xmlSucker=self)
            
            if self.foundFirstNode==None and self.firstTime:
                self.firstTime=False
                if hasattr(self.mod, 'FIRSTNODE'):self.foundFirstNode=getattr(self.mod, 'FIRSTNODE')
                else:
                    self.foundFirstNode=class_instance
                    self.mod.checkFirstNode(class_instance)
                            
            if thetag[-1:]!='/':
                self.parentNode.append(nod)

        return '<' + thetag + '>'

    def getAttributes(self, p_elt):
        selfMethod='getAttributes'
        if  __debug__ and p_elt.id not in self.nodeAttributes:
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, self.errorPrefix + 'Unknown elt')
        return self.nodeAttributes[p_elt.id]

    @staticmethod
    def treatCDATA(src, errorPrefix='', doB64=True): #A007
        selfMethod='treatCDATA'
        import base64
        pos=0

        while True:
            ct_start=src.find(CDATA_BEGIN, pos)
            if ct_start<0:break

            ct_end=src.find(CDATA_END, ct_start)
            if ct_end<0:raise epicxception.epicxmlXmlSyntaxException('XmlSuckerScraper', selfMethod, errorPrefix + ' Found: ' + CDATA_BEGIN + ' with no end !')
            content=src[ct_start+9:ct_end]
            if doB64:content=B64FLAG + base64.urlsafe_b64encode(bytes(content, 'utf-8')).decode("utf-8")
            src=src[:ct_start] + content + src[ct_end+3:]

            pos= ct_start + len(content)

        return src

    @staticmethod
    def treatBackSlash(src, errorPrefix=''):
        """
        Treat lines ending with BackSlash.
        Change : 
        <tag 
            at1=1 
            at1=2
        >
        <tag2 
            at1=3
        >
        <tag3 at1=1 at2=2>
        to
        <tag at1=1 at1=2>
        <tag2 at1=3>
        <tag3 at1=1 at2=2>    
        """
        import io
        lines=src.strip().split('\n')

        #-- Comment recording : record first line <? as a comment.
        spec_line=None
        if lines[0].startswith('<?'):
            spec_line=lines[0]
            del lines[0]

        lines, comment_recorders=destroyComments(lines, errorPrefix=errorPrefix)
##        lines, comment_recorders=lines, {}
        
        wrk_lines=list(lines)
        
        i=0
        adjust=0
        while i<len(wrk_lines):
            line=wrk_lines[i].strip()
            if not line.startswith('<') or line.endswith('>'):
                i+=1
                continue
            
            inf_idx=i
            i+=1
            sb=io.StringIO()
            previous_line=line
            if line.endswith('\\'):sb.write(line[:-1])
            else:sb.write(line)
            while i<len(wrk_lines):            
                line=wrk_lines[i].strip()
                if not previous_line.endswith('\\'):
                    if line.endswith('\\'):sb.write(' ' + line[:-1])
                    else:sb.write(' ' + line)
                else:
                    if line.endswith('\\'):sb.write(line[:-1])
                    else:sb.write(line)
                previous_line=line
                if line.endswith('>'):
                    break
                i+=1

            _line=sb.getvalue()
            sup_idx=i

            del lines[inf_idx-adjust:sup_idx-adjust]
            lines[inf_idx-adjust] = _line
            adjust=adjust + sup_idx - inf_idx

            i+=1

        #-- Comment recording : record first line <? as a comment.
        if spec_line!=None:
            if 'I1' not in comment_recorders:comment_recorders['I1']=[spec_line]
            else:comment_recorders['I1']=[spec_line] + comment_recorders['I1']
        
        return '\n'.join(lines), comment_recorders


def destroyComments(lines, errorPrefix=''):
    selfMethod='destroyComments'
    i=0
    new_lines=[]
    max=len(lines)
    new_inline_comment=''
    
    #-- Comment recording.
    comment_recorders={}
    
    while i < max:
        
        if new_inline_comment!='':line=new_inline_comment
        else:line=real_line=lines[i]        
        new_inline_comment=''
        
        # Track begining -->
        start_pos=line.find('<!--')
        if start_pos>=0:

            real_line=''
            memo_line=line
            if start_pos!=0:
                real_line=line[:start_pos]
                
                #-- Comment recording.
                comment_line=line[start_pos:]
            else:
                #-- Comment recording.
                comment_line=line
                
            #-- Comment recording: guess the future attached Node Tag Unique Name.
            tun='I' + str(len(RE_SUP.findall(''.join(new_lines) + real_line)) + 1)
            if tun in comment_recorders:more=comment_recorders[tun]
            else:more=[]
            comment_recorders[tun]=[]

            # Track end -->
            exit=False
            while i < max and not exit:
                end_pos=line.find('-->')
                if end_pos>=0:
                    exit=True

                    #-- There are more stuff beyong the end comenmt mark.
                    if end_pos!=len(line)-4:
                        s=line[end_pos+3:]
                        
                        #-- There are more commments on this line
                        nlc_pos=s.find('<!--')
                        if nlc_pos>=0:new_inline_comment=s[nlc_pos:]
                        else:nlc_pos=len(s)
                        
                        real_line=real_line + s[:nlc_pos]
                        
                        #-- Comment recording.
                        comment_recorders[tun].append(comment_line[:(end_pos+3 - start_pos)])
                        if len(more)!=0:comment_recorders[tun]=more + comment_recorders[tun]
                    else:
                        #-- Comment recording.
                        comment_recorders[tun].append(comment_line)
                        if len(more)!=0:comment_recorders[tun]=more + comment_recorders[tun]
                    continue

                else:
                    #-- Comment recording.
                    comment_recorders[tun].append(comment_line)
                i+=1
                
                if i<max:line=comment_line=lines[i]
                start_pos=0
                
            
            if not exit:raise epicxception.epicxmlXmlSyntaxException('Main', selfMethod, errorPrefix + 'Unable to find Comment end, for Comment starting with line:' + memo_line + ' !')
        
        real_line=real_line.strip()
        new_lines.append(real_line)
        
        if new_inline_comment=='':i+=1

    return new_lines, comment_recorders 



class DictKeys(dict):
    def __init__(self):
        dict.__init__(self)
        self.__orderedAttrs=[]
        
    def getOrderedAttrs(self):
        return self.__orderedAttrs   
         
    def setOrderedAttrs(self, oa):
        self.__orderedAttrs=oa



class node:
    ELEMENT_NODE='tag'
    TEXT_NODE='text'
    
    def __init__(self, name='', id=0, nodeType='', nodeValue='', parentNode=None):
        selfMethod='__init__'
        if  __debug__ and name=='':
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Undef name')
        if  __debug__ and id==0:
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Undef id')                
        if  __debug__ and nodeType not in (node.ELEMENT_NODE, node.TEXT_NODE):
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Undef nodeType')       
        self.nodeName=name        
        self.id=id
        self.nodeType=nodeType
        self.nodeValue=nodeValue
        self.__weakParentNode=None
        self.setParentNode(parentNode)

    def getParentNode(self):
        if self.__weakParentNode!=None and self.__weakParentNode()!=None:
            return self.__weakParentNode()
        else:return None
    
    def setParentNode(self, parentNode):
        if parentNode==None:
            self.__weakParentNode=None
            return
        self.__weakParentNode=weakref.ref(parentNode)




if __name__ == '__main__':    
    pass