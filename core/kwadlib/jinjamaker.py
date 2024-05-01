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





from . import tmplxception


class  JinjaMaker:
    """
    Wrapper on Jinja2.
    """
        
    def __init__(self, sourceIn=None, fileIn=None, vars=None, fileOut=None, tempDir=None, template_lookup=None):
        selfMethod='__init__'
        from os import path
        self.__sourceIn=sourceIn
        self.__fileIn=fileIn
        if template_lookup==None:template_lookup=[]
        self.__template_lookup=template_lookup
        if vars==None:self.__vars={}
        else:self.__vars=vars
        self.__fileOut=fileOut
        
        if (sourceIn!=None and fileIn!=None) or (sourceIn==None and fileIn==None):raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Just one of sourceIn or fileIn must given.')                                    
        if tempDir==None:raise tmplxception.tmplmkParameterTypeException(str(self.__class__), selfMethod, 'tempDir', 'path', str(tempDir))
        if not path.isdir(path.normpath(tempDir)):raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'The tempDir :' + str(path.normpath(path.realpath(tempDir))) + ' must exist !')
        if not isinstance(template_lookup, list):raise tmplxception.tmplmkParameterTypeException(str(self.__class__), selfMethod, 'template_lookup', 'list', str(template_lookup))
        else:self.__tempDir=path.normpath(path.realpath(tempDir))

        if fileIn!=None:
            
            fileIn=path.normpath(str(fileIn))            
            if not path.isfile(fileIn):raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'fileIn: ' + fileIn + ' Must Exist.')                                    
            fd=open(fileIn, 'r')
            self.__sourceIn=fd.read()
            fd.close()
        else:
            if not isinstance(sourceIn, str):raise tmplxception.tmplmkParameterTypeException(str(self.__class__), selfMethod, 'sourceIn', 'str', str(sourceIn))
            self.__sourceIn=sourceIn
            
        if not isinstance(self.__vars, dict):raise tmplxception.tmplmkParameterTypeException(str(self.__class__), selfMethod, 'vars', 'dict', str(vars))

        if self.__fileOut!=None:
            self.__fileOut=path.normpath(str(self.__fileOut))
            fd=open(self.__fileOut, 'wb')
            fd.close()
            
    # A003
    def setRepozInfos(self, repoz, alias):
        import weakref
        self.__repoz=weakref.ref(repoz)   
        self.__alias=alias       

    def getRepozInfos(self):
        if self.__repoz==None or self.__repoz()==None:return None
        return {'repoz': self.__repoz(), 'alias': self.__alias}

    def clearRepozInfos(self):
        self.__repoz=None
        self.__alias=None
        
    def _SessionBeforStore_(self):
        self.clearRepozInfos()

    def operate(self):
        selfMethod='operate'
        from jinja2 import Environment, PackageLoader, select_autoescape

        env = Environment(
            loader=PackageLoader(self.__template_lookup),
            autoescape=select_autoescape(
                enabled_extensions=('jinja',),
                default_for_string=True,
                default=True,
            )
        )

        try:
            # template = env.from_string('Hello {{ name }}!')
            # template.render({'name': 'John Doe'})
            template = env.from_string(self.__sourceIn)
            result = template.render(self.__vars)
                
        except Exception as e:
            if self.__fileOut!=None:fo=' on file:' + self.__fileOut
            else:fo=''
            raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Jinja Template processing error' + fo + ' ! SubException is: ' + str(e) + '.')

        except:
            if self.__fileOut!=None:fo=' on file:' + self.__fileOut
            else:fo=''
            raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Jinja Template processing error' + fo + ' !')

        if self.__fileOut!=None:
            fd=open(self.__fileOut, 'wb')
            fd.write(bytes(result, 'utf-8'))
            fd.close()
        
        return result

    def show(self, sb=None, **prt_keywords):
        """ Facade for Repository """
        from io import StringIO
        if sb==None:sb=StringIO()

        sb.write(self.operate())

        return sb



#--------------------#
# Processor Commands #
#--------------------#


#=== xpath ===#


def xpath_options(parser):
    import optparse

    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option("-H", "--HELP", dest="HELP", action="store_true", default=False, help="Shows the processor extended options.")
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False, help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")

    #-- Print extended options:
    og=optparse.OptionGroup(parser, 'Print extended options', description='The following options are allowed in conjunction with command show and save commands.')
    parser.add_option_group(og)
    
    parser.add_option("-a", "--alias", dest="alias", help="The repoz entry alias.")
    
def save_and_show_options(parser):

    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option('-a', "--all", dest="all", action="store_true", default=False, help="(default False) If used, save all processors.")
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False, help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")

def xpath_usage():
    return """
    Supported xpath commands are: save, show

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

def xpath_command(tm, command, pcInfo, fct_save=None, verbose=0, sb=None):
    self_funct='xpath_command'
    ALLOWED_COMMANDS=('show', 'save')
    import optparse
    import shlex
    
    args=shlex.split(command)
    command=args[0]
    del args[0]
    
    if command not in ALLOWED_COMMANDS:raise tmplxception.tmplmkSystemException('Main', self_funct, 'UnSupported command:' + command.split()[0] + '. Supported commands are:' + str(ALLOWED_COMMANDS)[1:-1].replace("'", '') + ' !')
    
    parser = optparse.OptionParser(xpath_usage())
    if command in ('save', 'show'):save_and_show_options(parser)    
    else:xpath_options(parser)
    
    try:(options, xpaths) = parser.parse_args(args)    
    except:raise tmplxception.tmplmkOptionException('Main', self_funct) 
    
    if verbose==0:verbose=options.verbose
        
    if command in ('show', 'save'):
        
        if command=='show':

            if len(xpaths)!=0:raise tmplxception.epicxmlSystemException('Main', self_funct, 'No arguments is allowed with the show command !')
            tm.show(sb=sb, **{})
            return

        print_keywords={'all':options.all}
        fct_save(alias=pcInfo.getAlias(), sb=sb, force=options.xforce, **print_keywords)
        return




#------#
# Main #
#------#


def main(args):
    from .tmplmaker import TmplMaker
    temp=TmplMaker(fileIn='test.tmpl', fileOut='test.out', vars={'var1':'yes', 'var2':[1, 2, 3], 'A1':'1234', 'A2':456, 'A3':'1234'})
    #print temp.operate()

if __name__ == '__main__':  
    import sys
    main(sys.argv)