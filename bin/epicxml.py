#!/usr/bin/python3
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
epicxml is a versatile permisive xml parser.
"""


SELF_MODULE='epicxml'


import utils
KAST_HOME=utils.getInstallDir()
KAST_PLUGINS = utils.getPluginsDir()



def doImport():
    global epicxception
    global epicxmlp
    
    from kwadlib import epicxception as _epicxception
    from kwadlib import epicxmlp as _epicxmlp
    
    epicxception=_epicxception
    epicxmlp=_epicxmlp



##########
## Main ##
##########


def usage():
    return """
    epicxml.py -f /my/xml/file -t TD
    or 
    epicxml.py -f /my/xml/file -T TDC

    Syntax:
    -------
    TD (Top down query):  TAG[/TAG]@ATTR[,ATTR]

    ex: tag1/tag2/tag3@attr3
    
    This will retreive attribute: attr3 on node with tag: tag3.
    tag3 is child of tag2.
    tag2 is child of tag1.
    
    ex: tag1/tag2/tag3@*
    
    Retreives all attributes/values
    
    
    TDC (Top down complete query): TAG[@ATTR=VALUE[,@ATTR=VALUE]],@ATTR Tag sep:/

    ex: tag1/tag2@attr1=val1,@attr2=val2/tag3@attr1,attr2,attr3
        
    This will retreive the attributes: attr1,attr2,attr3 on node with tag: tag3.
    tag3 is child of tag2 (matching attributes/values: attr1=val1,@attr2=val2.
    tag2 is child of tag1.
    
    ex: tag1/tag2@attr1=val1,@attr2=val2/tag3@*

    Retreives all attributes/values
    
    Note:
    -----
    Retreived node must be unique at each intermediate level.
    Last level accepts multiple nodes.
    """

def main(file, xfiles=False, options=None, verbose=0, attr_separator=None, node_separator=None):
        top=epicxmlp.digest(file_source=file, file_desc=options.file_desc, capSensitive=options.cap_sensitive, force=options.force, verbose=verbose)

        if options.td!=None:
            ## TD Check:
            ##----------
            ## pxq='tag1_1.tag2.tag3.attr3'
            result=top.td(options.td, checkIsNode=False, checkIsAttr=True, checkIsUnique=False, attr_separator=attr_separator, node_separator=node_separator)
            
        else:
            ## TDC Check:
            ##-----------
            ## pxq='t:tag1,a:attr1=val1.1,a:attr4=val4.2.t:tag2,a:attr2=val2.1.t:tag3,a:attr3'
            result=top.tdc(options.tdc, checkIsNode=False, checkIsAttr=True, checkIsUnique=False, attr_separator=attr_separator, node_separator=node_separator)
            
        if xfiles:result = file + ':' + result
        print(result)

    
if __name__ == '__main__':
    self_funct='main'
    import optparse
    from os import path
    global VERBOSE
    VERBOSE=None
    import sys


    ## Set paths
    for _path in (KAST_HOME + '/core', KAST_PLUGINS + ''):
        if not _path in sys.path:sys.path.append(_path)
    doImport()

    parser = optparse.OptionParser(usage())
    parser.add_option("-v", "--verbose", dest="verbose", type=int, help="The verbose level.")
    parser.add_option("-t", "--td", dest="td", help="Top down pattern.")
    parser.add_option("-T", "--tdc", dest="tdc", help="Top down complete pattern.")
    parser.add_option("-s", "--attr_separator", dest="attr_separator", default=' ', help="Separator when multiple Attributes are returned.")
    parser.add_option("-S", "--node_separator", dest="node_separator", default=',', help="Separator when multiple Attributes are returned.")
    parser.add_option("-H", "--HELP", dest="HELP", help="Extended help.")

    #-- advanced options:
    og=optparse.OptionGroup(parser, 'Advanced options', description=None)
    parser.add_option_group(og)
    og.add_option("-d", "--file_desc", dest="file_desc", help="An xml descriptor file.")
    og.add_option("-i", "--cap_sensitive", dest="cap_sensitive", action="store_true", default=True, help="(default True) Is this xml fie cap sensitive.")
    og.add_option("-F", "--force", dest="force", action="store_true", default=False, help="(default False) force writing with no check and regardingless to descriptor file.")

    
    (options, args) = parser.parse_args()
    
    try:
        if options.HELP:
            print('TODO')
            sys.exit()
            
        if options.td!=None and options.tdc!=None:raise epicxception.epicxmlSystemException('Main', self_funct, 'Just one of options --td (-t) or -tdc (-T) must be guiven.Not both !')
        if (options.td, options.tdc)==(None, None):raise epicxception.epicxmlSystemException('Main', self_funct, 'One of options --td (-t) or -tdc (-T) must be guiven ! ')
    
        if sys.stdin.isatty() and len(args)==0:
            print(usage())
            raise epicxception.epicxmlSystemException('Main', self_funct, 'At least one xml file must be guiven ! ')
        files=args
        if len(files)>1:xfiles=True
        else:xfiles=False
        
        ## run
        if not sys.stdin.isatty():                                              # Pipe management
            xfiles=True
            for line in sys.stdin:
                print(line.rstrip('\n'))
                file=line.rstrip('\n')
                main(file, xfiles=xfiles, options=options, verbose=options.verbose, attr_separator=options.attr_separator, node_separator=options.node_separator)
        for file in files:main(file, xfiles=xfiles, options=options, verbose=options.verbose, attr_separator=options.attr_separator, node_separator=options.node_separator)
        
    except Exception as e:
        
        if VERBOSE==None:
            try:VERBOSE=int(options.verbose)
            except:VERBOSE=0
        if VERBOSE>=10:raise

        import sys
        if not hasattr(e, 'short1') or not hasattr(e, 'short2'):message=e.__class__.__name__ + ': ' + str(e)
        elif VERBOSE<5:message=e.short1()
        elif VERBOSE>=5:message=e.short2()
        sys.stderr.write(message + '\n')
        sys.exit(2)