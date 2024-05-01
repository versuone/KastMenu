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



# 20120306:A001


SELF_MODULE='apimenup'

from kwadlib.default import *
from . import tools
from . import kastmenuxception
APIMENU_HOME=tools.getInstallDir()
LANG_DIR=APIMENU_HOME + '/langs'
MULTILANG_SHAPE='%lang/<file_path>/<key>'
MULTILANG_LINE_SHAPE='key=<some text>'
USER_TEMP_DIR = getUserKastTempDir()
USER_LANGS_DIR =  getLangsDir()





class MultiLang:

    def __init__(self):
        selfMethod='__init__'
        from os import path, mkdir
        self.__verbose=0
        self.__lang_dir=None
        self.__user_langs_dir = USER_LANGS_DIR
        if not path.isdir(self.__user_langs_dir):mkdir(self.__user_langs_dir)
    
    def init(self, verbose=0, lang_dir=None, temp_dir=None):
        selfMethod='init'
        #A001:
        if temp_dir!=None:
            if not isinstance(temp_dir, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'temp_dir', 'temp_dir', str(temp_dir))
        else:self.__temp_dir=USER_TEMP_DIR
        if lang_dir!=None:
            lang_dir=LANG_DIR
            self.__lang_dir = lang_dir.replace('$install_dir', APIMENU_HOME)
        else:self.__lang_dir=getLangsDir()

        self.__verbose=verbose

        return self
    
    def __getFile(self, file):
        selfMethod='__getFile'
        """ Please note that anydbm do not support to be affected to a dictionary of fd ==> we do not store anydbm references """
        import dbm
        from os import path
        from io import StringIO
        
        _file=path.abspath(path.normpath(self.__lang_dir + '/' + file))
        if not path.isfile(_file):
            if self.__verbose>0:kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'MultiLang, File:' + str(_file) + ', Not found !').warn()
            return None
        
        fdb=self.__user_langs_dir + '/' + file + '.db'
        fsig=self.__user_langs_dir + '/' + file + '.sig'
        
        #D001:if (not path.isfile(fsig) or not tools.checkSig(fsig, [_file])) or not path.isfile(fdb):
        # M001:
        if (not path.isfile(fsig) or not tools.checkSig(fsig, [_file], temp_dir=self.__temp_dir)) or not path.isfile(fdb):
            from os import remove
            if path.isfile(fdb):remove(fdb)

            fd=open(_file)
            lines=fd.readlines()
            fd.close()

            ## Check line endind with \
            wrk_lines=lines
            lines=[]
            sb=StringIO()
            for line in wrk_lines:
                if line=='' or line.isspace() or line.startswith('#'):continue

                line=line.strip()
                if line.endswith('\\'):
                    sb.write(line[:-1] + '\n')
                    continue
                sb.write(line)
                
                line=sb.getvalue()
                sb=StringIO()
                if line.find('=')<=0:raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'MultiLang, file:' + str(_file) + ' Uncorrect line:' + line + ' ! Correct line shape is: ' + MULTILANG_LINE_SHAPE + '.')
                lines.append(line)

                
            ## Feed anydbm
            try:
                fds=dbm.open(fdb, 'c')
            except:
                import sys, traceback
                traceback.print_exc(file=sys.stdout)
                raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'MultiLang, Unable to open file: ' + fdb + '  in write mode !')
            
            for line in lines:
                # - key
                spl=line.split('=')                
                key=spl[0].strip()
                del spl[0]
                # - value
                value='='.join(spl)                
                fds[key]=value
            lines=None
            fds.close()
            fds=None
            
            fd=open(fsig, 'wb')
            fd.write(bytes(tools.getFileSignature(_file), 'utf-8'))
            fd.close()

        return dbm.open(fdb)
    
    def convert(self, *fields):
        selfMethod='convert'
        has_error=False
        if not isinstance(fields, (list, tuple)):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'fields', 'list', str(fields))
        founds=[]
        
        for field in fields:

            while True:
                if field==None or not isinstance(field, str):break
                if not field.startswith('%lang/'):break
                
                fds=field.split('/')
                if len(fds)!=3:
                    if self.__verbose>0:kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'MultiLang: Bad structure for MultiLang suppport for field:' + field + ' ! The MultiLang Shape is:' + MULTILANG_SHAPE + '.').warn()
                    has_error=True
                    break
                
                del fds[0]
                file=fds[0]
                key=fds[1].split('/')[-1]
                
                fds=self.__getFile(file)
                if fds==None:
                    has_error=True
                    break
                
                if not key in fds:
                    if self.__verbose>0:kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'MultiLang: Unknown key:' + key + ', in MultiLang file:' + file + ' !').warn()
                    has_error=True
                    break

                field=fds[key].decode("utf-8")
                break

            founds.append(field)
            
        if has_error and self.__verbose>=3:
            print()
            raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Some errors encountred while parsing lang conversion! Please consult previous messages.')

        if len(founds)==1:return founds[0]
        else:return founds
        
    def convertWk(self, wks):
        if wks==None:return wks
        if '*label' in wks:wks['*label']=self.convert(wks['*label'])
        if '*help' in wks:wks['*help']=self.convert(wks['*help'])
        if '*lhelp' in wks:wks['*lhelp']=self.convert(wks['*lhelp'])
    
MULTILANG=MultiLang()
