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




SELF_MODULE='crypt_password'



import utils
KAST_HOME=utils.getInstallDir()


def doImport():
    global tools
    global xception
    global KAST_HOME
    
    from kwadlib import tools as _tools
    from kwadlib import xception as _xception
    
    tools=_tools
    xception=_xception
    
def setVerbose(verbose):
    global VERBOSE
    VERBOSE=verbose

def run(file):
    self_funct='run'
    out_contents=[]
    passed=False
    
    # read file
    fd=open(file, 'rb')
    in_contents=fd.readlines()
    fd.close()

    for line in in_contents:
        out_contents.append(line)
        
        line=line.strip()
        if line.startswith('#'):continue
        lines=line.split()
        if not len(lines)>2:continue
        
        key, equal, value=lines[0], lines[1], lines[2]
        if not equal=='=':continue
        if not key.startswith('software_'):continue
        if not key.endswith('_password'):continue
        if value.startswith('?'):continue
        passed=True
        
        repsc=tools.ReproductibleCrypt()
        lines[2]='?' + repsc.encode(value)
        out_contents[len(out_contents) -1]=' '.join(lines) + '\n'
    
    # write file
    if passed:
        print('Rewriting crypted file:' + file + '.')
        fd=open(file, 'wb')
        for line in out_contents:fd.write(bytes(line, 'utf-8'))
        fd.close()



##########
## Main ##
##########



def usage():
    return """  
    crypt_passwords <file>
    
    crypt_passwords -h: for help.

    Password crypting for kwad.attrs file.
    Will crypt all attributes whose name end with "_password" within the referenced file.
    
    File: The path to the kwad.attrs file to crypt.
    
    Note:
    This file name must end with ".attrs".
    """
  
def main():
    self_funct='main'
    from os import path    
    import optparse
    import sys
    global VERBOSE
    VERBOSE=None
    file=None

    
    ## Set paths
    for _path in ('core',):
        _path=path.normpath(KAST_HOME + '/' + _path)
        if not _path in sys.path:sys.path.append(_path)
    doImport()

    parser = optparse.OptionParser(usage())
    parser.add_option("-v", "--verbose", dest="verbose", default=0, type=int, help="The verbose level. A number from 0 to 30.")

    (options, args) = parser.parse_args()

    try:
        if len(args)==0:
            print(usage())
            raise xception.kwadSystemException('Main', self_funct, 'Argument <file> cannot be none ! ')
        elif len(args)!=1:
            print(usage())
            raise xception.kwadSystemException('Main', self_funct, 'Only one Argument <file> is accepted ! ')
        file=args[0]

        if not path.isfile(file):raise xception.kwadSystemException('Main', self_funct, 'Option file (-f): Incorrect, the file: ' + file + ' must exist !')
        if not file.endswith('.attrs'):raise xception.kwadSystemException('Main', self_funct, 'Option file (-f): Incorrect, the file name: ' + file + ' must end with ".attrs" !')
        
        ## Run SoftClasses
        run(file)
        
        ## Set globals
        setVerbose(options.verbose)

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

if __name__ == '__main__':
    main()
