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


"""
"""

# 2012/04/25  | 002 | Bug correction on __link__ support on desc : run clone only once when generating
# descriptor Links on the flow.
# 2012/05/15  | 003 | Bug print tag details on exceptions.
# 2012/05/26  | 004 | Postpone Descriptor Check from initFrom_xmlNode to visitor to allow support of Special Tags like SoftClassNodes does.
# 2012/09/20  | 005 | Support of left, rigth and bottom icons.
# 2012/12/12  | 006 | Support of * on f_tags and support of __all__ for * in select.
# 2013/01/10  | 007 | Change Link support model.
# 2014/12/08  | 008 | Adding printJSON
# 2015/03/15  | 009 | create *texts bug correction into __setRdNode
# 2015/03/15  | 010 | None support
# 2015/05/25  | 011 | Epicxmlp Cache support
# 2015/05/25  | 011 | Todo: mako function:
#                       Dont associate temp_dir to cache_dir. Use explicite digest parameter for mako cache_dir in mako_kws !!!
#                       Get rid of template_lookup if not explicite parameter.
# 2022/08/30  | 012 | Mako parsing moved into tools.convertSource
# 2022/09/18  | 013 | Modify TreatCDATA to Support b64
# 2022/09/18  | 014 | Bug correction
# 2022/09/20  | 015 | Force support of capSensitivez on MakeDefaultNode/newTagdesc
# 2022/09/20  | 016 | Bug correction
# 2022/10/02  | 017 | Bug correction
# 2022/12/03  | G001 | (G for Global) Support for outputs. Now SoftClasses of sub_type: configuration, control and datasrouce support the return of:
#                      structured values as output.
#                      The tag <output> must be defined into the SoftClass's descriptor file.
# 2023/03/10  | 018 | Bug correction
# 2023/03/13  | 019 | (See epicbase 008) Add noParentWeakRef. Previously and currently if not set at the top level: if the top node reference is lost by the program, the underlaying childs loose their aggregatParent becoming None.
# 2023/03/20  | 020 | Bug Correction 
# 2023/03/30  | 021 | Bug Correction
# 2023/06/09  | 022 | Adding force to clone/add
# 2023/06/14  | 023 | Adding addAttr
# 2023/06/19 | 024 (see softclass_node/009 ) | Replacing pixmlp by epicxmlp. _getPArent replaced by getAggreagatParent everywhere. ._isFirstNode() Replaced by .isFirstNode() EveryWhere.
# 2023/06/19 | 030 | Replacing pixmlp by epicxmlp. _getPArent replaced by getAggreagatParent everywhere. ._isFirstNode() Replaced by .isFirstNode() EveryWhere.
# 2023/06/27 | 031 | Bug Correction
# 2023/06/27 | 031 | OpenApi Evolution
# 2023/07/18 | 032 | Support of CDATA
# 2023/07/18 | 033 | A true tun that supports cloning.
# 2023/07/20 | 034 | Replace epicxmlSystException by epicxmlAttrNotFound
# 2023/07/21 | 035 | EveryWhere replacement of Node.texts as list by Node.text.
# 2023/07/21 | 036 | Adding withCoolTyping + withJson support in printXml
# 2023/08/28 | 037 | Allow setAttrs on epicfiles with no decriptor: self.peerTagdesc == None.
# 2023/09/20 | 038 | Bug correction
# 2023/09/21 | 039 | Bug correction : attrs was not treated on continue
# 2023/09/21 | 039.1 | Bug correction : support of type list or dict
# 2023/10/02 | 040 | Bug correction : add remove childs on remove
# 2023/10/02 | 041 | Bug correction
# 2023/10/04 | 042 | Support for KamleCase k8s names
#                    Notice: k8s explicitly remove the yaml top tag and replace it by kind.
# 2024/04/23 | 043 | Bug correction
# printJSON (for yaml/hcl): Add Management of tag_desc with multichild
#                           Adding Recursive __Link__ management (future tag_desc cannot be anticipated)
#                           Tested with kastmenu/menu.desc.xml

from . import epicbase
from . import epicvisitor
from . import epicwvisitor
from . import epicxception
from . import wk
from . import ct
from io import StringIO
from .xmlsuckerscraper import Node as sNode
import re
RE_BRACES = re.compile(r'[\(\)]')
import random
random.seed()

# Bug ? TAG_RE=r'[\(\)]' : Do not work like pv=re.split(r'[\(\)]', s) !

TEST_LINK = False
ESC_SLASH = 'eacute_slash'

XMLSUCKER_NODE_EQUIV = {
    '*': 'WideNode',
    '#text': 'Xml_Text',
}

ACCESS_MODES = { \
    'xget': 'r', 'xupdate': 'w', 'xcreate': 'w', 'xdelete': 'w', 'xsave': 'w', \
    'select': 'r', 'cselect': 'r', 'ccselect': 'r', 'rselect': 'r', 'crselect': 'r', 'xselect': 'r', \
    'create': 'w', 'ccreate': 'w', 'rcreate': 'w', \
    'update': 'w', 'delete': 'w', 'duplicate': 'w', \
    }
CPICKLE_OPTIMIZED_PROTOCOL = 2
FS_EQUIV_CARS = (
('\\', '_2_'), (':', '_3_'), ('|', '_4_'), ('"', '_5_'), ("'", '_6_'), (';', '_7_'), ('<', '_8_'), ('>', '_9_'),
('?', '_10_'), ('!', '_11_'), ('$', '_12_'), ('*', '_13_'), ('+', '_14_'), ('-', '_15_'), ('.', '_16_'))

TD_SYNTAX = 'TAG[/TAG]@ATTR\n' + \
            'TAG[/TAG]@ATTR[,ATTR]\n' + \
            'TAG[/TAG]@*'

PRINT_HCL_COMPACT = "compact" # if many parents have no attribute they are writen in one line with no {
PRINT_HCL_TERRAFORM = "notcompact" # as expected by TerraForm
PRINT_HCL_NOTCOMPACT = "notcompact"


def getAccesMode(operation):
    selfMethod = 'getAccesMode'
    if operation not in ACCESS_MODES: raise epicxception.epicxmlSystemException('Main', selfMethod,
                                                                                'Unsupported operation:' + str(
                                                                                    operation) + '. Supported operations are:' + str(
                                                                                    list(ACCESS_MODES.keys())) + '.')
    return ACCESS_MODES[operation]


def makeQstring(xtop=None, xseattr=None, xsescope=None, xsesign=None, xhelp=None, xtree=None, xgrid=None,
                xcubelang=None, logical_files=None):
    from .tools import CoolTyping
    kws = {}
    file_source, file_desc, file_rest, file_target = logical_files

    if xtop != None:
        kws['xtop'] = '&xtop=' + xtop.strip()
    else:
        kws['xtop'] = ''
    if xseattr != None:
        kws['xseattr'] = '&xseattr=' + xseattr.strip()
    else:
        kws['xseattr'] = ''
    if xsescope != None:
        kws['xsescope'] = '&xsescope=' + xsescope.strip()
    else:
        kws['xsescope'] = ''
    if xsesign != None:
        kws['xsesign'] = '&xsesign=' + xsesign.strip()
    else:
        kws['xsesign'] = ''
    if xhelp != None:
        kws['xhelp'] = '&xhelp=' + str(xhelp)
    else:
        kws['xhelp'] = ''
    if xtree != None:
        kws['xtree'] = '&xtree=' + CoolTyping.unDress(xtree).replace('#',
                                                                     'None')  # WebBrowser/WebServer considers # as comment into self.path !
    else:
        kws['xtree'] = ''
    if xgrid != None:
        kws['xgrid'] = '&xgrid=' + CoolTyping.unDress(xgrid)
    else:
        kws['xgrid'] = ''
    if xcubelang != None:
        kws['xcubelang'] = '&xcubelang=' + xcubelang
    else:
        kws['xcubelang'] = ''
    if file_source != None:
        kws['file_source'] = '&file_source=' + file_source.strip()
    else:
        kws['file_source'] = ''
    if file_desc != None:
        kws['file_desc'] = '&file_desc=' + file_desc.strip()
    else:
        kws['file_desc'] = ''
    if file_rest != None:
        kws['file_rest'] = '&file_rest=' + file_rest.strip()
    else:
        kws['file_rest'] = ''
    if file_target != None:
        kws['file_target'] = '&file_target=' + file_target.strip()
    else:
        kws['file_target'] = ''

    qstring = ''
    for key in ('xtop', 'xseattr', 'xsescope', 'xsesign', 'xcubelang', 'file_source', 'file_desc', 'file_rest'):
        if xseattr != None and key in epicbase.VW_STORED_PARAMETERS: continue
        qstring += kws[key]

    # qstring=xtop + xseattr + xsescope + xsesign + xhelp + xtree + xgrid + xrepoz + file_source + file_desc + file_rest

    return qstring

    # =====================#
    #                     #
    #  Node localisation  #
    #    Utility class    #
    #                     #
    # =====================#


class PxQuery:

    def checkAttrKeys(self, **keywords):
        self_funct = 'checkAttrKeys'

        for key in list(keywords.keys()):
            if not self.isCapSensitive(): key = key.upper()
            if key not in list(self._getdAttrs().keys()): raise epicxception.epicxmlSystemException(
                self.__class__.__name__, self_funct, 'Not supported attribute:' + key + ' !')
            if str(keywords[key]) != str(self._getdAttrs()[key]): return False
        return True

    # ---------------------------------- #
    # Node localisation/PxQuery methods #
    # --------------------------------- #

    def get(self, tag=None, **keywords):
        """
        If this node has any child nodes of this tag, matching this set of keyword attributes,
        returns a python list of these nodes.
        tag: a tag name.
        **attrs: is a set of pair attr=value keyword parameters.
        Ex:
            nodes=top.get(tag='tag1', attr1='attr1', attr2='attr2')

        topic: Localisation methods
        """
        selfMethod = 'get'
        founds = []
        found = False
        ca = False
        last_exception = None

        if not self.isCapSensitive(): tag = tag.capitalize()

        if tag not in self.getQuickTagKeys(): raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                        selfMethod,
                                                                                        'Not supported Tag:' + tag + ' !')

        _l = self.getQuickTagNodes(tag)
        for node in _l:
            try:
                ca = node.checkAttrKeys(**keywords)
            except Exception as e:
                last_exception = e
                continue
            if not ca: continue
            found = True
            founds.append(node)

        if not found and last_exception != None: raise last_exception

        return founds

    def getAlias(self, pattern):
        _l = self.getNodes()
        for node in _l:
            if node.getTag() == '__alias__' and node.hasAttr('name') and node.getAttr('name') == pattern:
                return node.getAttr('value')

        if self.isFirstNode(): return None
        return self.getAggregatParent().getAlias(pattern)

    def pxq_bu(self, pxq):
        """
        Bottom Up PxQuery request
        -------------------------
        pxq:bu.url@value
        servers.server.host
        To retreive an attribute (if this node is child of server):
        server.servers.type
        """
        BU_SYNTAX = 'TAG[/TAG]@ATTR\n'
        self_funct = 'pxq_bu'
        from io import StringIO
        og_pxq = pxq

        # Retreives more attrs.
        more_attrs = pxq.split(',')
        del more_attrs[0]
        if len(more_attrs) > 0: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                           'td:Bad Format: Multiple Attributes are not allowed !\nYour Bottom Up PxQuery request:' + og_pxq + 'The correct bu syntax is:\n' + TD_SYNTAX + '.')

        if pxq.find('*') >= 0:
            raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                       'td:Bad Format: All Attributes archetype is not allowed !\nYour Bottom Up PxQuery request:' + og_pxq + '. The correct bu syntax is:\n' + TD_SYNTAX + '.')

        # Check first attr.
        if pxq.startswith('@'):
            attr = pxq[1:]
            if not self.hasAttr(attr):raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                'td:Bad Format: This Attribute: ' + attr + ' do not exist at current level: ' + self.getTag() + ' ! Your Bottom Up PxQuery request:' + og_pxq + '. The correct bu syntax is:\n' + TD_SYNTAX + '.')
            return self.getAttr(attr)

        if pxq.find('@') <= 0: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                          'td:Bad Format: Target Attribute is required ! Your Bottom Up PxQuery request:' + og_pxq + '. The correct bu syntax is:\n' + TD_SYNTAX + '.')
        sb_reverse = StringIO()
        _l = list(range(len(pxq)))
        for i in _l: sb_reverse.write(pxq[len(pxq) - i - 1])
        s_reverse = sb_reverse.getvalue()
        pos = len(pxq) - s_reverse.find('@') - 1

        if pxq[pos + 1:].find('/') >= 0:
            raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                       'td:Bad Format: Target Attribute:' + pxq[
                                                                                            pos + 1:] + ' should not contain: "/" !. Your Bottom Up PxQuery request:' + og_pxq + '. The correct td syntax is:\n' + TD_SYNTAX + '.')

        pxq = pxq[:pos] + '/' + pxq[pos + 1:]

        # pxq
        spl = pxq.split('/')  # ['tag1', 'tag2', 'attr1']

        i = 0
        parent_node = self
        previous_tag = None
        for tag in spl:
            if i == len(spl) - 1: break

            tag = tag.strip()
            if tag == '':
                if previous_tag != None:
                    msg = 'Last correct Tag was: ' + previous_tag + '.'
                else:
                    msg = 'First node incorrect.'
                raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                           'bu:Bad Format: Incorrect Tag definition.\n' +
                                                           msg + '\n' +
                                                           'Your Bottom Up PxQuery request:' + og_pxq + '.\n' +
                                                           'The bu syntax is:' + BU_SYNTAX + '.')

            previous_node = parent_node
            parent_node = parent_node.getAggregatParent()

            if parent_node == None:
                raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                           'bu:Request Error: No parent found for node:' + previous_node.getTag() + ', is already the top Node.\n' +
                                                           'Your Bottom Up PxQuery request:' + og_pxq + '.\n')

            if parent_node.getTag() != tag:
                raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                           'bu:Request Error: No parent found with tag:' + tag + '.The parent of node:' + previous_node.getTag() + ', has tag:' + parent_node.getTag() + '.\n' +
                                                           'Your Your Bottom Up PxQuery request:' + og_pxq + '.\n')

            i += 1

        return parent_node.getAttr(tag)

    def td(self, pxq, checkIsNode=True, checkIsAttr=False, checkIsUnique=False, attr_separator=epicbase.ATTR_SEP,
           node_separator=epicbase.NODE_SEP, text_separator=epicbase.TEXT_SEP):
        """
        PxQuery top down method.
        pxq: syntax: TAG[/TAG][@ATTR]
        e.g.:
            tag1/tag2/tag3 or
            tag1/tag2/tag3@attr1

        If last item is a tag and checkIsNode is True returns a python list of all matching nodes.
        If last item is an attribute and checkIsAttr is True returns a separated list value(s) of this attribute for the matching nodes.
        checkIsNode: If true last item is treated as a tag name and a python list of matching nodes is returned.
        checkIsAttr: If true last item is treated as an attribute name and this attribute's value for the matching nodes is returned.
        checkIsUnique: checks if the last found nodes are uniques.
            Note:the intermediate nodes must be uniques.
        separator: allows a custom separator.

        topic: Localisation/PxQuery methods
        """
        # f814290522f79d1e9e5ae4ae83e967b4

        self_funct = 'td'
        og_pxq = pxq

        if (checkIsNode, checkIsAttr) == (True, True) or (checkIsNode, checkIsAttr) == (
        False, False): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,
                                                                    'Tag:' + self.getTag() + ', checkIsNode and checkIsAttr, if one is False the Other must be True !')

        # Retreives more attrs.
        more_attrs = pxq.split(',')
        _pxq = more_attrs[0]
        del more_attrs[0]
        if pxq.find('*') >= 0:
            if len(more_attrs) > 0: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                               'td:Bad Format: You have to choose between * (all Attributes) and specific Attribute names. !\nYour Top Down PxQuery request:' + og_pxq + 'The correct td syntax is:\n' + TD_SYNTAX + '.')
            if pxq[-2:] != '@*': raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                            'td:Bad Format: * (all Attributes) can only be use at the end of the pattern !\nYour Top Down PxQuery request:' + og_pxq + '. The correct td syntax is:\n' + TD_SYNTAX + '.')
            pxq = pxq.replace('*', '__DO_ATTR_ALL__')
        else:
            pxq = _pxq

        if checkIsAttr:

            # Check first attr.
            if pxq.find('@') <= 0: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                              'td:Bad Format: Target Attribute is required ! Your Top Down PxQuery request:' + og_pxq + '. The correct td syntax is:\n' + TD_SYNTAX + '.')
            sb_reverse = StringIO()
            _l = list(range(len(pxq)))
            for i in _l: sb_reverse.write(pxq[len(pxq) - i - 1])
            s_reverse = sb_reverse.getvalue()
            pos = len(pxq) - s_reverse.find('@') - 1

            if pxq[pos + 1:].find(epicbase.TAG_SEP) >= 0:
                raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                           'td:Bad Format: Target Attribute:' + pxq[
                                                                                                pos + 1:] + ' should not contain: "/" !. Your Top Down PxQuery request:' + og_pxq + '. The correct td syntax is:\n' + TD_SYNTAX + '.')

            pxq = pxq[:pos] + epicbase.TAG_SEP + pxq[pos + 1:]

        # pxq
        spl = pxq.split(epicbase.TAG_SEP)  # ['servers',  'server'] or
        # ['servers',  'server', 'ip']

        if not len(spl) >= 2: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                         'td:Bad Format: Incorrect Tag definition.\n' +
                                                                         'A td definition must contain at least two arguments !' + '\n' +
                                                                         'Your Top Down PxQuery request:' + og_pxq + '.\n' +
                                                                         'The td syntax is:\n' + TD_SYNTAX + '.')

        i = 0
        node = self
        nodes = [self]
        firstime = True
        last_level = False
        previous_tag = None
        for tag in spl:
            if i == len(spl) - 1: break
            if i == len(spl) - 2: last_level = True

            tag = tag.strip()
            if tag == '':
                if previous_tag != None:
                    msg = 'Last correct Tag was: ' + previous_tag + '.'
                else:
                    msg = 'First node incorrect.'
                raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                           'td:Bad Format: Incorrect Tag definition.\n' +
                                                           msg + '\n' +
                                                           'Your Top Down PxQuery request:' + og_pxq + '.\n' +
                                                           'The td syntax is:\n' + TD_SYNTAX + '.')

            if firstime:
                if not node.getTag() == tag: raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                        self_funct,
                                                                                        'td:Request Error: First Tag is not:' + tag + ', but:' + node.getTag() + '.\n' +
                                                                                        'Your Top Down PxQuery request:' + og_pxq + '.')
            else:
                try:
                    nodes = node.get(tag=tag)
                except Exception as e:
                    _e = epicxception.epicxmlPxQueryNoNodeFoundException(self.__class__.__name__, self_funct,
                                                              'td:Request Error: No node found for Sub Tag:' + tag + '.\n' +
                                                              'Your Top Down PxQuery request:' + og_pxq + '.\n' +
                                                              'SubException is:' + str(e))
                    _e.setSubException(e)
                    raise _e

            if not (last_level and checkIsAttr and not checkIsUnique) and len(
                nodes) > 1: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                       'td:Request Error: More than one node found for Sub Tag:' + tag + '.\n' +
                                                                       'Your Top Down PxQuery request:' + og_pxq + '.\n')

            if not firstime:
                node = nodes[0]
            else:
                firstime = False

            i += 1

        if checkIsNode:

            error = epicxception.epicxmlPxQueryNoNodeFoundException(self.__class__.__name__, self_funct,
                                                         'td:Request Error: No node found for Sub Tag:' + tag + '.\n' +
                                                         'Your Top Down PxQuery request:' + og_pxq + '.')
            try:
                nodes = node.get(tag=tag)

            except Exception as e:
                error.setMessage(error.getMessage() + 'SubException is:' + str(e))
                error.setSubException(e)
                raise error

            if len(nodes) == 0: raise error
            if len(nodes) > 1 and checkIsUnique: raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                            self_funct,
                                                                                            'td:Request Error: More than one node found for Sub Tag:' + tag + '.\n' +
                                                                                            'Your Top Down PxQuery request:' + og_pxq + '.\n')

            return nodes

        elif checkIsAttr:

            l = []
            for attr in more_attrs:
                if not attr.startswith('@'): raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                        self_funct,
                                                                                        'tdc:Request Error: Bad format, Incorect target attribute:' + attr + ' should start with "@" !\n')
                l.append(attr[1:])
            more_attrs = l

            if not checkIsUnique:
                sb = StringIO()
                first = True

                for node in nodes:
                    if not first: sb.write(node_separator)
                    first = False

                    found, value = pxq_multi_attrs(tag, node, more_attrs, attr_separator, text_separator)
                    ##                    if not found:value=str(node.getAttr(tag))
                    sb.write(value)

                return sb.getvalue()

            else:
                found, value = pxq_multi_attrs(tag, nodes[0], more_attrs, attr_separator, text_separator)
                return value

    def tdc(self, pxq, checkIsNode=True, checkIsAttr=False, doRetNodeIfIsAttr=False, checkIsUnique=False,
            doUpdate=False, picpath_attr_separator=epicbase.PICPATH_ATTR_SEP,
            picpath_text_separator=epicbase.PICPATH_TEXT_SEP, attr_separator=epicbase.ATTR_SEP,
            node_separator=epicbase.NODE_SEP, text_separator=epicbase.TEXT_SEP, verbose=0):
        selfMethod = 'tdc'
        """
        PxQuery top down complete method.
        pxq: syntax: TAG[@ATTR=VALUE[,@ATTR=VALUE]],@ATTR Tag sep:/
        ex:   tag1/tag2/tag3@attr1              
              tag1/tag2@attr1=val1,@attr2=val2/tag3@attr1=val1,@attr2
            Working with text:
              tag1/tag2/tag3@%text
        PxQuery with update  method.
        pxq: syntax: PxQuery[@ATTR=VALUE[,@ATTR=VALUE]]
        ex:   tag1/tag2@attr1=val1,@attr2=val2/tag3@attr1=val1[@attr3=val3,@attr4=val4]
            Working with text:
              tag1/tag2/tag3[@%text=value1;value2 with blanks]

        e.g.:
            To retreive a node:
            servers@type=backend,@site=london/server
            or to retreive an attribute:
            servers@type=backend,@site=london/server@host=axane,@ip

        If last item is a tag and checkIsNode is True returns a python list of all matching nodes.
        If last item is an attribute and checkIsAttr is True returns a separated list value(s) of this attribute for the matching nodes.
        checkIsNode: If true last item is treated as a tag name and a python list of matching nodes is returned.
        checkIsAttr: If true last item is treated as an attribute name and this attribute's value for the matching nodes is returned.
        checkIsUnique: checks if the last found nodes are uniques.
            Note:the intermediate nodes must be uniques.
        separator: allows a custom separator.

        topic: Localisation/PxQuery methods
        """
        self_funct = 'tdc'
        if picpath_attr_separator == None: picpath_attr_separator = epicbase.ATTR_SEP
        TDC_SYNTAX = 'TAG[@ATTR=VALUE[' + picpath_attr_separator + '@ATTR=VALUE]]' + picpath_attr_separator + '@ATTR Tag sep:/\n' + \
                     'TAG[@ATTR=VALUE[' + picpath_attr_separator + '@ATTR=VALUE]]' + picpath_attr_separator + '@ATTR[' + picpath_attr_separator + '@ATTR]\n' + \
                     'TAG[@ATTR=VALUE[' + picpath_attr_separator + '@ATTR=VALUE]]' + picpath_attr_separator + '@*' + \
                     'Working with text:' + \
                     'TAG[@ATTR=VALUE[' + picpath_attr_separator + '@ATTR=VALUE]]' + picpath_attr_separator + '@%text'
        og_pxq = pxq = pxq.strip()

        if (checkIsNode, checkIsAttr) == (True, True) or (checkIsNode, checkIsAttr) == (
        False, False): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,
                                                                    'checkIsNode and checkIsAttr, if one is False the Other must be True !')
        if not isinstance(doUpdate, bool): raise epicxception.epicxmlParameterTypeException(self.__class__.__name__,
                                                                                            selfMethod, 'doUpdate',
                                                                                            'bool', str(doUpdate))
        if picpath_attr_separator == picpath_text_separator: raise epicxception.epicxmlParameterException(
            self.__class__.__name__, self_funct,
            'The parameter:picpath_attr_separator cannot equal: picpath_text_separator ! Your value for both:' + str(
                picpath_attr_separator) + '.')

        ## Retreive the update part.
        pxq_updates = None
        if doUpdate:
            if not checkIsNode or checkIsAttr: raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                            self_funct,
                                                                                            'When doUpdate is True: checkIsNode must be: True and and checkIsAttr: False ! Your values are doUpdate:' + str(
                                                                                                doUpdate) + ', checkIsNode:' + str(
                                                                                                checkIsNode) + ', checkIsAttr:' + str(
                                                                                                checkIsAttr) + ' !')
            if pxq.find('[') < 0 or not pxq.endswith(']'): raise epicxception.epicxmlPxQueryException(
                self.__class__.__name__, self_funct,
                'tdc:Bad Format: When given for update, PxQuery must end with the shape:[@ATTR=VALUE[,@ATTR=VALUE]].\n' +
                'e.g.:tag1/tag2/tag3[@attr1=val1,@attr2=val2]\n' +
                'Your Top Down Complete PxQuery request:' + og_pxq + '.\n' +
                'The tdc syntax is:\n' + TDC_SYNTAX + '.')

            spl = pxq.split('[')
            pxq = spl[0]
            pxq_updates = spl[1][:-1]

            attrs = pxq_updates.split(picpath_attr_separator)
            pxq_updates = pxq_split_attrs(attrs, level=pxq_updates, og_pxq=og_pxq, tdc_syntax=TDC_SYNTAX)

        # Sample : tag1@attr1=a/tag2@attr2=i,@attr3=j/tag4/tag5@attr1,@attr2
        spl = pxq.split(epicbase.TAG_SEP)  # ['tag1@attr1=a', 'tag2@attr2=i,@attr3=j, 'tag4', 'tag5@attr1,@attr2']

        i = 0
        node = self
        nodes = [self]
        firstime = True
        last_level = False
        previous_level = None
        for level in spl:
            if i == len(spl) - 1: last_level = True
            level = level.strip()
            if level == '':
                if previous_level != None:
                    msg = 'Last correct node was: ' + previous_level + '.'
                else:
                    msg = 'First node incorrect. Correct first node is:' + self.getTag() + '.'
                raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                           'tdc:Bad Format: Incorrect node definition.\n' +
                                                           msg + '\n' +
                                                           'Your Top Down Complete PxQuery request:' + og_pxq + '.\n' +
                                                           'The tdc syntax is:\n' + TDC_SYNTAX + '.')

            # ['tag2@attr2=i,@attr3=j']
            spl1 = level.strip().split(picpath_attr_separator)
            spl2 = spl1[0].split('@')
            del spl1[0]

            # Get tag:
            tag = spl2[0]
            del spl2[0]
            first_attr = '@' + '@'.join(spl2)

            # Get attrs: ['@type=backend', '@site=london']
            if first_attr != '@':
                attrs = [first_attr]
                attrs.extend(spl1)
            else:
                attrs = spl1

            ## Tag
            if tag == '':
                raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                           'tdc:Bad Format: Incorrect node/Tag definition. No tag is guiven.\n' +
                                                           'For Level:' + level + '.\n' +
                                                           'Your Top Down Complete PxQuery request:' + og_pxq + '.\n' +
                                                           'The tdc syntax is:\n' + TDC_SYNTAX + '.')

            ## Attributes
            keywords = {}
            target_attribute = None
            more_attrs = []
            if len(attrs) > 0:
                if last_level:
                    og_attrs = attrs

                    # Retreives more attrs.
                    firstime1 = True
                    idx_del = len(attrs)
                    for i in range(len(attrs)):
                        attr = attrs[i]

                        if not attr.find('=') > 0:
                            idx_del = i
                            firstime1 = False
                            more_attrs.append(attr)
                        elif not firstime1:
                            raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                       'tdc:Bad Format: "=" found into target Attributes liste:' + picpath_attr_separator.join(
                                                                           og_attrs) + ' !\nYour Top Down Complete PxQuery request:' + og_pxq + '.')

                    if len(more_attrs) != 0: attrs = attrs[:-len(more_attrs)]

                    # Retreives first attr

                    if len(more_attrs) != 0:
                        target_attribute = more_attrs[
                            0]  # If last level and with attributes ==> last attribute is a target.
                        del more_attrs[0]

                    if pxq.find('*') >= 0:
                        if len(more_attrs) > 0: raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                           self_funct,
                                                                                           'tdc:Bad Format: You have to choose between * (all Attributes) and specific Attribute names. !\nYour Top Down Complete PxQuery request:' + og_pxq + '.\n' + 'The correct tdc syntax is:' + TDC_SYNTAX + '.')
                        if og_pxq[-2:] != '@*': raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                           self_funct,
                                                                                           'tdc:Bad Format: * (all Attributes) can only be use at the end of the pattern !\nYour Top Down Complete PxQuery request:' + og_pxq + '.\n' + 'The correct tdc syntax is:' + TDC_SYNTAX + '.')
                        target_attribute = '@__DO_ATTR_ALL__'

                    if not checkIsAttr and (target_attribute == '@__DO_ATTR_ALL__' or len(
                        more_attrs) > 0): raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                     self_funct,
                                                                                     'tdc:Bad Format or Parameter: This syntax: \nTAG[@ATTR=VALUE[,@ATTR=VALUE]],@*\nis only allowed with checkIsAttr: True !')

                keywords = pxq_split_attrs(attrs, level=level, og_pxq=og_pxq, tdc_syntax=TDC_SYNTAX)
                if '%text' in list(keywords.keys()): raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                                self_funct,
                                                                                                'tdc:%text is not allowed as search key !\nYour Top Down Complete PxQuery request:' + og_pxq + '.\n' + 'The correct tdc syntax is:' + TDC_SYNTAX + '.')

            error = epicxception.epicxmlPxQueryNoNodeFoundException(self.__class__.__name__, self_funct,
                                                         'tdc:Request Error: No node found for Sub Level:' + level + '.\n' +
                                                         'Your Top Down Complete PxQuery request:' + og_pxq + '.')

            if firstime:
                firstime = False
                if not node.getTag() == tag: raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                        self_funct,
                                                                                        'td:Request Error: First Tag is not:' + tag + ', but:' + node.getTag() + '.\n' +
                                                                                        'Your Top Down PxQuery request:' + og_pxq + '.')
                if len(keywords) != 0: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                                  'td:Request Error: First Tag do not accept @ATTR=VALUE at ' + level + ' !')
            else:
                try:
                    nodes = node.get(tag=tag, **keywords)
                except Exception as e:
                    error.setMessage(error.getMessage() + 'SubException is:' + str(e))
                    error.setSubException(e)
                    raise error

            if len(nodes) == 0: raise error
            if len(nodes) > 1 and not (last_level and not checkIsUnique): raise epicxception.epicxmlPxQueryException(
                self.__class__.__name__, self_funct,
                'tdc:Request Error: More than one node found for Sub Level:' + level + '.\n' +
                'Your Top Down Complete PxQuery request:' + og_pxq + '.')

            previous_level = level
            if not firstime:
                node = nodes[0]
            else:
                firstime = False

            i += 1

        if checkIsNode:

            if pxq_updates != None:

                for node in nodes:
                    sb = StringIO()
                    pxq_update(node, pxq_updates, sb, picpath_text_separator, verbose=verbose)

                    if verbose >= 3: print(sb.getvalue())

            return nodes

        elif checkIsAttr:

            l = []
            for attr in more_attrs:
                if not attr.startswith('@'): raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                        self_funct,
                                                                                        'tdc:Request Error: Bad format, Incorect target attribute:' + attr + ' should start with "@" !\n')
                l.append(attr[1:])
            more_attrs = l

            if target_attribute == None: raise epicxception.epicxmlPxQueryException(self.__class__.__name__, self_funct,
                                                                                    'tdc:Request Error: Bad format, target attribute is not guiven !\n')
            if not target_attribute.startswith('@'): raise epicxception.epicxmlPxQueryException(self.__class__.__name__,
                                                                                                self_funct,
                                                                                                'tdc:Request Error: Incorect target attribute:' + target_attribute + ' should starts with "@" !')
            attr = target_attribute[1:]

            if checkIsUnique:
                found, value = pxq_multi_attrs(attr, nodes[0], more_attrs, attr_separator, text_separator)
                if doRetNodeIfIsAttr: return value, nodes[0]
                return value
            else:
                sb = StringIO()
                first = False

                for node in nodes:
                    if first: sb.write(node_separator)
                    first = True
                    found, value = pxq_multi_attrs(attr, node, more_attrs, attr_separator, text_separator)
                    sb.write(value)

                if doRetNodeIfIsAttr:
                    return sb.getvalue(), nodes
                else:
                    return sb.getvalue()



def checkFirstNode(obj):
    """
        Check for authorized first Node.
    """

    if isinstance(obj, FirstWideNode):
        return True
    return False


def firstNode(parms):
    return FirstWideNode(parms)


class Xml_Text:
    def __init__(self, xmlNode=None, xmlSucker=None):
        # D013:from .xmlsuckerscraper import NEW_CDATA_BEGIN, ALTER_SUP, ALTER_INF
        # A013:
        from kwadlib import xmlsuckerscraper as Scraper
        import base64
        node = xmlNode
        src = str(node.nodeValue)

        # - Treat <> inside CDATA
        """ D013:
        if src.find(NEW_CDATA_BEGIN)>=0:
            src=src.replace(ALTER_SUP, '>')
            src=src.replace(ALTER_INF, '<')
        """
        # A013:
        if src.strip().startswith(Scraper.B64FLAG):
            src = base64.urlsafe_b64decode(src.strip()[len(Scraper.B64FLAG):]).decode("utf-8")
            node.getParentNode().instanceLnk._was_cdtata = True

        node.getParentNode().instanceLnk._setText(src)


# A004:
class WideNode(sNode, PxQuery):
    _apb_isinstance_FirstNode = 'WideNode'

    def init(self, name=None, **keywords):
        self.allowedChilds = (WideNode,)
        if name != None:
            self.__name = name
        else:
            self.__name = None
        self.aggregatParent = None
        self.listWideNodes = []
        self.__attrs = {}
        self.__text = None
        self.__quickTags = {}
        self.__orderedAttrs = []

    def setOrderedAttrs(self, orderedAttrs=None):
        if orderedAttrs==None:orderedAttrs=[]
        self.__orderedAttrs = orderedAttrs

    def clone(self, firstNode=None):
        if firstNode != None:
            parent = firstNode
        else:
            parent = None

        clone = self.workClone = WideNode(name=self.__name)
        clone._setAttrs(dict(self.__attrs))
        clone._setText(self.__text)

        if parent != None: parent.add(clone)

    def isCapSensitive(self):
        return self.capSensitive

    def isFirstNode(self):
        return False

    def getFirstNode(self, parms):
        return firstNode(parms)

    def getName(self):
        return self.__name

    def getTag(self):
        return self.getName()

    def setName(self, p_name=None):
        if isinstance(p_name, str) != True: raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, 'setName', 'p_name', 'str', str(p_name))
        self.__name = p_name

    def _setText(self, text):
        self.__text = text

    def _getdAttrs(self):
        return self.__attrs

    def getdAttrs(self):
        return dict(self.__attrs)

    def _setAttrs(self, attrs):
        self.__attrs = attrs

    def setAttrs(self, **keywords):
        self.__attrs = {}

        for attr in keywords:
            value = keywords[attr]
            # if value=='':value=None # D010
            if value in ('', 'None'): value = None  # A010

            if not self.isCapSensitive():
                self.__attrs[attr.upper()] = value
            else:
                self.__attrs[attr] = value

    def hasAttr(self, attr):
        selfMethod = 'hasAttr'
        if not self.isCapSensitive(): attr = attr.upper()
        if attr in self.__attrs: return True
        return False

    def getAttr(self, attr):
        selfMethod = 'getAttr'
        if not self.isCapSensitive(): attr = attr.upper()
        # A034:
        if attr not in self.__attrs: raise epicxception.epicxmlAttrNotFound(self.__class__.__name__, selfMethod,
            'Attribute:' + str(attr) + ' is not defined for tag:' + self.getName() + ', defined attributes are:' + str(list(self.__attrs.keys())) + '.')
        return self.__attrs[attr]

    def setAttr(self, attr, value):
        self.__attrs[attr] = value

    def accept(self, p_visitor):

        if (p_visitor.childFirst):
            p_visitor.visitWideNodes(self)
            if p_visitor.treatAncestor:
                p_visitor.visitWideNode(self)
            else:
                p_visitor.treatAncestor = True
        else:
            if p_visitor.treatAncestor:
                p_visitor.visitWideNode(self)
            else:
                p_visitor.treatAncestor = True
            p_visitor.visitWideNodes(self)

    def getAggregatParent(self):
        if self.aggregatParent != None:
            return self.aggregatParent()
        else:
            return None

    def setAggregatParent(self, p_wideNode):
        import weakref
        if __debug__ and not hasattr(p_wideNode, 'isinstance') and not p_wideNode.isinstance('WideNode'):
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, 'setAggregatParent', 'p_wideNode', 'WideNode', str(p_wideNode))

        self.aggregatParent = weakref.ref(p_wideNode)

    def removeAggregatParent(self):
        self.aggregatParent = None

    def getTopParent(self):
        if not (self.isFirstNode() or self.getAggregatParent() == None):
            return self.getAggregatParent().getTopParent()
        return self

    def getTop(self):
        return self.getTopParent()

    def getQuickTagKeys(self):
        return list(self.__quickTags.keys())

    def getQuickTagNodes(self, tag):
        return self.__quickTags[tag]

    def getNode(self, tag):
        """
        If this node has any child nodes of this tag,
        returns a python list of these nodes.
        topic: Localisation methods
        """
        selfMethod = 'getNode'
        founds = []
        found = False
        if not self.isCapSensitive(): tag = tag.capitalize()

        if tag not in self.getQuickTagKeys(): raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                        selfMethod,
                                                                                        'Not supported Tag:' + tag + ' !')
        return self.getQuickTagNodes(tag)

    def getNodes(self):
        return list(self.listWideNodes)

    def add(self, p_wideNode):
        selfMethod = 'add'
        p_wideNode.setAggregatParent(self)
        if p_wideNode in self.listWideNodes: raise epicxception.AppPreexistingObjectError(str(self.__class__),
                                                                                          p_wideNode.__class__,
                                                                                          id(p_wideNode))
        self.listWideNodes.append(p_wideNode)

        if p_wideNode.getName() not in self.__quickTags: self.__quickTags[p_wideNode.getName()] = []
        self.__quickTags[p_wideNode.getName()].append(p_wideNode)

    def initFrom_xmlNode(self, xmlSucker):
        selfMethod = 'initFrom_xmlNode'
        node = self.xmlNodeLnk

        if node == None or (node != None and node.nodeType not in (node.ELEMENT_NODE)):
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, "Class:" + str(
                self.__class__) + " received Incorect value received for node:" + str(node))

        if self.isCapSensitive():
            nodeName = str(node.nodeName).strip()
        else:
            nodeName = str(node.nodeName).strip().capitalize()

        self.setName(nodeName)
        lstNodeAttr = xmlSucker.getAttributes(node)
        self.setOrderedAttrs(lstNodeAttr.getOrderedAttrs())

        node.instanceLnk = self
        if hasattr(node.getParentNode(), 'instanceLnk'):
            parent = node.getParentNode().instanceLnk
        else:
            if xmlSucker.foundFirstNode == None:
                xmlSucker.foundFirstNode = FirstWideNode(xmlSucker.trivialParmToFirstNode)
                xmlSucker.foundFirstNode.capSensitive = self.isCapSensitive()
            parent = xmlSucker.foundFirstNode

        parent.add(self)
        self.setAttrs(**lstNodeAttr)
        self.clearTrivialRef()

    def workMkNode(self, visitor):
        selfMethod = 'workMkNode'

        if visitor.foundFirstNode == None:
            visitor.foundFirstNode = FirstNode(**self.getTopParent().trivialParmToFirstNode)
            parent = visitor.foundFirstNode
        else:
            parent = self.getAggregatParent().work_node

        # M030:
        if not visitor.clasIsSoftClassNode:node = self.work_node = Node(name=self.__name)
        else:
            raise Exception('clasIsSoftClassNode is not Supported by KastMenu (DKwad only) !' )
        node.capSensitive = self.isCapSensitive()

        if parent.isPartial() and not parent.peerTagdesc.isStrict():
            force = True
        else:
            force = False

        parent.add(node, force=force)

        # Check for non described Tag
        try:
            node.peerTagdesc = node.getPeerTagdesc(node.getFiliation())
            if node.peerTagdesc.isStrict(): force = False
        except epicxception.epicxmlUnSupportedTagException as e:  ## actually force True only adn parent.isPartial() only !

            # If isPartial create missing tag on Parent Descriptor tag.
            if node.isPartial():
                ptag = node.getFiliation().split(epicbase.TAG_SEP)
                ctag = ptag.pop()

                if __debug__:
                    ptag = epicbase.TAG_SEP.join(ptag)
                    if ptag != parent.getFiliation(): raise epicxception.epicxmlSystemException(node.__class__.__name__,
                                                                                                selfMethod,
                                                                                                'Unmatching filiation:"' + str(
                                                                                                    ptag) + '" and "' + str(
                                                                                                    parent.getFiliation()) + '" !')

                from .epicdesc import Tagdesc
                node.peerTagdesc = Tagdesc.newTagdesc(ctag, parent=parent.peerTagdesc, orderedAttrs=self.__orderedAttrs)
            else:
                raise

        node.feedRestrictor()
        node.setAttrs(_force=force, **dict(self.__attrs))
        if self.__text!=None:node.setText(self.__text, _force=force)


# A004:
class FirstWideNode(WideNode):
    _apb_isinstance_FirstNode = 'FirstWideNode'

    def _init(self, trivialParmToFirstNode):
        self.trivialParmToFirstNode = trivialParmToFirstNode
        WideNode.init(self, name='FIRSTNODE')

    def isFirstNode(self):
        return True

    def treatForeach(self):
        self_funct = 'treatForeach'

        # M001:20120901
        wrk = epicwvisitor.WorkForeach()
        self.accept(wrk)
        while True:
            wrk.mayHaveMore = False
            self.accept(wrk)
            if not wrk.mayHaveMore: break

            # =============#
            #             #
            #  Real Node  #
            #             #
            # =============#


class Attributes():
    pass


# M004:
class Node(epicbase.rImbricatedNodeBase, PxQuery):
    _apb_isinstance_Node = 'Node'

    def _init(self, name=None, **keywords):
        self.allowedChilds = (Node,)
        epicbase.rImbricatedNodeBase.init(self, **keywords)
        if name != None: self.setName(name)
        self.__attrs = {}
        self.__text =  None
        self.peerTagdesc = None
        self.peerTagrest = None
        self.__tun = None
        self.__file_desc = None
        self.__file_rest = None
        # A030: Later to move to epicdesc
        self.__tagOrders = []
        self.capSensitive = True

    def isCapSensitive(self):
        return self.capSensitive

    # A019:
    def noParentWeakRef(self):
        top = self.getTopParent()
        if not isinstance(top, FirstNode):return False
        else:return top.no_parent_weakref

    def hardLinkTopParent(self):
        self.__top_hard_link = self.getTopParent()

    def destroy(self):
        if hasattr(self, '__top_hard_link'): delattr(self, '__top_hard_link')

    def doLBBeforTag(self):
        """ For printXml() """
        return False

    def updQuickTun(self):
        self.filiation = None
        self.getTopParent()._setQuickTun(self.getTun(), self)

        # ------------------------------- Descriptor/Restrictor Proxies facilities (BEGIN) -------------------------------#

    def getFileDesc(self):  # Having this, at the node level instead of at the FirtNode level, allows xml subsets to have their own descritor/restrictor.
        return self.__file_desc

    def setFileDesc(self, file_desc):
        self.__file_desc = file_desc

    def getFileRest(self):  # Having this, at the node level instead of at the FirtNode level, allows xml subsets to have their own descritor/restrictor.
        return self.__file_rest

    def setFileRest(self, file_rest):
        self.__file_rest = file_rest

    def hasRestrictor(self):
        return self.peerTagdesc.hasRestrictor()

    def getDescs(self):
        return self.peerTagdesc.getDescs()

    def getDescWk(self, attr):
        """
        This return the value of this attr alike getAttr.
        But the value is the guiven Attribute's descriptor.
        """
        return self.peerTagdesc.getDescWk(attr)

    def getTextDescWk(self):
        return self.peerTagdesc.getTextDescWk()

    def getTagDescWk(self):
        return self.peerTagdesc.getTagDescWk()

    def getRests(self):
        return self.peerTagdesc.getRests()

    def getRestWk(self, attr):
        return self.peerTagdesc.getRestWk(attr)

    def getTextRestWk(self):
        return self.peerTagdesc.getTextRestWk()

    def getTagRestWk(self):
        return self.peerTagdesc.getTagRestWk()

    def getDescDft(self, attr):
        return self.peerTagdesc.getDescDft(attr)

    def getTextDescDft(self):
        return self.peerTagdesc.getTextDft()

    def getRestDft(self, attr):
        return self.peerTagdesc.getRestDft(attr)

    def getTextRestDft(self):
        return self.peerTagdesc.getTextRestDft()

    def getDft(self, attr):
        """
        If this configuration has a restrictor :
        this method will return the Attributes value retreived from the softclass's resctrictor.
        Otherwise :
        this method will return  the Attributes value retreived from the softclass's descriptor.
        """
        # f814290522f79d1e9e5ae4ae83e967b4
        return self.peerTagdesc.getDft(attr)

    def getTextDft(self):
        return self.peerTagdesc.getTextDft()

    def eqDescDft(self, attr, value):
        return self.peerTagdesc.eqDescDft(attr, value)

    def eqTextDescDft(self, value):
        return self.peerTagdesc.eqTextDescDft(value)

    def eqRestDft(self, attr, value):
        return self.peerTagdesc.eqRestDft(attr, value)

    def eqTextRestDft(self, value):
        return self.peerTagdesc.eqTextRestDft(value)

    def eqDft(self, attr, value):
        return self.peerTagdesc.eqDft(attr, value)

    def eqTextDft(self, value):
        return self.peerTagdesc.eqTextDft(value)

    # ------------------------------- Descriptor/Restrictor proxies facilities (END) -------------------------------#

    # ------------------------------- Wk aliens proxies facilities (BEGIN) -------------------------------#

    def isDenied(self, attr, doExcptCls=False, doRaise=False):
        return self.peerTagdesc.isDenied(attr, doExcptCls=doExcptCls, doRaise=doRaise)

    def isTextDenied(self, doExcptCls=False, doRaise=False):
        return self.peerTagdesc.isTextDenied(doExcptCls=doExcptCls, doRaise=doRaise)

    def isTagDenied(self, doExcptCls=False, doRaise=False):
        return self.peerTagdesc.isTagDenied(doExcptCls=doExcptCls, doRaise=doRaise)

    def isDisplayable(self, attr):
        return self.peerTagdesc.isDisplayable(attr)

    def isTextDisplayable(self):
        return self.peerTagdesc.isTextDisplayable()

    def isTagDisplayable(self):
        return self.peerTagdesc.isTagDisplayable()

    def isUpdatable(self, attr):
        return self.peerTagdesc.isUpdatable(attr)

    def isTextUpdatable(self):
        return self.peerTagdesc.isTextUpdatable()

    def isTagUpdatable(self):
        return self.peerTagdesc.isTagUpdatable()

    def showShortCut(self):
        return self.peerTagdesc.showShortCut()

    def getHelp(self, attr):
        return self.peerTagdesc.getHelp(attr)

    def getLHelp(self, attr):
        return self.peerTagdesc.getLHelp(attr)

    def getTextHelp(self):
        return self.peerTagdesc.getTextHelp()

    def getTextLHelp(self):
        return self.peerTagdesc.getTextLHelp()

    def getTagHelp(self):
        return self.peerTagdesc.getTagHelp()

    def getTagLHelp(self):
        return self.peerTagdesc.getTagLHelp()

    # ------------------------------- Wk aliens proxies facilities (END) -------------------------------#

    def isTag(self, name):
        self_funct = 'isTag'
        if self.getTag() != name: raise epicxception.epicxmlSystemException(self.__class__.__name__, self_funct,
                                                                            'Tag:' + self.getTag() + ', Imbrication ERROR, this tag should be: ' + name + ' and not: ' + self.getTag() + ' !')

    def getTag(self):
        """
        Returns this node tag name.
        topic: Utility methods
        """
        return self.getName()

    def isSoftClass(self):
        if self.hasAttr('type') and self.getAttr('type') == 'softclass': return True
        return False

    def getTun(self):
        if self.__tun == None: self.__tun = self.getTopParent().mkTun()
        return self.__tun

    def getNodes(self):
        """
        Returns this node child nodes.
        topic: Utility methods
        """
        return self.getChilds()

    def getOrderedNodes(self):
        return self.getNodes()

    # A030:
    def getTagOrders(self):
        return self.__tagOrders
    def _setTagOrders(self, orders):
        self.__tagOrders = orders

    def hasNode(self, tag):
        """
        Checks if this node has any child nodes of this tag.
        topic: Localisation methods
        """
        if not self.isCapSensitive(): tag = tag.capitalize()

        if tag in self.getQuickTagKeys():
            return True
        return False

    def checkNodes(self, dct):
        self_funct = 'checkNodes'
        if dct != None and not isinstance(dct, dict): raise epicxception.epicxmlParameterTypeException(
            self.__class__.__name__, self_funct, 'Tag:' + self.getTag() + ', dct', 'dict', dct)
        keys1 = list(dct.keys())
        keys2 = self.getQuickTagKeys()

        for elt in keys2:
            if elt not in keys1: raise epicxception.epicxmlSystemException(self.__class__.__name__, self_funct,
                                                                           "Tag: " + elt + " is not valid. Valid tags are: " + str(
                                                                               keys1) + ".")

        for elt in keys1:
            if dct[elt] == True and elt not in keys2: raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                                self_funct,
                                                                                                "The Tag: " + elt + " is required. The given tags are: " + str(
                                                                                                    keys2) + ".")

    def getNode(self, tag):
        """
        If this node has any child nodes of this tag,
        returns a python list of these nodes.
        topic: Localisation methods
        """
        selfMethod = 'getNode'
        founds = []
        found = False

        if not self.isCapSensitive(): tag = tag.capitalize()

        if tag not in self.getQuickTagKeys(): raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                        selfMethod,
                                                                                        'Not supported Tag:' + tag + ' !')
        return self.getQuickTagNodes(tag)

    def getAttrDescs(self):
        return dict(self.peerTagdesc.attrDescs)

    def getAttrOrders(self):
        keys = []
        if self.peerTagdesc != None: keys = [attr for attr in self.peerTagdesc.orderedAttrDescs if attr in self.__attrs]
        keys.extend([attr for attr in self.__attrs if attr not in keys])

        return keys

    # A023:
    def addAttr(self, attr, value, wks=None, prepend=False, force=False):
        self_funct='addAttr'
        from kwadlib.security.crypting import sanitize
        sanitize(class_exit=self.__class__.__name__, method_exit=self_funct, **{'attr': attr})
        if wks == None:wks = {'*type': 'str'}
        if not force:raise epicxception.epicxmlSystemException(self.__class__.__name__, self_funct, 'Must be explicitly called with force=True !')
        if not self.isCapSensitive(): attr = attr.upper()

        # checks wk:
        wk.isWKDefinition(wks, class_exit=self.__class__.__name__, method_exit=self_funct)
        p = wk.WantedKeywords()
        p=wks
        wk.getKeywords(wantedKeywords=p, keywords={'attr': value}, class_exit=self.__class__.__name__, method_exit=self_funct)
        self.peerTagdesc.attrDescs[attr] = wks

        if prepend:self.peerTagdesc.orderedAttrDescs.insert(0, attr)
        else:self.peerTagdesc.orderedAttrDescs.append(attr)
        self.__attrs[attr] = value

        return True

    def delAttr(self, attr):
        if not self.isCapSensitive(): attr = attr.upper()
        if attr not in self.__attrs: return False

        del self.__attrs[attr]
        if attr in self.peerTagdesc.orderedAttrDescs:self.peerTagdesc.orderedAttrDescs.remove(attr) # A023
        self.peerTagdesc.delDescWk(attr)
        self.peerTagdesc.delRestWk(attr)

        return True

    def hasAttr(self, attr):
        """
        Checks if this node support this tag attribute.
        topic: Utility methods
        """
        if not self.isCapSensitive(): attr = attr.upper()
        if attr in self.__attrs: return True
        return False

    def getAttr(self, attr):
        """
        Returns an object which attributes are the node's tag attributes.
        topic: Utility methods
        """
        selfMethod = 'getAttr'
        if not self.isCapSensitive(): attr = attr.upper()
        # A034:
        if attr not in self.__attrs: raise epicxception.epicxmlAttrNotFound(self.__class__.__name__, selfMethod,
            'Attribute:' + str(attr) + ' is not defined for tag:' + self.getName() + ', defined attributes are:' + str(list(self.__attrs.keys())) + '.')
        return self.__attrs[attr]

    def checkAttr(self, attr, value, allowNone=False):
        self_funct = 'checkAttr'
        from kwadlib.repozwkextension import wkExtension
        error_class = None

        repoz_infos = self.getTopParent().getRepozInfos()
        if repoz_infos != None:
            wkExtension = wkExtension(repoz_infos['repoz'], repoz_infos['alias'], self)
        else:
            wkExtension = None

        try:
            try:
                self.isTagDenied(doRaise=True)
                # allowNone: Do we allow user to set None on denied attr that may have default:
                if not (allowNone and value==None):self.isDenied(attr, doRaise=True)
            except Exception as e:
                if not self.eqDft(attr, value):
                    error_class = e.__class__.__name__
                    if error_class.find('Descriptor') >= 0:
                        error_prefix = '[DescriptorCheck]'
                    else:
                        error_prefix = '[RestrictorCheck]'
                    raise

            descs = []
            descs.append((self.getDescWk(attr), 'epicxmlDescriptorCheckException', '[DescriptorCheck]'))
            rwks = self.getRestWk(attr)
            if rwks != None: descs.append((rwks, 'epicxmlRestrictorCheckException', '[RestrictorCheck]'))

            for wks in descs:
                error_class = wks[1]
                error_prefix = wks[2]
                wks = wks[0]

                p = wk.WantedKeywords()
                setattr(p, attr, wks)

                wk.getKeywords(wantedKeywords=p, keywords={attr: value}, wkExtension=wkExtension,
                               class_exit=self.__class__, method_exit=self_funct)
                value = getattr(p, attr)  # keep default

        except Exception as e:
            if error_class == None:error_class = e.__class__.__name__
            if not hasattr(epicxception, error_class): raise e
            _e = getattr(epicxception, error_class)(self.__class__.__name__, self_funct,
                                                    error_prefix + ' Tag:' + self.getFiliation() + '@Attribute:' + attr + ' got incorrect value:' + str(
                                                        value) + ' ! SubException is:' + str(e))
            _e.setSubException(e)
            raise _e


        return value

    def checkAttrs(self):
        attrs = self.getdAttrs()

        for attr in self.peerTagdesc.orderedAttrDescs:

            if attr in attrs:
                value = attrs[attr]
            else:
                value = None
            self.setAttr(attr, value)

        return True

    def checkWholeNode(self):
        self.checkAttrs()
        self.checkText(self.getText())

    def setAttr(self, attr, value, _force=False):
        """
        Set value to this node's tag attribute: attr.
        **attrs: is a set of pair attr=value keyword parameters.
        topic: Utility methods
        """
        selfMethod = 'setAttr'
        if not _force and self.isForce(): _force = True
        if not self.isCapSensitive(): attr = attr.upper()

        if self.isForce2() and  attr in self.peerTagdesc.partialAttrDescs:pass
        elif not _force and (attr not in self.peerTagdesc.attrDescs or attr in self.peerTagdesc.partialAttrDescs):
            allowed_attrs = [at for at in self.peerTagdesc.attrDescs if attr not in self.peerTagdesc.partialAttrDescs]

            # M003: raise epicxception.epicxmlUnSupportedTagAttributeException(self.__class__.__name__, selfMethod, "[DescriptorCheck] For tag:" + self.getName() + ' Not allowed attribute:' + attr + ', allowed attributes are:' + str(allowed_attrs) + '. Advice: describe attribute:' + attr + ' into your xml descriptor file or use _force.')
            raise epicxception.epicxmlUnSupportedTagAttributeException(self.__class__.__name__, selfMethod,
                "[DescriptorCheck] For tag:" + self.getFiliation() + ', Not allowed attribute:' + attr + ', allowed attributes are:' + str(
                allowed_attrs) + '. Advice: describe attribute:' + attr + ' into your xml descriptor file or use _force.')

        if _force and attr not in self.peerTagdesc.attrDescs:
            # Mark this Attribute as partial.
            if attr not in self.peerTagdesc.partialAttrDescs: self.peerTagdesc.partialAttrDescs.append(attr)
            # And accept it.
            self.peerTagdesc.attrDescs[attr] = {'*type': 'str'}

        try:
            if _force:
                descs = self.getDescs()
                if (attr not in descs) or (
                        attr in descs and '*type' in descs[attr] and descs[attr]['*type'] == 'str'): value = str(value)
            self.__attrs[attr] = self.checkAttr(attr, value)
        except:
            if not _force:
                raise
            else:
                import sys, warnings
                message = 'Error happend setting the Attribute:' + attr + '. SubException is:' + str(
                    sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1])
                warnings.warn(message)

    def _getdAttrs(self):
        """
        For internalm use only.
        """
        return self.__attrs

    def getdAttrs(self):
        """
        Returns a dict which entries are the node's tag attributes.
        topic: Utility methods
        """
        return dict(self.__attrs)

    def getAttrs(self):
        """
        Returns an object which attributes are the node's tag attributes.
        topic: Utility methods
        """
        o = Attributes()
        for attr in self.__attrs: setattr(o, attr, self.__attrs[attr])

        return o

    def _setAttrs(self, attrs):
        """
        For internalm use only.
        """
        self.__attrs = attrs

    def setAttrs(self, _update=False, _force=False, **p_attrs):
        """
        Set value to this node's tag attribute: attr.
        **attrs: is a set of pair attr=value keyword parameters.
        topic: Utility methods
        """
        selfMethod = 'setAttrs'

        # A037: If this epicfile has no desc we just set and go:
        if self.peerTagdesc==None:
            self.__attrs = dict(p_attrs)
            return


        if not isinstance(_update, bool) or not isinstance(_force, bool): raise epicxception.epicxmlParameterException(
            self.__class__.__name__, selfMethod,
            'Only bool value are accepted for parameter _update and _force ! Your values are _update:' + str(
                _update) + ', _force:' + str(_force) + '.')
        if not _force and self.isForce(): _force = self.isForce()

        dattrs = {}
        if not isinstance(p_attrs, dict):
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'p_attrs', 'dict',
                                                             str(p_attrs))

        for attr in p_attrs:
            if not self.isCapSensitive():
                dattrs[attr.upper()] = p_attrs[attr]
                attr = attr.upper()

            if self.isForce2() and attr in self.peerTagdesc.partialAttrDescs:pass
            elif not _force and (attr not in self.peerTagdesc.attrDescs or attr in self.peerTagdesc.partialAttrDescs):
                allowed_attrs = [at for at in self.peerTagdesc.attrDescs if at not in self.peerTagdesc.partialAttrDescs]
                raise epicxception.epicxmlUnSupportedTagAttributeException(self.__class__.__name__, selfMethod,
                                                                           "[DescriptorCheck] For tag:" + self.getName() + ' Not allowed attribute:' + attr + ', allowed attributes are:' + str(
                                                                               allowed_attrs) + '. Advice: describe attribute:' + attr + ' into your xml descriptor file or use _force.')

            if _force and attr not in self.peerTagdesc.attrDescs:
                # Mark this Attribute as partial.
                self.peerTagdesc.partialAttrDescs.append(attr)
                # And accept it.
                self.peerTagdesc.attrDescs[attr] = {'*type': 'str'}

        if self.isCapSensitive(): dattrs = dict(p_attrs)

        if _update:
            dct = dict(self.getdAttrs())
            dct.update(dattrs)
            dattrs = dct
        else:
            self.__attrs = {}

        if not _force:
            for attr in self.peerTagdesc.attrDescs:
                if attr in dattrs:
                    value = dattrs[attr]
                else:
                    value = None

                self.__attrs[attr] = self.checkAttr(attr, value, allowNone=True)

        else:  # When force or partial we allow raw creation of attrs without setting default values.

            for attr in self.peerTagdesc.attrDescs:
                if attr in dattrs:
                    value = dattrs[attr]
                else:
                    value = None
                try:
                    self.__attrs[attr] = self.checkAttr(attr, value)
                except:
                    self.__attrs[attr] = value

            for attr in dattrs:
                if attr in self.peerTagdesc.attrDescs: continue
                value = dattrs[attr]
                try:
                    self.__attrs[attr] = self.checkAttr(attr, value)
                except:
                    self.__attrs[attr] = value

    def _getText(self):
        """
        For internal use only.
        """
        return self.__text

    def hasText(self):
        if self.__text != None: return True

    def getText(self):
        return self.__text

    def _setText(self, text):
        """
        For internal use only.
        """
        self.__text = text

    def checkText(self, text):
        self_funct = 'checkText'
        from kwadlib.repozwkextension import wkExtension

        repoz_infos = self.getTopParent().getRepozInfos()
        if repoz_infos != None:
            wkExtension = wkExtension(repoz_infos['repoz'], repoz_infos['alias'], self)
        else:
            wkExtension = None

        try:
            try:
                self.isTagDenied(doRaise=True)
                self.isTextDenied(doRaise=True)
            except Exception as e:
                if not self.eqTextDft(text):
                    error_class = e.__class__.__name__
                    if error_class.find('Descriptor') >= 0:
                        error_prefix = '[DescriptorCheck]'
                    else:
                        error_prefix = '[RestrictorCheck]'
                    raise

            descs = []
            descs.append((self.getTextDescWk(), 'epicxmlDescriptorCheckException', '[DescriptorCheck]'))
            rwks = self.getTextRestWk()
            if rwks != None: descs.append((rwks, 'epicxmlRestrictorCheckException', '[RestrictorCheck]'))

            for wks in descs:
                error_class = wks[1]
                error_prefix = wks[2]
                wks = wks[0]

                p = wk.WantedKeywords()
                setattr(p, 'text', wks)

                wk.getKeywords(wantedKeywords=p, keywords={'text': text}, wkExtension=wkExtension,
                               class_exit=self.__class__, method_exit=self_funct)
                text = p.text  # keep default

        except Exception as e:
            _e = _e = getattr(epicxception, error_class)(self.__class__.__name__, self_funct,
                                                         error_prefix + ' Tag:' + self.getFiliation() + '/Text: got incorrect value:' + str(
                                                             text) + ' ! SubException is:' + str(e))
            _e.setSubException(e)
            raise _e

        return text


    def setText(self, p_text, _force=False):
        """
        topic: Utility methods
        """
        selfMethod = 'setText'
        if not isinstance(_force, bool): raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, '_force)', 'bool', str(_force))
        if not _force and self.isForce(): _force = self.isForce()

        try:
            ret = self.checkText(p_text)
            if ret == None: return
        except:
            if not _force: raise
            ret = p_text

        self.__text = ret


    # -------------- #
    # Print methods #
    # ------------- #

    def printText(self, doChild=True, indent='', step=4, doLBBeforTag=True, noDft=True, noDftRaise=False, noNone=True,
                  _sb=None):
        """
        Print a text represention of this node and its children if doChild is True (default).

        indent (integer) : if indent is given text is printed respecting this margin.
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        step (integer) : width between each tree node when doChild is True.
        doLBBeforTag (bool) : if True do a line break befor writing tag.
        _sb : internal use only.
        """
        self_funct = 'printText'
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                       self_funct,
                                                                                       'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(
                                                                                           doChild) + '. Type:' + str(
                                                                                           type(doChild)) + '.')
        if not isinstance(indent, str) and not indent.isspace(): raise epicxception.epicxmlParameterException(
            self.__class__.__name__, self_funct,
            'Bad type for parameter: indent. Expected type is: a blank str ! Received:' + str(indent) + '. Type:' + str(
                type(indent)) + '.')
        if not isinstance(step, int): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,
                                                                                   'Bad type for parameter: step. Expected type is: ! Received:' + str(
                                                                                       step) + '. Type:' + str(
                                                                                       type(step)) + '.')
        if not isinstance(doLBBeforTag, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                            self_funct,
                                                                                            'Bad type for parameter: doLBBeforTag. Expected type is: bool ! Received:' + str(
                                                                                                doLBBeforTag) + '. Type:' + str(
                                                                                                type(
                                                                                                    doLBBeforTag)) + '.')

        if _sb == None: _sb = StringIO()
        if doLBBeforTag and self.doLBBeforTag():
            do_lb_befor_tag = True
        else:
            do_lb_befor_tag = False
        pos = indent
        # indent +  step*' '

        if do_lb_befor_tag: _sb.write('\n')
        _sb.write(indent + 'Tag : ' + self.getTag() + '\n')

        # attrs order
        attrs = self.getdAttrs()
        attrs_keys = list(attrs.keys())
        attrorders = self.getAttrOrders()
        if attrorders == None:
            attrorders = attrs_keys
        else:
            attrorders = attrorders + [attr for attr in attrs_keys if attr not in attrorders]

        for attr in attrorders:
            if attr not in attrs_keys: continue
            try:
                if (noDft and self.eqDft(attr, attrs[attr])) or (noNone and attrs[attr] == None): continue
            except:
                if noDftRaise: raise

            quote = "'"
            if str(attrs[attr]).find("'") >= 0: quote = '"'
            _sb.write(indent + step * ' ' + attr + ' : ' + quote + str(attrs[attr]) + quote + '\n')


        if self.hasText():_sb.write(self.getText())

        if doChild:
            l = self.getOrderedNodes()
            for node in l:
                _sb.write('\n')
                node.printText(doChild=doChild, indent=indent, step=step, noDft=noDft, noDftRaise=noDftRaise,
                               doLBBeforTag=doLBBeforTag, _sb=_sb)

        if do_lb_befor_tag: _sb.write('\n')

        return _sb

    def printXml(self, doChild=True, indent='', step=4, doSpaceWrapEq=False, doLBBeforTag=True, doLBAfterTag=True,
                 doLBBeforAttr=False, noDft=False, noDftRaise=False, noNone=True, noComment=False, _nbstep=0, _sb=None,
                 omit_attrs=None, fct_omit=None):
        """
        Print an xml represention of this node and its children if doChild is True (default).

        indent (integer) : if indent is given text is printed respecting this margin.
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        doSpaceWrapEq (bool) : if doSpaceWrapEq is True a space will wrap the sign equal in the output, likewise: ATTR_NAME = 'ATTR_VALUE'.
            if doSpaceWrapEq is False no space will wrap the sign equal in the output, likewise: ATTR_NAME='ATTR_VALUE'.
        step (integer) : width between each tree node when doChild is True.
        doLBBeforTag (bool) : if True do a line break befor writing tag.
        _nbstep : internal use only.
        _sb : internal use only.
        """
        self_funct = 'printXml'
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(doChild) + '. Type:' + str(type(doChild)) + '.')
        if not isinstance(noDft, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: noDft. Expected type is: bool ! Received:' + str(noDft) + '. Type:' + str(type(noDft)) + '.')
        if not isinstance(noNone, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: noNone. Expected type is: bool ! Received:' + str(noNone) + '. Type:' + str(type(noNone)) + '.')
        if not isinstance(indent, str) and not indent.isspace(): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: indent. Expected type is: a blank str ! Received:' + str(indent) + '. Type:' + str(type(indent)) + '.')
        if not isinstance(step, int): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: step. Expected type is: int ! Received:' + str(step) + '. Type:' + str(type(step)) + '.')
        if not isinstance(doSpaceWrapEq, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: doSpaceWrapEq. Expected type is: bool ! Received:' + str(doSpaceWrapEq) + '. Type:' + str(type(doSpaceWrapEq)) + '.')
        if not isinstance(doLBBeforTag, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: doLBBeforTag. Expected type is: bool ! Received:' + str(doLBBeforTag) + '. Type:' + str(type(doLBBeforTag)) + '.')
        if not isinstance(doLBAfterTag, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: doLBAfterTag. Expected type is: bool ! Received:' + str(doLBAfterTag) + '. Type:' + str(type(doLBAfterTag)) + '.')
        if not isinstance(doLBBeforAttr, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: doLBBeforAttr. Expected type is: bool ! Received:' + str(doLBBeforAttr) + '. Type:' + str(type(doLBBeforAttr)) + '.')
        if omit_attrs and not isinstance(omit_attrs, (tuple, list)): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: omit_attrs. Expected type is: tuple/list ! Received:' + str(omit_attrs) + '. Type:' + str(type(omit_attrs)) + '.')

        if _sb == None: _sb = StringIO()
        if doLBBeforTag and self.doLBBeforTag():
            do_lb_befor_tag = True
        else:
            do_lb_befor_tag = False
        if doSpaceWrapEq:
            equalspc = ' '
        else:
            equalspc = ''
        pos = indent + _nbstep * step * ' '

        # -- Comment management
        try:
            comment_recorders = self.getTopParent().getCommentRecorders()
        except:comment_recorders = []

        if not noComment and self.getTun() in comment_recorders:
            comments = comment_recorders[self.getTun()]
            for line in comments: _sb.write(line + '\n')

        if do_lb_befor_tag: _sb.write('\n')
        _sb.write(pos + '<' + self.getTag())

        # attrs order
        attrs = self.getdAttrs()
        attrs_keys = list(attrs.keys())
        attrorders = self.getAttrOrders()
        # A036:
        attrdescs = self.getAttrDescs()
        if attrorders == None:
            attrorders = attrs_keys
        else:
            attrorders = attrorders + [attr for attr in attrs_keys if attr not in attrorders]

        for attr in attrorders:
            if attr not in attrs_keys: continue
            if omit_attrs and attr in omit_attrs: continue
            # A065:
            value = attrs[attr]
            out_value = value
            if attr in attrdescs:
                wks = attrdescs[attr]
                if '*withCoolTyping' in wks and wks['*withCoolTyping']:out_value = ct.unDress(value)
                elif '*withJson' in wks and wks['*withJson']:
                    import json
                    out_value = json.dumps(value)
            try:
                # if (noDft and self.eqDft(attr, attrs[attr])) or (noNone and attrs[attr]==None):continue
                if (noDft and self.eqDft(attr, value)) or (noNone and value in (None, 'None')): continue
            except:
                if noDftRaise: raise

            if doLBBeforAttr:
                _sb.write('\n' + pos + step * ' ')
            else:
                _sb.write(' ')
            quote = "'"
            if str(value).find("'") >= 0: quote = '"'
            _sb.write(attr + equalspc + '=' + equalspc + quote + str(value) + quote)

        if len(self.getNodes()) != 0 or self.hasText():
            _sb.write('>\n')
        else:
            _sb.write('/>\n')
        if doLBAfterTag: _sb.write('\n')

        if self.hasText():
            text = self.getText()
            out_text = text

            # TreatCDATA: A032:
            text_wks = self.getTextDescWk()
            if '*withCoolTyping' in text_wks and text_wks['*withCoolTyping']:
                out_text = ct.unDress(text)
            elif '*withJson' in text_wks and text_wks['*withJson']:
                import json
                out_text = json.dumps(text)
            else:out_text = str(out_text)

            if text_wks.__contains__('*raw') and text_wks['*raw']:
                from kwadlib.xmlsuckerscraper import CDATA_BEGIN, CDATA_END
                _sb.write(CDATA_BEGIN + '\n')
                _sb.write(out_text + '\n')
                _sb.write(CDATA_END + '\n')
            else:
                _sb.write(out_text + '\n')

        if doChild:
            l = self.getOrderedNodes()
            for node in l:
                if fct_omit != None:
                    if fct_omit(node): continue

                node.printXml(doChild=doChild, indent=indent, step=step, doSpaceWrapEq=doSpaceWrapEq,
                              doLBBeforTag=doLBBeforTag, doLBBeforAttr=doLBBeforAttr, noDft=noDft,
                              noDftRaise=noDftRaise, noNone=noNone, _nbstep=_nbstep + 1, _sb=_sb, omit_attrs=omit_attrs, fct_omit=None)

        if len(self.getNodes()) != 0 or self.hasText():
            _sb.write(pos + '</' + self.getTag() + '>\n')
            if doLBAfterTag: _sb.write('\n')

        if do_lb_befor_tag: _sb.write('\n')

        return _sb

        # A008:

    def printInternalJSON(self, doChild=True, noDft=True, noDftRaise=False, noNone=True, fct_omit=None):
        import json
        founds = self._printInternalJSON(doChild=doChild, noDft=noDft, noDftRaise=noDftRaise, noNone=noNone,
                                         fct_omit=fct_omit)

        return json.dumps(founds)

    # A008:
    def _printInternalJSON(self, doChild=True, noDft=True, noDftRaise=False, noNone=True, fct_omit=None, parent_childs=None):
        """
        Print an JSON represention of this node and its children if doChild is True (default).
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        """
        self_funct = 'printXml'
        if parent_childs==None:parent_childs=[]
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                       self_funct,
                                                                                       'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(
                                                                                           doChild) + '. Type:' + str(
                                                                                           type(doChild)) + '.')
        if not isinstance(noDft, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                     self_funct,
                                                                                     'Bad type for parameter: noDft. Expected type is: bool ! Received:' + str(
                                                                                         noDft) + '. Type:' + str(
                                                                                         type(noDft)) + '.')
        if not isinstance(noNone, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                      self_funct,
                                                                                      'Bad type for parameter: noNone. Expected type is: bool ! Received:' + str(
                                                                                          noNone) + '. Type:' + str(
                                                                                          type(noNone)) + '.')

        childs = []
        tags = {'___tag___': self.getTag(), '___text___': None, '___childs___': childs}
        parent_childs.append(tags)

        # attrs order
        attrs = self.getdAttrs()

        for attr in attrs:
            try:
                if (noDft and self.eqDft(attr, attrs[attr])) or (noNone and attrs[attr] in (None, 'None')): continue
            except:
                if noDftRaise: raise

            tags[attr] = attrs[attr]

        tags['___text___'] = self.getText()

        if doChild:
            l = self.getOrderedNodes()
            for node in l:
                if fct_omit != None:
                    if fct_omit(node): continue

                node._printInternalJSON(doChild=doChild, noDft=noDft, noDftRaise=noDftRaise, noNone=noNone,
                                        fct_omit=None, parent_childs=childs)

        return parent_childs

    def printYAML(self, tok8yaml=True, doChild=True, noDft=True, noDftRaise=False, noNone=True, fct_omit=None, step = 4):
        sb = StringIO()
        import yaml
        if step == None:step = 4

        json = self.printJSON(to_yaml=True, tok8yaml=tok8yaml, doChild=doChild, noDft=noDft, noDftRaise=noDftRaise, noNone=noNone,
                              fct_omit=fct_omit)

        """ Sample read/write:
    import yaml
    import json

    with open('config.json', 'r') as file:
        configuration = json.load(file)

    with open('config.yaml', 'w') as yaml_file:
        yaml.dump(configuration, yaml_file)

    with open('config.yaml', 'r') as yaml_file:
        print(yaml_file.read())

    obj_json = json.loads(source)
    # yaml.safe_dump(obj_json)
    """
        # See: https://stackoverflow.com/questions/8651095/controlling-yaml-serialization-order-in-python
        sb.write(yaml.dump(json, indent=step, allow_unicode=True, default_flow_style=False, sort_keys=False))

        return sb

    # A008:
    def printJSON(self, to_yaml=False, tok8yaml=False, doChild=True, noDft=True, noDftRaise=False, noNone=True, fct_omit=None):
        js_attrs = {}
        founds = {self.getTag(): js_attrs}
        self._printJSON(to_yaml=True, doChild=doChild, noDft=noDft, noDftRaise=noDftRaise, noNone=noNone,
                        fct_omit=fct_omit, js_attrs=js_attrs)

        # if tok8yaml: remove top key:
        if tok8yaml:
            keys = list(founds.keys())
            if len(keys) == 1:
                founds = founds[keys[0]]

        return founds

    # A008:
    def _printJSON(self, to_yaml=False, doChild=True, noDft=True, noDftRaise=False, noNone=True, fct_omit=None,
                   js_attrs=None, force_parent=False):
        """
        Print an JSON represention of this node and its children if doChild is True (default).
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        """
        self_funct = 'printJSON'
        if js_attrs==None:js_attrs={}
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(doChild) + '. Type:' + str(type(doChild)) + '.')
        if not isinstance(noDft, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: noDft. Expected type is: bool ! Received:' + str(noDft) + '. Type:' + str(type(noDft)) + '.')
        if not isinstance(noNone, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct, 'Bad type for parameter: noNone. Expected type is: bool ! Received:' + str(noNone) + '. Type:' + str(type(noNone)) + '.')
        from kwadlib import epicdesc


        isPartial = self.isPartial() # <=> self.getTop().getFileDesc())

        def treat(child_tag, js_attrs, new_js_attrs):
            if child_tag in js_attrs:
                parent_childs = js_attrs[child_tag]
                parent_childs.append(new_js_attrs)
            else:
                parent_childs = []
                js_attrs[child_tag] = parent_childs
                parent_childs.append(new_js_attrs)

        def treatAttrs(node, js_attrs):
            attrdescs = node.getAttrDescs() # A039.1
            # attrs order
            attrs = node.getdAttrs()
            attr_keys = node.getAttrOrders()
            for attr in attr_keys:
                wks = attrdescs[attr]
                try:
                    if (noDft and node.eqDft(attr, attrs[attr])) or (noNone and attrs[attr] in (None, 'None')): continue
                except:
                    if noDftRaise: raise

                # M039.1:
                if attrs[attr] != None:
                    if '*type' in wks and (wks['*type'] in ('list', 'dict')):
                        js_attrs[attr] = str(attrs[attr])
                    else:js_attrs[attr] = attrs[attr]
                elif not noNone:
                    js_attrs[attr] = None

        # M039: becomes a function:
        treatAttrs(self, js_attrs)

        if doChild:
            childs = self.getOrderedNodes()
            parent_tag_desc_childsOfParent = self.peerTagdesc.getChilds()
            for node in childs:
                tag_desc_childsOfChild = node.peerTagdesc.getChilds()
                # node_childs = node.getChilds()
                node_childs = node.getOrderedNodes()

                if fct_omit != None:
                    if fct_omit(node): continue
                new_js_attrs = {}
                text = node.getText()
                text_wk = node.getTextDescWk()

                child_tag = node.getTag()
                tag_wk = node.getTagDescWk()

                # - if tag has text and textDesc is *raw and has no child:True => js_attrs[child_tag] = '\n'.join(self.getText())
                if text != None:
                    if not isPartial and text_wk.__contains__('*raw') and text_wk['*raw'] \
                            and len(tag_desc_childsOfChild) == 0:
                        new_js_attrs[child_tag] = text
                        # A039: Attrs was not already ran on this node:
                        treatAttrs(node, new_js_attrs)

                        # A038:
                        treat(child_tag, js_attrs, new_js_attrs)
                        continue
                    else:
                        new_js_attrs['__text__'] = text


                # Retreives Array properties:
                # Bypass empty tag:
                if to_yaml and len(tag_desc_childsOfChild) == 1:
                    cwks = tag_desc_childsOfChild[0].getTagDescWk()

                    if epicdesc.YAML_AND_HCL_MARK_NEWTAG in cwks and cwks[epicdesc.YAML_AND_HCL_MARK_NEWTAG]:
                        # A039: Attrs was not already ran on this node:
                        new_js_attrs = {} #A039
                        treat(child_tag, js_attrs, new_js_attrs) #A039
                        treatAttrs(node, new_js_attrs) #A039

                        if len(node_childs) == 0:
                            continue

                        for i in range(len(node_childs)):
                            node = node_childs[i]
                            node._printJSON(to_yaml=to_yaml, doChild=doChild, noDft=noDft, noDftRaise=noDftRaise,
                                            noNone=noNone, fct_omit=fct_omit, js_attrs=new_js_attrs, force_parent=True)
                            # D039:
                            if i < len(node_childs)-1:
                                new_js_attrs = {}
                                treat(child_tag, js_attrs, new_js_attrs)
                        continue

                # Retreives properties:
                if not isPartial and ('*le' in tag_wk and tag_wk['*le'] == 1) or ('*eq' in tag_wk and tag_wk['*eq'] == 1):
                    js_attrs[child_tag] = new_js_attrs
                else:
                    treat(child_tag, js_attrs, new_js_attrs)

                node._printJSON(to_yaml=to_yaml, doChild=doChild, noDft=noDft, noDftRaise=noDftRaise, noNone=noNone,
                                fct_omit=fct_omit, js_attrs=new_js_attrs, force_parent=False)

    # A008:
    # def printXml(self, doChild=True, indent='', step=4, doSpaceWrapEq=False, doLBBeforTag=True, doLBAfterTag=True, doLBBeforAttr=False, noDft=True, noDftRaise=False, noNone=True, noComment=False, _nbstep=0, _sb=None, fct_omit=None):
    def printHCL(self, printMode=PRINT_HCL_TERRAFORM, doTerraNames=False, doChild=True, indent='', step=4, noDft=True, noDftRaise=False, noNone=True, fct_omit=None):
        """
        PRINT_HCL_COMPACT = "compact" # if many parents have no attribute and only one target child: they are writen in one line with no {.
        e.g.: spec containers container {...} intead of spec = { containers = { container {...}}}
        PRINT_HCL_TERRAFORM = "notcompact" # as expected by TerraForm
        PRINT_HCL_NOTCOMPACT = "notcompact"

        doTerraNames: Convert tags and Attributes names as expected by Terra.
        """
        js_attrs = {}
        terra_names = {}
        founds = {epicbase.convertTerra(self.getTag(), doTerraNames=doTerraNames, terra_names=terra_names): js_attrs}
        self._printJSON(doChild=doChild, noDft=noDft, noDftRaise=noDftRaise, noNone=noNone, fct_omit=fct_omit, js_attrs=js_attrs)
        _sb = StringIO()

        if printMode==PRINT_HCL_COMPACT:
            terra_names = self._printHCLCompact(doTerraNames=doTerraNames, isFirstNode=True, doChild=doChild, indent=indent, step=step, noDft=noDft, noDftRaise=noDftRaise,
                           noNone=noNone, fct_omit=fct_omit, js_attrs=js_attrs, _sb=_sb, _terra_names=terra_names)
        else:
            terra_names = self._printHCL(doTerraNames=doTerraNames, isFirstNode=True, doChild=doChild, indent=indent, step=step, noDft=noDft, noDftRaise=noDftRaise,
                           noNone=noNone, fct_omit=fct_omit, js_attrs=js_attrs, _sb=_sb, _terra_names=terra_names)

        return _sb

    def _printHCL(self, doTerraNames=False, isFirstNode=False, doChild=True, isInList=False, indent='', step=4, noDft=True, noDftRaise=False, noNone=True,
                  fct_omit=None, js_attrs=None, isTagList=None, tag_list_name=None,
                  tag_list_parent=None, _nbstep=1, _sb=None, _terra_names = None):
        """
        Print an JSON represention of this node and its children if doChild is True (default).
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        """
        self_funct = 'printHCL'
        if js_attrs == None: js_attrs = {}
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,self_funct,'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(doChild) + '. Type:' + str(type(doChild)) + '.')
        if not isinstance(indent, str) and not indent.isspace(): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,'Bad type for parameter: indent. Expected type is: a blank str ! Received:' + str(indent) + '. Type:' + str(type(indent)) + '.')
        if not isinstance(step, int): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,'Bad type for parameter: step. Expected type is: int ! Received:' + str(step) + '. Type:' + str(type(step)) + '.')
        if not isinstance(noDft, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,self_funct,'Bad type for parameter: noDft. Expected type is: bool ! Received:' + str(noDft) + '. Type:' + str(type(noDft)) + '.')
        if not isinstance(noNone, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,self_funct,'Bad type for parameter: noNone. Expected type is: bool ! Received:' + str(noNone) + '. Type:' + str(type(noNone)) + '.')
        if doTerraNames and _terra_names == None: _terra_names = {}
        quote = '"'

        postag = indent + (_nbstep - 1) * step * ' '
        posattr = indent + _nbstep * step * ' '

        hasYHSingleListedChild = False
        if not isFirstNode and self.hasYHSingleListedChild() and not isInList:
            hasYHSingleListedChild = True
            _sb.write('\n' + postag + epicbase.convertTerra(self.getTag(), doTerraNames=doTerraNames, terra_names=_terra_names) + ' = [')
            doEnd = "]"
        elif not isFirstNode and isInList:
            _sb.write('\n' + postag + ' {')
            doEnd = "}"
        else:
            _sb.write('\n' + postag + epicbase.convertTerra(self.getTag(), doTerraNames=doTerraNames, terra_names=_terra_names) + ' = {')
            doEnd = "}"

        # attrs:
        nbdict = 0
        hasAttr = False
        attr_keys = list(js_attrs.keys())
        for attr in attr_keys:
            value = js_attrs[attr]

            hasnode = self.hasNode(attr)
            if (isinstance(value, list) and hasnode) or \
                    (isinstance(value, dict) and hasnode):
                if (isinstance(value, dict) and hasnode): nbdict += 1
                continue

            if isinstance(value, str):
                if value.find('"') >= 0: value.replace('"', '\"')
                value = quote + str(value) + quote
            elif isinstance(value, list):
                value = str(value)
                if value.find('"') >= 0: value.replace('"', '\"')
                value = str(value).replace("'", quote)
            elif isinstance(value, dict):
                value = str(value)
                if value.find('"') >= 0: value.replace('"', '\"')
                value = str(value).replace("'", quote)

            # attr:
            _sb.write('\n' + posattr)
            _sb.write(epicbase.convertTerra(attr, doTerraNames=doTerraNames, terra_names=_terra_names) + ' = ' + str(value))

        # Treat tag dict only:
        for attr in attr_keys:
            dvalue = js_attrs[attr]
            if not (isinstance(dvalue, dict) and self.hasNode(attr)):
                continue

            self.getNode(attr)[0]._printHCL(doTerraNames=doTerraNames, doChild=doChild, isInList=False, indent=indent, step=step, noDft=noDft,
                noDftRaise=noDftRaise, noNone=noNone, fct_omit=fct_omit, js_attrs=dvalue, isTagList=False, tag_list_name=tag_list_name,
                tag_list_parent=tag_list_parent,_nbstep=_nbstep + 1, _sb=_sb, _terra_names=_terra_names)

        # Treat tag list only/and hcl long Name representation (isTagList = True):
        firstime = True
        for ltag in attr_keys:
            lvalue = js_attrs[ltag]
            if not (isinstance(lvalue, list) and self.hasNode(ltag)):
                continue

            # hasParentDictWithAttr and isTagList: List Normal JSON representation:
            if len(lvalue) > 0:
                isInList = hasYHSingleListedChild
                for i in range(len(lvalue)):
                    if isInList and not firstime: _sb.write(',')
                    firstime = False
                    dvalue = lvalue[i]

                    self.getNode(ltag)[i]._printHCL(doTerraNames=doTerraNames, doChild=doChild, isInList=isInList, indent=indent, step=step, noDft=noDft, noDftRaise=noDftRaise, noNone=noNone, fct_omit=fct_omit,
                        js_attrs=dvalue, isTagList=True, tag_list_name=tag_list_name, tag_list_parent=tag_list_parent, _nbstep=_nbstep + 1, _sb=_sb, _terra_names=_terra_names)

        if doEnd: _sb.write('\n' + postag + doEnd)

        return _terra_names

    def hasYHSingleListedChild(self):
        p = self.peerTagdesc
        if p == None:return False
        return p.hasYHSingleListedChild()

    # A008:
    def _printHCLCompact(self, doTerraNames=False, isFirstNode=False, doChild=True, indent='', step=4, noDft=True, noDftRaise=False, noNone=True,
                  fct_omit=None, js_attrs=None, isTagList=None, hasParentDictWithAttr=False, tag_list_name=None,
                  tag_list_parent=None, _nbstep=1, _sb=None, _terra_names = None):
        """
        Print an JSON represention of this node and its children if doChild is True (default).
        doChild (bool) : if doChild is True inner subtree nodes are also printed, otherwise only this node is printed.
        """
        self_funct = 'printHCL'
        if js_attrs == None: js_attrs = {}
        if not isinstance(doChild, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                       self_funct,
                                                                                       'Bad type for parameter: doChild. Expected type is: bool ! Received:' + str(
                                                                                           doChild) + '. Type:' + str(
                                                                                           type(doChild)) + '.')
        if not isinstance(indent, str) and not indent.isspace(): raise epicxception.epicxmlParameterException(
            self.__class__.__name__, self_funct,
            'Bad type for parameter: indent. Expected type is: a blank str ! Received:' + str(indent) + '. Type:' + str(
                type(indent)) + '.')
        if not isinstance(step, int): raise epicxception.epicxmlParameterException(self.__class__.__name__, self_funct,
                                                                                   'Bad type for parameter: step. Expected type is: int ! Received:' + str(
                                                                                       step) + '. Type:' + str(
                                                                                       type(step)) + '.')
        if not isinstance(noDft, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                     self_funct,
                                                                                     'Bad type for parameter: noDft. Expected type is: bool ! Received:' + str(
                                                                                         noDft) + '. Type:' + str(
                                                                                         type(noDft)) + '.')
        if not isinstance(noNone, bool): raise epicxception.epicxmlParameterException(self.__class__.__name__,
                                                                                      self_funct,
                                                                                      'Bad type for parameter: noNone. Expected type is: bool ! Received:' + str(
                                                                                          noNone) + '. Type:' + str(
                                                                                          type(noNone)) + '.')
        if doTerraNames and _terra_names == None: _terra_names = {}
        hasChildDictWithAttr = False
        doEnd = False
        quote = '"'

        def clearTagList():
            nonlocal tag_list_name
            nonlocal tag_list_parent
            tag_list_parent = self
            tag_list_name = ''

        if tag_list_parent == None: clearTagList()
        if tag_list_name == '':
            tag_list_name = self.getTag()
        else:
            tag_list_name += ' ' + self.getTag()

        if isTagList:
            if hasParentDictWithAttr:
                hcl_tag_name = self.getTag()
                # _nbstep -= len(tag_list_name.split()) - 1
            else:
                if tag_list_name in (None, ''):
                    hcl_tag_name = self.getTag()
                else:
                    hcl_tag_name = tag_list_name
                _nbstep -= len(hcl_tag_name.split()) - 1
                ## filiations = tag_list_parent.getFiliation(asList=True)
            clearTagList()

        else:
            hcl_tag_name = self.getTag()
            ## filiations = self.getFiliation(asList=True)

        ## _nbstep = len(filiations)
        postag = indent + (_nbstep - 1) * step * ' '
        posattr = indent + _nbstep * step * ' '

        if isFirstNode:
            _sb.write('\n' + postag + epicbase.convertTerra(self.getTag(), doTerraNames=doTerraNames, terra_names=_terra_names) + ' {')
        # hasParentDictWithAttr and isTagList: List Normal JSON representation:
        elif hasParentDictWithAttr and isTagList:
            doEnd = True
            _sb.write('\n' + postag + '{')
        elif hasParentDictWithAttr and not isTagList:
            doEnd = True
            _sb.write('\n' + postag + epicbase.convertTerra(hcl_tag_name, doTerraNames=doTerraNames, terra_names=_terra_names) + ' = {')
        # not hasParentDictWithAttr and isTagList: Long Name hcl representation:
        elif isTagList:
            doEnd = True
            _sb.write('\n' + postag + epicbase.convertTerra(hcl_tag_name, doTerraNames=doTerraNames, terra_names=_terra_names) + ' {')

        # attrs:
        nbdict = 0
        hasAttr = False
        attr_keys = list(js_attrs.keys())
        for attr in attr_keys:
            value = js_attrs[attr]

            if (isinstance(value, list) and self.hasNode(attr)) or \
                    (isinstance(value, dict) and self.hasNode(attr)):
                if (isinstance(value, dict) and self.hasNode(attr)): nbdict += 1
                continue

            if isinstance(value, str):
                if value.find('"') >= 0: value.replace('"', '\"')
                value = quote + str(value) + quote
            elif isinstance(value, list):
                value = str(value)
                if value.find('"') >= 0: value.replace('"', '\"')
                value = str(value).replace("'", quote)
            elif isinstance(value, dict):
                value = str(value)
                if value.find('"') >= 0: value.replace('"', '\"')
                value = str(value).replace("'", quote)

            # tag:
            if not hasAttr:  # Firstime
                hasAttr = True
                tag_wk = self.getTagDescWk()
                """ The following two tags stands to manage weird hcl list represention:
                - if hcl finds many properties with no Attribute ending by one list, it representes the list like this:
                List long Name represention:  
                spec containers container { <------
                    image = "mysql"
                    name = "mysql"
                    env envi {
                        name = "MYSQL_ROOT_PASSWORD"
                        value = "rootpasswd"
                    }
                    volumeMounts volumeMount { <------
                        mountPath = "/var/lib/mysql"
                        name = "site-data"
                        subPath = "mysql"
                    }
                    volumeMounts volumeMount {
                        mountPath = "/opt/myotherlib"
                        name = "site-data"
                        subPath = "otherlib"
                    }
                }
                - if at list one parent of the list had attrs it represents the list as classical JSON:
                List JSON represention:
                httpHeaders = {
                    httpHeader = [
                        {
                        name = "X-Custom-Header"
                        value = "Awesome"
                        },
                        {
                        name = "X-Custom-Header2"
                        value = "Awesome2"
                        }
                    ]
                }
                Flag hasParentDictWithAttr: stands for detecting if a parent in the list filiation had any attrs.
                Flag isTagList: stands for a list found either with parents with attrs or not.
                """
                # Detects dict properties not dict in list:
                if not isFirstNode and (
                        ('*le' in tag_wk and tag_wk['*le'] == 1) or ('*eq' in tag_wk and tag_wk['*eq'] == 1)):
                    hasParentDictWithAttr = True
                clearTagList()
                if not doEnd and not isFirstNode: _sb.write('\n' + postag + epicbase.convertTerra(hcl_tag_name, doTerraNames=doTerraNames, terra_names=_terra_names) + ' = {')
                doEnd = True

            # attr:
            _sb.write('\n' + posattr)
            _sb.write(epicbase.convertTerra(attr, doTerraNames=doTerraNames, terra_names=_terra_names) + ' = ' + str(value))

        # Treat tag dict only:
        for attr in attr_keys:
            dvalue = js_attrs[attr]
            if not (isinstance(dvalue, dict) and self.hasNode(attr)):
                continue

            self.getNode(attr)[0]._printHCLCompact(doTerraNames=doTerraNames, doChild=doChild, indent=indent, step=step, noDft=noDft,
                                            noDftRaise=noDftRaise, noNone=noNone, fct_omit=fct_omit, js_attrs=dvalue,
                                            isTagList=False, hasParentDictWithAttr=hasParentDictWithAttr,
                                            tag_list_name=tag_list_name, tag_list_parent=tag_list_parent,
                                            _nbstep=_nbstep + 1, _sb=_sb, _terra_names=_terra_names)

        # Treat tag list only/and hcl long Name representation (isTagList = True):
        firstime = True
        for ltag in attr_keys:
            lvalue = js_attrs[ltag]
            if not (isinstance(lvalue, list) and self.hasNode(ltag)):
                continue

            # hasParentDictWithAttr and isTagList: List Normal JSON representation:
            if len(lvalue) > 0:
                if hasParentDictWithAttr: _sb.write('\n' + postag + step * ' ' + ltag + ' = [')
                for i in range(len(lvalue)):
                    if hasParentDictWithAttr and not firstime: _sb.write(',')
                    firstime = False
                    dvalue = lvalue[i]

                    self.getNode(ltag)[i]._printHCLCompact(doTerraNames=doTerraNames, doChild=doChild, indent=indent, step=step, noDft=noDft,
                                                    noDftRaise=noDftRaise, noNone=noNone, fct_omit=fct_omit,
                                                    js_attrs=dvalue, isTagList=True,
                                                    hasParentDictWithAttr=hasParentDictWithAttr,
                                                    tag_list_name=tag_list_name, tag_list_parent=tag_list_parent,
                                                    _nbstep=_nbstep + 1, _sb=_sb, _terra_names=_terra_names)

                if hasParentDictWithAttr: _sb.write('\n' + postag + step * ' ' + ']')

        if doEnd: _sb.write('\n' + postag + '}')

        return _terra_names

    def show(self, sb=None, **print_keywords):
        """ Facade for Repository """
        if sb == None: sb = StringIO()

        return self.printXml(_sb=sb, **print_keywords)

    def parseJSON(self, tag, json, force=False, from_yaml=False, from_hcl=False, clasIsSoftClassNode=False):
        selfMethod = 'parseJSON'
        fs = self.getTop().getFileUser()
        if fs:
            prefix = 'Parsing file: %s, ' % fs
        else:
            prefix = ''
        prefix = prefix + 'At tag: %s>' % '.'.join(self.getFiliation().split('/')[1:])
        if from_yaml and from_hcl: raise epicxception.epicxmlParameterException('Node', selfMethod, prefix + 'from_yaml and from_hcl cannot be True together !')
        if not isinstance(json, dict): raise epicxception.epicxmlParameterException('Node', selfMethod, prefix + 'At this step: %s, value must be a dict ! Found: %s' % (self.getTag(), json))
        keys = list(json.keys())
        attrs = {}
        dchilds = {}  # dict means unique
        lchilds = {}  # list means multiple

        # Dispatch Attrs:
        # ---------------
        # tag is a child of self:
        fil = self.getFiliation() + epicbase.TAG_SEP + str(tag)

        try: # A043:
            peer_desc = self.getPeerTagdesc(fil) # A043:
        except: # A043: Adding Recursive __Link__ management (future desc cannot be anticipated):
            # Detect recursive __Link__ tags:
            # If Recursive Nodes created by __link__ => listNodeBases is list of Link not of TagDesc !
            desc_childs = {o.getName():o for o in self.peerTagdesc.listNodeBases}
            descQuickTuns = self.peerTagdesc.getTop()._getQuickTuns()
            from kwadlib.epicdesc import Lnk
            found = False

            if tag in desc_childs and isinstance(desc_childs[tag], Lnk):
                for tun in descQuickTuns:
                    if tag == tun.split(epicbase.TAG_SEP)[-1]:
                        peer_desc = descQuickTuns[tun]
                        found = True
                if not found:raise

                descQuickTuns[self.getFiliation() + epicbase.TAG_SEP + str(tag)] = peer_desc
            else:
                raise

        # M043: attr_descs = self.getPeerTagdesc(fil).getDescs()
        attr_descs = peer_desc.getDescs()
        tag_childs = [c.getName() for c in peer_desc.listNodeBases] # A043:
        _text_ = None

        for key in keys:
            value = json[key]
            if not key in attr_descs and (isinstance(value, dict) or isinstance(value, list)): continue
            if key == '__text__':
                _text_ = value
                continue
            attrs[key] = value

        # special parameter force: preserv attr:
        if 'force' in attrs:
            vforce = attrs['force']
            del attrs['force']

        nn = self.newNode(tag, checkDefault=False, force=force, clasIsSoftClassNode=clasIsSoftClassNode, **attrs)
        # special parameter force: preserv attr:
        if 'force' in keys:nn.setAttr('force', vforce)
        
        if _text_!=None:nn.setText(_text_.split(','))

        # Dispatch dict/list:
        # -------------------
        for key in keys:
            if key in attr_descs: continue
            value = json[key]

            # dchilds:
            if isinstance(value, dict):
                dchilds[key] = dict(value)
                continue

            # A043: The python yaml module: groups tag by name even if they are multiple different child tags.
            # => a list always contains the same tag.
            # And here we treat xml tags with multi child (not treated by: checkIsListOfDict):
            elif isinstance(value, list) and not peer_desc.isPartial() and len(tag_childs)>1:
                for v in value:
                    nn.parseJSON(key, v, force=force, from_yaml=from_yaml, from_hcl=from_hcl)
                continue

            # attrs:
            if isinstance(value, list):
                found_attrs, a, b = nn._checkIsListOfDict(key, value, prefix, from_yaml=from_yaml, from_hcl=from_hcl)
                if a and b: raise epicxception.epicxmlParameterException('Node', selfMethod,
                                                                         prefix + 'At this step: %s, found a list of mixup value of dict and type ! In a JSON list if there is one dict all the other entry must also be dict.' % self.getTag())
                if a:  # lchilds:
                    if key in lchilds:
                        lchilds[key].extend(found_attrs)
                    else:
                        lchilds[key] = list(found_attrs)
                    continue
                else:
                    wks = nn.getAttrDescs()
                    if key in wks and '*ltype' in wks and wks['*ltype'] == 'str':
                        value = [str(v) for v in value]

                    nn.setAttr(key, value)
                    continue

        newkeys = list(dchilds.keys())  # dict means unique
        for newtag in newkeys:
            nn.parseJSON(newtag, dchilds[newtag], force=force, from_yaml=from_yaml, from_hcl=from_hcl)

        newkeys = list(lchilds.keys())  # list means multiple instances for same tag
        for newattr in newkeys:
            ll = lchilds[newattr]
            nn2 = nn.newNode(newattr, checkDefault=False, force=force, clasIsSoftClassNode=clasIsSoftClassNode)
            ## else:nn2 = nn

            for l in ll:
                newtag, dct = l
                nn2.parseJSON(newtag, dct, force=force, from_yaml=from_yaml, from_hcl=from_hcl)

    def _checkIsListOfDict(self, attr, listattrs, prefix, from_yaml=False, from_hcl=False):
        selfMethod = '_checkIsListOfDict'
        prefix += 'Checking Attribute: %s> ' % attr
        found_one_dict = False
        found_other = False
        found_attrs = []

        import json

        for dct in listattrs:
            if isinstance(dct, dict):
                found_one_dict = True

                if from_yaml or from_hcl:
                    # Gess Tag from parent desc's unique child:
                    fil = self.getFiliation() + epicbase.TAG_SEP + str(attr)
                    desc = self.getPeerTagdesc(fil)
                    # Guess New Tag:
                    # - has descriptor:
                    if not desc.isPartial():
                        desc_childs = desc.getChilds()
                        if len(desc_childs) == 0:continue
                        elif len(desc_childs) != 1:
                            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, prefix + 'New Tag Guessing> This tag s descriptor should contains one unique child ! Found multiple childs: %s on the descriptor for this tag: %s.' % (', '.join(list(map(lambda c: c.name, desc_childs))), fil))
                        newtag = desc_childs[0].name
                        """
                        if newtag.lower != attr.lower:
                            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,  'New Tag Guessing> The New tag name: %s (found from the unique node child descriptor) dont match the Attribute name: %s' % ( newtag, dct))
                        """
                    # - has no descriptor:
                    else:
                        if not attr.endswith('s'):
                            newtag = attr[:-1]
                        else:
                            newtag = attr[:-1] + 'i'

                    found_attrs.append((newtag, dct))

                else:  # len(value) == 1:
                    if len(dct) != 1: raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                        prefix + 'New Tag Guessing> Found at least one dict in list of length different than one entry ! Found dict is: %s.' % json.dumps(dct))
                    newtag = list(dct.keys()[0])
                    if not isinstance(dct[newtag], dict):
                        raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                            prefix + 'New Tag Guessing> The key: %s in dict should be of type dict ! Found dict is: %s.' % (newtag, json.dumps(dct)))

                    found_attrs.append((newtag, dct))

            else:
                found_other = True
                continue

        return found_attrs, found_one_dict, found_other


    @staticmethod
    def parseK8SOpenApiToDesc(node, tagOrAttr, json, first_tag, category, software, temp_dir=None, deploy=False, isNewSoftClass=False, required=False, fdhelp=None, verbose=0):
        selfMethod = 'parseK8SOpenApiToDesc'
        s = '.'.join(node.getFiliation().split('/')[1:]) + '.' + tagOrAttr
        if s == '': s = tagOrAttr
        prefix = 'At tag: %s>' % s + ': '
        """
        NEWTAG UNIQUE CHILD INSTANCE :
        ------------------------------
        "spec": {
            "description": "PodSpec is a description of a pod.",
            "properties": {  <========= NEWTAG (spec)
                ...
            }
            "required": [
                "apiVersion",
                "kind",
                "name",
                "uid",
                "containers"  : PR SES CHILD ATTRS, DC C LE PERE DE SPEC QUI DIT S'IL EST REQUIS
            ],
            "type": [
                "object",  <=============== REQUIS
                "null"
            ],
            "additionalProperties": false
        },
        """
        import json as jsonmod
        description = json['description'] if json.__contains__('description') else None
        if description == 'null': description = None
        properties = json['properties'] if json.__contains__('properties') else None
        if properties == 'null': properties = None
        items = json['items'] if json.__contains__('items') else None
        if items == 'null': items = None
        additionalProperties = json['additionalProperties'] if json.__contains__('additionalProperties') else False
        if additionalProperties in ('false', 'null'): additionalProperties = False
        requireds = json['required'] if json.__contains__('required') else []
        if requireds == 'null': required = []
        type = json['type'] if json.__contains__('type') else None
        if type == 'null': type = None
        format = json['format'] if json.__contains__('format') else None
        if format == 'null': format = None
        enum = json['enum'] if json.__contains__('enum') else None
        if enum == 'null': enum = None
        oneOf = json['oneOf'] if json.__contains__('oneOf') else None
        if oneOf == 'null': oneOf = None
        # Useless: from kwadlib.epicdesc import YAML_AND_HCL_MARK_NEWTAG

        if description != None:
            wkhelp, wklhelp, fdhelp = Node.pk8SMakeHelp(node, tagOrAttr, description, first_tag, category, software, temp_dir=temp_dir, deploy=deploy, isNewSoftClass=isNewSoftClass, fdhelp=fdhelp)
            isNewSoftClass = False
        else:
            wkhelp = None
            wklhelp = None

        # Mutual exclusives: properties=None, items=None, additionalProperties
        # parseK8SOpenApiToDesc(node, json, description=None, properties=None, items=None, additionalProperties=False, required=None, type=None):
        if (properties, items, additionalProperties) == (None, None, False):
            pass
        else:
            l = [properties != None, items != None, additionalProperties != False]
            l.sort()
            if l != [False, False, True]: raise epicxception.epicxmlParameterException('Node', selfMethod,
                prefix + 'Parameter error for: properties, items, additionalProperties. Only one of: properties, items, additionalProperties can be provided received:\n   properties: %s\n   items: %s\n   additionalProperties: %s !\nPartial json is: %s' % (jsonmod.dumps(properties), jsonmod.dumps(items), jsonmod.dumps(additionalProperties), jsonmod.dumps(json)))

        if type != None and oneOf != None:
            raise epicxception.epicxmlSystemException('Node', selfMethod, prefix + 'When oneOf is provided type cannot !\nReceived type: %s\nReceived oneOf: %s!\nPartial json is: %s' % (jsonmod.dumps(type), jsonmod.dumps(oneOf), jsonmod.dumps(json)))
        wk = Node.pk8SGetWk(tagOrAttr, type, prefix, json, format=format, additionalProperties=additionalProperties, enum=enum, oneOf=oneOf)

        # This a base attr type:
        if oneOf != None or additionalProperties:
            if required: wk['*required'] = True
            node.setAttr(tagOrAttr, wk)
            return fdhelp

        if wk != 'object':
            if required: wk['*required'] = True
            if wk.__contains__('*type') and wk['*type'] == 'list' and items == None:
                raise epicxception.epicxmlSystemException('Node', selfMethod,
                    prefix + 'items is required when type is Array ! Received type: %s!\nPartial json is: %s' % (jsonmod.dumps(type), jsonmod.dumps(json)))
            elif items != None and (not wk.__contains__('*type') or wk['*type'] != 'list'):
                raise epicxception.epicxmlSystemException('Node', selfMethod,
                    prefix + 'When items is provided type must be Array !\nReceived type: %s\nReceived items: %s!\nPartial json is: %s' % (jsonmod.dumps(type), jsonmod.dumps(items), jsonmod.dumps(json)))

            if wkhelp != None:
                wk['*help'] = wkhelp
                wk['*lhelp'] = wklhelp

            if items != None:
                # This a base attr type:
                if items.__contains__('type') and (
                not (items['type'] == 'object' or (isinstance(items['type'], list) and items['type'][0] == 'object'))):
                    _wk = Node.pk8SGetWk(tagOrAttr, items['type'], prefix, json,
                                         format=items['format'] if items.__contains__('format') else None)
                    wk['*ltype'] = {'*type': _wk['*type']}
                    node.setAttr(tagOrAttr, wk)
                    return fdhelp
                elif items.__contains__('type') and (items['type'] == 'object' or (
                        isinstance(items['type'], list) and items['type'][0] == 'object')):
                    if not items.__contains__('properties'): raise epicxception.epicxmlSystemException('Node',
                        selfMethod, prefix + 'Unsupported items of type: object, Should have a key properties ! Received items: %s\nPartial json is: %s' % (jsonmod.dumps(items), jsonmod.dumps(json)))
                    wk = 'object'
                else:
                    raise epicxception.epicxmlSystemException('Node', selfMethod, prefix + 'Unsupported items type !\nPartial json is: %s' % jsonmod.dumps(json))
            else:
                # This a base attr type:
                node.setAttr(tagOrAttr, wk)
                return fdhelp

        """
        if wk == 'object' and (properties==None and items==None):
            raise epicxception.epicxmlSystemException('Node', selfMethod, prefix + 'Type object, is only expected with properties or items !\nPartial json is: %s' % jsonmod.dumps(json))
        """

        if properties != None:
            wk = {'*le': 1}
            attrs = properties
        elif items != None:
            wk = {}
            attrs = items['properties']
        else:
            wk = {'*type': 'str', '*raw': True, '*le': 1}

        if wkhelp != None:
            wk['*help'] = wkhelp
            wk['*lhelp'] = wklhelp
        if required: wk['*eq'] = 1

        if properties != None:  # Single Child Tag one instance
            newnode = node.newNode(tagOrAttr, checkDefault=False)
            newnode.setAttr('__wk__', wk)
        elif items != None:  # Single Child Tag Xtiple instance (with items)
            if tagOrAttr.endswith('s'):
                n = tagOrAttr[:-1]
            else:
                n = tagOrAttr + 'i'
            nn = node.newNode(tagOrAttr, checkDefault=False)
            # A017
            wk['*le'] = 1
            nn.setAttr('__wk__', wk)
            newnode = nn.newNode(n, checkDefault=False)
            # Mark this one as new artefact, should be destroy reversing back to yaml: Now it is dynamic in standard in epicxmlp parser throught: worktext.
            # Useless: newnode.setAttr('__wk__', {YAML_AND_HCL_MARK_NEWTAG: True})
        else:
            from . import ct
            newnode = node.newNode(tagOrAttr, checkDefault=False)
            newnode._setText(['__wk__=' + ct.unDress(wk)])
            return fdhelp

        keys = list(attrs.keys())
        for attr in keys:
            if not Node.pk8SCheckTagAndAttrName(node, attr, prefix): continue
            if attr in requireds:
                required = True
            else:
                required = False
            # parseK8SOpenApiToDesc(node, tagOrAttr, json, first_tag, software, category, temp_dir=None, deploy=False, required=False, fdhelp=None):
            fdhelp = Node.parseK8SOpenApiToDesc(newnode, attr, attrs[attr], first_tag, category, software, temp_dir=temp_dir, deploy=deploy, isNewSoftClass=isNewSoftClass, required=required, fdhelp=fdhelp, verbose=verbose)

        return fdhelp

    @staticmethod
    def pk8SMakeHelp(node, attr, help, first_tag, category, software, temp_dir=None, deploy=False, isNewSoftClass=False, fdhelp=None):
        selfMethod = 'pk8SMakeHelp'
        """ e.g.:
        # -------------#
        # General help #
        # -------------#


        # -----------------------#
        # SoftClass sys.mkdirs help #
        # -----------------------#

        mkdirs.allow_remove.help = Do remove on Kwad/Remove operation.
        mkdirs.allow_remove.lhelp = Do remove on Kwad/Remove operation.\
        System resources wont be removed, on Kwad remove operation,\
        except when allow_remove is true.
        """

        from kwadlib.tools import genHelp
        wkhelp, wklhelp, fdhelp = genHelp(category, software, first_tag, node.getFiliation().replace(epicbase.TAG_SEP, '.')[1:], attr, help.strip().split('.')[0], help, temp_dir, lang='en', deploy=deploy, isNewSoftClass=isNewSoftClass, deleteFile=True, _fdhelp=fdhelp)

        return wkhelp, wklhelp, fdhelp

    @staticmethod
    def pk8SCheckTagAndAttrName(node, tagOrAttr, prefix):
        FORBID_CHARS = ('.', '-', '&', '@')
        for char in FORBID_CHARS:
            if tagOrAttr.__contains__(char):
                print(prefix + 'Except unsupported Tag or Attribute name:: %s !' % tagOrAttr)
                return False
        return True

    @staticmethod
    def pk8SGetWk(attr, type, prefix, json, format=None, additionalProperties=False, enum=None, oneOf=None):
        selfMethod = 'pk8SGetWk'
        prefix += 'Attribute: %s' % attr + ': '
        """
        "additionalProperties": {
          "oneOf": [
            {
              "type": [
                "string",
                "null"
              ]
            },
            {
              "type": [
                "number",
                "null"
              ]
            }
          ]
        },
        """
        import json as jsonmod
        wk = {}

        # additionalProperties:
        if additionalProperties:
            wk['*type'] = 'dict'
            return wk

        # oneOf:
        if oneOf != None:
            wk['*type'] = 'str'
            return wk

        # type & default:
        dft = None
        if isinstance(type, str):
            _type = type
        elif len(type) != 2:
            raise epicxception.epicxmlSystemException('Node', selfMethod,
                                                      prefix + 'Unexpected type:%s ! Must be a list of size 2 !\nPartial json is: %s' % (
                                                      jsonmod.dumps(type), jsonmod.dumps(json)))
        else:
            _type = type[0]
            dft = type[1]
            if dft == 'null': dft = None
            if dft != None: wk['*value'] = dft

        # enum:
        """
        "kind": {
          "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
          "type": [
            "string",
            "null"
          ],
          "enum": [
            "Deployment"
          ]
        },
        """
        if enum != None:
            wk['*checkIn'] = list(enum)
            if len(enum) == 1:
                wk['*required'] = True
                if dft != None:
                    wk['*value'] = enum[0]

        if _type == "string" and format == 'date-time':
            wk['*ts'] = None
        else:
            if _type == "object":
                return 'object'
            elif _type == "string":
                _type = "str"
            elif _type == "string" and format == 'date-time':
                _type = "ts"
            elif _type in ("integer", "number"):
                _type = 'int'
            elif _type == "boolean":
                _type = 'bool'
            elif _type == "array":
                _type = 'list'
            else:
                raise epicxception.epicxmlSystemException('Node', selfMethod,
                                                          prefix + 'Unsupported type: %s\nPartial json is: %s' % (
                                                          jsonmod.dumps(_type), jsonmod.dumps(json)))

            wk['*type'] = _type

        return wk

    # ---------------- #
    # EpicXql methods #
    # --------------- #

    def getdNode(self, doHelp=False, doTun=False):
        """
        {*TAG:NAME,ATTR1:VALUE1,ATTR2:VALUE1,ATTR3:VALUE1,*TEXT:[TEXT,]}
        """
        dct = self.getdAttrs()
        dct['*TAG'] = self.getName()
        text = self.getText()
        if text != None: dct['*TEXT'] = text
        dct['*HELPS'] = ''
        if doHelp and self.peerTagdesc != None: dct['*HELPS'] = self.peerTagdesc.attrHelps
        if doTun: dct['*TUN'] = self.getTun()

        return dct

    def getRdNode(self, doHelp=False, doTun=False):
        """
        Return itself and its childs list below itself.
        {*TAG:NAME,ATTR1:VALUE1,ATTR2:VALUE1,ATTR3:VALUE1,*TEXT:TEXT,*CHILDS:[*TAG:NAME,...]}
        """
        dct = self.getdNode(doHelp=doHelp, doTun=doTun)
        childs = []

        _l = self.getChilds()
        for child in _l:
            childs.append(child.getRdNode(doHelp=doHelp, doTun=doTun))

        if childs != []: dct['*CHILDS'] = childs

        return dct

    def setRdNode(self, rdnode, sb=None, space=0, newnodes=None):
        """
        Set the childs list below itself.
        {*TAG:NAME,ATTR1:VALUE1,ATTR2:VALUE1,ATTR3:VALUE1,*TEXT:TEXT,*CHILDS:[*TAG:NAME,...]}
        """
        selfMethod = 'setRdNode'
        if newnodes == None: newnodes=[]
        try:
            ## Avoid recursives exceptions in this recursive method.
            self.__setRdNode(rdnode, sb=sb, space=space, newnodes=newnodes)
        except:
            import sys
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                      'Error creating a Node on parent Node:' + self.getFiliation() + ' *tun:' + self.getTun() + '. Rtag should have this shape:[{*TAG:NAME,ATTR1:VALUE1,ATTR2:VALUE1,ATTR3:VALUE1,*TEXT:TEXT,*CHILDS:[*TAG:NAME,...]}]. SubException is:' + str(
                                                          sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + '.')

    def __setRdNode(self, rdnode, sb=None, space=0, newnodes=None):
        selfMethod = 'setRdNodes'
        if newnodes==None:newnodes = []
        if not isinstance(rdnode, dict): raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                                   "Received Incorect value received for rdnode:" + str(
                                                                                       rdnode) + '. Rdnode should be a dict. Your rdnode:' + str(
                                                                                       rdnode) + '.')
        if sb != None:
            if not isinstance(sb, StringIO): raise epicxception.epicxmlParameterTypeException(self.__class__.__name__,
                                                                                              selfMethod, 'sb',
                                                                                              'StringIO', str(sb))
        if not isinstance(space, int): raise epicxception.epicxmlParameterTypeException(self.__class__.__name__,
                                                                                        selfMethod, 'space', 'int',
                                                                                        str(space))

        if self.isCapSensitive():
            _rdnode = dict(rdnode)
        else:
            _rdnode = {}
            for attr in rdnode:
                _rdnode[attr.upper()] = rdnode[attr]

        if self.isCapSensitive():
            tag = rdnode['*TAG']
        else:
            tag = _rdnode['*TAG'].capitalize()

        del _rdnode['*TAG']

        node = self.makeDefaultNode(tag, clasIsSoftClassNode=False)
        newnodes.append(node)
        if sb != None: sb.write(
            ' ' * space + 'Creating Node:' + node.getName() + ' *tun:' + node.getTun() + ', on Node:' + self.getFiliation() + '.\n')

        if '*TEXT' in _rdnode:
            text = _rdnode['*TEXT']
            del _rdnode['*TEXT']
            node.setText(text)

        childs = []
        if '*CHILDS' in _rdnode:
            childs = _rdnode['*CHILDS']
            del _rdnode['*CHILDS']

        node.setAttrs(_update=True, **_rdnode)

        for child in childs:
            if sb != None: sb.write('\n')
            node.setRdNode(child, sb=sb, space=space + 4, newnodes=newnodes)

    def getXml(self, spaces='', doHelp=True):
        #      <tag3 attr1="value10" attr3="value30">
        #          some texte
        #          <tag4 attr1="value10" attr5="value50">
        #              <tag5>
        #                  some texte
        #              <tag5>
        #          <tag4>
        #      </tag3>
        selfMethod = 'getXml'

        if not isinstance(spaces, str): raise epicxception.epicxmlParameterTypeException(self.__class__.__name__,
                                                                                         selfMethod, 'spaces', 'str',
                                                                                         str(spaces))
        if not spaces == len(spaces) * ' ': spaces = ''
        sb = StringIO()

        rdnode = self.getRdNode(doHelp=doHelp)
        self.__wxml(sb, dict(rdnode), doHelp, spaces)

        return sb.getvalue()

    def __wxml(sb, dnode, doHelp, spaces):

        ## tag
        tag = dnode['*TAG']
        del dnode['*TAG']

        ## help
        if doHelp:
            helps = dnode['*HELPS']
            del dnode['*HELPS']

        ## text
        text = None
        if '*TEXT' in dnode:
            text = dnode['*TEXT']
            del dnode['*TEXT']

        ## childs
        childs = []
        if '*CHILDS' in dnode:
            childs = dnode['*CHILDS']
            del dnode['*CHILDS']

        ## attrs
        attrs = ''
        for attr in dnode:
            attrs += ' ' + attr + '="' + ct.unDress(dnode[attr]) + '"'
        attrs.strip()

        ## Write tag
        if doHelp:
            passe = False
            for attr in helps:
                if helps[attr] == '': continue
                if not passe:
                    passe = True
                    sb.write('\n')
                spl = helps[attr].split('. ')
                sb.write(spaces + '<!-- ' + attr + ': ' + spl[0] + ' -->\n')
                del spl[0]
                for line in spl: sb.write(spaces + '<!--   ' + line + ' -->\n')

        if tag != 'FIRSTNODE': sb.write(spaces + '<' + tag + ' ' + attrs + '>\n')

        ## text suite
        if text!=None:sb.write(spaces + ' ' * 4 + ct.unDress(text) + '\n')

        ## childs suite
        for child in childs:
            Node.__wxml(sb, dict(child), doHelp, spaces + ' ' * 4)
        if tag != 'FIRSTNODE': sb.write(spaces + '</' + tag + '>\n')

    # ------#
    # Xql  #
    # ------#

    def xql(self, xqlString=None, sb=None):
        """
        AskApy xql

        Samples are better than spare words.

        AskApy xql supports four family of orders :

        1 select

        select orders : select, cselect, ccselect, rselect, crselect, xselect

        1.1 description

            select orders return a list of matching tags.

            These selects differs by the way they organize the result.

            Let suppose that these two nodes match a select request:

            1.1.1 select returns a tabbed formatted text of the returned attributes like sql does.
                ex:
                                    *tun    attr1       attr3       *text

                .tag1.tag2.tag3
                                    I7      value10     value30     [some texte1,some texte2,some texte3]
                                    I8      value11     value31     [some texte]
                                    I9      value12     value32     [some texte]

                .tag1.tag8
                                    I10     value13     value33     []
                                    I11     value14     value34     [some texte]

            1.1.2 cselect returns a CoolTyped listing of the returned tags.
                ex:
                .tag1.tag2.tag3
                    *tun:I7 {*TAG:tag3,ATTR10:value10,ATTR3:value30,*TEXT:[some texte,some texte2,some texte3]}
                    *tun:I8 {*TAG:tag3,...,...,...}
                    *tun:I9 {*TAG:tag3,...,...,...}
                .tag1.tag8
                    *tun:I10 {*TAG:tag8,ATTR1:value13,ATTR3:value33}
                    *tun:I11 {*TAG:tag8,...,...,...}
                These tags' CoolTyped expressions can be used into ccreate orders.
                These tag's CoolTyped expressions can be cutted and pasted in the O_WHAT clause of a ccreate order.

            1.1.3 ccselect returns a CoolTyped expression of matching the tag.
            If more than one tag matching an exception is thrown.
                ex:
                {*TAG:tag3,ATTR10:value10,ATTR3:value30,*TEXT:[some texte,some texte2,some texte3]}
                This is the same than the previous cselect but less verbose and for one resulting tag.

            1.1.4 rselect returns a recursive CoolTyped listing of the returned tags.
                Recursive means that each tag dict of the CoolTyped listing,
                now contains one more key *child, within all the tag's children.
                These tags' recursive CoolTyped expressions can be used into rcreate orders.
                These tag's CoolTyped expressions can be cutted and pasted in the O_WHAT clause of a ccreate order.

            1.1.5 crselect returns a recursive CoolTyped list of the returned tag.
            If more than one tag matching an exception is thrown.
            This is the same than the previous rselect but less verbose and for one resulting tag.

            1.1.6 xselect returns a Xml recursive (obviously) representation of each returned tags.
            ex:
            .tag1.tag2.tag3
                *tun:I7
                    <tag3 attr1="value10" attr3="value30">
                        some texte
                        <tag4 attr1="value10" attr5="value50">
                            <tag5>
                                some texte
                                some texte2
                                some texte3
                            <tag5>
                        <tag4>
                    </tag3>
                *tun:I8
                    ...
                *tun:I9
                    ...

            .tag1.tag8
                *tun:I10
                    <tag8 attr1="value13" attr3="value33">
                        <tag6 attr6="value60" attr7="value70">
                        <tag6>
                    </tag8>
                *tun:I11
                    ...

        1.2 syntax

            select
            cselect
            rselect
            xselect
            select O_WHAT at F_TAGS where F_ATTRS

            example:
            --------
            select attr2,attr4 at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges
            select attr2,attr4 at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where (name=georges or name=jules) and adresse=toronto

            Note:
                Attributes comparaison operators are : =, <=, >=, <, >, <>, *between, *in.
                Attributes comparaison criterions can be imbricated into parenthesis.

            For more information about criterions and F_TAGS or F_ATTRS,
            from a command line type: doc.py xfilter.


        2 update

        update order : update

        2.1 description

            update order, updates one tag but not its children.

        2.2 syntax

            update F_TAGS where F_ATTRS O_SET

            example:
            --------
            update tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges set name=charlie


            A complete list of ATTR=VALUE separated by ";" can be given to the O_SET clause.

            example:
            --------
            update tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges set name=charlie;adresse=5 clemence street;*TEXT=roller,cycle,car


        3 create

        create order : create,ccreate,rcreate

        3.1 description

            create order, creates one tag ands its children.
            Theses creates differs by their input.

            create from a set (alike the update syntax).
            ccreate : creates from a CoolTyped tag's expression.
            rcreate : creates from a recursive CoolTyped tag's expression.

        3.2 syntax

            ccreate
            create
            rcreate
            create  O_WHAT O_SET at F_TAGS where F_ATTRS
            ccreate O_WHAT at F_TAGS where F_ATTRS
            rcreate O_WHAT at F_TAGS where F_ATTRS

            example:
            -------
            create tag4 set name=charlie at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges


        4 delete

        delete order : delete

        4.1 description

            delete order, recursivley deletes one tag and its children.

        4.2 syntax

            delete F_TAGS where F_ATTRS

            example:
            --------
            delete tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges


        5 duplicate

        duplicate order : duplicate

        5.1 description

            duplicate order, recursively duplicate one portion of the xml tree to another(s).

        5.2 syntax

            duplicate F_TAGS where F_ATTRS at F_TAGS where F_ATTRS

            example:
            -------
            duplicate tag3.tag4 where name=charlie at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges


        NOTES:
        By default, AskApy Xql engine considers tags and attributes as cases insensitives
        (attribute's values are always cases sensitives).
        This can be changed retreiving it with xmlktools.getXmlMaker(file_desc=None, file_source=None, capSensitive=False),
        setting the capSensitive parameter to True.

        Each request have an order part and a filter part.
        In the following samples in the code, these two parts are respectfully signaled by :
        ___________ (Order part)
        ----------- (Filter part)
        """
        selfMethod = 'xql'
        SUPPORTED_SELECT_ORDERS = ('select', 'cselect', 'ccselect', 'rselect', 'crselect', 'xselect')
        SUPPORTED_ORDERS = list(SUPPORTED_SELECT_ORDERS)
        SUPPORTED_CREATE_ORDERS = ('create', 'ccreate', 'rcreate')
        SUPPORTED_ORDERS.extend(SUPPORTED_CREATE_ORDERS)
        SUPPORTED_ORDERS.extend(['update', 'delete', 'duplicate'])
        SUPPORTED_ORDERS = tuple(SUPPORTED_ORDERS)
        if sb == None: sb = StringIO()
        if not isinstance(xqlString, str) or xqlString == '' or len(
            xqlString) * ' ' == xqlString: raise epicxception.epicxmlParameterTypeException(self.__class__.__name__,
                                                                                            selfMethod, 'xqlString',
                                                                                            'str', str(xqlString))
        _xqlString = xqlString.strip()
        i = _xqlString.find(' ')
        o_name = _xqlString[:i]
        _xqlString = _xqlString[i:].strip()

        if o_name not in (SUPPORTED_ORDERS): raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                       selfMethod,
                                                                                       'xql: The order:' + str(
                                                                                           o_name) + ' is not a supported order. Supported orders are:' + str(
                                                                                           SUPPORTED_ORDERS) + '. Your request:' + xqlString + '.')
        if o_name in SUPPORTED_SELECT_ORDERS: return self.__xql_select(o_name, _xqlString, sb=sb)
        if o_name == 'update': return self.__xql_update(o_name, _xqlString, sb=sb)
        if o_name in SUPPORTED_CREATE_ORDERS: return self.__xql_create(o_name, _xqlString, sb=sb)
        if o_name == 'delete': return self.__xql_delete(o_name, _xqlString, sb=sb)
        if o_name == 'duplicate': return self.__xql_duplicate(o_name, _xqlString, sb=sb)

    def __xql_select(self, o_name, xqlString, sb=None):
        SELECT_ATTR_MAX_LEN = 20
        SELECT_MARGE = 20
        """
        # =======
        # SYNTAXE:
        # =======
        #
        # select
        # cselect
        # rselect
        # xselect
        # select O_WHAT at F_TAGS where F_ATTRS
        # See xmlBase.Filter for F_TAGS and F_ATTRS possibly values.
        # example:
        # =======
        # select *
        # select __all__
        # select * where name=georges
        # select attr2,attr4 at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges
        # select attr2,attr4 at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where (name=georges or name=jules) and adresse=toronto
        # //tag3/tag2/tag3/tag4,/tag1/tag2/tag3/@attr2,@attr4
        # ___________________ -------------------------------------------------------------------
        ## Tests
        # select at31,at32 at tag1.tag2.tag3 where at31=bbbbbbbbb
        """
        selfMethod = '__xql_select'

        def whead(what, sb):
            fhead = ' ' * SELECT_MARGE + '%-5s' + len(what) * (' %-' + str(SELECT_ATTR_MAX_LEN) + 's')
            fhead = fhead + ' %s'
            l = ['*tun']
            l.extend(what)
            l.append('*text')
            sb.write(fhead % tuple(l))
            sb.write('\n')

        _xqlString = xqlString

        ## ORDER ##
        error_what_not_found = epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                   'xql:' + o_name + ':The O_WHAT clause is not defined in your request. Supported O_WHAT clauses are: * or ATTR1,ATTR2,...,ATTRN. Your request:' + o_name + ' ' + xqlString + '.')
        message_general = 'xql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + xqlString + '. SubException is:'

        ## o_what
        i = _xqlString.find(' at ')

        # A006:
        if i <= 0:  # at not found
            i = _xqlString.find(' where ')
            if i <= 0: i = len(_xqlString)  # where not found
            _l = 0
        else:
            _l = 4
        if i <= 0: raise error_what_not_found

        o_what = []
        what = _xqlString[:i].strip()
        # D006: _xqlString=_xqlString[i+_l:].strip()
        _xqlString = _xqlString[i + _l:]  # A006
        if what in ('', '__all__'): what = '*'  # A006
        if what != '*':
            spl = what.split(',')
            for s in spl:
                if s == '' or s == len(s) * ' ': continue
                o_what.append(s)
            if o_what == []: raise error_what_not_found
            if not self.isCapSensitive(): o_what = [w.upper() for w in o_what]

        else:
            o_what = what

        ## FILTER ##
        try:
            f_tags, f_attrs, f_attrs_skel, f_count = self.__xql_getFilter(_xqlString)
            filter = epicbase.Filter(ftags=f_tags, fattrs=f_attrs, fattrs_skel=f_attrs_skel,
                                     capSensitive=self.capSensitive)
            ## See the docstring of class Filter to understand how it works.
            extraAttrs = []
            if o_what != '*': extraAttrs = o_what
            v = epicvisitor.WorkFilter(filter, count=f_count, extraAttrs=extraAttrs)
            self.accept(v)
            foundnodes = v.nodes
        except:
            import sys
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                      message_general + str(sys.exc_info()[0]) + ' ' + str(
                                                          sys.exc_info()[1]))

        ## DO ORDER ##
        ob = []
        # ccselect and crselect : return a colltyped type and not a listing like the others.

        if o_name in ('crselect', 'ccselect') and len(foundnodes) > 1: raise epicxception.epicxmlSystemException(
            self.__class__.__name__, selfMethod,
            message_general + o_name + ' is supported only for one Node. If you use ' + o_name + ', your request should match one unique Node. Nodes matched by your request: ' + str(
                [node.getFiliation() for node in foundnodes]))

        if o_name == 'select' and o_what != '*': whead(o_what, sb)

        for node in foundnodes:
            if o_name == 'select':
                #               select returns a tabbed formatted text like sql does of the returned attributes (plus *tun and *text).
                #                   ex:
                #                                       *tun    attr1       attr3       *text
                #
                #                   .tag1.tag2.tag3
                #                                       I7      value10     value30     [some texte]
                #                                       I8      value11     value31     [some texte]
                #                                       I9      value12     value32     [some texte]
                #
                #                   .tag1.tag8
                #                                       I10     value13     value33     []
                #                                       I11     value14     value34     [some texte]

                ## head
                what = o_what
                if o_what == '*':
                    sb.write('\n')
                    what = list(node.getdAttrs().keys())
                    whead(what, sb)

                ## filiation
                sb.write(node.getFiliation() + '\n')

                ## body
                fbody = ' ' * SELECT_MARGE + '%-5s' + len(what) * (' %-' + str(SELECT_ATTR_MAX_LEN) + 's')
                fbody = fbody + ' %s'

                l = []
                l.append(node.getTun())
                for attr in what:
                    l.append(ct.unDress(node.getAttr(attr)))
                l.append(ct.unDress(node.getText()))

                sb.write(fbody % tuple(l))
                sb.write('\n')

                ob.append(node)

            elif o_name == 'cselect':
                #               cselect returns a CoolTyped listing of the returned nodes.
                #               ex:
                #               .tag1.tag2.tag3
                #                   *tun:I7 {*TAG:tag3,attr10:value10,attr3:value30,*text:[some texte]}
                #                   *tun:I8 {*TAG:tag3,...,...,...}
                #                   *tun:I9 {*TAG:tag3,...,...,...}
                #               .tag1.tag8
                #                  *tun:I10 {*TAG:tag8,attr1:value13,attr3:value33}
                #                   *tun:I11 {*TAG:tag8,...,...,...}
                #               These tags dict can be used in the update or create order
                sb.write(node.getFiliation() + '\n')
                sb.write(' ' * 4 + '*tun:' + node.getTun() + ' ' + ct.unDress(node.getdNode()) + '\n')

            elif o_name == 'ccselect':
                #               cselect returns a CoolTyped list of the returned attribute
                #               ex: [value10,value30]

                if o_what == '*':
                    # if * return the tag itself.
                    sb.write(ct.unDress(node.getdNode()))
                else:
                    # otherwise return the attributes list.
                    l = []
                    for attr in o_what:
                        l.append(node.getAttr(attr))
                    sb.write(ct.unDress(l))

            elif o_name == 'rselect':
                #               rselect returns a recursive CoolTyped listing of the returned nodes.
                sb.write(node.getFiliation() + '\n')
                sb.write(' ' * 4 + '*tun:' + node.getTun() + ' ' + ct.unDress(node.getRdNode()) + '\n')

            elif o_name == 'crselect':
                #               rselect returns a recursive CoolTyped list of the returned node.
                sb.write(ct.unDress(node.getRdNode()))

            elif o_name == 'xselect':
                #               xselect returns a Xml recursive (obviously) representation of each returned nodes.
                #               ex:
                #               .tag1.tag2.tag3
                #                   *tun:I7
                #                       <tag3 attr1="value10" attr3="value30">
                #                           some texte
                #                           <tag4 attr1="value10" attr5="value50">
                #                               <tag5>
                #                                   some texte
                #                               <tag5>
                #                           <tag4>
                #                       </tag3>
                #                   *tun:I8
                #                       ...
                #                   *tun:I9
                #                       ...
                #
                #               .tag1.tag8
                #                   *tun:I10
                #                       <tag8 attr1="value13" attr3="value33">
                #                           <tag6 attr6="value60" attr7="value70">
                #                           <tag6>
                #                       </tag8>
                #                   *tun:I11
                #                       ...
                sb.write('\n')
                sb.write(node.getFiliation() + '\n')
                sb.write(' ' * 4 + '*tun:' + node.getTun() + '\n\n')
                sb.write(node.getXml(spaces=' ' * 8))
                sb.write('\n')

        # ccselect and crselect : return a colltyped type and not a listing like the others.

        if o_name == 'select': return ob

    def __xql_update(self, o_name, xqlString, sb=None):
        """
        update F_TAGS where F_ATTRS O_SET
        example:
        =======
        update tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges set name=charlie
        ______ -------------------------------------------------------------------------------
        """
        selfMethod = '__xql_update'
        _xqlString = xqlString

        ## ORDER ##
        error_set_not_found = epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                  'xql:' + o_name + ':The O_SET clause is not defined in your request. Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXT=TEXT;...;ATTRN=VALUEN. Your request:' + o_name + ' ' + xqlString + '.')
        message_general = 'xql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + xqlString + '. SubException is:'

        ## o_set
        i = _xqlString.find(' set ')
        if i <= 0: raise error_set_not_found

        try:
            o_set = {}
            set = _xqlString[i + 5:].strip()
            _xqlString = _xqlString[:i].strip()

            spl = set.split(';')
            for s in spl:
                if s == '' or s == len(s) * ' ': continue
                spl = s.split('=')
                if spl[0] == '' or len(spl) != 2: raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                            selfMethod,
                                                                                            'xql:' + o_name + ':The portion:' + s + ' of your O_SET clause is incorrect. Your set clause:' + set + ', Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXT=TEXT;...;ATTRN=VALUEN.')
                attr = spl[0].strip()
                value = ct.dress(spl[1])
                if self.isCapSensitive():
                    o_set[attr] = value
                else:
                    o_set[attr.upper()] = value

            if o_set == {}: raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                      'xql:' + o_name + ':Your O_SET clause is incorrect. Your set clause:' + set + ',  Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXT=TEXT;...;ATTRN=VALUEN.')
        except:
            import sys
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                      message_general + str(sys.exc_info()[0]) + ' ' + str(
                                                          sys.exc_info()[1]))

        ## FILTER ##
        try:
            f_tags, f_attrs, f_attrs_skel, f_count = self.__xql_getFilter(_xqlString)
            filter = epicbase.Filter(ftags=f_tags, fattrs=f_attrs, fattrs_skel=f_attrs_skel,
                                     capSensitive=self.capSensitive)
            ## See the docstring of class Filter to understand how it works.
            v = epicvisitor.WorkFilter(filter, count=f_count)
            self.accept(v)
            foundnodes = v.nodes
        except:
            import sys
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                      message_general + str(sys.exc_info()[0]) + ' ' + str(
                                                          sys.exc_info()[1]))

        ## DO ORDER ##

        filiation = None
        for node in foundnodes:
            if filiation != node.getFiliation(): sb.write(node.getFiliation() + '\n')
            sb.write('Updating *tun:' + node.getTun() + '\n')
            try:
                for attr in o_set:
                    if attr == '*TEXT':
                        node.setText(o_set[attr])
                        continue
                    node.setAttr(attr, o_set[attr])
            except:
                import sys
                raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                          'xql:' + o_name + ':Error updating attribute:' + attr + ' on Node ' + node.getFiliation() + ' *tun:' + node.getTun() + '. SubException is:' + str(
                                                              sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]))

            sb.write('\n')

        return foundnodes

    def __xql_create(self, o_name, xqlString, sb=None):
        """
        # ccreate
        # create
        # rcreate
        create  O_WHAT O_SET at F_TAGS where F_ATTRS
        ccreate O_WHAT at F_TAGS where F_ATTRS
        rcreate O_WHAT at F_TAGS where F_ATTRS
        example:
        =======
        create tag4 set name=charlie at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges
        ____________________________    --------------------------------------------------------------
        """
        selfMethod = '__xql_create'
        _xqlString = xqlString

        ## ORDER ##
        error_what_not_found = epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                   'xql:' + o_name + ': O_WHAT is not defined in your request. Your request:' + o_name + ' ' + xqlString + '.')
        error_to_not_found = epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                 'xql:' + o_name + ': The AT (FILTER) clause is not defined in your request. Your request:' + o_name + ' ' + xqlString + '.')
        error_set_not_found = epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                  'xql:' + o_name + ':The O_SET clause is not defined in your request. Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXT=TEXT;...;ATTRN=VALUEN. Please note that pair/value separators are semi-colon. Your request:' + o_name + ' ' + xqlString + '.')
        message_general = 'xql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + xqlString + '. SubException is:'
        noSet = False

        try:

            ## o_what
            borne = ' at '
            idx = 4
            if o_name == 'create':
                if _xqlString.find(' set ') > 0:
                    borne = ' set '
                    idx = 5
                else:
                    noSet = True
                    idx = 4

            i = _xqlString.find(borne)
            if i <= 0: raise error_what_not_found
            o_what = _xqlString[:i].strip()
            _xqlString = _xqlString[i + idx:]

            if o_name in ('ccreate', 'rcreate'):
                o_what = ct.dress(o_what)
                if not isinstance(o_what, dict):
                    if o_name == 'ccreate': raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                      selfMethod,
                                                                                      'xql:' + o_name + ': O_WHAT clause should be a CoolTyped dict. Supported O_WHAT clause is: {*TAG:NAME,ATTR1:VALUE1,ATTR2:VALUE1,ATTR3:VALUE1,*TEXT:TEXT}. Your request:' + o_name + ' ' + xqlString + '.')
                    if o_name == 'rcreate': raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                      selfMethod,
                                                                                      'xql:' + o_name + ': O_WHAT clause should be a CoolTyped dict. Supported O_WHAT clause is: {*TAG:NAME,ATTR1:VALUE1,ATTR2:VALUE1,ATTR3:VALUE1,*TEXT:TEXT,*CHILDS:[*TAG:NAME,...]}. Your request:' + o_name + ' ' + xqlString + '.')

            ## o_set
            if o_name == 'create':
                if noSet: _xqlString = ' at ' + _xqlString
                if not self.isCapSensitive(): o_what = o_what.capitalize()

                ## o_to
                i = _xqlString.find(' at ')
                if i < 0: raise error_to_not_found

                _o_set = _xqlString[:i]
                spl = _o_set.split(';')
                _xqlString = _xqlString[i + 4:]

                o_set = {}
                for s in spl:
                    if s == '' or s.isspace(): continue
                    spl = s.split('=')
                    if spl[0] == '' or len(spl) != 2: raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                                selfMethod,
                                                                                                'xql:' + o_name + ':The portion:' + s + ' of your O_SET clause is incorrect. Your set clause:' + _o_set + ', Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXT=TEXT;...;ATTRN=VALUEN.')
                    attr = spl[0].strip()
                    value = ct.dress(spl[1])
                    if self.isCapSensitive():
                        o_set[attr] = value
                    else:
                        o_set[attr.upper()] = value

                if not noSet and o_set == {}: raise epicxception.epicxmlSystemException(self.__class__.__name__,
                                                                                        selfMethod,
                                                                                        'xql:' + o_name + ':Your O_SET clause is incorrect. Supported O_SET clause is: set ATTR1=VALUE1;ATTR2=VALUE2;*TEXT=TEXT;...;ATTRN=VALUEN.')

                o_what = {'*TAG': o_what}
                o_what.update(o_set)

            ## FILTER ##

            f_tags, f_attrs, f_attrs_skel, f_count = self.__xql_getFilter(_xqlString)
            filter = epicbase.Filter(ftags=f_tags, fattrs=f_attrs, fattrs_skel=f_attrs_skel,
                                     capSensitive=self.capSensitive)
            ## See the docstring of class Filter to understand how it works.
            v = epicvisitor.WorkFilter(filter, count=f_count)
            self.accept(v)
            foundnodes = v.nodes
            newnodes = []

            ## DO ORDER ##

            filiation = None

            for node in foundnodes:
                if filiation != node.getFiliation(): sb.write(node.getFiliation() + '\n')
                node.setRdNode(o_what, sb=sb, space=4, newnodes=newnodes)
                sb.write('\n')

            return newnodes

        except:
            import sys
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                      message_general + str(sys.exc_info()[0]) + ' ' + str(
                                                          sys.exc_info()[1]))

    def __xql_delete(self, o_name, xqlString, sb=None):
        """
        delete F_TAGS where F_ATTRS
        example:
        =======
        delete tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges
        ______--------------------------------------------------------------
        """
        selfMethod = '__xql_delete'
        _xqlString = xqlString

        ## ORDER ##
        message_general = 'xql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + xqlString + '. SubException is:'

        try:

            ## FILTER  ##
            f_tags, f_attrs, f_attrs_skel, f_count = self.__xql_getFilter(_xqlString)
            filter = epicbase.Filter(ftags=f_tags, fattrs=f_attrs, fattrs_skel=f_attrs_skel,
                                     capSensitive=self.capSensitive)
            ## See the docstring of class Filter to understand how it works.
            v = epicvisitor.WorkFilter(filter, count=f_count)
            self.accept(v)
            foundnodes = v.nodes

            ## DO ORDER ##

            filiation = None
            for node in foundnodes:
                if filiation != node.getFiliation(): sb.write(node.getFiliation() + '\n')

                sb.write(
                    ' ' * 4 + 'Deleting Node:' + node.getName() + ' *tun:' + node.getTun() + ', on Node:' + node.getAggregatParent().getFiliation() + ' *tun:' + node.getAggregatParent().getTun() + '.\n')
                node.suicide()
                sb.write('\n')

            return foundnodes

        except:
            import sys
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                      message_general + str(sys.exc_info()[0]) + ' ' + str(
                                                          sys.exc_info()[1]))

    def __xql_duplicate(self, o_name, xqlString, sb=None):
        """
        duplicate F_TAGS where F_ATTRS at F_TAGS where F_ATTRS
        example:
        =======
        duplicate tag3.tag4 where name=charlie at tag3,tag2.tag3.tag4,.tag1.tag2.tag3,*tun=I7 where name=georges
        _________ ----------------------------------------------------------------------------------------------
        Duplicate is composed of 2 requests.
        The first request must return an unique tag.
        """
        selfMethod = '__xql_duplicate'
        _xqlString = xqlString

        ## ORDER ##
        error_to_not_found = epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                 'xql:' + o_name + ': The AT (FILTER) clause is not defined in your request. Your request:' + o_name + ' ' + xqlString + '.')
        message_general = 'xql:' + o_name + ': Not Suported request. Your request:' + o_name + ' ' + xqlString + '. SubException is:'

        try:

            ## Filters
            borne = ' at '
            idx = 4
            if o_name == 'create':
                borne = ' set '
                idx = 5

            i = _xqlString.find(' at ')
            if i <= 0: raise error_to_not_found

            srcXqlString = _xqlString[:i].strip()
            trgXqlString = _xqlString[i + 4:]

            ## FILTER 1 ##

            f_tags, f_attrs, f_attrs_skel, f_count = self.__xql_getFilter(srcXqlString)
            filter = epicbase.Filter(ftags=f_tags, fattrs=f_attrs, fattrs_skel=f_attrs_skel,
                                     capSensitive=self.capSensitive)
            ## See the docstring of class Filter to understand how it works.
            v = epicvisitor.WorkFilter(filter, count=f_count)
            self.accept(v)

            source = None
            sources = list(v.nodes)
            if len(sources) > 1:
                import warnings
                warnings.warn(str(epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                  'xql:' + o_name + ':Filter: More than one Node found for the duplication source, only the first one is kept.' + '. Filter Found Nodes:' + str(
                                                                      [node.getName() for node in sources]) + '. kept:' + str(sources[0].getName()) + '. Your request:' + o_name + ' ' + xqlString + '.')))
            if len(sources) > 0: source = sources[0]

            ## FILTER 2 ##

            f_tags, f_attrs, f_attrs_skel, f_count = self.__xql_getFilter(trgXqlString)
            filter = epicbase.Filter(ftags=f_tags, fattrs=f_attrs, fattrs_skel=f_attrs_skel,
                                     capSensitive=self.capSensitive)
            ## See the docstring of class Filter to understand how it works.
            v = epicvisitor.WorkFilter(filter, count=f_count)
            self.accept(v)
            targets = list(v.nodes)

            ## DO ORDER ##
            if source == None: return

            filiation = None
            foundnodes = []
            for node in targets:
                if filiation != node.getFiliation(): sb.write(node.getFiliation() + '\n')

                try:

                    v = epicvisitor.WorkClone()
                    source.accept(v)
                    clone = source.workClone
                    ## cleanup
                    v = epicvisitor.WorkClearClone()
                    source.accept(v)
                    node.add(clone, doCheckKey=False)
                    foundnodes.append(clone)
                    ## update quickTuns
                    v = epicvisitor.WorkupdQuickTun()
                    clone.accept(v)

                    sb.write(
                        ' ' * 4 + 'Duplicating Node:' + clone.getName() + ' *tun:' + clone.getTun() + ', on Node:' + node.getFiliation() + '.\n')

                    sb.write('\n')

                except:
                    raise
                    import sys
                    raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                              'Error Duplicating Node:' + source.getName() + ', on Node:' + node.getFiliation() + ' *tun:' + node.getTun() + '. SubException is:' + str(
                                                                  sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]))

            return foundnodes

        except:
            raise
            import sys
            raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                      message_general + str(sys.exc_info()[0]) + ' ' + str(
                                                          sys.exc_info()[1]))

    def __xql_getFilter(self, xqlString, sb=None):
        selfMethod = '__xql_getFilter'
        _xqlString = xqlString
        hasWhere = False  # A006

        ## f_tags
        i = _xqlString.find(' where ')
        if i < 0:
            i = len(_xqlString)
        else:
            hasWhere = True  # A006

        f_tags = _xqlString[:i].strip()
        if f_tags == '': f_tags = '*'  # A006

        f_count = epicvisitor.WorkFilter.MAX_FOUND
        imore = 0

        if f_tags.endswith(']'):
            i = f_tags.find('[')
            if i < 0: raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                'Filter: From : Cannot find the begining of your count expression. The format of a count expression is [###].')
            count = f_tags[i + 1:-1]
            imore = len(count) + 1
            if not count.isdigit(): raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                              'Filter: From : The value of your count expression is not numeric. The format of a count expression is [###].')
            f_count = int(count)
            f_tags = f_tags[:i]

        if f_tags != '*':
            spl = f_tags.split(',')
            f_tags = [s for s in spl if not (s == '' or s.isspace())]

        # A006
        f_attrs = []
        f_attrs_skel = 'True'
        if hasWhere:
            _xqlString = _xqlString[i + 7 + imore:].strip()

            ## f_attrs
            if _xqlString != '':
                # ex : s="((at31=bbbb and  at32=bbbb) and  at33=bbbb) or (at34=bbbb and  at35=bbbb) and at36=bbbb"
                f_attrs_skel = _xqlString

                # Get pair-values
                s = f_attrs_skel.replace(' and ', ')')
                s = s.replace(' or ', ')')

                pv = RE_BRACES.split(s)

                for s in pv:
                    if s == '' or s.isspace(): continue

                    f_attrs_skel = f_attrs_skel.replace(s, str(len(f_attrs)), 1)
                    f_attrs.append(s)
        # D006
        # else:
        #    f_attrs_skel='True'

        return f_tags, f_attrs, f_attrs_skel, f_count

    def fgetMatch(self, fil):
        """
        Xql Filter, deep tree searching.
        """

        # Stop climbing up the tree if not need.
        if self.isFirstNode(): return (False, None)

        myfil = self.getFiliation()

        if fil.startswith(epicbase.TAG_SEP):
            if myfil == fil: return (True, self)
            return self.getAggregatParent().fgetMatch(fil)

        if myfil.endswith(epicbase.TAG_SEP + fil):
            return (True, self)
        else:
            return self.getAggregatParent().fgetMatch(fil)

    def isPartial(self):
        return self.getTopParent().getTopTagDesc().isPartial()

    def isThisTagPartial(self):
        return self.peerTagdesc.isPartial()

    def getPeerTagdesc(self, filiation):
        return self.getTopParent().getTopTagDesc().getPeerTagdesc(filiation)

    def getPeerTagrest(self, filiation):
        return self.getTopParent().getTopTagRest().getPeerTagdesc(filiation)

    def isForce(self):
        top = self.getTopParent()
        if not hasattr(top, 'force'): return False
        return self.getTopParent().force

    def setForce2(self, value):
        """
        # force2 will allow setAttr for attrs into self.peerTagdesc.partialAttrDescs:
        """
        top = self.getTopParent()
        top.force2 = value == True

    def isForce2(self):
        """
        force2 will allow attr into self.peerTagdesc.partialAttrDescs
        """
        top = self.getTopParent()
        if not hasattr(top, 'force2'): return False
        return self.getTopParent().force2

    def feedRestrictor(self):
        if self.getTopParent().getTopTagRest() == None: return
        attrRests = None

        try:
            peerTagrest = self.getPeerTagrest(self.getFiliation())
            attrRests = {
                'attrdescs': dict(peerTagrest.attrDescs),
                'attrorders': list(peerTagrest.orderedAttrDescs),
                'textdescs': dict(peerTagrest.textDesc),
                'tagdescs': dict(peerTagrest.tagDesc)
            }

            for attr in list(self.peerTagdesc.attrDescs.keys()):
                if attr not in attrRests['attrdescs']:
                    self.peerTagdesc.attrDescs[attr]['*deny'] = True
                    self.peerTagdesc.attrDescs[attr]['*display'] = False
        except:
            self.peerTagdesc.tagDesc['*deny'] = True
            self.peerTagdesc.tagDesc['*display'] = False

        self.peerTagdesc.attrRests = attrRests

    def add(self, p_node, doAddToQuickTun=True, doCheckKey=True, force=False):
        """
        Adds a python list of new Node objects to this node.
        topic: Utility methods
        """
        selfMethod = 'add'
        if not hasattr(p_node, 'isinstance') or not p_node.isinstance('Node'):
            raise epicxception.epicxmlParameterTypeException(self.__class__.__name__, selfMethod, 'p_node', 'Tag', str(p_node))
        # check Max __occurences__
        # M021: if p_node.getTag() in self.getQuickTagKeys(): self.peerTagdesc.checkMaxTagNodes(p_node.getTag(), len(self.getQuickTagNodes(p_node.getTag())))
        if not force and p_node.getTag() in self.getQuickTagKeys(): self.peerTagdesc.checkMaxTagNodes(p_node.getTag(), len(self.getQuickTagNodes(p_node.getTag())))
        epicbase.ImbricatedNodeBase.add(self, p_node, doAddToQuickTun=doAddToQuickTun, doCheckKey=doCheckKey, force=force)
        if self.getTag() not in self.__tagOrders: self.__tagOrders.append(self.getTag()) # A030

    # A040:
    def remove(self, p_nodeBase, doRemoveFromQuickTun=True):
        """
        Removes this guiven node from its parent (self).
        topic: Utility methods
        """
        if  p_nodeBase not in self.listNodeBases:raise epicxception.AppNonPreexistingObjectError(str(self.__class__), p_nodeBase.__class__,str(p_nodeBase))
        from kwadlib import epicvisitor
        # Remove childs first from QuickTun:
        # wrk = epicvisitor.WorkrmvQuickTun()
        # p_nodeBase.accept(wrk)
        # Then remove iself:
        epicbase.ImbricatedNodeBase.remove(self, p_nodeBase, doRemoveFromQuickTun=doRemoveFromQuickTun)

    def suicide(self):
        if hasattr(self, '__top_hard_link'): delattr(self, '__top_hard_link')
        self.clearChilds()
        self.getAggregatParent().remove(self)
        self.isDead = True

    def isAllowedChilds(self, p_nodeBase, force=False, createDescForRecursiveLink=False):
        selfMethod = 'isAllowedChilds'

        # A037: If this epicfile has no desc we just say True:
        if self.peerTagdesc==None:return True

        ## A007:
        if not force and self.isForce(): force = self.isForce()
        epicbase.ImbricatedNodeBase.isAllowedChilds(self, p_nodeBase, force=force)
        if force: return True
        found = False

        if not force and not self.isFirstNode():
            if p_nodeBase.getTag() in self.peerTagdesc.getQuickTagKeys():
                found = True
            else:
                if p_nodeBase.getTag() in self.peerTagdesc.getQuickTagAndLinkKeys():

                    if self.peerTagdesc.getQuickTagAndLinkNodes(p_nodeBase.getTag())[0].isinstance('Lnk'):
                        found = True

                        # Clone Link
                        """ Will match the first tag with the same name. """
                        uc = self.peerTagdesc.getTopParent().getUniqueTags()
                        if p_nodeBase.getName() not in uc: raise epicxception.epicxmlSystemException(
                            self.__class__.__name__, selfMethod, "Impossible to fing a tag for the Link named:" + str(
                                p_nodeBase.getName()) + '. Know tags are: ' + str(list(uc.keys())))

                        tagdesc = uc[p_nodeBase.getName()]
                        mstrict = tagdesc.isStrict()
                        tagdesc._setIsStrict(
                            value=self.peerTagdesc.getAggregatParent().isStrict())  # Propaging partial clause isStrict if parent is.

                        # tagdesc must be cloned to avoid cross-ref on getAggregatParent.
                        # Lnk are not cloned.
                        from . import epicdescvisitor
                        v = epicdescvisitor.WorkClone(doCloneLink=True)
                        tagdesc.accept(v)
                        clone = tagdesc.workClone
                        tagdesc._setIsStrict(value=mstrict)

                        ## cleanup
                        v = epicdescvisitor.WorkClearClone()
                        tagdesc.accept(v)

                        self.peerTagdesc.add(clone)

                        ## update quickTuns
                        v = epicdescvisitor.WorkupdQuickTun()
                        clone.accept(v)

            if not found:
                raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                          "Not allowed child:" + p_nodeBase.getName() + ' for Node:' + self.getName() + '. Allowed children are:' + str(
                                                              [o.getName() for o in self.peerTagdesc.listNodeBases])[
                                                                                                                                                                    1:-1] + ', or use force.')
            if self.peerTagdesc.getQuickTagNodes(p_nodeBase.getTag())[0].isTagDenied():
                raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                          "Child:" + p_nodeBase.getName() + ' denied for Node:' + self.getFiliation() + ' !')

        return found

    # M016: def newNode(self, tag, checkDefault=False, **attrs):
    def newNode(self, tag, checkDefault=False, force=True, clasIsSoftClassNode=False, **attrs):
        """
        Instanciates a new object of class Node,
        adds it to this node and returns it.
        tag: a tag name.
        **attrs: is a set of pair attr=value keyword parameters.
        Ex:
            top=Node(name='mytop')
            top.newNode('mytag', attr1='value1', attr2='value2', attr3='value3')

        topic: Utility methods
        """
        # M032: + force:

        node = self.makeDefaultNode(tag, checkDefault=checkDefault, _new_orderedAttrs=list(attrs.keys()), clasIsSoftClassNode=clasIsSoftClassNode, force=force)

        if not checkDefault and force:
            _force = True
        elif force:
            _force = True
        else:
            _force = False

        node.setAttrs(_force=_force, **attrs)

        return node

    # M032: +force:
    def makeDefaultNode(self, tag, checkDefault=False, _new_orderedAttrs=None, clasIsSoftClassNode=False, force=False):
        if _new_orderedAttrs == None: _new_orderedAttrs = []

        if not force and not self.isForce() and (
                not self.isPartial() or
                (self.isPartial() and self.peerTagdesc.isStrict())
        ):

            fil = self.getFiliation() + epicbase.TAG_SEP + str(tag)
            tagDesc = self.getPeerTagdesc(fil)
            node = tagDesc.makeDefaultNode(self, checkDefault=checkDefault, clasIsSoftClassNode=clasIsSoftClassNode)

        else:  # When force or partial we allow raw creation of attrs without setting default values.

            if clasIsSoftClassNode:
                raise Exception('clasIsSoftClassNode is not Supported by KastMenu (DKwad only) !' )
            else:node = Node(name=tag)
            node.capSensitive = self.isCapSensitive()

            self.add(node, force=force)

            # When explicit option force allows tag creation.
            try:
                node.peerTagdesc = self.getPeerTagdesc(node.getFiliation())
            except:
                # M032: if not self.isForce(): raise
                if not self.isForce() and not force: raise
                from .epicdesc import Tagdesc
                # node.peerTagdesc=Tagdesc.newTagdesc(tag, parent=self.getAggregatParent().peerTagdesc, orderedAttrs=_new_orderedAttrs)
                # M015: node.peerTagdesc=Tagdesc.newTagdesc(tag, parent=self.peerTagdesc, orderedAttrs=_new_orderedAttrs)
                node.peerTagdesc = Tagdesc.newTagdesc(tag, parent=self.peerTagdesc, orderedAttrs=_new_orderedAttrs, capSensitive=self.isCapSensitive())

            # feed Attrs
            attrs = node._getdAttrs()
            text = node._getText()

            for attr in node.peerTagdesc.attrDescs:
                value = None
                if '*value' in node.peerTagdesc.attrDescs[attr]: value = node.peerTagdesc.attrDescs[attr]['*value']
                attrs[attr] = value
                # D014: if '*value' in node.peerTagdesc.textDesc and isinstance('*value' in node.peerTagdesc.textDesc, (tuple, list)):node._setTexts(list(node.peerTagdesc.textDesc['*value']))

            # A014:
            if '*value' in node.peerTagdesc.textDesc and isinstance('*value' in node.peerTagdesc.textDesc, (tuple, list)): node._setText(node.peerTagdesc.textDesc['*value'])

        if self.getTopParent().getTopTagRest() != None: node.peerTagrest = self.getPeerTagrest(node.getFiliation())
        node.setFileDesc(self.getFileDesc())
        node.setFileRest(self.getFileRest())

        return node

    def accept(self, p_visitor):

        epicbase.NodeBase.accept(self, p_visitor)
        if (p_visitor.childFirst):
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveNode)
            if p_visitor.treatAncestor:
                p_visitor.visitNode(self)
            else:
                p_visitor.treatAncestor = True
        else:
            if p_visitor.treatAncestor:
                p_visitor.visitNode(self)
            else:
                p_visitor.treatAncestor = True
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveNode)

    def clearChilds(self):
        v = epicvisitor.WorKill()
        self.accept(v)
        self.listNodeBases = []

    def Clone(self):
        # Prepare File desc:
        from . import epicdesc
        desc = epicdesc.FirstNode(isPartial=True)
        desc.capSensitive = True
        firstNode = FirstNode(topTagdesc=desc, force=True)
        firstNode.capSensitive = True
        firstNode.peerTagdesc = desc
        # parentNode.setFiles(file_source=file_source)

        # - clone
        v = epicvisitor.WorkClone(firstNode=firstNode)
        self.accept(v)
        clone = self.workClone
        # -- cleanup
        v = epicvisitor.WorkClearClone()
        self.accept(v)

        utop = firstNode.getNodes()[0]
        utop.hardLinkTopParent()

        return utop

    def clone(self, firstNode=None, doAddToQuickTun=False, clasIsSoftClassNode=False):
        selfMethod = 'clone'

        if clasIsSoftClassNode:
            raise Exception('clasIsSoftClassNode is not Supported by KastMenu (DKwad only) !' )
        else:concreteObj = Node(name=self.getName())
        epicbase.NodeBase.clone(self, concreteObj)
        concreteObj._setAttrs(dict(self.__attrs))
        concreteObj._setText(self.__text)
        concreteObj._setTagOrders(list(self.__tagOrders))
        concreteObj.peerTagdesc = self.peerTagdesc
        concreteObj.capSensitive = self.capSensitive

        parentNode = None
        if firstNode != None:
            parentNode = firstNode
        elif hasattr(self.getAggregatParent(), 'workClone'):
            parentNode = self.getAggregatParent().workClone
        self.workClone = concreteObj
        # M022: if parentNode != None: parentNode.add(concreteObj, doAddToQuickTun=False, doCheckKey=False, force=True)
        if parentNode != None: parentNode.add(concreteObj, doAddToQuickTun=doAddToQuickTun, doCheckKey=False, force=True)
        return concreteObj

    __wxml = staticmethod(__wxml)


class FirstNode(Node):
    _apb_isinstance_FirstNode = 'FirstNode'
    idxFIRST_TUNE = 'I1'

    # A019:
    def _init(self, topTagdesc=None, topTagrest=None, force=False, noParentWeakRef=False, comment_recorders=None):
        if comment_recorders==None:comment_recorders = []

        self.__idx = 0
        self.__quickTuns = {}
        self.__topTagdesc = topTagdesc
        self.__topTagrest = topTagrest
        self.force = force
        self.force2 = False
        self.__file_source = None
        self.__file_desc = None
        self.__file_rest = None
        self.__file_target = None
        self.__lFile_source = None
        self.__lFile_desc = None
        self.__lFile_rest = None
        self.__lFile_target = None
        self.__comment_recorders = comment_recorders
        Node._init(self, name='FIRSTNODE')
        self.__allowSave = True
        self.peerTagdesc = topTagdesc
        self.peerTagrest = topTagrest
        # A019:
        self.no_parent_weakref = noParentWeakRef
        self.__repoz = None
        self._hasBeenEvaluated = False

    def hasBeenEvaluated(self):
        return self._hasBeenEvaluated

    def treatForeach(self):
        self_funct = 'treatForeach'
        # M030:
        if not self.isFirstNode(): epicxception.epicxmlSystemException(self.__class__.__name__, self_funct, 'This method is only allowed on first Node !')
        from kwadlib import node_visitor as visitor

        # M001:20120901
        wrk = visitor.WorkForeach()
        while True:
            wrk.mayHaveMore = False
            self.accept(wrk)
            if not wrk.mayHaveMore: break

    def setRepozInfos(self, repoz, alias):
        import weakref
        self.__repoz = weakref.ref(repoz)
        self.__alias = alias

    def getRepozInfos(self):
        if self.__repoz == None or self.__repoz() == None: return None
        return {'repoz': self.__repoz(), 'alias': self.__alias}

    def clearRepozInfos(self):
        self.__repoz = None
        self.__alias = None

    def getCommentRecorders(self):
        return self.__comment_recorders

    def dontAllowSave(self):
        self.__allowSave = False

    def getAttrDescs(self):
        selfMethod = 'getAttrDescs'
        raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod, 'FirstNode do not support getAttrDescs.')

    def getTopTagDesc(self):
        return self.__topTagdesc

    def getTopTagRest(self):
        return self.__topTagrest

    def mkTun(self):
        # D033: self.__idx += 1
        # D033: return 'I' + str(self.__idx)
        # A033:
        from time import time
        ts = int(time() * 100000)
        rand = random.randint(1, 10000)
        rand = str(ts) + "%04i" % rand

        return 'I' + rand

    def getRdNodes(self):
        """
        [{*TAG:NAME,ATTR1:VALUE1,ATTR2:VALUE1,ATTR3:VALUE1,*TEXT:[TEXT,],*CHILDS:[*TAG:NAME,...]}]
        """
        l = []

        _l = self.getChilds()
        for child in _l:
            l.append(child.getRdNode())

        return l

    def isFirstNode(self):
        return True

    def getQuickTunKeys(self):
        return list(self.__quickTuns.keys())

    def getQuickTunNode(self, tun):
        selfMethod = 'getQuickTunNode'
        # if tun=='main':return self
        if tun == 'main': return self.getNodes()[0]
        if not tun in self.__quickTuns: raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                                  'This tun (Node Unique Name):' + str(
                                                                                      tun) + ' , is unknown. Known tun are: ' + str(
                                                                                      list(
                                                                                          self.__quickTuns.keys())) + '.')
        return self.__quickTuns[tun]

    def _hasQuickTun(self, tun):
        return tun in self.__quickTuns

    def _setQuickTun(self, tun, p_nodeBase):
        self.__quickTuns[tun] = p_nodeBase

    def _delQuickTun(self, tun):
        if tun in self.__quickTuns: del self.__quickTuns[tun]

    def vwBasicGetView(self, top=None, view=None, message=None, apb_session=None, apb_callerctx=None, xtop=None,
                       xmain=None, xseattr=None, xsescope=None, xsesign=None, xhelp=None, xtree=None, xgrid=None,
                       xcubelang=None, xrepoz=None):
        self.vwBasicGetView(top=self, view=view, message=message, apb_session=apb_session, apb_callerctx=apb_callerctx,
                            xtop=xtop, xmain=xmain, xseattr=xseattr, xsescope=xsescope, xsesign=xsesign, xhelp=xhelp,
                            xtree=xtree, xgrid=xgrid, xcubelang=xcubelang, xrepoz=xrepoz)

    def vwMobileGetView(self, top=None, view=None, message=None, apb_session=None, apb_callerctx=None, xtop=None,
                        xmain=None, xseattr=None, xsescope=None, xsesign=None, xhelp=None, xtree=None, xgrid=None,
                        xcubelang=None, xrepoz=None):
        self.vwMobileGetTopView(top=self, view=view, message=message, apb_session=apb_session,
                                apb_callerctx=apb_callerctx, xtop=xtop, xmain=xmain, xseattr=xseattr, xsescope=xsescope,
                                xsesign=xsesign, xhelp=xhelp, xtree=xtree, xgrid=xgrid, xcubelang=xcubelang,
                                xrepoz=xrepoz)

    def accept(self, p_visitor):

        epicbase.NodeBase.accept(self, p_visitor)
        if (p_visitor.childFirst):
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveNode)
            if p_visitor.treatAncestor:
                p_visitor.visitFirstNode(self)
            else:
                p_visitor.treatAncestor = True
        else:
            if p_visitor.treatAncestor:
                p_visitor.visitFirstNode(self)
            else:
                p_visitor.treatAncestor = True
            epicbase.ImbricatedNodeBase.accept(self, p_visitor, p_visitor.recursiveNode)

    def getAccesMode(operation):
        return getAccesMode(operation)

    def getFiles(self):
        return self.__file_source, self.__file_desc, self.__file_rest, self.__file_target

    def setFiles(self, file_source=None, file_desc=None, file_rest=None, file_target=None):
        self.__file_source = file_source
        self.__file_desc = file_desc
        self.__file_rest = file_rest
        self.__file_target = file_target

    def getFileUser(self):
        return self.__file_source

    def setFileUser(self, file_source):
        self.__file_source = file_source

    def getFileDesc(self):
        return self.__file_desc

    def setFileDesc(self, file_desc):
        self.__file_desc = file_desc

    def getFileRest(self):
        return self.__file_rest

    def setFileRest(self, file_rest):
        self.__file_rest = file_rest

    def getFileTarget(self):
        return self.__file_target

    def setFileTarget(self, file_target):
        self.__file_target = file_target

    def getLogicalFiles(self):
        return self.__lFile_source, self.__lFile_desc, self.__lFile_rest, self.__lFile_target

    def setLogicalFiles(self, lFile_source=None, lFile_desc=None, lFile_rest=None, lFile_target=None):
        """ Only set whith a different value than files if loading an apb resource file. """
        self.__lFile_source = lFile_source
        self.__lFile_desc = lFile_desc
        self.__lFile_rest = lFile_rest
        self.__lFile_target = lFile_target

    def show(self, sb=None, **print_keywords):
        """ Facade for Repository """
        # return self.getXml(doHelp=doHelp)
        if sb == None: sb = StringIO()

        return self.getNodes()[0].printXml(_sb=sb, **print_keywords)

    def save(self, toFile=None, **print_keywords):
        selfMethod = 'save'
        if not self.__allowSave: raise epicxception.epicxmlSystemException(self.__class__.__name__, selfMethod,
                                                                           'This maker is not allowed to save !')

        file_source, file_desc, file_rest, file_target = self.getFiles()

        file = file_source
        if toFile != None:
            file = toFile
        elif file_target != None:
            file = file_target

        content = self.show(**print_keywords).getValue()

        fd = open(file, 'w')
        fd.write(content)
        fd.close()

    def _SessionBeforStore_(self):
        """ See Vistor docstring to understand what append here. """
        from . import epicdescvisitor
        self.clearRepozInfos()

        v = epicdescvisitor.WorkSwitchWeakToRef()
        topDesc = self.getTopTagDesc()
        topDesc.accept(v)

        v = epicvisitor.WorkSwitchWeakToRef()
        self.accept(v)

    def _SessionAfterStore_(self):
        from . import epicdescvisitor

        v = epicdescvisitor.WorkSwitchRefToWeak()
        topDesc = self.getTopTagDesc()
        topDesc.accept(v)

        v = epicvisitor.WorkSwitchRefToWeak()
        self.accept(v)

    def _SessionAfterLoad_(self):
        self._SessionAfterStore_()

    getAccesMode = staticmethod(getAccesMode)

    # ===================#
    #                   #
    #                   #
    #  Utility Methods  #
    #                   #
    #                   #
    # ===================#


def pxq_update(node, pxq_updates, sb, picpath_text_separator, verbose=0):
    self_funct = 'pxq_update'

    sb.write('updated node:' + node.getFiliation() + '>\n')
    for attr in pxq_updates:
        try:
            if attr == '%text':
                sb.write('   From ' + attr + ':\n')
                text = node.getText()
                if text!=None:sb.write(15 * ' ' + str(text) + '\n')
                value = pxq_updates[attr]
                if value!=None:node.setText(value)
            else:
                sb.write('   From ' + attr + ':' + str(node.getAttr(attr)))
                node.setAttr(attr, pxq_updates[attr])
        except Exception as e:
            if verbose >= 3: print(sb.getvalue())
            error = epicxception.epicxmlPxQueryException('Main', self_funct,
                                                         'tdc:Error trying to update Node:' + node.getFiliation() + ', Attribute:' + attr + '!')
            error.setMessage(error.getMessage() + 'SubException is:' + str(e))
            error.setSubException(e)
            raise error

        if attr == '%text':
            sb.write('   To ' + attr + ':\n')
            text = node.getText()
            if text!=None: sb.write(15 * ' ' + str(text) + '\n')
        else:
            sb.write(' To ' + attr + ':' + str(node.getAttr(attr)) + '\n')

    # Finally checkAll()
    node.checkWholeNode()


def pxq_split_attrs(attrs, level=None, og_pxq=None, tdc_syntax=None):
    self_funct = 'pxq_split_attrs'
    founds = {}

    for attr in attrs:
        if not attr.startswith('@'):
            message = 'tdc:Bad Format: Incorrect Attribute:' + attr + ' ! Attribute should start with "@".\n' + \
                      'For Level:' + level + '.\n' + \
                      'Your Top Down Complete PxQuery request:' + og_pxq + '.\n'
            if tdc_syntax != None:
                message = 'The tdc syntax is:\n' + message + tdc_syntax + '.'
            else:
                message = message + '.'

            raise epicxception.epicxmlPxQueryException('Main', self_funct, message)

        spl1 = attr.split('=')
        if len(spl1) != 2: raise epicxception.epicxmlPxQueryException('Main', self_funct,
                                                                      'tdc:Bad Format: Incorrect Attribute:' + attr + ' ! Attribute have this shape ATTR=VALUE !\n' +
                                                                      'For Level:' + level + '.\n' +
                                                                      'Your Top Down Complete PxQuery request:' + og_pxq + '.\n' +
                                                                      'The tdc syntax is:\n' + tdc_syntax + '.')

        attr, value = spl1[0][1:], spl1[1]

        value = value.replace(ESC_SLASH, '/')
        founds[attr] = value
    return founds


def pxq_multi_attrs(attr, node, more_attrs, attr_separator, text_separator):
    first = True

    if attr == '__DO_ATTR_ALL__':

        sb = StringIO()
        attrs = node.getdAttrs()

        _l = node.getAttrOrders()
        for attr in _l:
            if not first: sb.write(attr_separator)
            first = False

            sb.write(attr + ':' + str(attrs[attr]))

        return True, sb.getvalue()

    elif len(more_attrs) > 0:
        sb = StringIO()
        more_attrs = [attr] + more_attrs

        for attr in more_attrs:
            if not first: sb.write(attr_separator)
            first = False

            if attr == '%text':
                value = node.getText()
            else:
                value = node.getAttr(attr)

            sb.write(attr + ':' + str(value))
        return True, sb.getvalue()

    else:
        if attr == '%text': return False, node.getText()
        return False, str(node.getAttr(attr))


# -----------------------------#
# Massive Picpaths operations #
# -----------------------------#


def picpaths(root_node, operation, picpaths, doForce=False, picpath_attr_separator=epicbase.PICPATH_ATTR_SEP,
             picpath_text_separator=epicbase.PICPATH_TEXT_SEP, attr_separator=epicbase.ATTR_SEP,
             node_separator=epicbase.NODE_SEP, text_separator=epicbase.TEXT_SEP, sb=None, sbBoth=True, verbose=0):
    selfMethod = 'picpaths'
    ALLOWED_OPERATIONS = ('list', 'update', 'create', 'remove', 'copy', 'move')

    if operation not in ALLOWED_OPERATIONS: raise epicxception.epicxmlParameterException('Node', selfMethod,
                                                                                         'Not allowed operation:' + str(
                                                                                             operation) + ', operation must be in :' + str(
                                                                                             ALLOWED_OPERATIONS)[
                                                                                                                                       1:-1].replace(
                                                                                             "'", ''))
    from .epicbase import TAG_SEP

    ## - copy and move
    if operation in ('copy', 'move'):
        if len(picpaths) != 2:
            raise epicxception.epicxmlSystemException('Main', selfMethod,
                                                      'copy or move requires to picpaths arguments ! Received:' + str(
                                                          picpaths)[1:-1].replace("'", '') + '.')
        listnodes = []

        for picpath in picpaths:
            # -- manage / (root) picpath
            picpath, base_node, indice = __picpaths_adapt(root_node, picpath, doIndice=True)

            nodes = base_node.tdc(picpath, checkIsNode=True, checkIsAttr=False,
                                  picpath_attr_separator=picpath_attr_separator,
                                  picpath_text_separator=picpath_text_separator, attr_separator=attr_separator,
                                  node_separator=node_separator, text_separator=text_separator)
            if indice != None:
                if len(nodes) > indice:
                    nodes = [nodes[indice]]
                else:
                    nodes = []

            if len(nodes) == 0:
                which = 'source'
                if len(listnodes) == 1: which = 'target'
                raise epicxception.epicxmlSystemException('Main', selfMethod,
                                                          'Found no ' + which + ' node to ' + operation + '!')

            listnodes.append(nodes)

        for snode in listnodes[0]:
            for tnode in listnodes[1]:
                # - clone
                v = epicvisitor.WorkClone()
                snode.accept(v)
                clone = snode.workClone
                # -- cleanup
                v = epicvisitor.WorkClearClone()
                snode.accept(v)
                # - add
                tnode.add(clone, doCheckKey=False, force=doForce)
                print('   Adding child:' + clone.getFiliation())

        if operation == 'move':
            for snode in listnodes[0]: snode.suicide()

        return listnodes[1]


    ## - Update
    elif operation == 'update':
        updnodes = []

        firstime = True
        for picpath in picpaths:

            # -- manage / (root) picpath
            picpath, base_node = __picpaths_adapt(root_node, picpath)

            if not firstime:
                picpaths_print('', both=sbBoth, sb=sb)
            else:
                firstime = False

            try:  # New Allow exception (printed) when more than one Picpath
                nodes = base_node.tdc(picpath, checkIsNode=True, checkIsAttr=False,
                                      picpath_attr_separator=picpath_attr_separator,
                                      picpath_text_separator=picpath_text_separator, attr_separator=attr_separator,
                                      node_separator=node_separator, text_separator=text_separator, doUpdate=True,
                                      verbose=3)
            except Exception as e:
                if len(picpaths) == 1:
                    raise
                else:
                    sb.write('One Error occured running picpath:' + picpath + '\n' + str(e))
                continue

            updnodes.extend(nodes)

        return updnodes


    ## - Create
    elif operation == 'create':
        newnodes = []

        firstime = True
        for picpath in picpaths:
            if not firstime:
                picpaths_print('', both=sbBoth, sb=sb)
            else:
                firstime = False
            # -- manage / (root) picpath
            picpath, base_node = __picpaths_adapt(root_node, picpath)

            # newpicpath
            spl = picpath.split(TAG_SEP)
            newpicpath = TAG_SEP.join(spl[:-1])
            newnode = spl[-1]

            # checkIfHasAnUpdate part
            spl = newnode.split('[')
            if len(spl) > 1:
                hasUpdate = True
                pxq_updates = spl[1][:-1]
                attrs = pxq_updates.split(picpath_attr_separator)
                pxq_updates = pxq_split_attrs(attrs, level=picpath,
                                              og_pxq=str(picpaths)[1:-1].replace("'", '').replace(',', ''),
                                              tdc_syntax=None)
            else:
                hasUpdate = False

            # newnode
            newnode = spl[0]
            if newnode.find('@') > 0 or newnode.find(
                picpath_attr_separator) > 0: raise epicxception.epicxmlSystemException('Main', selfMethod,
                                                                                       'New node should not contains any Attribute and should be a valid Tag name under parent level:' + newpicpath + ' ! Your value for the new tag:' + newnode + '.')

            nodes = base_node.tdc(newpicpath, checkIsNode=True, checkIsAttr=False,
                                  picpath_attr_separator=picpath_attr_separator,
                                  picpath_text_separator=picpath_text_separator, attr_separator=attr_separator,
                                  node_separator=node_separator, text_separator=text_separator)

            for node in nodes:
                if doForce or hasUpdate:
                    checkDefault = False
                else:
                    checkDefault = True

                node = node.newNode(newnode, checkDefault=checkDefault, clasIsSoftClassNode=False)
                picpaths_print('Created node: ' + node.getFiliation() + '>', both=sbBoth, sb=sb)

                if hasUpdate:
                    pxq_update(node, pxq_updates, sb, picpath_text_separator, verbose=verbose)

                newnodes.append(node)

        return newnodes


    ## - Remove
    elif operation == 'remove':
        listnodes = []

        firstime = True
        for picpath in picpaths:
            if not firstime:
                picpaths_print('', both=sbBoth, sb=sb)
            else:
                firstime = False
            # -- manage / (root) picpath
            picpath, base_node = __picpaths_adapt(root_node, picpath)

            try:  # New Allow exception (printed) when more than one Picpath
                nodes = base_node.tdc(picpath, checkIsNode=True, checkIsAttr=False,
                                      picpath_attr_separator=picpath_attr_separator,
                                      picpath_text_separator=picpath_text_separator, attr_separator=attr_separator,
                                      node_separator=node_separator, text_separator=text_separator)
            except Exception as e:
                if len(picpaths) == 1:
                    raise
                else:
                    sb.write('One Error occured running picpath:' + picpath + '\n' + str(e))
                continue

            listnodes.extend(nodes)

            for node in nodes:
                picpaths_print('Removed: ' + node.getFiliation() + '<', both=sbBoth, sb=sb)
                node.suicide()

        return listnodes


    ## - List
    elif operation == 'list':
        listnodes = []

        firstime = True
        for picpath in picpaths:
            if not firstime:
                picpaths_print('', both=sbBoth, sb=sb)
            else:
                firstime = False
            # -- manage / (root) picpath
            picpath, base_node, indice = __picpaths_adapt(root_node, picpath, doIndice=True)

            # - checks if is Attribute request:
            #   e.g.: jvm/verbose@cl=true,@gc,@jni
            isAttrRequest = True
            last_level = picpath.split(TAG_SEP)[-1]

            if last_level.find(picpath_attr_separator) < 0 and last_level.find('@') < 0:
                isAttrRequest = False
            else:
                last_level = last_level.split(picpath_attr_separator)[-1]
                if last_level.find('=') >= 0: isAttrRequest = False

            try:  # New Allow exception (printed) when more than one Picpath
                if isAttrRequest:
                    ret, node = base_node.tdc(picpath, checkIsNode=False, checkIsAttr=True, doRetNodeIfIsAttr=True,
                                              picpath_attr_separator=picpath_attr_separator,
                                              picpath_text_separator=picpath_text_separator,
                                              attr_separator=attr_separator, node_separator=node_separator,
                                              text_separator=text_separator)
                    picpaths_print(ret, both=sbBoth, sb=sb)
                    listnodes.append(node)
                else:
                    nodes = base_node.tdc(picpath, checkIsNode=True, checkIsAttr=False,
                                          picpath_attr_separator=picpath_attr_separator,
                                          picpath_text_separator=picpath_text_separator, attr_separator=attr_separator,
                                          node_separator=node_separator, text_separator=text_separator)
                    if indice != None:
                        if len(nodes) > indice:
                            nodes = [nodes[indice]]
                        else:
                            continue
                    listnodes.extend(nodes)

                    firstime1 = True
                    for node in nodes:
                        if not firstime1:
                            sb.write('\n')
                        else:
                            firstime1 = False

                        sb.write(node.getFiliation() + '>')
                        # - Write node Attrs
                        attrs = node.getdAttrs()
                        firstime2 = True
                        for attr in node.peerTagdesc.orderedAttrDescs:
                            if attr not in attrs: continue
                            if not firstime2:
                                sb.write(attr_separator)
                            else:
                                firstime2 = False
                                sb.write(' ')
                            sb.write(attr + ':' + str(attrs[attr]))

                        sb.write('\n')
                        # - Write node Child nodes
                        child_nodes = node.getOrderedNodes()
                        for node in child_nodes: sb.write(node.getTag() + '\n')

            except Exception as e:
                if len(picpaths) == 1:
                    raise
                else:
                    sb.write('One Error occured running picpath:' + picpath + '\n' + str(e))
                continue

        return listnodes


def picpaths_print(value, noRet=False, both=True, sb=None):
    if sb == None or both:
        if noRet:
            print(value, end=' ')
        else:
            print(value)
    if sb != None:
        if not noRet: value = value + '\n'
        sb.write(value)


def __picpaths_adapt(root_node, picpath, doIndice=False):
    base_node = root_node
    indice = None

    if doIndice:
        start = picpath.find('[')
        if start > 0 and picpath.endswith(']'):
            indice = picpath[start + 1:-1]
            if indice.isdigit():
                indice = int(indice)
                picpath = picpath[:start]

    if picpath == '/':
        base_node = root_node.getTopParent().getNodes()[0]
        picpath = base_node.getFiliation()[1:]

    elif picpath.startswith('..'):
        base_node = root_node.getAggregatParent()
        if base_node == None or base_node.isFirstNode(): base_node = root_node
        picpath = picpath.replace('..', base_node.getTag(), 1)

    elif picpath.startswith('.'):
        picpath = picpath.replace('.', root_node.getTag(), 1)
    elif picpath.startswith('/'):
        base_node = root_node.getTopParent().getNodes()[0]

    if doIndice:
        return picpath, base_node, indice
    else:
        return picpath, base_node


# --------------------#
# Processor Commands #
# --------------------#


from optparse import OptionParser


class myOptionParser(OptionParser):
    def error(self, message):
        raise epicxception.epicxmlSystemException('Main', 'lpath_command', message)

    def exit(self): pass


##=== xpath ===##

def xpath_options(parser):
    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option("-H", "--HELP", dest="HELP", action="store_true", default=False,
                      help="Shows the processor extended options.")
    parser.add_option("-X", "--force", dest="force", action="store_true", default=False,
                      help="(default False) In conjunction with the new command option will allow the creation of nodes with unchecked attribute values.")
    parser.add_option("-s", "--attr_separator", dest="attr_separator", default=' ',
                      help="Separator when multiple Attributes are returned  (default: space).\nOption --attr_separator (-s) is allowed when not using: --console (-o), --update  (-u), --create (-n) and --remove (-e) options.")
    parser.add_option("-S", "--node_separator", dest="node_separator", default=',',
                      help="Separator when multiple nodes are returned  (default: ,).\nOption --attr_separator (-s) is allowed when not using: --console (-o), --update  (-u), --create (-n) and --remove (-e) options.")
    parser.add_option("-t", "--text_separator", dest="text_separator", default=';',
                      help="Separator when multiple lines of text are returned  (default: ;).\nOption --text_separator (-t) is allowed when not using: --console (-o), --update  (-u), --create (-n) and --remove (-e) options.")
    parser.add_option("-z", "--picpath_attr_separator", dest="picpath_attr_separator", default=',',
                      help="Attribute Separator but for the picpath expression (default: ,).\nOption --picpath_attr_separator (-z) is allowed when not using: --console (-o), --update  (-u), --create (-n) and --remove (-e) options.")
    parser.add_option("-T", "--picpath_text_separator", dest="picpath_text_separator", default=';',
                      help="Text item Separator but for the picpath expression (default: ;).\nOption --picpath_text_separator (-T) is allowed when not using: --console (-o), --update  (-u), --create (-n) and --remove (-e) options.")
    parser.add_option("--print", dest="oprint", action="store_true", default=False,
                      help="(default False) If used the resulting xml file is printed to the output.")
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False,
                      help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")

    # -- exit extended options:
    # og=optparse.OptionGroup(parser, 'Exit extended options', description='The following options are allowed in conjunction with command xpc, show and save.')
    # parser.add_option_group(og)


def save_and_show_options(parser):
    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option('--indent', dest="indent", default=0, type=int, help="Margin for the whole text block.")
    parser.add_option("--steps", dest="steps", default=4, type=int, help="Indentation gap between tag levels.")
    parser.add_option("--space_wrap_eq", dest="space_wrap_eq", action="store_true", default=False,
                      help='(default False) If used, one blank space is writen on the left and rigth of the "=" symbol.')
    parser.add_option("--no_lb_befor_tag", dest="no_lb_befor_tag", action="store_true", default=False,
                      help="(default False) If used, a line break is writen befor each tag.")
    parser.add_option('-n', "--show_dft", dest="show_dft", action="store_true", default=False,
                      help="(default False) If used, Attributes whose match their default values are not shown.")
    parser.add_option("--dft_raise", dest="dft_raise", action="store_true", default=False,
                      help="(default False, advanced) If used and an exception is encountered trying to retreive the default value for one Attribute, the exception is raised.")
    parser.add_option('-N', "--show_none", dest="show_none", action="store_true", default=False,
                      help="(default False) If used, Attributes whose value is None are not shown.")
    parser.add_option('-a', "--all", dest="all", action="store_true", default=False,
                      help="(default False) If used, save all processors.")
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False,
                      help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")


def xpath_usage():
    return """
    Supported xpath commands are: cd, ls, upd, new, rm, cp, mv, set, save, show

    For help on command type: 
        h (or help) <command>
    """


def save_and_show_usage():
    return """
    Save the current mounted  processor,
    or the whole processor with the --all (-a) option.
    The best practice is to use --all.

    Syntax:
    -------
    save [--all]
    """


def xpath_command(root_node, command, pcInfo, fct_save=None, verbose=0, sb=None):
    self_funct = 'xpath_command'
    ALLOWED_COMMANDS = ('show', 'save', 'cd', 'ls', 'upd', 'new', 'rm', 'cp', 'mv', 'set')
    SET_SYNTAX = 'set ATTR = VALUE'
    import shlex

    args = shlex.split(command)
    command = args[0]
    del args[0]

    if command not in ALLOWED_COMMANDS: raise epicxception.epicxmlSystemException('Main', self_funct,
                                                                                  'UnSupported command:' +
                                                                                  command.split()[
                                                                                      0] + '. Supported commands are:' + str(
                                                                                      ALLOWED_COMMANDS)[1:-1].replace(
                                                                                      "'", '') + ' !')

    try:
        parser = myOptionParser(xpath_usage())
    except:
        raise epicxception.epicxmlOptionException('Main', self_funct, 'xxxxxxxxx')

    if command in ('save', 'show'):
        save_and_show_options(parser)
    else:
        xpath_options(parser)

    (options, xpaths) = parser.parse_args(args)

    if verbose == 0: verbose = options.verbose

    if command in ('show', 'save'):
        print_keywords = {'indent': '' * options.indent, 'step': options.steps, 'doSpaceWrapEq': options.space_wrap_eq,
                          'doLBBeforTag': options.no_lb_befor_tag == False, 'noDft': options.show_dft == False,
                          'noDftRaise': options.dft_raise == False, 'noNone': options.show_none == False}
        if len(xpaths) != 0: raise epicxception.epicxmlSystemException('Main', self_funct,
                                                                       'The ' + command + ' command do not support any argument !')

        if command == 'show':
            root_node.printXml(_sb=sb, **print_keywords)
            return

        print_keywords['all'] = options.all
        fct_save(alias=pcInfo.getAlias(), sb=sb, force=options.xforce, **print_keywords)

        return

    ## Treat light command set
    if command == 'set':
        founds = {}

        if len(xpaths) != 3 or xpaths[1] != '=':
            raise epicxception.epicxmlSystemException('Main', self_funct,
                                                      'The command set requires two arguments separated by:= ! Received:' + str(
                                                          xpaths)[1:-1].replace("'", '') + '.')

        attr = xpaths[0]
        value = xpaths[2]
        root_node.setAttr(attr, value, _force=options.force)

        founds[attr] = root_node.getAttr(attr)
        return founds

    ## os:Adapt xpath
    # => All
    _l = list(range(len(xpaths)))
    for i in _l:
        xpath = xpaths[i]
        if xpath.startswith('.') or xpath == epicbase.TAG_SEP: continue
        xpaths[i] = root_node.getTag() + epicbase.TAG_SEP + xpath

    # => ls/cd ..
    if command in ('ls', 'cd'):
        if xpaths == []: xpaths = [root_node.getTag()]

    ## Checks args

    if len(xpaths) == 0:
        print(xpath_usage())
        print('At least one picpath argument is required!')
        return
    if options.HELP:
        parser = myOptionParser(xpath_usage())
        xpath_options(parser)
        parser.print_help()
        return
    if '-h' in args:
        parser.print_help()
        return

    ## Checks options

    if command not in ('new', 'cp', 'mv') and options.force: raise epicxception.epicxmlSystemException('Main',
                                                                                                       self_funct,
                                                                                                       '--force (-x) option can only be used in conjunction with commands new, cp and mv !')

    # - Translate some operations
    if command == 'upd':
        operation = 'update'
    elif command == 'new':
        operation = 'create'
    elif command == 'rm':
        operation = 'remove'
    elif command == 'cp':
        operation = 'copy'
    elif command == 'mv':
        operation = 'move'
    elif command in ('ls', 'cd'):
        operation = 'list'

    ## Run
    nodes = picpaths(
        root_node,
        operation,
        xpaths,
        doForce=options.force,
        attr_separator=options.attr_separator,
        node_separator=options.node_separator,
        text_separator=options.text_separator,
        picpath_attr_separator=options.picpath_attr_separator,
        picpath_text_separator=options.picpath_text_separator,
        sb=sb,
        sbBoth=False,
        verbose=verbose
    )

    ## Print
    if options.oprint: root_node.printXml(noDft=options.no_dft, noDftRaise=options.xforce).getvalue()

    # => cd
    if command == 'cd':
        if nodes == None or len(nodes) == 0:
            raise epicxception.epicxmlSystemException('Main', self_funct, 'Cannot cd, no node found for this picpath !')
        elif len(nodes) > 1:
            raise epicxception.epicxmlSystemException('Main', self_funct,
                                                      'Cannot cd, more than one node found for this picpath !')
        pcInfo.setCurrentNode(nodes[0])
        pcInfo.setCurrentPath(nodes[0].getFiliation())

    return nodes


##=== xql ===##

def xql_command(root_node, command, pcInfo, verbose=0, sb=None):
    return root_node.xql(xqlString=command, sb=sb)


# --------#
# digest #
# --------#



def normalize(file):
    for cars in FS_EQUIV_CARS:
        file = file.replace(cars[0], cars[1])

    return file





# ------ #
# digest #
# ------ #
# A030: +_clasIsSoftClassNode
def digest(file_desc=None, source_desc=None, file_rest=None, source_rest=None, file_source=None, source=None, type=None, capSensitive=True, force=False, showResultingSourceOnly=False, temp_dir=None, tmpl_kws=None, aliases=None, keep_temp_dir=False, get_desc_only=False, _clasIsSoftClassNode=False, verbose=0):
    """
    if file_desc is provided it can be any of the following suffixes: xml, json, yaml, hcl or swagger.
    Notice: json, yaml, hcl are accepted if they were generated by convert. swagger are standard yaml OpenApi swagger files.
    """
    selfMethod = 'digest'
    from kwadlib import tools
    from . import xmlsuckerscraper
    from os import path, mkdir, makedirs
    import pickle
    cache_file = None


    if tmpl_kws==None:tmpl_kws={}

    cache_src = ''
    from_cache = False
    # A011:
    docstring_source = None
    docstring_desc = None
    docstring_rest = None

    # A011:
    if file_source!=None and source!=None: raise epicxception.epicxmlParameterException('Main', selfMethod, 'file_source and source are not allowed together !')
    if file_source!=None and type!=None: raise epicxception.epicxmlParameterException('Main', selfMethod, 'type is not allowed with file_source !')
    if source!=None and type==None: raise epicxception.epicxmlParameterException('Main', selfMethod, 'type is required for parameter source !')
    if temp_dir == None or not isinstance(temp_dir, str) or not path.isdir(temp_dir): raise epicxception.epicxmlSystemException('Main', selfMethod, 'temp_dir:' + str(temp_dir) + ' should exist !')

    if not (get_desc_only and file_source == None and source == None):
        if tmpl_kws == None: tmpl_kws = {}

        if file_source == None and source == None: raise epicxception.epicxmlSystemException('Main', selfMethod, 'file_source or source should be provided !')
        if not isinstance(showResultingSourceOnly, bool): raise epicxception.epicxmlParameterTypeException('Main', selfMethod, 'showResultingSourceOnly', 'bool', str(showResultingSourceOnly))
        if not isinstance(tmpl_kws, dict): raise epicxception.epicxmlParameterTypeException('Main', selfMethod, 'tmpl_kws','dict', str(tmpl_kws))

        ## SOURCES
        #AG001:
        if file_source != None:
            newfile = file_source
            if file_source.endswith('.mako'): newfile = file_source[:-5]  # mako
            if file_source.endswith('.jinja'): newfile = file_source[:-6]  # Jinja:
            suffix = newfile.split('.')[-1]
            file_source = path.normpath(path.abspath(path.normpath(file_source)))
            if not path.isfile(file_source): raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(file_source) + ' should exist !')
            if verbose >= 10:print('epicxmlp/digest: reading file: ' + file_source + '.')

            # Read File source:
            fd = open(file_source, 'rb')
            docstring_source = fd.read().decode("utf-8")
            fd.close()
        else:
            docstring_source = source
            suffix = type
            new_from_source = path.normpath(temp_dir + '/from_source_' + tools.genUid() + '.' +type)
            fd = open(new_from_source, 'w')
            fd.write(docstring_source)
            fd.close()


        # A010: This will convert the file to xml or json:
        docstring_source = tools.Convert.convertSource(docstring_source, file_source if source==None else new_from_source, temp_dir=temp_dir,
            keep_temp_dir=keep_temp_dir, tmpl_kws=tmpl_kws, aliases=aliases)

        doEVEX = False
        """ Because SoftClassNode expression evalution is cost expansive we want to know soon, if we have to run it. """
        from kwadlib.epicwvisitor import ALIAS_BEGIN_CHAR
        for express in (ALIAS_BEGIN_CHAR, 'pxo:', 'pxq:', '__alias__', '__foreach__'):
            if docstring_source.find(express) > 0:
                doEVEX = True
                break

        if showResultingSourceOnly: return docstring_source

        # if is json: parse json instead of xml:
        if suffix in ('json', 'yaml', 'hcl'):
            from_yaml = False
            from_hcl = False
            if suffix == 'yaml':
                from_yaml = True
            elif suffix == 'hcl':
                from_hcl = True

            utop = digestJSON(file_source=file_source if source==None else new_from_source, source=docstring_source, file_desc=file_desc,
                  capSensitive=capSensitive, force=force, temp_dir=temp_dir, from_yaml=from_yaml,
                  from_hcl=from_hcl, keep_temp_dir=keep_temp_dir, _clasIsSoftClassNode=_clasIsSoftClassNode, verbose=verbose)

            utop.getTop().doEVEX = doEVEX
            return utop

        cache_src += docstring_source


    # Read File desc:
    desc_suffix = None
    rest_suffix = None
    if file_desc != None:
        file_desc = path.abspath(path.normpath(file_desc))
        fbase, desc_suffix = path.splitext(file_desc)
        desc_suffix = desc_suffix[1:]
        # Search for any suffix:
        if not path.isfile(file_desc):
            if not path.isfile(file_desc):
                for desc_suffix in ('xml', 'swagger', 'json', 'yaml', 'hcl'):
                    if path.isfile(fbase + '.' + desc_suffix):
                        file_desc = path.normpath(fbase + '.' + desc_suffix)
                        break

        if not path.isfile(file_desc): raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(
            file_desc) + ' should exist or with any suffix: .xml, .swagger, .json, .yaml or .hcl !')

        fd = open(file_desc, 'rb')
        docstring_desc = fd.read().decode("utf-8")
        fd.close()
        cache_src += docstring_desc

        # Read File rest:
        if file_rest != None:
            file_rest = path.abspath(path.normpath(file_rest))
            fbase, rest_suffix = path.splitext(file_rest)
            rest_suffix = rest_suffix[1:]
            # Search for any suffix:
            if not path.isfile(file_rest):
                for rest_suffix in ('xml', 'json', 'yaml', 'hcl'):
                    if path.isfile(fbase + '.' + rest_suffix):
                        file_rest = path.normpath(fbase + '.' + rest_suffix)
                        break

            if not path.isfile(file_rest): raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(
                file_rest) + ' should exist or with any suffix: .xml, .swagger, .json, .yaml or .hcl !')

            fd = open(file_rest, 'rb')
            docstring_rest = fd.read().decode("utf-8")
            fd.close()
            cache_src += docstring_rest

    ## CACHE/LOAD
    if not (get_desc_only and file_source == None) and source == None:
        # Sig files:
        cache_sig = tools.getSignature(cache_src, temp_dir=temp_dir)

        # Sig parameters:
        parm_sig = tools.getSignature(repr({
            'file_desc': file_desc,
            'source_desc': source_desc,
            'file_rest': file_rest,
            'source_rest': source_rest,
            'file_source': file_source,
            'source': source,
            'type': type,
            'capSensitive': capSensitive,
            'force': force,
            'showResultingSourceOnly': showResultingSourceOnly,
            'tmpl_kws': tmpl_kws,
            'aliases': aliases,
            '_clasIsSoftClassNode': _clasIsSoftClassNode,
        }), temp_dir=temp_dir)

        # def digest(file_desc=None, source_desc=None, file_rest=None, source_rest=None, file_source=None, source=None, type=None, capSensitive=True, force=False, showResultingSourceOnly=False, temp_dir=None, tmpl_kws=None, aliases=None, keep_temp_dir=False, get_desc_only=False, _clasIsSoftClassNode=False, verbose=0):

        # Cache file:
        cache_dir = temp_dir + '/cache_epicxmlp'
        _file_source = normalize(file_source)

        fdir, fname = path.split(_file_source)
        fdir = path.normpath(cache_dir + '/' + fdir)
        if not path.isdir(path.normpath(temp_dir + '/cache_epicxmlp')): mkdir(path.normpath(temp_dir + '/cache_epicxmlp'))
        if not path.isdir(fdir): makedirs(fdir)

        cache_file = path.normpath(fdir + '/' + fname) + '.' + cache_sig + '.' + parm_sig + '.p'

        if path.isfile(cache_file) and not get_desc_only:
            if verbose >= 10: print('Loadng from Cache file:', cache_file)
            try:
                fd = open(cache_file, 'rb')
                nn = pickle.load(fd)
                fd.close()
                nn._SessionAfterStore_()
                ## if get_desc_only: return nn.getPeerTagdesc(nn.getFiliation())

                from_cache = True
            except:
                pass


    ## PARSING
    if not from_cache:
        rest = None
        ## get descriptors tree
        from . import epicdesc
        if docstring_desc == None:
            from . import epicdescvisitor

            desc = epicdesc.FirstNode(isPartial=True)
            desc.capSensitive = capSensitive
        else:
            desc = epicdesc.getXmlDesc(docstring_desc, desc_suffix, file = file_desc, capSensitive=capSensitive, doXMLDescIncludes= {'file_source': file_source, 'docstring_source': docstring_source, 'docstring_node': None}, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir, verbose=verbose)

            ## get restrictor tree
            if docstring_rest != None:
                rest = epicdesc.getXmlDesc(docstring_rest, rest_suffix, file = file_rest, capSensitive=capSensitive, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir, verbose=verbose)

        if get_desc_only:
            desc = desc.getChilds()[0]
            return desc

        s = xmlsuckerscraper.XmlSuckerScraper(modName='kwadlib.epicxmlp', docString=docstring_source, trivialParmToFirstNode={'topTagdesc': desc, 'topTagrest': rest, 'force': force}, capSensitive=capSensitive, verbose=verbose)
        # D006: s=xmlsuckerscraper.XmlSuckerScraper(modName = 'kwadlib.epicxmlp', docPath=file_source, trivialParmToFirstNode={'topTagdesc':desc, 'topTagrest':rest, 'force':force}, capSensitive=capSensitive, showResultingSourceOnly=showResultingSourceOnly, temp_dir=temp_dir, tmpl_kws=tmpl_kws, verbose=verbose)
        # D006: if showResultingSourceOnly:return s.source

        """
        # A004: Le 20221022: Observation sur inter 004: report de treatForeah et pxquery de SoftClassNode sur Epixmlp:
        Inutil car pas besoins de ce support au sein de Epixmlp qui supporte deja jinja + mako.
        De plus kcac n'est pas digéré par epicxmlp mais par SoftClassNode.
        La partie qui suit evalExpress reste buggué (si True) car pas entierement reportée (de SoftClassNode vers Epixmlp).
        +Tard voir si on supprime ou adapte. 
        if evalExpress:
            from kwadlib.softclass_node import evalExpress as evex
            evex(top=wn, treatForeach=True)  # A004: Run Special tags support on WideNodes
        """

        # A004: Create real Nodes
        wn = s.foundFirstNode
        # A030:
        v = epicwvisitor.WorkMkNode(clasIsSoftClassNode=_clasIsSoftClassNode)
        wn.getNodes()[0].accept(v)
        nn = v.foundFirstNode
        nn.capSensitive = wn.isCapSensitive()

        v = epicvisitor.WorkCheck()
        nn.accept(v)

        ## check restrictor tree
        if file_rest != None:
            from . import epicdescvisitor
            v = epicdescvisitor.WorkCheckRestrictor(descriptor=desc)
            rest.accept(v)

        # -- Because of the weak ref mechanism, of the aggregatParent tree:
        # the Top Node: need to be hard referenced by the user top node, or it would disappear (as been garbagde).
        # And the user Top Node would have no parent !

        nn.setFiles(file_source=file_source, file_desc=file_desc, file_rest=file_rest)

        ## CACHE/STORE
        if cache_file != None and not path.isfile(cache_file):
            ra = nn.getRepozInfos()
            nn.clearRepozInfos()
            nn._SessionBeforStore_()
            file = open(cache_file, 'wb')
            file.write(pickle.dumps(nn, protocol=CPICKLE_OPTIMIZED_PROTOCOL))
            file.close()
            nn._SessionAfterStore_()
            if ra != None: nn.setRepozInfos(ra['repoz'], ra['alias'])

    # User top Node:
    nn.doEVEX = doEVEX
    utop = nn.getNodes()[0]
    ## utop.getTop().setFiles(file_source=file_source, file_desc=file_desc, file_rest=file_rest)
    utop.hardLinkTopParent()

    return utop


# -------------- #
# digestJSON     #
# -------------- #
def digestJSON(file_source=None, source=None, file_desc=None, capSensitive=True, force=False, temp_dir=None, from_yaml=False, from_hcl=False, returnDesc=False, keep_temp_dir=False, _clasIsSoftClassNode=False, verbose=0):
    selfMethod = 'digest'
    from os import path
    import json as jsonmod

    if file_source == None: raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(file_source) + ' should exist !')
    if temp_dir == None or not isinstance(temp_dir, str) or not path.isdir(temp_dir): raise epicxception.epicxmlSystemException('Main', selfMethod, 'temp_dir:' + str(temp_dir) + ' should exist !')

    # Read file_source:
    file_source = path.normpath(path.abspath(path.normpath(file_source)))
    if not path.isfile(file_source): raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(
        file_source) + ' should exist or with any suffix: .xml, .json, .yaml or .hcl !')
    if verbose >= 10: print('epicxmlp/digestjson: reading file: ' + file_source + '.')
    if source != None:
        docstring_source = source
    else:
        fd = open(file_source, 'rb')
        docstring_source = fd.read().decode("utf-8")
        fd.close()

    try:
        json = jsonmod.loads(docstring_source)
    except Exception as e:
        raise epicxception.epicxmlSystemException('Main', selfMethod, 'Unable to parse to JSON, File:' + str(file_source) + '! SubException  is: %s' % e)

    # Read File desc:
    from . import epicdesc
    if file_desc != None:
        file_desc = path.abspath(path.normpath(file_desc))
        fbase, desc_suffix = path.splitext(file_desc)
        desc_suffix = desc_suffix[1:]
        # Search for any suffix:
        if not path.isfile(file_desc):
            for desc_suffix in ('xml', 'json', 'yaml', 'hcl', 'swagger'):
                if path.isfile(fbase + '.' + desc_suffix):
                    file_desc = path.normpath(fbase + '.' + desc_suffix)
                    break

        if not path.isfile(file_desc): raise epicxception.epicxmlSystemException('Main', selfMethod, 'File:' + str(file_desc) + ' should exist !')

        fd = open(file_desc, 'rb')
        docstring_desc = fd.read().decode("utf-8")
        fd.close()
        
        # 6070:
        desc = epicdesc.getXmlDesc(docstring_desc, desc_suffix, file = file_desc, doXMLDescIncludes= {'file_source': file_source, 'docstring_source': docstring_source, 'docstring_node': None}, capSensitive=capSensitive, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir, verbose=verbose)
        desc.capSensitive = capSensitive
        parentNode = FirstNode(topTagdesc=desc, force=False)
    else:
        force = True
        from . import epicdescvisitor
        desc = epicdesc.FirstNode(isPartial=True)
        desc.capSensitive = capSensitive
        parentNode = FirstNode(topTagdesc=desc, force=True)

    # Prepare File desc:
    parentNode.capSensitive = capSensitive
    parentNode.peerTagdesc = desc
    if file_desc == None:
        parentNode.setFiles(file_source=file_source)
    else:
        parentNode.setFiles(file_source=file_source, file_desc=file_desc)

    prefix = 'Parsing file: %s to JSON' % file_source
    if not isinstance(json, dict): raise epicxception.epicxmlParameterException('Node', selfMethod, prefix + '. First attribute must be a dict ! json is: %s' % jsonmod.dumps(json))
    keys = list(json.keys())

    # Gess first Tag name:
    # --------------------
    if len(json) == 1:
        tag = keys[0]
        # M018: value = json[tag]
        ## M031: value = json
        value = json[tag]
    else:
        if not from_yaml:
            raise epicxception.epicxmlParameterException('Node', selfMethod, prefix + 'First dict attribute must have an unique key ! Founds: %s' % ','.join(keys))
        """
        if 'kind' in json:
            tag = json['kind'].lower()  # Kub exception
            value = json
        else:
            # Gess Tag from parent desc's unique child:
            desc = parentNode.getPeerTagdesc(parentNode.getFiliation())
            if not desc.isPartial():
                desc_childs = desc.getChilds()
                if len(desc_childs) != 1:
                    raise epicxception.epicxmlSystemException('Main', selfMethod, prefix + 'Top Tag Guessing> This tag s descriptor should contains one unique child ! Found multiple childs: %s on this tag descriptor.' % ', '.join(list(map(lambda c: c.getTag(), desc_childs))))
                tag = desc_childs[0].getTag()
                value = json
        """
        if not desc.isPartial():
            # Gess Tag from parent desc's unique child:
            ## desc = parentNode.getPeerTagdesc(parentNode.getFiliation())
            desc = parentNode.peerTagdesc
            desc_childs = desc.getChilds()
            if len(desc_childs) != 1:
                raise epicxception.epicxmlSystemException('Main', selfMethod, prefix + 'Top Tag Guessing> This tag s descriptor should contains one unique child ! Found multiple childs: %s on this tag descriptor.' % ', '.join(list(map(lambda c: c.getTag(), desc_childs))))
            tag = desc_childs[0].getName()
            value = json
        elif 'kind' in json:
            # M042: tag = json['kind'].lower()  # Kub exception
            tag = json['kind']  # Kub exception
            value = json
        else:
            raise epicxception.epicxmlSystemException('Main', selfMethod, prefix + '\nCannot parse yaml with no descriptor file !')

    # Call:
    # -----
    parentNode.parseJSON(tag, value, force=force, from_yaml=from_yaml, from_hcl=from_hcl, clasIsSoftClassNode=_clasIsSoftClassNode)

    """
    # A004: Create real Nodes
    v = epicwvisitor.WorkMkNode()
    wn.getNodes()[0].accept(v)
    nn = v.foundFirstNode
    nn.capSensitive = wn.isCapSensitive()
    v = epicvisitor.WorkCheck()
    nn.accept(v)
    """

    # -- Because of the weak ref mechanism, of the aggregatParent tree:
    # the Top Node: need to be hard referenced by the user top node, or it would disappear (as been garbagde).
    # And the user Top Node would have no parent !

    # User top Node:
    utop = parentNode.getNodes()[0]
    utop.hardLinkTopParent()

    if returnDesc:return utop, desc

    return utop


# ----------------- #
# digestOPenApiJSON #
# ----------------- #

def makeEmptyNode(file_source = None, noParentWeakRef=False):
    from kwadlib.security.crypting import sanitize_path
    if file_source!=None: sanitize_path(file_source)
    from kwadlib import epicdesc
    desc = epicdesc.FirstNode(isPartial=True)
    desc.capSensitive = True
    parentNode = FirstNode(topTagdesc=desc, noParentWeakRef=noParentWeakRef, force=True)
    # Prepare File desc:
    parentNode.capSensitive = True
    parentNode.peerTagdesc = desc
    if file_source!=None: parentNode.setFiles(file_source=file_source)
    else: parentNode.setFiles(file_source=file_source)

    return parentNode


def mergeDescToNode(node_desc, temp_dir, node=None, source=None, _clasIsSoftClassNode=False, verbose=0):
    self_funct='mergeDescToNode'
    """
    In case node and nodesc was generated separatly, but node was not created with this node_desc descriptor.
    Will recreate node based on node_desc as descriptor.
    """
    from kwadlib.tools import genUid
    if (node == None and source == None) or (node != None and source != None):raise epicxception.epicxmlParameterException('Main', self_funct, 'One and only one of node or source is required !')
    if node!=None:source = node.printXml(doChild=True, indent='', step=4, doSpaceWrapEq=False, doLBBeforTag=True, doLBBeforAttr=True, noDft=False, noDftRaise=False, noNone=False, noComment=False, _nbstep=0, _sb=None, fct_omit=None).getvalue()
    fdesc = temp_dir + '/node_desc_' + genUid() + '.xml'
    desc = node_desc.printXml(doChild=True, indent='', step=4, doSpaceWrapEq=False, doLBBeforTag=True, doLBBeforAttr=True, noDft=False, noDftRaise=False, noNone=False, noComment=False, _nbstep=0, _sb=None, fct_omit=None).getvalue()
    with open(fdesc, 'w') as f: f.write(desc)
    node = digest(file_desc=fdesc, source=source, type='xml', temp_dir=temp_dir, keep_temp_dir=False, _clasIsSoftClassNode=_clasIsSoftClassNode, verbose=verbose)

    return node

#  MainTest ===================================================================/
if __name__ == '__main__':
    pass