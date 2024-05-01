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


# 20220829: 001: Python 2 to 3 Conversion
# 20230530: 002: Bug Correction


from . import wk
from .epicbase import TAG_SEP
from . import epicxception

ROLES_AUTZ_DFT={'*anyone': '+all'}
TEXTDESCS_ROLES_AUTZ_DFT={'*anyone': '-allow;-display'}
BAL_SYNTAX='<category>/<software>.<softclass_name>'


class Visitor:

    def __init__(self, childFirst = True, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        self.childFirst = childFirst
        # Imbricated classes Treat the caller ?
        self.treatAncestor=treatAncestor
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
    


class WorkTestParent(Visitor):
    
    def __init__(self, childFirst = False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                             
        self.space=""
    
    def visitNodeBase(self, element):        
        if not element.isFirstNode():
            print(self.space + "Element:" + str(element)  + "::Parent:" + str(element.getAggregatParent()))    
            print(self.space + "_Name:" + str(element.name))            
            print(self.space + "_Attributes:" + str(element.getdAttrs()))
            print(self.space + "_Texts:" + str(element.getText()))
            print(self.space + "_PeerTagdesc:" + str(element.peerTagdesc) + "_Name:" + str(element.peerTagdesc.getName()))                    
            print(self.space + "_PeerTagdesc_.tagDesc:" + str(element.peerTagdesc.tagDesc))                    
            print(self.space + "_PeerTagdesc_.attrDescs:" + str(element.peerTagdesc.attrDescs))                    
            print(self.space + "_PeerTagdesc_.attrRests:" + str(element.peerTagdesc.attrRests))                    
                   
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        self.space=self.space + "      "
        print('element.listNodeBases', element.listNodeBases)
        for c in element.listNodeBases:                                       
            c.accept(self)
        self.space=self.space[0:len(self.space) - 6]            
    
    def visitNode(self, element):       
        pass
    
    def visitFirstNode(self, element):       
        pass 


class WorkCheckLang(Visitor): # internal use only
    
    def __init__(self, childFirst = False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True, dontRaise=False, doFeed=False):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                             
        self.__dontRaise=dontRaise
        self.__doFeed=doFeed
    
    def visitNodeBase(self, element):        
        from kwadlib import ct, tools
        from kwadlib.multilangue import MultiLang
        from os import  path
        
        kwad_home=tools.getInstallDir()
        
        if not element.isFirstNode():
            print("Tag>>" + str(element.name))            
            attrs=element.getdAttrs()
            
            for attr in attrs:
                value=attrs[attr]
                if value==None:continue
                if not value.startswith('{'):continue
                print(' '*3, 'Attribute:', attr)
                if value.find('"')>=0 or value.find("'")>=0:values=ct._eval(value)
                else:values=ct.dress(value)
                if '*help' not in value and '*lhelp' not in values:continue
                
                for hlp in ('*help', '*lhelp'):
                    if hlp not in values:continue
                    # e.g.: {*eq:1,*help:%lang/softclass.was.en/scope.help,*lhelp:%lang/softclass.was.en/scope.lhelp}
                    hlp=values[hlp]
                    if not hlp.startswith('%'):continue
                    
                    spl=hlp.split('/')
                    lang_file=spl[1]
                    lang_key=spl[2]
                    
                    lang_file=path.normpath(kwad_home + '/langs/' + lang_file)
                    if not path.isfile(lang_file):
                        if not self.__dontRaise:raise Exception('Lang File:' +  lang_file + ' not found !')
                        print('Lang File:', lang_file + ' Not found !')
                        return
                    
                    fd=open(lang_file)
                    s=fd.read()
                    fd.close()
                    
                    multilang=MultiLang().init(verbose=0)
                    multilang.convertWk(values)
                    
                    fdx=s.find('\n' + lang_key)
                    if fdx>0:
                        if s[fdx-1]=='\\':raise Exception('! Lang File:', lang_file + ' , Lang Key:' + lang_key + ' found previous non finishing key !')
                        continue
                    
                    if not self.__doFeed:
                        if not self.__dontRaise:raise Exception('! Lang File:', lang_file + ' , Lang Key:' + lang_key + ' Not found !')
                        print('! Lang File:', lang_file + ' , Lang Key:' + lang_key + ' not found !')
                    else:
                        print('-> Feeding Lang Key:' + lang_key + ' into  Lang File:', lang_file + '.')
                        prefix=lang_key
                        entry='\n\n' + lang_key + '=Todo\n'
                        fdx=-1
                        while prefix.find('.')>0:
                            prefix='.'.join(prefix.split('.')[:-1])
                            
                            fdx=s.rfind('\n' + prefix)
                            if fdx>=0:break                                          
                            
                        if fdx<0:
                            title='SoftClass: ' + lang_key.split('.')[0] + ' help'
                            s= s + '\n\n# ' + '-'*(len(title)) + ' #\n# ' + title + ' #\n# ' + '-'*(len(title)) + ' #\n' + entry
                        else:
                            fdx=s.find('\n', fdx+1)
                            while s[fdx-1]=='\\':
                                fdx=s.find('\n', fdx+1)
                            if fdx<0:fdx=len(s)
                            
                            s=s[:fdx] + entry + s[fdx:]
                        
                        
                        while s.find('\n\n\n\n')>0: # Avoid increasing \n
                            s=s.replace('\n\n\n\n', '\n') 
                        
                        fd=open(lang_file, 'wb')
                        s=fd.write(bytes(s, 'utf-8'))
                        fd.close()


    def visitImbricatedNodeBase(self, element):
        for c in element.listNodeBases:                                       
            c.accept(self)
    
    def visitNode(self, element):       
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
        import weakref
        # M001: if not str(type(element.aggregatParent))=="<type 'weakref'>":return
        if not str(type(element.aggregatParent))=="<class 'weakref'>":return
        element.aggregatParent=element.aggregatParent()
        
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)



class WorkCheck(Visitor):
    
    def __init__(self, updatableOnly=False, childFirst=False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                             
        self.softclass_nodes=[]
        self.__updatableOnly=updatableOnly
    
    def visitNodeBase(self, element):
        
        ## Desc//Apply Default RolesAutz to All
        # Top default
        if not element.isFirstNode():
            
            for type in ('desc' , 'rest'):            
                top_wks=getattr(element.getTop(), 'getTag' + type.capitalize() + 'Wk')()
                top_texts_wks=getattr(element.getTop(), 'getText' + type.capitalize() + 'Wk')()
                if top_wks==None:break
                
                # AutzDft
                if '*rolesAutzDft' in top_wks:rolesAutzDft=top_wks['*rolesAutzDft']
                else:rolesAutzDft=ROLES_AUTZ_DFT
                if '*anyone' in rolesAutzDft and '+all' in rolesAutzDft['*anyone'].split(';'):optimistic='+*optimistic'
                else:optimistic='-*optimistic'                
                if '*anyone' not in rolesAutzDft:rolesAutzDft['*anyone']=optimistic
                elif rolesAutzDft['*anyone'].find('*optimistic')<0:rolesAutzDft['*anyone']+=';' + optimistic                
                # Text AutzDft
                if top_texts_wks != None and '*rolesAutzDft' in top_texts_wks:texts_rolesAutzDft=top_texts_wks['*rolesAutzDft']
                else:texts_rolesAutzDft=TEXTDESCS_ROLES_AUTZ_DFT
                if '*anyone' in texts_rolesAutzDft and '+all' in texts_rolesAutzDft['*anyone'].split(';'):optimistic='+*optimistic'
                else:optimistic='-*optimistic'                
                if '*anyone' not in texts_rolesAutzDft:texts_rolesAutzDft['*anyone']=optimistic
                elif texts_rolesAutzDft['*anyone'].find('*optimistic')<0:texts_rolesAutzDft['*anyone']+=';' + optimistic

                # - attr
                attr_descs=getattr(element, 'get' + type.capitalize() +  's')()
                for attr in attr_descs:attr_descs[attr]['*rolesAutzDft']=rolesAutzDft
                # if '*rolesAutz' not in wks:wks['*rolesAutz']={'*anyone': '-allow;-display'}
                # - tag
                wks=getattr(element, 'getTag' + type.capitalize() + 'Wk')()
                wks['*rolesAutzDft']=rolesAutzDft
                # - text
                wks=getattr(element, 'getText' + type.capitalize() + 'Wk')()
                wks['*rolesAutzDft']=texts_rolesAutzDft
        
        
        ## CheckWholeNode
        if self.__updatableOnly and not element.peerTagdesc.isTagUpdatable():return
        element.checkWholeNode()

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""

        # - check tagdesc
        l=element.peerTagdesc.getQuickTagKeys()
        for tag in l:
            if tag in element.getQuickTagKeys():ll=element.getQuickTagNodes(tag)
            else:ll=[]
            element.peerTagdesc.checkTag(tag, len(ll))
        
        # - childs
        for c in element.listNodeBases:
            if c.isThisTagPartial():continue
            if c.hasAttr('type') and c.getAttr('type')=='softclass':
                if id(c) not in self.softclass_nodes:self.softclass_nodes.append(id(c))
                else:continue

            c.accept(self)
    
    def visitNode(self, element):       
        pass 
        
    def visitFirstNode(self, element):       
        pass 

   
class vwBasicWorkTreeView(Visitor):
    
    def __init__(self, view=None, apb_session=None, top=None, xtop=None, xmain=None, xseattr=None, xsescope=None, xsesign=None, xhelp=None, xtree=None, xgrid=None, xcubelang=None, xrepoz=None, message=None, childFirst = False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        selfMethod = '__init__'
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                                     
        if top==None:raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'top', 'Node', str(top))                        
        if view==None:raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'view', 'view', str(view))                        
        import weakref
        self.top=weakref.ref(top)
        self.xtop=xtop
        self.xmain=xmain
        self.xseattr=xseattr
        self.xsescope=xsescope
        self.xsesign=xsesign
        self.xhelp=xhelp
        self.xtree=xtree
        self.xgrid=xgrid
        self.xcubelang=xcubelang
        self.xrepoz=xrepoz
        self.view=view
        self.apb_session=apb_session
        self.message=message

    def visitNodeBase(self, element):        
        selfMethod='visitNodeBase'
        
        # Check descriptor/restrictor new wk attributes.
        isTagDisplayable   = element.peerTagdesc.isTagDisplayable()
        isTagDenied, cls = element.peerTagdesc.isTagDenied(doExcptCls=True)
        
        # -- Bounce Denied
        if isTagDenied:
            if element==self.top():raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'The tag Named:' + element.getFiliation() + ' : is denied ! Advice check your Descriptor/Restrictor files.')
            return
        # -- Bounce Displayed
        if not isTagDisplayable:
            if element==self.top():raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'The tag Named:' + element.getFiliation() + ' : is not displayable ! Advice check your Descriptor/Restrictor files.')
            return

        if element==self.top():element.vwBasicGetTopTreeView(self.view, apb_session=self.apb_session, message=self.message, xtop=self.xtop, xmain=self.xmain, xseattr=self.xseattr, xsescope=self.xsescope, xsesign=self.xsesign, xhelp=self.xhelp, xtree=self.xtree, xgrid=self.xgrid, xcubelang=self.xcubelang, xrepoz=self.xrepoz)
        else:element.vwBasicGetTreeView(self.view, message=self.message, xtop=self.xtop, xmain=self.xmain, xseattr=self.xseattr, xsescope=self.xsescope, xsesign=self.xsesign, xhelp=self.xhelp, xtree=self.xtree, xgrid=self.xgrid, xcubelang=self.xcubelang, xrepoz=self.xrepoz)
        
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)
    
    def visitNode(self, element):       
        pass 
    
    def visitFirstNode(self, element):       
        pass 

   
   
class vwMobileWorkTreeView(Visitor):
    
    def __init__(self, view=None, apb_session=None, top=None, xtop=None, xmain=None, xseattr=None, xsescope=None, xsesign=None, xhelp=None, xtree=None, xgrid=None, xcubelang=None, xrepoz=None, message=None, childFirst = False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        selfMethod = '__init__'
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                                     
        if top==None:raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'top', 'Node', str(top))                        
        if view==None:raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'view', 'view', str(view))                        
        import weakref
        self.top=weakref.ref(top)
        self.xtop=xtop
        self.xmain=xmain
        self.xseattr=xseattr
        self.xsescope=xsescope
        self.xsesign=xsesign
        self.xhelp=xhelp
        self.xtree=xtree
        self.xgrid=xgrid
        self.xcubelang=xcubelang
        self.xrepoz=xrepoz
        self.view=view
        self.apb_session=apb_session
        self.message=message

    def visitNodeBase(self, element):        
        selfMethod='visitNodeBase'
        
        # Check descriptor/restrictor new wk attributes.
        isTagDisplayable   = element.peerTagdesc.isTagDisplayable()
        isTagDenied, cls = element.peerTagdesc.isTagDenied(doExcptCls=True)
        
        # -- Bounce Denied
        if isTagDenied:
            if element==self.top():raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'The tag Named:' + element.getFiliation() + ' : is denied ! Advice check your Descriptor/Restrictor files.')
            return
        # -- Bounce Displayed
        if not isTagDisplayable:
            if element==self.top():raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'The tag Named:' + element.getFiliation() + ' : is not displayable ! Advice check your Descriptor/Restrictor files.')
            return

        if element==self.top():element.vwMobileGetTopTreeView(self.view, apb_session=self.apb_session, message=self.message, xtop=self.xtop, xmain=self.xmain, xseattr=self.xseattr, xsescope=self.xsescope, xsesign=self.xsesign, xhelp=self.xhelp, xtree=self.xtree, xgrid=self.xgrid, xcubelang=self.xcubelang, xrepoz=self.xrepoz)
        else:element.vwMobileGetTreeView(self.view, message=self.message, xtop=self.xtop, xmain=self.xmain, xseattr=self.xseattr, xsescope=self.xsescope, xsesign=self.xsesign, xhelp=self.xhelp, xtree=self.xtree, xgrid=self.xgrid, xcubelang=self.xcubelang, xrepoz=self.xrepoz)
        
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)
    
    def visitNode(self, element):       
        pass 
    
    def visitFirstNode(self, element):       
        pass 



class vwWorkClearView(Visitor):

    def __init__(self, childFirst = False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)  
    
    def visitNodeBase(self, element):        
        element.vNode=None
        element.vTree=None
        
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



class WorkFilter(Visitor):
    """ See the docstring of class Filter to understand how it works. """
    MAX_FOUND=9999

    def __init__(self, filter=None, count=MAX_FOUND, extraAttrs=[], childFirst = False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        selfMethod = '__init__'
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                                     
        if filter==None or not hasattr(filter, 'isinstance') and not filter.isinstance('Filter'):raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'filter', 'Filter', str(filter))                        
        self.filter=filter
        self.count=count
        self.extraAttrs=extraAttrs
        self.nodes=[]
    
    def visitNodeBase(self, element):        
        pass
        
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)
    
    def visitNode(self, element): 
        if element.isFirstNode():return 
        if len(self.nodes)>=self.count:return 
        node = element 

        
        ## Extra Attrs presence prereqsuiste check
        for attr in self.extraAttrs:
            if not node.hasAttr(attr):return  


        ## ftags test      ##
        while True:
            ftags_passe=False

            if self.filter.ftag.hierarTags==[] and self.filter.ftag.tun==None and self.filter.ftag.basics==[]:
                ftags_passe=True
                break
            

            ## tun test
            if node.getTun()==self.filter.ftag.tun:
                ftags_passe=True
                break


            ## basic test
            if node.getName() in self.filter.ftag.basics:
                ftags_passe=True
                break
            

            ## hierarchical from top test
            if node.getFiliation() in self.filter.ftag.hierarTags:
                ftags_passe=True
                break
            

            ## hierarchical test
            for fil in self.filter.ftag.hierarTags:
                if fil.startswith(TAG_SEP):continue
                if node.getFiliation().endswith(TAG_SEP + fil):
                    ftags_passe=True
                    break
            break
            
        if not ftags_passe:return 

        fattrs_passe=True
        
        skeleton=self.filter.fattr.skeleton

        
        ## basic test
        for attrdefs in self.filter.fattr.basics:
            attr     = attrdefs[0]
            attrdesc = attrdefs[1]
            skelidx  = attrdefs[2]
            
            fattrs_passe=self.__checkAttr(node, attr, attrdesc)
            skeleton=skeleton.replace(str(skelidx), str(fattrs_passe))

        
        ## all hierarchical tests
        for attrdefs in self.filter.fattr.hierarAttrs:
            
            filattr  = attrdefs[0]
            attrdesc = attrdefs[1]
            skelidx  = attrdefs[2]
            
            spl=filattr.split(TAG_SEP)
            attr=spl.pop()
            fil=TAG_SEP.join(spl)
                
            ok, m_node = node.fgetMatch(fil)

            if not ok:fattrs_passe=False
            else:fattrs_passe=self.__checkAttr(m_node, attr, attrdesc)
            skeleton=skeleton.replace(str(skelidx), str(fattrs_passe))

        from .ct import _eval
        fattrs_passe=_eval(skeleton)
        try:
            fattrs_passe=_eval(skeleton)
        except:
            pass
        if not fattrs_passe:return
        
        self.nodes.append(node)


    ## fattrs test      ##
    def __checkAttr(self, node, attr, attrdesc): 
        selfMethod='__checkAttr'
        try:
            value=node.getAttr(attr)
        except:
            return False

        passe=False
        try:
            p=wk.WantedKeywords()
            setattr(p, attr, attrdesc)
            wk.getKeywords(wantedKeywords=p, keywords={attr:value,}, class_exit=self.__class__.__name__, method_exit=selfMethod)                    
            passe=True
        except:
            pass
        
        return passe

    def visitFirstNode(self, element):       
        pass  
 



class WorKill(Visitor):
    
    def __init__(self, childFirst = False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                             
    
    def visitNodeBase(self, element):        
        if not element.isFirstNode():
            pass

    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)       
    
    def visitNode(self, element): 
        element.getTopParent()._delQuickTun(element.getTun())      
        element.isDead=True
    
    def visitFirstNode(self, element):       
        pass
        

        
class WorkClone(Visitor):

    def __init__(self, doAddToQuickTun=False, doCloneLink=False, firstNode=None, clasIsSoftClassNode=False, childFirst = False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)
        self.__firstNode=firstNode
        self.__clasIsSoftClassNode = False
        self.__doCloneLink=doCloneLink
        self.__doAddToQuickTun = doAddToQuickTun

    def visitNodeBase(self, element):        
        # M002: element.clone(firstNode=self.__firstNode, doCloneLink=self.__doCloneLink)
        element.clone(firstNode=self.__firstNode, doAddToQuickTun=self.__doAddToQuickTun, clasIsSoftClassNode = self.__clasIsSoftClassNode)
        self.__firstNode=None
        
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

    
    
class WorkClearClone(Visitor):

    def __init__(self, childFirst = False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)  
    
    def visitNodeBase(self, element):        
        if not hasattr(element, 'workClone'):return
        delattr(element, 'workClone')

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
    


class WorkupdQuickTun(Visitor):

    def __init__(self, childFirst = False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                                    
    
    def visitNodeBase(self, element):        
        element.updQuickTun()
        
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

    def __init__(self, childFirst = False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)
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


class WorkNodeByFiliation(Visitor):

    def __init__(self, oneLevel=False, og_node=None, childFirst=False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)                                    
        self.oneLevel=oneLevel
        self.og_node=og_node
        self.orderedFiliation_lists=[]
        self.orderedFiliation_dicts={}
    
    def visitNodeBase(self, element):        
        fil=element.getFiliation()
        if fil not in self.orderedFiliation_lists:
            self.orderedFiliation_lists.append(fil)
            self.orderedFiliation_dicts[fil]=[]

        self.orderedFiliation_dicts[fil].append(element)
        
    def visitLnk(self, element): 
        pass
        
    def visitImbricatedNodeBase(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:  
            if self.oneLevel and (element!=self.og_node):return
            if not element.peerTagdesc.isTagDisplayable():continue                                    
            c.accept(self)
        
    
    def visitNode(self, element):       
        pass      
        
    def visitFirstNode(self, element):           
        pass     
 

   
class WorkSoftClassNodes(Visitor):

    def __init__(self, firstNode=None, childFirst = False, treatAncestor=False, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)     
        self.softclass_node_by_injectors={}

    def visitNodeBase(self, element):
        selfMethod='visitNodeBase'
        if not self.isSoftClass(element):return
        from kwadlib import tools

        if not element.getAttr('bsl').find('/')>0:
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'Incorect bsl:'  +  element.getAttr('bsl') + ', for softclass:' + element.getTag() + ' ! Bsl must contain the category, the corect syntax is: ' + BAL_SYNTAX + '.')
        balCategory, more=element.getAttr('bsl').split('/')
        balSoftware=more.split('.')[0]
        balInjector=tools.getInjectorAttrs(balSoftware, category=balCategory)
        
        if balInjector not in list(self.softclass_node_by_injectors.keys()):self.softclass_node_by_injectors[balInjector]=list()
        self.softclass_node_by_injectors[balInjector].append(element)
        
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
        
    def isSoftClass(element):
        if element.hasAttr('type') and element.getAttr('type')!=None and element.getAttr('type')=='softclass':return True
        return False
    
    isSoftClass=staticmethod(isSoftClass)



class WorkQuickTun(Visitor):
    def __init__(self, childFirst = False, treatAncestor=True, recursiveImbricatedNodeBase=True, recursiveNode=True):
        Visitor.__init__(self, childFirst, treatAncestor, recursiveImbricatedNodeBase, recursiveNode)
        self.__top = None

    def visitImbricatedNodeBase(self, element):
        """ Recursivity on imbricated Classes. """
        for c in element.listNodeBases:
            c.accept(self)

    def visitNodeBase(self, element):
        self_funct='visitNode'

        if self.__top == None:
            self.__top = element.getTopParent()

        # Node:
        # -----
        # Top QuickTun:
        if not self.__top._hasQuickTun(element.getTun()):self.__top._setQuickTun(element.getTun(), element)
