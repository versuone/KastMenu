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
# 2012/09/05  | 003 | Support of kwad_attrs : softclass_access_alloweds, softclass_access_denieds and softclass_restriction_...
# 2013/09/13  | 050 | SoftClass Version Directory cross implementation
# 2015/12/06  | 004 | Add Support for optoxml.
# 2015/12/06  | 005 | Support for SoftClass.doRead() : method getSrcTop should return the original Source node.
# 2015/01/28  | 006 | subprocess calls replaced by: execute, cause: subprocess do Not return stdout !!!
# 2015/03/22  | 007 | highLight support.
# 2015/04/17  | 008 | Support of injector external file: <kwad_dir>/plugins/categories/middleware/softclasses/injectors.attrs.
# 2022/08/19  | 010 | Along xml, Accept yaml and hcl for softclasses and combined softclass files.
# 2022/08/29  | 011 | Python 2 to 3 conversion no more popen2
# 2022/11/16  | 012 | Bug correcion with Python2 to Python3
# 2023/04/24  | M013 | Koption now fully supports wks.
# 2023/04/28  | ANNUL003: of softclass_access_alloweds, softclass_access_denieds and softclass_restriction_... from kwad_attrs. See ANNUL003 in softclass_node.
# 2023/04/30  | ANNU008: Now there is only one injector: python: pyt.
# 2023/07/20  | M014 | Adding add_output_option in use by OptStruct along with add_option.
# 2023/07/29  | M015 | Adding password management:
#                       if wks['*password'] is True: This means this field is a password and must be managed as well.
#                       So we will add a special callback to this field that will allow it to be empty (in OptParse.add_option)).
#                       The cinematic will be the following and will be managed by KOption:
#                       - if passord has a value (--password value) : this will be used as the password.
#                       - if passord has no value or has a value starting with /:
#                           An Exception: KwadkOptionSecurePasswordInput will be thrown:
#                           with the list of all field password that must be managed a sercure way.
#                           mod attributte of the Exception will be either :
#                           - "prompt" if no value was provided or
#                           - "file" with value if was starting by /
#                           It is the responsability of the interactive interface receiving this Exception, to manage password input the rigth way.
# 2023/10/07  | M016 | todo later: _is_multiple_ was removed cause epicmlp do not manage attr starting with: _
#                    | we'll see later how to propagate the is_multiple information.
# 2023/10/10  | M017 | Adding support of generating Lang help (needed by optstruct).


SELF_MODULE='tools'
from kwadlib.default import *
DESIGN_NOTICE='Designed by kwad at dkwad@dkwad.org and dkwad@dkwad.org.'
ACTION_ATTRS_FORMAT='softclass = {software:SOFTWARE,name:ACTION,by:BY_WHO,license_name:LICENCE_NAME,license_file:LICENCE_FILE,multiple:TRUE_FALSE,version:VERSION,autors:(AUTOR1,),site:WEB_SITE}'
INJECTOR_ATTRS={}
KNOWN_INJECTORS=('pyt',)
KAST_SCOPE_EXCEPT_CARS=(',', ';', '/', '\\', '|', '"', "'", '<', '>', '?', '!', '$', '*', '+', '-', '.')
TEMP_DIR = None
SUPPORTED_SUFFIXES = ('xml', 'yaml', 'hcl', 'json')
ALIAS_BEGIN_CHAR='$['
ALIAS_END_CHAR=']'

# A007:
HIGHLIGHT_BEGIN='>>>high_light>>>{MORE}'
HIGHLIGHT_END='<<<high_light<<<'



import random
random.seed()

from kwadlib import wk
from kwadlib import ct as CoolTyping
from kwadlib import epicxception, xception
_eval=CoolTyping._eval
import re
RE_COMMENT = re.compile('<!--.*-->')
from datetime import datetime

def printlog(fromf, message, level=0, verbose=0):
    if verbose >= level:print (str(datetime.now()) + ' [%s] ' % fromf + message)


                                                    #--------------------#
                                                    #  Py/Jy file access #
                                                    #--------------------#

# -------- FILE CONVERTION [Begin] ------------#
# A010:
class Convert:

    @staticmethod
    def isSupportedFileType(file):
        if file.split('.')[-1] not in SUPPORTED_SUFFIXES:return False
        return True

    @staticmethod
    def resolveAliases(source, aliases):
        if aliases==None:return source
        if source.find(ALIAS_BEGIN_CHAR)<0: return source
        keys = list(aliases.keys())

        for key in keys:
            source = source.replace(ALIAS_BEGIN_CHAR + key + ALIAS_END_CHAR, str(aliases[key]))

        return source

    @staticmethod
    def convertSource(source, file, temp_dir = False, keep_temp_dir = False, tmpl_kws=None, aliases = None):
        self_funct = 'convertSource'
        newfile = file

        ## Mako:
        if file.endswith('.mako'):
            newfile = file[:-5]
            if not Convert.isSupportedFileType(newfile):raise xception.kwadParameterException('Main', self_funct, 'File: %s, Unsupported file type ! Unable to find expected type. Should end with either xml.mako or yaml.mako or hcl.mako.', file)
            source = Convert.mako(source, temp_dir=temp_dir, tmpl_kws=tmpl_kws)
            if keep_temp_dir:
                fd = open(newfile, 'wb')
                fd.write(bytes(source, 'utf-8'))
                fd.close()
        ## Jinja:
        elif file.endswith('.jinja'):
            newfile = file[:-6]
            if not Convert.isSupportedFileType(newfile): raise xception.kwadParameterException('Main', self_funct, 'File: %s, Unsupported file type ! Unable to find expected type. Should end with either xml.jinja or yaml.jinja or hcl.jinja.', file)
            source = Convert.jinja(source, temp_dir=temp_dir, tmpl_kws=tmpl_kws) # A005
            if keep_temp_dir:
                fd = open(newfile, 'wb')
                fd.write(bytes(source, 'utf-8'))
                fd.close()

        ## yaml, hcl, xml
        """
        This will convert the file to xml or json and put the xml into temp dir.
        """
        spl = newfile.split('.')
        suffix = spl[-1]
        basename = '.'.join(spl[:-1])
        new_file = temp_dir + '/' + newfile.split('/')[-1]

        source = Convert.resolveAliases(source, aliases)

        if suffix in ['xml', 'json']:pass
        elif suffix == 'yaml':source = Convert.convertYAMLtoJSON(source)
        elif suffix == 'hcl':source = Convert.convertHCLtoJSON(source)
        else:raise xception.kwadParameterException('Main', self_funct, 'File: %s, Unsupported file type: %s. Supported types are : xml (default), yaml, hcl, json.', file, suffix)

        if keep_temp_dir:
            fd = open(new_file + '.to.json', 'wb')
            fd.write(bytes(source, 'utf-8'))
            fd.close()

        return source

    # A011:
    @staticmethod
    def mako(source, temp_dir=None, tmpl_kws=None):
        selfMethod = 'mako'
        from mako.template import Template
        from mako.lookup import TemplateLookup
        from mako import exceptions as mako_exceptions  # A006
        if tmpl_kws==None:tmpl_kws={}
        tmpl_kws = dict(tmpl_kws)
        if temp_dir == None:temp_dir = getUserKastTempDir()

        ##    dir=path.split(file)[0]
        if 'template_lookups' in tmpl_kws:
            template_lookups = TemplateLookup(directories=tmpl_kws['template_lookups'])
            del tmpl_kws['template_lookups']
        else:
            template_lookups = None
        ##    else:directories=[dir]

        if temp_dir == None:
            cache_enabled = False
        else:
            cache_enabled = True

        tmpl = Template(text=source,
                        module_directory=temp_dir,
                        cache_enabled=cache_enabled, cache_dir=temp_dir,
                        lookup=template_lookups)

        try:
            return tmpl.render(**tmpl_kws)
        except Exception as e:  # A006
            print(mako_exceptions.text_error_template().render())
            raise xception.kwadSystemException('Main', selfMethod, 'One error found trying to parse the Template file to Mako, see previous messages ! SubException is:' + str(e))
        except:  # A006
            print(mako_exceptions.text_error_template().render())
            raise xception.kwadSystemException('Main', selfMethod, 'One error found trying to parse the Template file to Mako, see previous messages !')

    # A010:
    @staticmethod
    def jinja(source, temp_dir=None, tmpl_kws=None):
        selfMethod = 'jinja'
        from jinja2 import Environment, select_autoescape
        if temp_dir == None: temp_dir = getUserKastTempDir()
        if tmpl_kws==None:tmpl_kws={}
        tmpl_kws = dict(tmpl_kws)

        env = Environment(
            autoescape=select_autoescape(
                enabled_extensions=('jinja',),
                default_for_string=True,
                default=False,
            )
        )

        try:
            # template = env.from_string('Hello {{ name }}!')
            # template.render({'name': 'John Doe'})
            template = env.from_string(source)
        except Exception as e:
            raise xception.kwadSystemException('Main', selfMethod, 'One error found trying to parse the Template file to Jinja, see previous messages ! SubException is:' + str(e))
        except:
            raise xception.kwadSystemException('Main', selfMethod, 'One error found trying to parse the Template file to Jinja, see previous messages !')


        return template.render(tmpl_kws)


    # A010 [begin]:
    @staticmethod
    def convertYAMLtoJSON(source):
        selfMethod = 'convertYAMLtoJSON'
        import yaml, json
        """ e.g. use:
        import yaml
        import json
        
        with open('config.yml', 'r') as file:
            configuration = yaml.safe_load(file)
        
        with open('config.json', 'w') as json_file:
            json.dump(configuration, json_file)
            
        output = json.dumps(json.load(open('config.json')), indent=2)
        print(output)
    
        names_yaml = ""
        - 'eric'
        - 'justin'
        - 'mary-kate'
        ""
        obj_yaml = yaml.load(source)
        # obj_yaml = yaml.safe_load(source)
        """

        obj_yaml = yaml.safe_load(source)
        src_json = json.dumps(obj_yaml, indent=2, ensure_ascii=False)

        return src_json

    @staticmethod
    def convertJSONtoYAML(json):
        import yaml
        """ e.g. use:
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
        s = yaml.dump(json, safe=True, force_embed=False, indent=2, sort_dicts=False, allow_unicode=True)

        return s

    @staticmethod
    def convertHCLtoJSON(source):
        import pygohcl
        import json

        d = pygohcl.loads(source)

        return json.dumps(d, indent=2)



def increment(file):
    from os import path, listdir
    dir, fname = path.split(file)
    prefix, suffix = path.splitext(fname)

    if prefix.find('.') > 0:
        spl = prefix.split('.')
        last = spl.pop()
        if last.isdigit():
            max = int(last)
            prefix = '.'.join(spl)
        else:max=0
    else:max=0

    if path.isdir(dir):
        l = listdir(dir)
        for f in l:
            if not f.startswith(prefix + '.'):continue

            spl = f.split('.')
            last = spl.pop()
            if not last.isdigit():continue
            inc = int(last)
            if inc>max:max = inc

    return dir + '/' +  prefix + '.' + str(max + 1) + suffix


def fileRead(file):
    """
    Internal use only
    """
    fd=open(file)
    src=fd.read()
    fd.close()
    return src.split('\n')

import tarfile
import io

# See: https://stackoverflow.com/questions/59272304/python-tarfile-compress-an-object-in-memory
# and: https://stackoverflow.com/questions/15857792/how-to-construct-a-tarfile-object-in-memory-from-byte-buffer-in-python-3
def gzInMemory(listoftupleof_source_and_filenames):
    """
    Receive a list of tuple of (file_name, source)
    Returns the gz file content as bytes
    """
    from time import time
    ts = int(time())
    fh = io.BytesIO()

    with tarfile.open(fileobj=fh, mode='w:gz') as tar:
        for fname, source in listoftupleof_source_and_filenames:
            data = source
            source_f = io.BytesIO(initial_bytes=data)

            info = tarfile.TarInfo(fname)
            info.mtime = ts
            info.size = len(data)
            tar.addfile(info, source_f)

    # with open(tarname, 'wb') as f:
    #    f.write(fh.getvalue())

    return fh.getvalue()

def archive(srcdir, arcf, type='tar', mode=0o775, verbose=0):
    selfMethod='zip'
    from os import path, walk, chmod
    arcf=path.normpath(arcf)
    if srcdir==None or not path.isdir(srcdir):raise xception.kwadParameterTypeException('Main', selfMethod, 'srcdir', 'str/path', str(srcdir))
    if arcf==None or not path.isdir(path.split(arcf)[0]):raise xception.kwadSystemException('Main', selfMethod, 'File:' + arcf + ' base directrory:' + path.split(arcf)[0]+ ' should exist.')
    if path.isfile(arcf):raise xception.kwadSystemException('Main', selfMethod, 'File:' + arcf + ' should  not exist.')
    if type not in ('tar', 'zip'):raise xception.kwadParameterTypeException('Main', selfMethod, 'type', 'in (tar, zip)', str(type))
    srcdir=path.realpath(path.normpath(srcdir))

    if verbose>=10:print('Creating Archive file at:' + arcf + '.')

    if type=='zip':
        import zipfile
        """
        Tar : Odd behaviour with ?inzip/Winrar creates and inner zip file of the same name,
        containing thre real zip file under the target file directory structure !!!
        ==> Prefer ZipFile to be used with ?inzip:Winrar.
        """
        arc = zipfile.ZipFile(arcf, 'w', zipfile.ZIP_DEFLATED)
    else:
        import tarfile
        if type=='tar':type=''
        arc = tarfile.TarFile.open(arcf, 'w:' + type)

    ld1=walk(srcdir, topdown=True, onerror=_walk_error)
    for root, dirs, files in ld1:
        alls = files + dirs

        for file in alls:
            file=path.realpath(path.normpath(root +'/' + file))
            arcname=path.realpath(path.normpath(file)).split(srcdir)
            if len(arcname)!=2 or arcname[0]!='':raise Exception('Split error in sync')
            arcname=arcname[1]

            if verbose>=20:print('Adding file:' + file + ' at path:' + arcname + '.')

            if type=='zip':
                arc.write(file, arcname=arcname)
            else:
                arc.add(file, arcname=arcname, recursive=False)

    arc.close()
    chmod(arcf, mode)

def _walk_error(e):
    selfMethod='walk_error'
    raise e

def zipGetNList(src):
    selfMethod='zipGetNList'
    if not isinstance(src, str) or  not isinstance(src, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: src, expected: str, received:' + str(src) + ' !')
    import zipfile
    import os
    src=os.path.normpath(src)

    zfile=zipfile.ZipFile(src)

    return zfile.namelist()

def zipGetFile(src, path, check=False):
    """
    Extract a file from a zip.
    src : zip file.
    paths : path of the file in the zip.
    """
    selfMethod='zipGetFile'
    if not isinstance(src, str) or  not isinstance(src, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: src, expected: str, received:' + str(src) + ' !')
    if not isinstance(path, str) or  not isinstance(path, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: path, expected: str, received:' + str(path) + ' !')
    import zipfile
    import os
    src=os.path.normpath(src)

    zfile=zipfile.ZipFile(src)
    nlist=zfile.namelist()

    if check:return path in nlist

    return zfile.read(path).decode("utf-8"), nlist

def unzip(src=None, destDir=None, toSign=None, toLightSign=None, ignoreErrors=True, temp_dir=None, mode=0o755):
    """
    Unzip a file.
    src : the zip file.
    destDir : the destination directory where to uncompress.
    ignoreErrors : ignore errors.
    toSign : a path inside the destination directory where to dump the signature.
    """
    selfMethod='unzip'
    if not isinstance(src, str) or not isinstance(destDir, str):raise xception.kwadParameterException('Main', selfMethod, 'Parameters src and destDir are both required !')
    if toSign!=None and not isinstance(toSign, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: toSign, expected: str, received:' + str(toSign) + ' !')
    if toLightSign!=None and not isinstance(toLightSign, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: toLightSign, expected: str, received:' + str(toLightSign) + ' !')
    if toSign!=None and toLightSign!=None:raise xception.kwadParameterException('Main', selfMethod, 'Parameters toSign and toLightSign cannot be given together !')
    if not isinstance(ignoreErrors, bool):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: ignoreErrors, expected: bool, received:' + str(ignoreErrors) + ' !')
    if temp_dir==None or not isinstance(temp_dir, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: temp_dir, expected: str, received:' + str(temp_dir) + ' !')
    import zipfile
    import os
    src=os.path.normpath(src)
    destDir=os.path.normpath(destDir)

    if not os.access(destDir, os.F_OK):os.mkdir(destDir, mode)
    else:
        for f in os.listdir(destDir):
            f=os.path.normpath(destDir + '/' + f)
            import shutil
            if os.path.isdir(f):shutil.rmtree(f, ignore_errors=ignoreErrors)
            else:
                os.remove(f)

    zfile=zipfile.ZipFile(src)

    for name in zfile.namelist():
        doDir=False
        doFile=True

        if name.endswith('/'):
            doDir=True
            doFile=False
            dir=name
        elif name.find('/')>0:
            doDir=True
            spl=name.split('/')
            spl.pop()
            dir='/'.join(spl)

        if doDir and not os.access(os.path.normpath(destDir + '/' + dir), os.F_OK):
            os.makedirs(os.path.normpath(destDir + '/' + dir), mode)

        if doFile:
            fd=open(os.path.normpath(destDir + '/' + name), 'wb', mode)
            fd.write(bytes(zfile.read(name).decode("utf-8"), 'utf-8'))
            fd.close()
    zfile=None

    if toSign!=None or toLightSign!=None:
        if toSign!=None:
            s=toSign
            fd=open(src, 'rb')
            sig_src=getSignature(str(fd.read().decode("utf-8")), temp_dir=temp_dir)
            fd.close()
        else:
            s=toLightSign
            stat=os.stat(src)
            sig_src=str(int(stat.st_mtime))

        fd=open(os.path.normpath(destDir + '/' + s), 'wb', mode)
        fd.write(bytes(sig_src, 'utf-8'))
        fd.close()

#M001:
def getSignature(value, temp_dir=None):
    selfMethod='getSignature'
    import sys

    if not sys.platform.startswith('aix'): # python md5 is definitly buggy on aix
        try:
            from hashlib import md5

            m=md5()
            m.update(bytes(value, 'utf-8'))
            return str(m.hexdigest())

        except:
            if getOsType()!='unix':raise

    if temp_dir==None or not isinstance(temp_dir, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: temp_dir, expected: str, received:' + str(temp_dir) + ' !')
    import os

    fpath=os.path.normpath(os.path.realpath(temp_dir + '/getSignature_' + genUid() + '.dat'))
    fd=open(fpath, 'wb')
    fd.write(bytes(value, 'utf-8'))
    fd.close()

    # M006: ret, sig, stderr=subprocess(['cksum', fpath]) ! do Not return stdout !!!
    ret, sig=execute('cksum ' + fpath, doPrint=False)
    if ret!=0:raise xception.kwadSystemException('Main', selfMethod, 'Error running system command:cksum ' + fpath + ' !')

    return sig.split()[0]

def cksum(s):
    import hashlib
    return hashlib.md5(s.encode('utf-8')).hexdigest()

#M001:
def getFileSignature(fpath):
    self_funct = 'getFileSignature'
    import sys
    import os

    fpath=os.path.normpath(os.path.realpath(fpath))
    if not os.access(fpath, os.F_OK):return None

    if not sys.platform.startswith('aix'): # python md5 is definitly buggy on aix
        try:
            from hashlib import md5

            fd=open(fpath, 'rb')
            value=fd.read().decode("utf-8")
            fd.close()

            m=md5()
            m.update(bytes(value, 'utf-8'))
            return str(m.hexdigest())

        except:
            if getOsType()!='unix':raise

    # M006: ret, sig, stderr=subprocess(['cksum', fpath]) ! do Not return stdout !!!
    ret, sig=execute('cksum ' + fpath, doPrint=False)
    if ret!=0:raise xception.kwadSystemException('Main', self_funct, 'Error running system command:cksum ' + fpath + ' !')

    return sig.split()[0]


def getFilesSignature(fpaths, temp_dir=None):
    selfMethod='getFilesSignature'
    if temp_dir==None or not isinstance(temp_dir, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: temp_dir, expected: str, received:' + str(temp_dir) + ' !')
    import io

    sb=io.StringIO()
    for fpath in fpaths:
        fd=open(fpath, 'rb')
        sb.write(fd.read().decode("utf-8"))
        fd.close()

    return getSignature(sb.getvalue(), temp_dir=temp_dir)

#M001:+temp_dir
def checkSig(fsig, fpaths, temp_dir=None):
    """
    Compare a signature from fsig signature to the sum of several files pasted together.
    fsig : the file containing the signature to be compared with.
    paths : path of some files.
    """
    selfMethod='checkSig'
    if not isinstance(fsig, str) or  not isinstance(fsig, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: fsig, expected: str, received:' + str(fsig) + ' !')
    if not isinstance(fpaths, list):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: fpaths, expected: list, received:' + str(fpaths) + ' !')
    if temp_dir==None or not isinstance(temp_dir, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: temp_dir, expected: str, received:' + str(temp_dir) + ' !')
    import os
    fsig=os.path.normpath(fsig)
    if not os.access(fsig, os.F_OK):return False

    fd=open(fsig, 'rb')
    sig=fd.read().decode("utf-8")
    fd.close()

    if sig==getFilesSignature(fpaths, temp_dir=temp_dir):return True

    return False

def getWeakFileSignature(fpath):
    selfMethod='getWeakFileSignature'
    import base64
    import os

    fpath=os.path.normpath(os.path.realpath(fpath))
    if not os.access(fpath, os.F_OK):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect Parameter: fpath, file:' + str(fpath) + ' do not exist !')
    stat=os.stat(fpath)
    stat=str(stat.st_mtime) + ';' + str(stat.st_size)

    # b64 encode: s = base64.b64encode(bytes('sample_string_bytes', 'utf-8')).decode("utf-8")
    # b64 decode: s = base64.b64decode(s).decode("utf-8")

    # Python2: return base64.b .encodestring(stat).strip()
    # return base64.b64encode(bytes(stat, 'utf-8')).decode("utf-8").strip()
    return base64.urlsafe_b64encode(bytes(stat, 'utf-8')).decode("utf-8")



#M002:
def getMD5FilesSignature(fpaths):
    selfMethod='getMD5FilesSignature'
    """
    Prefer shunk read for big file:
    import StringIO
    
    sb=StringIO.StringIO()
    for fpath in fpaths:
        fd=open(fpath, 'rb')
        sb.write(fd.read())
        fd.close()        
        
    return getSignature(sb.getvalue(), temp_dir=temp_dir)
    """
    from hashlib import md5
    MD5_BLOCK_SIZE = 1000
    import os
    m=md5()

    for fpath in fpaths:
        if not os.access(fpath, os.F_OK):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect Parameter: fpaths, File:' + str(fpath) + ' do not exist !', fromClass='Main', fromMethod=selfMethod)

        with open(fpath,'rb') as f:
            for chunk in iter(lambda: f.read(MD5_BLOCK_SIZE), b''):m.update(bytes(chunk, 'utf-8'))

    return str(m.hexdigest())

#A003:
def getWeakFilesSignature(fpaths):
    selfMethod='getWeakFilesSignature'
    from io import StringIO
    import base64
    import os
    fistime=True
    sb=StringIO()

    for fpath in fpaths:
        fpath=os.path.normpath(os.path.realpath(fpath))
        if not os.access(fpath, os.F_OK):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect Parameter: fpaths, file:' + str(fpath) + ' do not exist !', fromClass='Main', fromMethod=selfMethod)
        if fistime:fistime=False
        else:sb.write('!')


        stat=os.stat(fpath)
        sb.write(str(stat.st_mtime) + ';' + str(stat.st_size))

    # Python2: return base64.encodestring(sb.getvalue()).strip()
    # return base64.b64encode(bytes(sb.getvalue(), 'utf-8')).decode("utf-8").strip()
    return base64.urlsafe_b64encode(bytes(sb.getvalue(), 'utf-8')).decode("utf-8")



                                                    #-------------#
                                                    #  Template   #
                                                    #-------------#



class Template:
    """
    Internal use only
    """
    def __init__(self, file, fout=None, doOverwrite=False, machine_locale=None, machine_cible=None, verbose=False):
        self_funct='__init__'
        prefix = SELF_MODULE + ' ' + self.__class__.__name__ + ' >> '
        if not isinstance(file, str) or file=='':raise xception.kwadSystemException(prefix, self_funct, str(file) + ' should be a non empty string !')
        if fout!=None and (not isinstance(fout, str) or fout==''):raise xception.kwadSystemException(prefix, self_funct, str(fout) + ' should be a non empty string !')
        self.verbose=verbose
        self.fileIn=file
        self.fileOut=None
        if fout!=None:self.fileOut=fout
        elif doOverwrite:self.fileOut=file
        self.vars={}

    def replace(self, var, value):
        self.vars[var]=value

    def process(self, machine_locale=None, machine_cible=None):
        return replace_in_file (self.vars, self.fileIn, fout=self.fileOut, machine_locale=machine_locale, machine_cible=machine_cible, verbose=self.verbose)

def replace_in_file(vars, file, fout=None, machine_locale=None, machine_cible=None, verbose=False):
    self_funct='replace_in_file'
    prefix = SELF_MODULE + ' ' + self_funct + ' >> '
    FLAG_LEFT='__'
    FLAG_RIGHT='__'
    if not isinstance(vars, dict):raise xception.kwadSystemException('Main', self_funct, str(vars) + ' should be a dict !')
    if not isinstance(file, str) or file=='':raise xception.kwadSystemException('Main', self_funct, str(file) + ' should be a non empty string !')
    if fout!=None and (not isinstance(fout, str) or fout==''):raise xception.kwadSystemException('Main', self_funct, str(fout) + ' should be a non empty string !')
    from io import StringIO
    doReturnStr=False
    fileIn=file
    fileOut=None
    if fout!=None:fileOut=fout

    if verbose:
        print(prefix + 'fileIn:', fileIn)
        print(prefix + 'fileOut:', fileIn)

    # Reading the file
    if machine_locale==machine_cible:
        ## in
        file_in = open(fileIn, 'r')
        file_content=file_in.read()
        file_in.close()
        ## out
        if fileOut==None:
            file_out=StringIO()
            doReturnStr=True
        else:file_out=open(fileOut, 'w')
    else:
        ## in
        cde = 'ssh ' + machine_cible + ' -c cat ' + fileIn
        ret, stdout_sdterr=execute(cde)
        if ret!=0:raise xception.kwadSystemException(SELF_MODULE, self_funct, "Failed executing the command !")
        file_content=stdout_sdterr
        ## out
        import random
        filet='/tmp/tools_replace_in_file_' + str(random.randrange( 1000, 9999 )) + '.dat'
        file_out = open(filet, 'w')

    # Update the content
    for var in vars:
        if verbose:print(prefix + 'Replacing: ', FLAG_LEFT + var.upper() + FLAG_RIGHT, ' by: ', str(vars[var]))
        file_content=file_content.replace(FLAG_LEFT + var.upper() + FLAG_RIGHT, str(vars[var]))

    # Writing
    file_out.write(file_content)
    if not doReturnStr:file_out.close()

    if machine_locale!=machine_cible:
        cde = 'scp ' + filet + ' ' + machine_cible + ': ' + fileIn
        ret, stdout_sdterr=execute(cde)
        if ret!=0:raise xception.kwadSystemException(SELF_MODULE, self_funct, 'Failed deleting the temporary file !')

    if doReturnStr:return file_out.getvalue()


                                                            # --------#
                                                            #  System #
                                                            # --------#

def sysAddGroup(group, gid):
    self_funct='sysAddGroup'
    from kwadlib.security.crypting import sanitize
    sanitize(group)
    if not str(gid).isdigit():raise  xception.kwadLdapParameterException('Main', self_funct, 'Unsupported parameter: gid (%s) should be numeric !' % str(gid))

    cmd = 'sudo groupadd %s -g %s' % (group, gid)
    p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    stdout, stderr = p.communicate()
    ret = p.wait()
    stdout_stderr = stdout
    if stderr != None: stdout_stderr = stdout + '\n' + stderr
    if ret!=0:raise  xception.kwadLdapSystemException('Main', self_funct, 'Unable to add group: %s !' % group)

    return ret, stdout_stderr

def sysDelGroup(group):
    self_funct='sysDelGroup'
    from kwadlib.security.crypting import sanitize
    sanitize(group)

    cmd = 'sudo groupdel %s' % group
    p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    stdout, stderr = p.communicate()
    ret = p.wait()
    stdout_stderr = stdout
    if stderr != None: stdout_stderr = stdout + '\n' + stderr
    if ret!=0:raise  xception.kwadLdapSystemException('Main', self_funct, 'Unable to del group: %s !' % group)

    return ret, stdout_stderr

def sysAddUserToGroup(group, user):
    self_funct='sysAddUserToGroup'
    from kwadlib.security.crypting import sanitize
    sanitize(group)
    sanitize(user)

    cmd = "sudo usermod -a -G %s %s" % (group, user)
    p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    stdout, stderr = p.communicate()
    ret = p.wait()
    stdout_stderr = stdout
    if stderr != None: stdout_stderr = stdout + '\n' + stderr
    if ret!=0:raise  xception.kwadLdapParameterException('Main', self_funct, 'Unable to add user:%s to group: %s !' % (user, group))

    return ret, stdout_stderr

def mkHomeDir(user):
    self_funct='mkHomeDir'
    from kwadlib.security.crypting import sanitize
    sanitize(user)

    cmd = "if  [ ! -d /home/{user} ]; then sudo mkdir /home/{user}; fi".format(user=user)
    p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    stdout, stderr = p.communicate()
    ret = p.wait()
    stdout_stderr = stdout
    if stderr != None: stdout_stderr = stdout + '\n' + stderr
    if ret!=0:raise  xception.kwadLdapParameterException('Main', self_funct, 'Unable to create home dir for user: %s !' % user)

    return ret, stdout_stderr

def rmHomeDir(user):
    self_funct='rmHomeDir'
    from kwadlib.security.crypting import sanitize
    sanitize(user)

    cmd = "if test -d /home/{user}; then sudo rm -fr /home/{user}; fi".format(user=user)
    p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    stdout, stderr = p.communicate()
    ret = p.wait()
    stdout_stderr = stdout
    if stderr != None: stdout_stderr = stdout + '\n' + stderr
    if ret!=0:raise  xception.kwadLdapParameterException('Main', self_funct, 'Unable to remove home dir for user: %s !' % user)

    return ret, stdout_stderr


                                                    #----------#
                                                    #  Process #
                                                    #----------#



def execute(cde, doPrint=True, part_cde=None):
    """
    Internal use only
    Run an Arbitrary command with python execute.
    """
    self_funct='execute'
    prefix = SELF_MODULE + ' ' + self_funct + ' >> '

    if not getOsType()=='unix':raise xception.kwadSystemException('Main', self_funct, "Exectue is supported only on unixes !")

    prt_cde=cde
    if part_cde!=None:prt_cde=part_cde
    if doPrint:print(prefix + 'execute command:', prt_cde)

    l=list(cde)

    # D011: import popen2

    p = Popen(cde, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    stdout, stderr = p.communicate()
    ret = p.wait()
    stdout_stderr = stdout
    if stderr != None: stdout_stderr = stdout + '\n' + stderr
    if doPrint:print(stdout_stderr)

    return ret, stdout_stderr

def system(cde, verbose=0, verbose_zero_temp_dir=None):
    """
    Internal use only
    Run an Arbitrary command with python system.
    Returns no stdout.
    """
    self_funct='system'
    from os import path
    from os import system
    from os import remove
    dev_null=None
    prefix = SELF_MODULE + ' ' + self_funct + ' >> '
    if verbose>=5:print(prefix + 'execute command:', cde)
    elif verbose==0 and verbose_zero_temp_dir!=None:
        dev_null=path.normpath(verbose_zero_temp_dir + '/dev_null_' + genUid() + '.out')
        cde=cde + ' > ' + dev_null

    ret=system(cde)
    if dev_null!=None:remove(dev_null)

    return ret

import subprocess
SUBPROCESS_PIPE=subprocess.PIPE
SUBPROCESS_STDOUT=subprocess.STDOUT
def Popen(*args, **kws):
    return subprocess.Popen(*args, **kws)

def check_output(*args, **kws):
    return subprocess.check_output(*args, **kws)

def subprocess2(cdes, doPrint=False, stdin=None, stdout=None, stderr=None, wait=True, verbose_zero_temp_dir=None, useshell=False, envs=None):
    """
    useshell (default False) : keep default when using direct call.
        e.g.: /where/is/myproc -f --some_parameters
    use True when using multi comand call like:
        ps -elf  | grep u203rhi37_rwas_abonnement-sms_jvm_01 |  grep -v grep  | awk '{print $4}'

    Internal use only
    Run an Arbitrary command with python subprocess.
    """
    self_funct='subprocess'
    import subprocess
    from os import path, remove
    _stdin=None
    dev_null=None
    if not wait and stdin==None and (stdout, stderr)!=(None, None):raise xception.kwadParameterException('Main', self_funct, 'Arguments stdout, stderr are only allowed with wait=False and stdin=None !')

    if doPrint:
        if isinstance(cdes, (list,tuple)):
            cde=''
            for e in cdes:cde+=e + ' '
        else:cde=cdes
        prefix = SELF_MODULE + ' ' + self_funct + ' >> '
        print(prefix + 'Processing command:', cde)

    elif isinstance(cdes, str) and verbose_zero_temp_dir!=None:
        dev_null=path.normpath(verbose_zero_temp_dir + '/dev_null_' + genUid() + '.out')
        cdes=cdes + ' > ' + dev_null

    # if wait and stdin==None:stdout=stderr=subprocess.PIPE
    if not wait and stdin==None:stdout=stderr=subprocess.PIPE
    ## cause hangup: if wait:
    ##        if stdout==None:stdout=subprocess.PIPE
    ##        if stderr==None:stderr=subprocess.PIPE

    if stdin!=None:_stdin=subprocess.PIPE

    if useshell:executable = '/bin/bash'
    else:executable = None
    p = subprocess.Popen(cdes, shell=useshell, stdin=_stdin, stdout=stdout, stderr=stderr, executable=executable, env=envs)

    if stdin!=None or wait:
        try:
            stdout, stderr=p.communicate(input=stdin)
        except KeyboardInterrupt:
            if getOsType()!='unix':raise
            from os import kill
            import signal
            kill(p.pid, signal.SIGINT)

        stdout, stderr = p.communicate()
        ret = p.wait()
        stdout, stderr = stdout, stderr
        ret=p.returncode

    ## cause hangup: elif wait:
    ##        p.wait()
    ##        ret=p.returncode
    ##        stdout=p.stdout.read() > cause hangup
    ##        stderr=p.stderr.read() > cause hangup

    if not (wait or stdin!=None):ret=0

    if stdout==None:stdout=''
    if stderr==None:stderr=''
    if dev_null!=None and path.isfile(dev_null):remove(dev_null)
    return ret, stdout, stderr

def execssh(host, cmd=None, sources=[], destdir=None, askpass=True, user=None, port=22, password=None, timeout=30, temp_dir=None, menu_configs=None, verbose=0):
    """
    :param host:
    :param cmd:
    :param sources:
    :param destdir:
    :param askpass:
    :param user:
    :param password:
    :param timeout:
    :param temp_dir:
    :param menu_config: If menu_config!=None, as been called froma process embeded wihin a menu chain.
                        In this case must use: menu_config for all outputs: print and process calls.
                        menu_config:{'config':config, 'menu':menu, 'option_index':option_index, 'id':id, 'id_type':id_type, 'fct_name': 'menu_fct_tplgen_operations'}
    :return:
    """
    selfMethod='execssh'
    if askpass and not (isinstance(user, str) and isinstance(password, str)):xception.kwadParameterException('Main', selfMethod, 'Parameters user/password are required wehn askpass is True !')
    if user!=None and not isinstance(user, str):xception.kwadParameterException('Main', selfMethod, 'Parameter user must be string ! Received: %s' % str(user))
    from kwadlib.security.crypting import sanitize, sanitize_path
    sanitize(host, user)
    sanitize_path(destdir, temp_dir, allowNone=True)
    if port!=None and not isinstance(port, str):xception.kwadParameterException('Main', selfMethod, 'Parameter port must be int ! Received: %s' % str(port))
    if port==None:port=22
    if port == 22:SCP_PORT = ''
    else:SCP_PORT = ' -P %s' % str(port)
    if cmd!=None and sources!=None:xception.kwadParameterException('Main', selfMethod, 'Parameters sources and destdir cannot be provided when cmd is guiven !')
    if sources in ([], None) and  cmd==None:xception.kwadParameterException('Main', selfMethod, 'Parameters cmd is required when parameters sources and destdir are not provided !')
    if sources not in ([], None) and not isinstance(destdir, str):xception.kwadParameterException('Main', selfMethod, 'Parameters destdir is required when sources is provided !')
    if sources!=None and not isinstance(sources, list):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: sources, expected: list, received:' + str(sources) + ' !')
    if temp_dir!=None and not isinstance(temp_dir, str):raise xception.kwadParameterException('Main', selfMethod, 'Incorrect parameter: temp_dir, expected: str, received:' + str(temp_dir) + ' !')
    selfMethod='execssh'
    if temp_dir==None:temp_dir=getUserKastTempDir()
    return_code=1
    from io import StringIO
    output=StringIO()
    if not askpass: password = None

    try:
        if cmd==None:
            ## scp
            ## ---
            import pexpect

            sources = ' '.join(sources)
            foutput=temp_dir + '/output.out_' + genUid() + '.txt'
            if askpass:_user=user + '@'
            else:_user=''
            cmd=str('/bin/sh -c "scp -p {port} {src} {user}@{host}:{dest};echo $?> {foutput}"').format(port=SCP_PORT, src=sources, user=user, host=host, dest=destdir, foutput=foutput)
            child = pexpect.spawn(cmd)
            if verbose>=5:output.write('Running Command >>> ' + cmd + '\n')

            if askpass:
                i = child.expect(['assword:', r"yes/no"], timeout=30)
                if i == 0:
                    child.sendline(password)
                elif i == 1:
                    child.sendline("yes")
                    child.expect("assword:", timeout=30)
                    child.sendline(password)

            data = child.read().decode("utf-8")
            output.write(data + '\n')
            child.close()

            # - Return Code
            try:
                from os import remove
                fd=open(foutput)
                return_code=fd.read().strip()
                fd.close()
                remove(foutput)
            except:pass

        else:

            ## ssh
            ## ---
            from pexpect import pxssh

            ssh_session = pxssh.pxssh(timeout=timeout)

            # if user==None or password==None:raise Exception('User/password is required for this SSH Session !', '\n', cmd, host)
            if not ssh_session.login (host, user, password, port=port):
                raise Exception('Failed to login to this SSH session with user: %s ! Check the provided password.' % user)
            if verbose>=30:output.write('SSH session: login successful.\n')

            ssh_session.sendline(cmd)
            if verbose>=30:output.write('SSH session: cmd sent\n')
            ssh_session.prompt()
            output.write(ssh_session.before.decode("utf-8") + '\n')

            # - Return Code
            ssh_session.sendline ('echo $?')
            if verbose>=30:output.write('SSH session: $? sent\n')
            ssh_session.prompt()
            return_code=ssh_session.before.decode("utf-8").split()[-1]
            if verbose>=30:output.write('SSH session: ret code retreived' + '\n')

            ssh_session.logout()
            if verbose>=30:output.write('SSH session: logged out' + '\n')

        if str(return_code).isdigit():return_code=int(return_code)

    except:
        import traceback, sys
        traceback.print_stack(file=sys.stdout)
        if menu_configs == None: print(output.getvalue())
        else: menu_configs['config'].ioprint_process_output(output=output.getvalue(), coid=menu_configs['coid'])
        raise

    return output.getvalue(), return_code

def kill(pid):
    """
    Internal use only
    """
    import ctypes
    import os

    if getOsType()!='windows':
        from signal import SIGTERM
        os.kill(int(pid), SIGTERM)
    else:
        handle=ctypes.windll.kernel32.OpenProcess(1, False, int(pid))
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)

def full_stack():
    # From: https://stackoverflow.com/questions/6086976/how-to-get-a-complete-exception-stack-trace-in-python
    import traceback, sys
    exc = sys.exc_info()[0]
    if exc is not None:
        f = sys.exc_info()[-1].tb_frame.f_back
        stack = traceback.extract_stack(f)
    else:
        stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
        stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr


                                                    #-----------#
                                                    #  Defaults #
                                                    #-----------#



# -----------------------------#
# Dict supporting keys as dict #
# -----------------------------#

class DictKeys:

    def __init__(self):
        self.__stores={}

    def keys(self):
        keys=list(self.__stores.keys())
        return [udksort(l) for l in keys]

    def __getitem__(self, item):
        return self.__stores[dksort(item)]

    def __setitem__(self, item, value):
        self.__stores[dksort(item)]=value

    def __delitem__(self, item):
        del self.__stores[dksort(item)]

    def __contains__(self, item):
        return dksort(item) in self.__stores

    def has_key(self, item):
        return self.__contains__(item)

    def __len__(self):
        return len(self.__stores)

    def __iter__(self):
        keys=list(self.__stores.keys())
        l=[udksort(l) for l in keys]
        for k in l:yield k

    def __str__(self):
        kstores={}
        for l in self.__stores:
            kstores[repr(udksort(l))]=self.__stores[l]

        return repr(kstores)

    def __keytransform__(self, key):
        return key

def dksort(dcts):
    l=[]
    keys=list(dcts.keys())
    keys.sort()

    for k in keys:l.append({k:dcts[k]})

    return repr(l)

def udksort(l):
    dcts={}

    l=_eval(l)
    for e in l:
        dcts[list(e.keys())[0]]=e[ list(e.keys())[0] ]

    return dcts

def feedDict(d, keys, value):
    """
    e.g.: keys: ('Domains', domain), ('Environments', env), ('CloudProviders', cloudp)
    Feed keys recursive dictionary
    """
    last=False
    for i in range(keys):
        if i == len(keys) - 1:last=True
        key1, key2 = keys[i]
        if key1 not in d:d[key1] = {key2: [] if last else {} }
        elif key2 not in d[key1]:d[key1][key2] = [] if last else {}
        d = d[key1][key2]

    d.append(value)


def getOsType():
    """
    Returns the os type.
    unix for unixes or
    windows for win32.
    """
    platform='unix'
    import sys
    if sys.platform=='win32':platform='windows'

    return platform

def clearConsol():
    from os import environ, system

    if getOsType()=='windows':system('cls')
    else:
        environ['TERM']='xterm-color'
        system('clear')

def getEnvironmentvariable(env):
    """
    Returns the value of a given system environment varibale name.
    """
    self_funct='getEnvironmentvariable'
    platform=getOsType()

    if platform=='unix':
        import os
        if env in os.environ:return os.environ[env]
        return None

    else:raise xception.kwadSystemException('Main', self_funct, 'Unmanaged platform:' + platform + '!')

def setEnvironmentvariable(env, value):
    """
    Internal use only/Experimental
    """
    self_funct='getEnvironmentvariable'
    platform=getOsType()

    if platform=='unix':
        import os
        os.environ[env]=str(value)

    else:raise xception.kwadSystemException('Main', self_funct, 'Unmanaged plateform:' + platform + '!')


def asParameter(key, options, dont_check_kwad_attrs=False):
    """
    Internal use only
    """
    self_funct='asParameter'

    if key=='kwad_attrs':raise Exception('Deprecated !')


    elif key=='softclass_dir':
        # ex: kact -c /where/are/softclasses or kact --cacdir /where/are/softclasses
        from os import path
        softclass_dir=getattr(options, 'softclass_dir')
        if softclass_dir==None:return False, None
        return True, path.normpath(softclass_dir)

    elif key=='template_dir':
        # ex: kiktpl -c /where/are/templates or kact --ctpdir /where/are/templates
        from os import path
        template_dir=getattr(options, 'template_dir')
        if template_dir==None:return False, None
        return True, path.normpath(template_dir)

    elif key=='restrictor_dir':
        # ex: kact -c /where/are/restrictors or kact --rst /where/are/restrictors
        from os import path
        restrictor_dir=getattr(options, 'restrictor_dir')
        if restrictor_dir==None:return False, None
        return True, path.normpath(restrictor_dir)

    elif key=='verbose':
        # ex: kact -c /where/are/restrictors or kact --rst /where/are/restrictors
        verbose=getattr(options, 'verbose')
        if verbose==None:return False, None
        return True, int(verbose)

def asEnvironmentVariable(key, dont_check_kwad_attrs=False):
    """
    Internal use only
    """

    if key=='kwad_attrs':raise Exception('Deprecated !')

    elif key=='softclass_dir':
        # ex: set KAST_ATTRS=/where/are/softclasses
        from os import path
        softclass_dir=getEnvironmentvariable('KAST_CACDIR')
        if softclass_dir!=None:return True, path.normpath(softclass_dir)
        else:return False, None

    elif key=='template_dir':
        # ex: set KAST_ATTRS=/where/are/templates
        from os import path
        template_dir=getEnvironmentvariable('KAST_CTPDIR')
        if template_dir!=None:return True, path.normpath(template_dir)
        else:return False, None

    elif key=='restrictor_dir':
        # ex: set KAST_RST=/where/are/restrictors
        from os import path
        restrictor_dir=getEnvironmentvariable('KAST_RST')
        if restrictor_dir!=None:return True, path.normpath(restrictor_dir)
        else:return False, None


def genUid(lite=False):
    """
    Generats a Unique Id.
    """
    import time

    id=str(int(time.time()*100))
    rand=random.randint(1, 100000)

    if lite:return "%05i" % rand
    return id + "%05i" % rand

def genRandomString(size):
    import random
    import string
    from io import StringIO
    sb = StringIO()

    for i in range(size):
        s = random.choice(string.ascii_letters)
        sb.write(s)

    return sb.getvalue()


def getTimeStamp():
    """
    Internal use only
    """
    import time

    id=time.strftime('%Y%m%d_%H%M%S_')
    rand=random.randint(1, 1000)
    return id + "%03i" % rand

def getTimeStamp2():
    """
    Internal use only
    """
    import time

    id=time.strftime('%Y%m%dH%H%M%SR')
    rand=random.randint(1, 1000)
    return id + "%03i" % rand

def getModule(mod):
    """
    Internal use only
    Load a module named mod.
    """
    self_funct='getModule'
    import importlib

    try:
        # M012: mod=__import__(mod, {}, {}, [mod])
        mod = importlib.import_module(mod)
    except Exception as e:
        raise xception.kwadSystemException('Main', self_funct, 'Unable to retreive the module:' + mod + '! SubException is:' + e.__class__.__name__ + ':' + str(e))

    return mod

def verbose(*args, **keywords):
    """
    Argument Parameters:
    --------------------
    If verbose has one hargument : this argument is printed at the indent position.
    If verbose has two harguments : these argument are considered to be a title and its value and
    these argument are printed like this: title: value

    Keywords Parameters:
    --------------------
    level : (required), numeric value, the current verbose level.
    ifLevel : (required), numeric value, print arg only if ifLevel>=level.
    indent : (optional) BEWARE must be a (blank) string not numeric.

    highLight: If true will highLight this message with an highLight mark.
    highLightMore: If highligth is true will use this mark.
    logFile: A file path where to write this message as well as stdout.txt.
    forceLogFile: If true will write to the logFile.
    """
    self_funct='verbose'
    from os import path
    import sys
    global HIGHLIGHT_INDEX

    title=None
    if len(args)==1:value=args[0]
    elif len(args)==2:title, value=args[0], args[1]
    else:raise xception.kwadParameterException('Main', self_funct, 'Arguments to be print are required !')

    if 'indent' not in keywords:keywords['indent']=''
    # if 'level' not in keywords or 'ifLevel' not in keywords:raise xception.kwadParameterException('Main', self_funct, 'The parameters: level and ifLevel are required !')
    if 'level' not in keywords: keywords['level'] = 0
    if 'ifLevel' not in keywords: keywords['ifLevel'] = 0
    # A007:
    if 'highLight' not in keywords:keywords['highLight']=False
    if 'highLightMore' not in keywords or not isinstance(keywords['highLightMore'], str):keywords['highLightMore']=''
    else:highLightMore='(' + keywords['highLightMore'] + '>)'
    if not isinstance(keywords['highLight'], bool):raise xception.kwadParameterTypeException('Main', self_funct, 'highLight', 'bool', str(keywords['highLight']))
    highLight=keywords['highLight']
    level=keywords['level']
    ifLevel=keywords['ifLevel']
    indent=keywords['indent']
    if indent==None:indent=''
    if level<ifLevel:return
    logFile=None
    if 'logFile' in keywords:logFile=keywords['logFile']
    if logFile and not path.isfile(logFile):logFile = None
    if not ('forceLogFile' in keywords and keywords['forceLogFile']==True):logFile=None
    if logFile:fdlog = open(logFile, 'a')

    def write(value):
        sys.stdout.write(value)
        if logFile:fdlog.write(value)

    if highLight:
        write(HIGHLIGHT_BEGIN.replace('{MORE}', str(highLightMore)) + '\n')
    if title==None:
        if isinstance(value, list):
            for entry in value:
                write(indent + 3*' ' + entry + '\n')
        else:
            write(indent + value + '\n')
    else:
        if isinstance(value, list):
            write(indent + title  + ':' + '\n')
            for entry in value:
                write(indent + 3*' ' + entry + '\n')
        else:
            write(indent + title  + ':' + str(value) + '\n')
    if highLight:write(HIGHLIGHT_END + '\n')

    if logFile: fdlog.close()

fct_verbose=verbose # this allows multiple verbose parameters without overiding this function.


class KOption:
    """
if wks['*password'] is True: This means this field is a password and must be managed as well.
    So we will add a special callback to this field that will allow it to be empty (in OptParse.add_option)).
    The cinematic will be the following and will be managed by KOption:
    - if passord has a value (--password value) : this will be used as the password.
    - if passord has no value or has a value starting with /:
        An Exception: KwadkOptionSecurePasswordInput will be thrown:
        with the list of all field password that must be managed a sercure way.
        mod attributte of the Exception will be either :
        - "prompt" if no value was provided or
        - "file" with value if was starting by /
        It is the responsability of the interactive interface receiving this Exception, to manage password input the rigth way.
    """
    # A015: above adding help for new password management.
    EQUIV_PYTHON_PARSE_TYPES={'int': int, 'str': str, 'bool': bool, 'unicode': str, 'float': float, 'tuple': str, 'list': str, 'dict': str, 'date': str, 'ts': str, 'xml': str, 'color': str, 'wkDef': str, 'url': str}
    CALL_SEQUENCE_ERROR="""
Call sequence Error:
An instance of MultiOptions must be called on the Python Optparse instance first:
kOption=MultiOptions.dynOption(optparse, parser)

Than after parsing:
(options, args) = parser.parse_args()

rtvOption must (can) be called on options:
found_moptions=multiOptions.rtvMultipleOptions(options)
    """
    OUTPUT_PREFIX = 'output_'
    # A015:
    NO_PASSWORD_DEFAULT='KOption_NO_PASSWORD_DEFAULT'
    NO_PASSWORD_INPUT_AS_FILE='file'
    NO_PASSWORD_INPUT_AS_PROMPT='prompt'
    NO_PASSWORD_INPUT_HELP= """
This option is a password and must will be managed as well.
    - if this option is provided with no value: a prompt will be proposed to enter the password.
    - if password has no value or has a value starting with /: The password is assumed to be contained in this file path.    
    - if this option is provided with a value not starting with /: it will be taken as the password.         
    """

    def __init__(self, usage, firsttag=None, callInteractive=False, class_exit=None, method_exit=None):
        self.__firsttag = firsttag
        self.__has_ran=0
        self._option_group_orders=[]
        self._option_group_by_names={}
        self._option_multiple_definitions={}
        self.__found_option_multiple_definitions={}
        self._group_nodes={}
        self.__class_exit, self.__method_exit = class_exit, method_exit
        # A015:
        self.__callInteractive=callInteractive
        import optparse

        self.__option_default_group=KOptionGroup(self, '__default__')

        # Avoid optparse to sys.exit wrecking the Exception error management: See: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_known_args
        # - and https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_known_args
        class ErrorOptionParser(optparse.OptionParser):
            def error(self, message=None):
                raise Exception(f'Error trying to parse the options: {message}')

            def exit(self, status=0, message=None):
                if status:
                    raise Exception(f'Error trying to parse the options: {message} with status: {status}' )
                # exit(status)

        self.__py_parser = ErrorOptionParser(usage, add_help_option=False)
        self.__py_parser.add_option('-h', "--help", action='store_true', dest="help", help="Show this help.")

    @staticmethod
    def b64(value):
        self_funct = 'b64'
        if value == None:return value
        if not isinstance(value, str):raise xception.kwadParameterTypeException('KOption', self_funct, 'value', 'str', type(value))
        import base64
        return base64.b64encode(bytes(value, 'utf-8')).decode('utf-8')
    @staticmethod
    def unb64(value):
        self_funct = 'unb64'
        if value == None:return value
        if not isinstance(value, str):raise xception.kwadParameterTypeException('KOption', self_funct, 'value', 'str', type(value))
        import base64
        return base64.b64decode(value).decode('utf-8')

    def __clear(self):
        self.__has_ran=1
        self.__found_option_multiple_definitions={}

    def getGroupNodes(self):
        return  dict(self._group_nodes)

    def getOptionGroupOrders(self):
        return list(self._option_group_orders)

    def getOptionGroups(self):
        return  dict(self._option_group_by_names)

    def __getOptionMultiplesShapeError(self):
        return """
    The syntax for Multi-Option is: <option_name>.<#>.<key> <value>
    where "#" represents an integer >=1.
    e.g:
    --datasrc.1.dbtype psql  --datasrc.1.jndiname my/ds1  --datasrc.1.dbname mydb1  --datasrc.1.host myhos1  --datasrc.1.port myport1  --datasrc.1.username myuser1  --datasrc.1.password mypass1
    --datasrc.2.dbtype psql  --datasrc.2.jndiname my/ds2  --datasrc.2.dbname mydb2  --datasrc.2.host myhos2  --datasrc.2.port myport2  --datasrc.2.username myuser2  --datasrc.2.password mypass2
    """ + '\n\
    Currently known Multiple Options are:' + str(list(self._option_multiple_definitions.keys()))[1:-1].replace("'", '') + '.\n'

    def add_option(self, short=None, int=None, dest=None, wks=None, help=None):
        self.__option_default_group.add_option(short=short, int=int, dest=dest, wks=wks, help=help)
    # A014:
    def add_output_option(self, short=None, int=None, dest=None, wks=None, help=None):
        """
        Use  this to Add output attr into your output_node descriptor.
        Further you can navigate optxml_node or output_node with the OptStruct function (prefixed os) on them:
        for example: optxml_node.osGetParentAttr(...) e.g.: osIsSet, osSet, osUnset).
        You can setAttr on your output_node.setAttr('myAttr', value).
        And later tell output_node.osSet() to activate your output_node as return value.
        """
        if int!=None:int = '--' + KOption.OUTPUT_PREFIX + int[2:]
        if dest!=None:dest = KOption.OUTPUT_PREFIX + dest
        self.add_option(short=short, int=int, dest=dest, wks=wks, help=help)

    def prt_options(self):
        import io
        sb = io.StringIO()
        gindex = 0
        oindex = 0
        for on in self._option_group_orders:
            if  len(self._option_group_orders)>1:gindex+=1
            ogs = self._option_group_by_names[on]
            sb.write('OptionGroup: %s' % on + '\n')
            for option in ogs['option_orders']:
                oindex += 1
                opts = ogs['options'][option]
                sb.write((str(gindex) + '.') if gindex>0 else '' + str(oindex) +  ')Option: %s%s wks: %s' % (option, '/' + opts['short'] if opts['short'] else '', opts['wks']) + '\n')

        return sb.getvalue()

    def OptionGroup(self, name, description=None, gwks=None):
        return KOptionGroup(self, name, description=description, gwks=gwks)

    def MultipleOptionGroup(self, name, label, description=None, gwks=None):
        return KMultipleOptionGroup(self, name, label, description=description, gwks=gwks)

    def parse(self, args):
        import sys
        if args!=None and not isinstance(args, list):raise Exception('kOption/' + self.__class__.__name__ + ': function parse: parameter parse must be a list !')

        if args==None:args=sys.argv[1:]

        # MultiOptions facility (finally register Multi Options): Position juste before : (options, args) = parser.parse_args()
        self.__parse_dynOption()
        # Py Parse
        """ todo:
        + add:
        type='list' + ltype
        type='dict' + dtype
        type='date' + dtype
        ... see wk        
        """
        options, args = self.__py_parser.parse_args(args=args)
        if not options.help:
            self.__parse_rtvSimpleOption(options)
            # MultiOptions facility (retreive values for Multi Options): Position juste after : (options, args) = parser.parse_args()
            found_moptions=self.__parse_rtvMultipleOptions(options)
        else:
            found_moptions=None


        return options, args, found_moptions, self.__py_parser

    def __parse_dynOption(self):
        import sys, shlex, optparse
        self.__clear()

        # ----------------- #
        # | Regular Options |
        # ----------------- #

        # Create dynamic optParse options
        for name in self._option_group_by_names:
            gdefs=self._option_group_by_names[name]
            if gdefs['type']=='KMultipleOptionGroup':continue


            # - Group
            if name!='__default__':
                og=optparse.OptionGroup(self.__py_parser, name, description=gdefs['description'])
                self.__py_parser.add_option_group(og)
            else:og=self.__py_parser

            for option in gdefs['options']:
                wks=gdefs['options'][option]['wks']

                type=KOption.EQUIV_PYTHON_PARSE_TYPES[wks['*type']]
                if '*value' in wks:default=wks['*value']
                else:default=None
                if '*help' in wks:help=wks['*help']
                else:help=None

                if type==bool:
                    if default==True:
                        action='store_false'
                        default=True
                    else:
                        action='store_true'
                        default=False
                    type=None
                else:action=None

                # - Option
                """ A015:
            if wks['*password'] is True: This means this field is a password and must be managed as well.
                So we will add a special callback to this field that will allow it to be empty (in OptParse.add_option)).
                The cinematic will be the following and will be managed by KOption:
                - if passord has a value (--password value) : this will be used as the password.
                - if passord has no value or has a value starting with /:
                    An Exception: KwadkOptionSecurePasswordInput will be thrown:
                    with the list of all field password that must be managed a sercure way.
                    mod attributte of the Exception will be either :
                    - "prompt" if no value was provided or
                    - "file" with value if was starting by /
                    It is the responsability of the interactive interface receiving this Exception, to manage password input the rigth way.
                """
                callback = None
                if self.__callInteractive and '*password' in wks and wks['*password']:
                    action='callback'
                    callback= oPtionalPassword()
                    help = help + KOption.NO_PASSWORD_INPUT_HELP

                if gdefs['options'][option]['short']!=None and gdefs['options'][option]['int']!=None:og.add_option(gdefs['options'][option]['short'], gdefs['options'][option]['int'], dest=gdefs['options'][option]['dest'], type=type, action=action, default=default, help=help, callback=callback)
                elif gdefs['options'][option]['short']!=None:og.add_option(gdefs['options'][option]['short'], dest=gdefs['options'][option]['dest'], type=type, action=action, default=default, help=help, callback=callback)
                elif gdefs['options'][option]['int']!=None:og.add_option(gdefs['options'][option]['int'], dest=gdefs['options'][option]['dest'], type=type, action=action, default=default, help=help, callback=callback)

        # ------------------ #
        # | Multiple Options |
        # ------------------ #

        # Intercept Multiple Options
        # - shape: datasrc.1.dbname mydb1 ...
        args=shlex.split(' '.join(sys.argv[1:]))
        do_help=False
        if '-h' in args or '--help' in args:
            do_help=True
            if '-h' in args:del args[args.index('-h')]
            if '--help' in args:del args[args.index('--help')]

        if do_help:
            for prefix in self._option_multiple_definitions:
                self.__found_option_multiple_definitions[prefix]={'#': {}}
        else:
            for prefix in self._option_multiple_definitions:
                for arg in args:
                    if not arg.startswith('--' + prefix + '.'):continue
                    spl=arg.split('.')

                    if len(spl)==2:
                        dummy, key=spl
                        index='0'
                    elif len(spl)==3:
                        dummy, index, key=spl
                        if index=='0':raise Exception('MultiOptions: ' + arg + ', Unsupported syntax: Index 0   is not supported !' + self.__getOptionMultiplesShapeError())
                    else:continue

                    if not index.isdigit():raise Exception('MultiOptions: ' + arg + ', Unsupported syntax ! ' + self.__getOptionMultiplesShapeError())
                    index=int(index)
                    if key not in self._option_multiple_definitions[prefix]['options']:raise Exception('MultiOptions: ' + arg + ', The Multiple Option:' + prefix + ' do not support the key:' + key + '. Supported keys are:' + str([k for k in list(self._option_multiple_definitions[prefix]['options'].keys())])[1:-1] + '.')

                    if prefix not in self.__found_option_multiple_definitions:self.__found_option_multiple_definitions[prefix]={}

                    if index not in self.__found_option_multiple_definitions[prefix]:self.__found_option_multiple_definitions[prefix][index]={}
                    elif key in self.__found_option_multiple_definitions[prefix][index]:
                        if index==0:_index='default'
                        else:_index=str(index)
                        raise Exception('MultiOptions: ' + arg + ', This Option appears twice (at index:' + _index + ') !')
                    self.__found_option_multiple_definitions[prefix][index][key]=None

        # Create dynamic optParse options
        for prefix in self.__found_option_multiple_definitions:
            # - Group
            og=optparse.OptionGroup(self.__py_parser, self._option_multiple_definitions[prefix]['label'], description=self._option_multiple_definitions[prefix]['description'])
            self.__py_parser.add_option_group(og)

            for index in self.__found_option_multiple_definitions[prefix]:
                for key in self._option_multiple_definitions[prefix]['options']:
                    if index==0:idx='.'
                    else:idx='.' + str(index) + '.'

                    wks=self._option_multiple_definitions[prefix]['options'][key]['wks']

                    type=KOption.EQUIV_PYTHON_PARSE_TYPES[wks['*type']]
                    if '*value' in wks:default=wks['*value']
                    else:default=None
                    if '*help' in wks:help=wks['*help']
                    else:help=None

                    if type==bool:
                        if default==True:
                            action='store_false'
                            default=True
                        else:
                            action='store_true'
                            default=False
                        type=None
                    else:action=None

                    # - Option
                    og.add_option ('--' + prefix + idx + key, dest=prefix + '_' + str(index) + '_' + key, type=type, action=action, default=default, help=help)
                    self.__found_option_multiple_definitions[prefix][index][key]=None

    # A999:
    def __parse_rtvSimpleOption(self, options):
        class_exit = self.__class_exit if self.__class_exit else self.__class__.__name__
        method_exit = self.__method_exit if self.__method_exit else '__parse_rtvMultipleOptions'
        # A015:
        listOfOptionInputModes = []

        if self.__has_ran != 1:
            print(KOption.CALL_SEQUENCE_ERROR)
            raise Exception('MultiOptions: Call sequence Error !')

        for name in self._option_group_by_names:
            gdefs = self._option_group_by_names[name]
            if gdefs['type'] == 'KMultipleOptionGroup': continue

            for option in gdefs['options']: # option is --<int>
                odefs = gdefs['options'][option]
                oattr = odefs['dest'] # oattr is optparse dest. optparse options only knows dest !!
                wks = odefs['wks']

                if not hasattr(options, oattr) and '*required' in wks and wks['*required']:
                    if '*value' in wks:setattr(options, oattr, wks['*value'])
                    else:raise Exception('kOption/' + 'From SubClass:%s SubMethod: %s, Option: %s is required !' % (class_exit, method_exit, option))

                value = getattr(options, oattr)
                if value == 'None':value = None

                """ A015:
            if wks['*password'] is True: This means this field is a password and must be managed as well.
                So we will add a special callback to this field that will allow it to be empty (in OptParse.add_option)).
                The cinematic will be the following and will be managed by KOption:
                - if passord has a value (--password value) : this will be used as the password.
                - if passord has no value or has a value starting with /:
                    An Exception: KwadkOptionSecurePasswordInputExcetion will be thrown:
                    with the list of all field password that must be managed a sercure way.
                    mod attributte of the Exception will be either :
                    - "prompt" if no value was provided or
                    - "file" with value if was starting by /
                    It is the responsability of the interactive interface receiving this Exception, to manage password input the rigth way.
                """
                if self.__callInteractive and '*password' in wks and wks['*password']:
                    if value == KOption.NO_PASSWORD_DEFAULT:
                        # password was not provided:
                        value = None
                        mode = KOption.NO_PASSWORD_INPUT_AS_PROMPT
                        listOfOptionInputModes.append({'option': option, 'value': value, 'mode': mode})
                        continue
                    elif value!=None and value.startswith('/'):
                        # value is password file:
                        mode = KOption.NO_PASSWORD_INPUT_AS_FILE
                        listOfOptionInputModes.append({'option': option, 'value': value, 'mode': mode})
                        continue

                p = wk.WantedKeywords()
                setattr(p, option, wks)
                wk.getKeywords(wantedKeywords=p, keywords={option: value}, remove=False, class_exit=class_exit, method_exit=method_exit)
                setattr(options, oattr, getattr(p, option))

                # Rtv group nodes:
                if not odefs['is_node']: continue
                value = getattr(options, oattr)
                if value == None: continue
                if not isinstance(value, str) or value.isspace(): raise Exception(
                    'kOption/KOptionGroup/Option: ' + odefs[
                        'int'] + ' for Group:' + name + ", incorect type should be 'str' when is_node is True ! value is:" + str(
                        value) + '.')

                group_nodes = self._group_nodes
                if value not in group_nodes: group_nodes[value] = []
                if odefs['node_type'] not in group_nodes[value]: group_nodes[value].append(odefs['node_type'])

        if len(listOfOptionInputModes)>0:raise KwadkOptionSecurePasswordInputExcetion(listOfOptionInputModes)

    def __parse_rtvMultipleOptions(self, options):
        class_exit = self.__class_exit if self.__class_exit else self.__class__.__name__
        method_exit = self.__method_exit if self.__method_exit else '__parse_rtvMultipleOptions'

        if self.__has_ran!=1:
            print(KOption.CALL_SEQUENCE_ERROR)
            raise Exception('MultiOptions: Call sequence Error !')

        self.__has_ran=2
        for prefix in self.__found_option_multiple_definitions:
            for index in self.__found_option_multiple_definitions[prefix]:
                for key in self.__found_option_multiple_definitions[prefix][index]:

                    oattr = prefix + '_' + str(index) + '_' + key
                    value=getattr(options, oattr)
                    if value == 'None': value = None

                    # A999:
                    delattr(options, oattr)
                    wks = self._option_multiple_definitions[prefix]['options'][key]['wks']
                    p = wk.WantedKeywords()
                    setattr(p, oattr, wks)
                    wk.getKeywords(wantedKeywords=p, keywords={oattr, value}, remove=False, class_exit=class_exit, method_exit=method_exit)

                    # M013:
                    self.__found_option_multiple_definitions[prefix][index][key]=getattr(p, oattr)

                    odefs=self._option_multiple_definitions[prefix]['options'][key]

                    # Rtv group nodes:
                    if not odefs['is_node']:continue
                    if  value==None:continue
                    if not isinstance(value, str) or value.isspace():raise Exception('kOption/KMultipleOptionGroup/Option: ' + key + ' for Group:' + prefix + ", incorect type should be 'str' when is_node is True ! value is:" + str(value) + '.')

                    group_nodes=self._group_nodes
                    if value not in group_nodes:group_nodes[value]=[]
                    if odefs['node_type'] not in group_nodes[value]:group_nodes[value].append(odefs['node_type'])

        return self.__found_option_multiple_definitions

    def getMultipleOptions(self):
        if self.__has_ran!=2:
            print(KOption.CALL_SEQUENCE_ERROR)
            print('Before calling getOptions.')
            raise Exception('MultiOptions: Call sequence Error !')

        return self.__found_option_multiple_definitions

# A015:
# See: https://stackoverflow.com/questions/1229146/parsing-empty-options-in-python
def oPtionalPassword():
    def func(option,opt_str,value,parser):
        if value!=None and not value.startswith('--'):
            val=value
        else:
            val=KOption.NO_PASSWORD_DEFAULT
        setattr(parser.values,option.dest,val)
    return func

# A015:
class KwadkOptionSecurePasswordInputExcetion(Exception):
    """
    list of: {'option': option, 'value': value, 'mode': mode}
    """
    def __init__(self, listOfOptionInputModes):
        import json as modjson
        if listOfOptionInputModes == None: raise Exception('Parameter listOfOptionInputModes cannot be None !')
        if not isinstance(listOfOptionInputModes, list): raise Exception('Parameter listOfOptionInputModes must be list ! Received: %s' % str(listOfOptionInputModes))
        self.__value = modjson.dumps(listOfOptionInputModes)

    def __str__(self):
        return 'KwadkOptionSecurePasswordInputExcetion:' + self.__value

    def getMessage(self):
        return self.__message

    def setMessage(self, message):
        self.__message = message



class KGroup:
    GROUP_EXCEPT_CARS=('/', '\\', ':', '|', '"', "'", ';', '<', '>', '?', '!', '$', '*', '+', '-', '.')

    def __init__(self, kOption, name, description=None, gwks=None):
        selfMethod='__init__'
        import weakref
        self.__kOption=weakref.ref(kOption)
        option_group_orders=self._kOption()._option_group_orders
        option_group_by_names=self._kOption()._option_group_by_names

        if gwks!=None:
            try:
                wk.isWKDefinition(gwks, class_exit=self.__class__.__name__, method_exit='add_option')
            except Exception as e:
                raise xception.kwadSystemException(self.__class__.__name__, selfMethod, 'Echec trying to digest gwks option for Group:' + name + ' ! SubException is:' + str(e))

        elif self.__class__.__name__=='KMultipleOptionGroup':gwks={'*ge': 0}
        else:gwks={'*le': 1}

        for car in KGroup.GROUP_EXCEPT_CARS:
            if name.find(car)>=0:raise Exception('kOption/' + self.__class__.__name__ + ': A ' + self.__class__.__name__ + ' with name:' + name + ' , caracter:' + car + ' is not allowed !')
        if name in option_group_orders:raise Exception('kOption/' + self.__class__.__name__ + ': A ' + self.__class__.__name__ + ' with name:' + name + ' is already defined !')

        self.__name=name
        if description!=None:gwks['*help']=description
        self.__description=description

        option_group_orders.append(name)
        option_group_by_names[name]= {
            'type': self.__class__.__name__,
            'description': self.__description,
            'gwks': gwks,
            'options': {},
            'option_orders':[]
        }

    def _kOption(self):
        try:
            return self.__kOption()
        except:raise Exception('kOption/' + self.__class__.__name__ + ': This instance of ' + self.__class__.__name__ + ' is lost, because its reference to the kOption instance is lost ! Advice: dont use it in this context.')

    def add_output_option(self, short=None, int=None, name=None, dest=None, wks=None, help=None, is_node=False, node_type=None):
        """
        Use  this to Add output attr into your output_node descriptor.
        Further you can navigate optxml_node or output_node with the OptStruct function (prefixed os) on them:
        for example: optxml_node.osGetParentAttr(...) e.g.: osIsSet, osSet, osUnset).
        You can setAttr on your output_node.setAttr('myAttr', value).
        And later tell output_node.osSet() to activate your output_node as return value.
        """
        if int!=None:int = '--' + KOption.OUTPUT_PREFIX + int[2:]
        if dest!=None:dest = KOption.OUTPUT_PREFIX + dest
        self.add_option(short=short, int=int, name=name, dest=dest, wks=wks, help=help, is_node=is_node, node_type=node_type)

    def add_option(self, short=None, int=None, name=None, dest=None, wks=None, help=None, is_node=False, node_type=None):
        selfMethod='add_option'
        if wks==None:wks={'*type': 'str'}
        if short=='-h' or int=='--help':raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + str(name) + ' for Group:' + self.__name + ', Option -h or --help is reserved !')
        if isinstance(self, KOptionGroup):
            if dest==None:raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' +str(name) + ' for Group:' + self.__name + ', parameter:dest is required for OptionGroup !')
            if int==None:raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + str(name) + ' for Group:' + self.__name + ', parameters: "int" is required for OptionGroup !')
            if name!=None:raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + str(name) + ' for Group:' + self.__name + ', parameters: "name"  is forbiden for OptionGroup !')
            name=int.split('--')[-1]

        elif isinstance(self, KMultipleOptionGroup):
            if dest!=None:raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + str(name) + ' for Group:' + self.__name + ', parameter: dest is forbidden for MultipleOptionGroup !')
            if (short, int)!=(None, None):raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + str(name) + ' for Group:' + self.__name + ', parameters: "short" and "int" are forbiden for MultipleOptionGroup !')
            if name==None:raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + str(name) + ' for Group:' + self.__name + ', parameters: "name"  is required for MultipleOptionGroup !')

        if short!=None and (short[0]!='-' or short[1:].startswith('-')):raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + name + ' for Group:' + self.__name + ', Incorect parameters: "short":' + short + ' ! The right shape is -<option_name>.')
        if int!=None and (int[0:2]!='--' or int[2:].startswith('-')):raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + name + ' for Group:' + self.__name + ', Incorect parameters: "int":' + int + ' ! The right shape is --<option_name>.')
        if not isinstance(is_node, bool):raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + name + ' for Group:' + self.__name + ', Incorect parameters: "is_node":' + str(is_node)+ ' ! Expected bool.')
        if is_node and not isinstance(node_type, str):raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + name + ' for Group:' + self.__name + ', Incorect parameters: "node_type":' + str(node_type)+ ' ! is required when is_node is True.')

        option_group_by_names=self._kOption()._option_group_by_names

        if name.find(' ')>=0 or name.find('-')>=0:raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + name + ' for Group:' + self.__name + ', bad Name, cannot contain any space, "-" or "." ! Your value:' + str(name) + '.')
        if name in option_group_by_names[self.__name]['option_orders']:raise Exception('kOption/' + self.__class__.__name__ + '/Option: An option named: ' + name + ' has already been added to Group: ' + self.__name +  ' !')

        try:
            wk.isWKDefinition(wks, class_exit=self.__class__.__name__, method_exit='add_option')
            if help!=None:wks['*help']=help
        except Exception as e:
            if self.__name!='__default__':more=', Group:' + self.__name
            else:more=''
            raise xception.kwadSystemException(self.__class__.__name__, selfMethod, 'Echec trying to digest wks option for Option:' + name + more + ' ! SubException is:' + str(e))

        if help!=None:wks['*lhelp']=help
        if '*type' not in wks:wks['*type']='str'
        if wks['*type'] not in list(KOption.EQUIV_PYTHON_PARSE_TYPES.keys()):raise Exception('kOption/' + self.__class__.__name__ + '/Option: ' + name + ' for Group:' + self.__name + ', bad Type: '  + str(wks['*type']) + ' supported Types are:' + str(list(KOption.EQUIV_PYTHON_PARSE_TYPES.keys())).replace(' ', '')[1:-1] +  ' !')

        option_group_by_names[self.__name]['option_orders'].append(name)
        option_group_by_names[self.__name]['options'][name]={'wks': wks, 'dest': dest, 'short': short, 'int': int, 'is_node': is_node, 'node_type': node_type}

class KOptionGroup(KGroup):

    def __init__(self, kOption, name, description=None, gwks=None):
        KGroup.__init__(self, kOption, name, description=description, gwks=gwks)

class KMultipleOptionGroup(KGroup):

    def __init__(self, kOption, name, label, description=None, gwks=None):
        selfMethod='__init__'
        KGroup.__init__(self, kOption, name, description=description, gwks=gwks)
        option_group_by_names=self._kOption()._option_group_by_names
        option_multiple_definitions=self._kOption()._option_multiple_definitions
        if name.find(' ')>=0 or name.find('-')>=0 or name.find('.')>=0:raise Exception('kOption/MultipleOptionGroup: A MultipleOptionGroup/name cannot contain any space or "." ! Your value:' + str(name) + '.')
        if name in option_multiple_definitions:raise Exception('kOption/MultipleOptionGroup: A MultipleOptionGroup with name:' + name + ' is already defined !')

        option_multiple_definitions[name]=option_group_by_names[name]
        option_multiple_definitions[name]['label']=label

# A017: +doHelps=None
def optoxml(kOption, optoxml_dir=None, firsTag=None, except_groups=[], except_options=[], group_alias=None, doHelps=None, verbose=0):
    """
    Expected doHelps:
    doHelps = {
        'category': !None,
        'software': !None,
        'softclass': !None,
        'lang': !None,
        'deploy': !False,
        'deleteFile': !False,
        '_fdhelp': !None,
        'temp_dir': !None
    }
    """
    self_funct="optoxml"
    XML_CLEANUPS=(('>', '&gt;'), ('<', '&lt;'), ("'", '-'), ('"', '-'), (',', ';'), (':', '-'), ('{', '-'), ('}', '-'), ('[', '-'), (']', '-'), ('(', '-'), (')', '-'))
    caller=firsTag
    err_prefix=firsTag + ':Options Check> '
    if group_alias:GROUP_ALIAS=group_alias
    else:GROUP_ALIAS='groups'
    fdhelp = None
    if doHelps!=None and ('deploy' not in doHelps or 'deploy' in doHelps and not doHelps['deploy']):doHelps=None

    class Options:
        def __init__(self):
            self._simple_options={}
            self._multiple_options={}

        def new_options(self, name=None, wks=None, group_name=None, group_wks=None):
##            if group_help!=None:
##                for cars in OPTOXML_CLEAN_HELPS:group_help=group_help.replace(cars[0], cars[1])
            gname=group_name.replace(' ', '_')
            if gname not in self._simple_options:
                self._simple_options[gname]={'_group_definiton_': {'title': group_name, 'is_multiple': False, 'gwks': group_wks}}
                self._simple_options[gname]['_options_']=[]
            self._simple_options[gname]['_options_'].append({'name': name, 'wks': wks})

        def new_xoptions(self, prefix=None, name=None, wks=None, group_name=None, group_wks=None):
            if prefix not in self._multiple_options:
                self._multiple_options[prefix]={'_group_definiton_': {'title': group_name, 'is_multiple': True, 'gwks': group_wks}}
                self._multiple_options[prefix]['_options_']=[]
            self._multiple_options[prefix]['_options_'].append({'name': name, 'wks': wks})

        def getValues(self):
            return self._simple_options, self._multiple_options

    # A017: +doHelps
    def mkGroups(desc_sb, source_sb, indent, dgroups, keys, doHelps=None):
        _fdhelp = None
        for group in keys:
            if group in except_groups:continue

            group_options=[]
            gdefns=dgroups[group]['_group_definiton_']
            is_multiple=gdefns['is_multiple']
            do_user=False

            wks={}

            ## Groups Wks
            if gdefns['gwks']!=None:wks.update(gdefns['gwks'])

            # A017:
            if doHelps!=None:
                tagfil = doHelps['softclass']
                if group != '__default__': tagfil += '.' + group
                attr = None
                help = None if gdefns['title'] != '__default__' else gdefns['title']
                category = doHelps['category']
                software = doHelps['software']
                softclass = doHelps['softclass']
                lang = doHelps['lang']
                deploy = doHelps['deploy']
                deleteFile = doHelps['deleteFile']
                isNewSoftClass = doHelps['isNewSoftClass']
                _fdhelp = doHelps['_fdhelp']
                temp_dir = doHelps['temp_dir']
                if '*help' in wks:lhelp = wks['*help']
                else:lhelp=None
                isNewSoftClass = False

                if help!=None and lhelp != None:
                    wks['*help'], lhelp, _fdhelp = genHelp(category, software, softclass, tagfil, attr, help, lhelp, temp_dir, lang=lang, deploy=deploy, deleteFile = deleteFile, isNewSoftClass=isNewSoftClass, _fdhelp=_fdhelp)
                    if lhelp!=None:wks['*lhelp'] = lhelp
                    doHelps['_fdhelp'] = _fdhelp
                    doHelps['isNewSoftClass'] = False
            else:
                if '*help' in wks:
                    wks['*lhelp']=xmlCleanup(wks['*help'])
                wks['*help']=gdefns['title']
                if wks['*help']!=None and len(wks['*help']) > 30:wks['*help'] = wks['*help'][0:25] + '...'


            if  '*eq' in wks and wks['*eq']==1 or \
                '*ge' in wks and wks['*ge']>=1 or \
                '*gt' in wks and wks['*gt']>=0:do_user=True


            # desc_sb.write(indent + '<' + group + '\n' + 2 * indent + ' __wk__="' + CoolTyping.unDress(wks) + '" ')
            if group!='__default__':
                # todo later: _is_multiple_ was removed cause epicmlp do not manage attr starting with: _ desc_sb.write('\n' + 2*indent + '<' + group + ' _is_multiple_="{*type:bool,*value:' +  str(is_multiple) + ',*rolesAutz:{*anyone:-allow;-display},*rolesAutzDft:{*anyone:-allow;-display}}"\n' + 3 * indent + ' __wk__="' + str(wks).replace('"', "'") + '" ')
                desc_sb.write('\n' + 2*indent + '<' + group + '\n' + 3 * indent + ' __wk__="' + str(wks).replace('"', "'") + '" ')
                if do_user:source_sb.write('\n' + 2*indent + '<' + group + '\n')

            odefns=dgroups[group]['_options_']

            for opts in odefns:
                attrs={}
                group_options.append(attrs)
                optname=opts['name']

                attrs[optname]=opts['wks']
                if '*withJson' not in attrs[optname] and '*withEval' not in attrs[optname]:attrs[optname]['*withCoolTyping']=True
                if '*required' in attrs[optname] and attrs[optname]['*required']:attrs[optname]['*help']='*'

                # A017:
                if doHelps != None:
                    tagfil = doHelps['softclass']
                    if group != '__default__': tagfil += '.' + group
                    attr = optname
                    category = doHelps['category']
                    software = doHelps['software']
                    softclass = doHelps['softclass']
                    lang = doHelps['lang']
                    deploy = doHelps['deploy']
                    deleteFile = doHelps['deleteFile']
                    isNewSoftClass = doHelps['isNewSoftClass']
                    _fdhelp = doHelps['_fdhelp']
                    temp_dir = doHelps['temp_dir']
                    help = None
                    lhelp = None
                    if '*help' in attrs[optname]: help=attrs[optname]['*help']
                    if '*lhelp' in attrs[optname]: lhelp=attrs[optname]['*lhelp']
                    isNewSoftClass = False

                    if (help, lhelp) != (None, None):
                        help, lhelp, _fdhelp = genHelp(category, software, softclass, tagfil, attr, help, lhelp, temp_dir, lang=lang, deploy=deploy, deleteFile = deleteFile, isNewSoftClass=isNewSoftClass, _fdhelp=_fdhelp)
                        doHelps['_fdhelp'] = _fdhelp
                        doHelps['isNewSoftClass'] = False

                    if help != None: attrs[optname]['*help'] = help
                    if lhelp != None: attrs[optname]['*lhelp'] = lhelp
                else:
                    if '*help' in attrs[optname]:attrs[optname]['*help']=xmlCleanup(attrs[optname]['*help'])
                    if '*lhelp' in attrs[optname]:attrs[optname]['*lhelp']=xmlCleanup(attrs[optname]['*lhelp'])
                    if '*lhelp' in attrs[optname] and attrs[optname]['*help'] != None and len(attrs[optname]['*help']) > 30: attrs[optname]['*help'] = attrs[optname]['*help'][0:25] + '...'


            for attrs in group_options:
                if group=='__default__' and list(attrs.keys())[0]=='help':continue
                if group=='__default__':idx=1
                else:idx=3

                desc_sb.write('\n' + idx * indent + list(attrs.keys())[0] + '="' + str(attrs[list(attrs.keys())[0]]).replace('"', "'") + '" ')
                if do_user or group=='__default__':
                    if '*value' in attrs[list(attrs.keys())[0]] and attrs[list(attrs.keys())[0]]['*value']!=None:value=attrs[list(attrs.keys())[0]]['*value']
                    elif attrs[list(attrs.keys())[0]]['*type']=='int':value=0
                    elif attrs[list(attrs.keys())[0]]['*type']=='bool':value=False
                    elif '*required' in attrs[list(attrs.keys())[0]] and attrs[list(attrs.keys())[0]]['*required']:value='MY_' + list(attrs.keys())[0].upper()
                    else:value=''

                    source_sb.write('\n' + idx * indent + list(attrs.keys())[0] + '="' + str(value) + '" ')

            if group=='__default__':
                # If more groups than default.
                if len(dgroups) > 1:
                    desc_sb.write('\n>\n' + indent + '<%s __wk__="{*eq:1}">\n' % GROUP_ALIAS)
                    source_sb.write('\n>\n' + indent + '<%s>\n' % GROUP_ALIAS)
                else:
                    desc_sb.write('\n>')
                    source_sb.write('\n>')
            else:
                desc_sb.write('\n' + 2*indent + '/>\n')
                if do_user:source_sb.write('\n' + 2*indent + '/>\n')

        return _fdhelp

    def xmlCleanup(source):
        if source==None:return

        for cars in XML_CLEANUPS:
            source=source.replace(cars[0], cars[1])

        return source


    o=Options()
    from os import path
    if optoxml_dir!=None and not path.isdir(optoxml_dir):raise xception.kwadSystemException(err_prefix, self_funct, 'The directory:' + str(optoxml_dir) + ', must exist !')


    ## Regulars Option:
    ## ----------------
    for group in kOption._option_group_by_names:
        gdefs=kOption._option_group_by_names[group]

        gname=group
        option_orders=gdefs['option_orders']

        for option in option_orders:
            if gname=='__default__' and option in  except_options:continue

            o.new_options(name=option, wks=gdefs['options'][option]['wks'], group_name=gname, group_wks=gdefs['gwks'])


    ## Multiple Option:
    ## ----------------
    for prefix in kOption._option_multiple_definitions:
        gdefs=kOption._option_multiple_definitions[prefix]

        gname=prefix
        option_orders=gdefs['option_orders']

        for option in option_orders:
            o.new_xoptions(prefix=prefix, name=option, wks=gdefs['options'][option]['wks'], group_name=gname, group_wks=gdefs['gwks'])


    from io import StringIO
    desc_sb=StringIO()
    source_sb=StringIO()
    indent=3*' '

    desc_sb.write('<' + firsTag)
    source_sb.write('<' + firsTag)

    # ------------
    # All Groups :
    # ------------
    # self._simple_options[gname]={'_group_definiton_': {'title': group_name, 'help': group_help}}
    # self._simple_options[gname]['_options_'].append({'name': name, 'type': type, 'default': default, 'help': help})
    # self._multiple_options[prefix]={'_group_definiton_': {'title': group_name, 'help': group_help}}
    # self._multiple_options[prefix]['_options_'].append({'name': name, 'type': type, 'default': default, 'help': help})
    dgroups=dict(o._simple_options)
    dgroups.update(o._multiple_options)
    keys=list(dgroups.keys())

    ## Ordering Groups
    keys=['__default__']
    del keys[keys.index('__default__')]
    keys.extend([name.replace(' ', '_') for name in kOption._option_group_orders])

    _fdhelp = mkGroups(desc_sb, source_sb, indent, dgroups, keys, doHelps=doHelps)


    # If more groups than default.
    if len(dgroups) > 1:
        desc_sb.write('\n' + indent + '</%s>' % GROUP_ALIAS)
        source_sb.write('\n' + indent + '</%s>' % GROUP_ALIAS)

    desc_sb.write('\n</' + firsTag  + '>')
    source_sb.write('\n</' + firsTag  + '>')

    if optoxml_dir==None:
        print('*' + (len('DESCRIPTPOR') + 2) *'=' + '*')
        print('* DESCRIPTPOR *')
        print('*' + (len('DESCRIPTPOR') + 2) *'=' + '*\n')
        print(desc_sb.getvalue())
    else:
        options_desc_file = path.normpath(optoxml_dir + '/' + caller + '_desc.xml')
        fd=open(options_desc_file, 'wb')
        if verbose>=0:print('optoxml writing Option Descriptor file at:' + path.normpath(optoxml_dir + '/' + caller + '_desc.xml') + '.')
        fd.write(bytes(desc_sb.getvalue(), 'utf-8'))
        fd.close()

    if optoxml_dir==None:
        print('\n\n*' + (len('SOURCE_FILE') + 2) *'=' + '*')
        print('* SOURCE_FILE *')
        print('*' + (len('SOURCE_FILE') + 2) *'=' + '*\n')
        print(source_sb.getvalue())
    else:
        options_file = path.normpath(optoxml_dir + '/' + caller + '.xml')
        fd=open(options_file, 'wb')
        if verbose>=0:print('optoxml writing Option Sample file at:' + path.normpath(optoxml_dir + '/' + caller + '_user.xml') + '.')
        fd.write(bytes(source_sb.getvalue(), 'utf-8'))
        fd.close()

    return source_sb.getvalue().strip(), desc_sb.getvalue().strip(), _fdhelp


class ReproductibleCrypt:

    def __init__(self, persistent_dir=None, recover=False):
        self_funct='__init__'
        from os import path
        if persistent_dir==None:persistent_dir=path.normpath(getInstallDir() + '/langs')
        if not path.isdir(persistent_dir):raise xception.kwadParameterException(self.__class__.__name__, self_funct, 'Parameter directory persistent_dir:' + str(persistent_dir) + ' must exist !')
        keyfile=path.normpath(persistent_dir + '/macuuid.key')
        if recover and not path.isfile(keyfile):raise xception.kwadParameterException(self.__class__.__name__, self_funct, 'The persistent keyfile (' + keyfile + ') do not exist !')

        if not recover:
            from uuid import getnode as get_mac
            self.__key=str(get_mac())
            fd=open(keyfile, 'wb')
            fd.write(bytes(self.__key, 'utf-8'))
            fd.close()
        else:
            fd=open(keyfile, 'rb')
            self.__key=fd.read().decode("utf-8")
            fd.close()

    def encode(self, value):
        from kwadlib.security.crypting import SimpleCrypt
        return SimpleCrypt.encode(self.__key, value)

    def decode(self, value):
        from kwadlib.security.crypting import SimpleCrypt
        return SimpleCrypt.decode(self.__key, value)


class Logger:
    SUFFIX='.log'

    def __init__(self, file, rotate=50):
        from os import chmod, path, listdir, stat, remove
        import sys
        if rotate == None: rotate = 50
        if isinstance(sys.stdout, Logger):
            sys.stdout.reopen()
            return

        self.__file=file
        pre_exist=path.isfile(self.__file)

        # Rotate
        log_dir=path.split(self.__file)[0]
        ld=listdir(log_dir)
        ld=[file for file in ld if path.isfile(path.normpath(log_dir + '/' + file)) and file.endswith(self.SUFFIX)]
        if len(ld)>=rotate:
            files={}
            delta=len(ld) - rotate
            for file in ld:
                file=path.normpath(log_dir + '/' + file)
                files[stat(file).st_ctime]=file

            keys=list(files.keys())
            keys.sort()

            for key in keys:
                remove(files[key])
                delta=delta - 1
                if delta==0:break

        # Open
        self.__fd = open(self.__file, "a")
        if not pre_exist:chmod(self.__file, 0o722)
        self.__terminal = sys.stdout
        sys.stdout=sys.stderr=self

    def write(self, message):
        try:
            self.__terminal.write(message)
            self.__terminal.flush()
        except:
            # To avoid some: BrokenPipeError: [Errno 32] Broken pipe (when called into a submodule of a main pg called by webMenu)
            pass
        self.__fd.write(message)
        self.__fd.flush()

    def writef(self, message):
        self.__fd.write(message)
        self.__fd.flush()

    def flush(self):
        self.__fd.flush()

    def close(self):
        if self.__fd!=None:self.__fd.close()
        self.__fd=None

    def reopen(self):
        self.close()
        self.__fd=open(self.__file, "a")


                                                    #------------------#
                                                    #  SoftClass tools #
                                                    #------------------#

def tracebackToString(e, count=None):
    import traceback
    spl = ''.join(traceback.format_exception(None, e, e.__traceback__))

    if count == None or len(spl) <= count:return ''.join(spl)
    else:return ''.join(traceback.format_exception(None, e, e.__traceback__)[-count:])

# -------------------------#
# Parse Tmpl Xml File Path #
# -------------------------#

def txfParsePath(xml_file_path, basedir=None):
    TMPL_XML_FILE_SHAPE="""
    <basedir>/activities/<activity>/categories/<category>/templates/<template>/by/<who>/environments/<environment>/template_instances/<template_instance>.xml
    """
    from os import path
    """
    /activities/default/categories/middleware/software/tom/templates/cluster/environments/recette/template_instances/rrifr1/scope
    /activities/default/categories/middleware/software/tom/templates/cluster/environments/recette/template_instances/rrifr1/rrifr1.xml
    """
    dkeys={'activities': ('activity', 1), 'environments': ('environment', 3), 'categories': ('category', 5), 'software': ('software', 7), 'templates': ('template', 9), 'by': ('byWho', 11), 'template_instances': ('template_instance', 13)}
    lkeys=('activities', 'environments', 'categories', 'software', 'templates', 'by', 'template_instances')
    llkeys=('activity', 'environment', 'category', 'software', 'template', 'byWho', 'template_instance')
    xml_file_path=path.normpath(xml_file_path)
    fname=path.split(xml_file_path)[-1]
    if basedir==None:
        spl=xml_file_path.split('/activities')
        if len(spl)!=2:return {'activity': None, 'environment': None, 'category': None, 'software': None, 'template': None, 'byWho': None, 'template_instance': None}, None
        basedir=spl[0]
    else:basedir=path.normpath(basedir)
    xscope_keys={}
    doclear=False

    if xml_file_path.startswith(basedir):
        xml_file_path=path.split(xml_file_path)[0].replace('//', '/')

        spl=xml_file_path.split('/activities')
        if len(spl)==2:
            xml_file_path='activities' + spl[-1]
            spl=xml_file_path.split('/')
            for k in lkeys:
                key, index=dkeys[k]
                if (len(spl)-1)<index-1:
                    doclear=True
                    break

                if spl[index-1]==fname:break
                if k!=spl[index-1]:
                    doclear=True
                    break

                if (len(spl)-1)<index:
                    doclear=True
                    break

                xscope_keys[key]=spl[index]

            # Check last key
            if k!='template_instances':doclear=True
        else:doclear=True

    for e in llkeys:
        if doclear or e not in xscope_keys:xscope_keys[e]=None

    if doclear:raise Exception('xml_file sope file at:' + xml_file_path + ', incorrect scope path !, The valid scope path shape is:' + TMPL_XML_FILE_SHAPE + ' .')

    return xscope_keys, basedir


# --------------------------------------#
# Check Tmpl Xml File Header (top Node) #
# --------------------------------------#

def txfCheckHeader(combined_file, temp_dir=None, verbose=0):
    selfMethod='txfCheckHeader'
    from kwadlib import epicxmlp
    from os import path
    if temp_dir==None:raise xception.kwadParameterTypeException('Main', selfMethod, 'temp_dir', 'str', str(temp_dir))

    cxf_xscope_keys, basedir=txfParsePath(combined_file)
    top_node=epicxmlp.digest(file_source=combined_file, temp_dir=temp_dir, verbose=5)
    # Attribute: TOP/location:
    if not top_node.hasAttr('location'):raise xception.kwadParameterTypeException('Main', selfMethod, ' The Template Xml File:' + combined_file + ': Incorect syntax: The first node must support the following Attribute: location !')
    location=top_node.getAttr('location')
    loc_xscope_keys, basedir=txfParsePath(location + '/' + path.split(combined_file)[-1])
    if cxf_xscope_keys!=loc_xscope_keys:raise  xception.kwadParameterTypeException('Main', selfMethod, ' The Template Xml File:' + combined_file + ': Incorect path, this file should be located into a directory: <base_dir>/' + location + ' as specified by the related "location" attribute within this xml file !')

    # Attribute: TOP/tmplid_orders:
    if not top_node.hasAttr('tmplid_orders'):raise xception.kwadParameterTypeException('Main', selfMethod, ' The Template Xml File:' + combined_file + ': Incorect syntax: The first node must support the following Attribute: tmplid_orders !')
    tmplid_orders=top_node.getAttr('tmplid_orders').split(',')
    # Attribute: TOP/tmplids:
    if not top_node.hasAttr('tmplids'):raise xception.kwadParameterTypeException('Main', selfMethod, ' The Template Xml File:' + combined_file + ': Incorect syntax: The first node must support the following Attribute: tmplids !')
    tmplids=top_node.getAttr('tmplids').split(',')
    if len(tmplid_orders)!=len(tmplids):raise xception.kwadParameterTypeException('Main', selfMethod, ' The Template Xml File:' + combined_file + ': Incorect syntax: The length of the Attribute: "tmplid_orders" must be the same as the length of the "tmplids" Attribute !')
    tmplids={tmplid_orders[i]:tmplids[i] for i in range(len(tmplid_orders))}
    # Attribute: TOP/kwad_attrs_scope:
    if not top_node.hasAttr('kwad_attrs_scope'):raise xception.kwadParameterTypeException('Main', selfMethod, ' The Template Xml File:' + combined_file + ': Incorect syntax: The first node must support the following Attribute: kwad_attrs_scope !')
    kwad_attrs_scope=top_node.getAttr('kwad_attrs_scope')

    return {'top_node': top_node, 'kwad_attrs_scope': kwad_attrs_scope, 'xscope_keys': loc_xscope_keys, 'tmplids': tmplids, 'tmplid_orders': tmplid_orders}



# ------------------#
# Init/Kwad.attrs #
# ------------------#

def cpfiles(files, dir):
    from shutil import copyfile
    from os import path
    new_files = []

    for file in files:
        copyfile(file, dir + '/' + path.split(file)[-1])
        new_files.append(path.split(file)[-1])

    return new_files

def listDirByTs(dir):
    from os import listdir, stat, path
    lmtimes = []
    dfiles = {}
    files = []

    l=listdir(dir)
    for f in l:
        f = (dir + '/' + f)
        st = stat(f)
        if st.st_mtime not in lmtimes:
            lmtimes.append(st.st_mtime)
            dfiles[st.st_mtime] = []

        dfiles[st.st_mtime].append(f)

    lmtimes.sort()
    lmtimes.reverse()
    for t in lmtimes:
        files.extend(dfiles[t])

    files = [path.split(f)[-1] for f in files]

    return files



import sys
class RedirectStd:

    def __init__(self, stdout=None, stderr=None, nostdout=False, nostderr=False, log_dir=None, log_file=None, log_dir2=None, log_file2=None):
        from os import path
        self.__is_closed = False
        if not ((log_dir!=None and log_file!=None) or ((log_dir, log_file) == (None,None))):raise Exception('log_dir and log_file work together !')
        if not ((log_dir2!=None and log_file2!=None) or ((log_dir2, log_file2) == (None,None))):raise Exception('log_dir2 and log_file2 work together !')
        if log_dir!=None:self.__log_file=open(path.normpath(log_dir + '/' + log_file), 'a')
        else:self.__log_file = None
        if log_dir2!=None:self.__log_file2=open(path.normpath(log_dir2 + '/' + log_file2), 'a')
        else:self.__log_file2=None
        self.__nostdout=nostdout
        self.__og_stdout=stdout
        if not nostderr:
            self.__og_stderr=stderr
            sys.stdout=sys.stderr=self
        else:sys.stdout=self
        self.__lastWasSlashN = False

    def getOgStdout(self):
        return self.__og_stdout

    def getOgStderr(self):
        return self.__og_stderr

    def write(self, value):
        if self.__is_closed:
            self.__og_stdout.write(value)
            return

        self.write_console(value)
        self.write_file(value)

    def write_console(self, value):
        if self.__nostdout:return
        self.__og_stdout.write(value)
        self.__og_stdout.flush()

    def write_file(self, value):
        self.__lastWasSlashN = value.endswith('\n')
        from datetime import datetime
        dt = datetime.now()
        if self.__lastWasSlashN and not value.startswith('\n'):strime = dt.strftime('%Y-%m-%d %H:%M:%S:  ')
        else:strime = ''

        if self.__log_file:
            self.__log_file.write(strime + value)
            self.__log_file.flush()
        if self.__log_file2:
            self.__log_file2.write(strime + value)
            self.__log_file2.flush()

    def flush(self):
        pass

    def close(self):
        import sys
        if self.__is_closed:return
        self.__is_closed = True
        if self.__log_file != None:self.__log_file.close()
        if self.__log_file2 != None:self.__log_file2.close()
        self.stdout = sys.stdout = self.__og_stdout
        if self.__og_stderr!=None:
            self.stderr = sys.stderr = self.__og_stderr



def genHelp(category, software, softclass, tagfil, attr, help, lhelp, temp_dir, lang='en', deleteFile=False, deploy=False, isNewSoftClass=False, _fdhelp=None):
    """
    Generates category.<category>.<lang>.db into the <temp_dir>/lang dir or <lang_dir> if deploy.
    """
    self_funct='genHelp'

    intro1 = """\
# -------------#
# General help #
# -------------#
    """
    intro2 = "# SoftClass <ctg>.<sfw>.<softclass> help #"
    from os import mkdir
    doHeader = False
    if help!=None:help = help.strip()
    if lhelp!=None:lhelp = lhelp.strip()
    if help == '':help = None
    if lhelp == '':lhelp = None


    if _fdhelp == None:
        from os import path
        if deploy:
            from kwadlib.default import getLangsDir
            instdir = getLangsDir()
        else:
            instdir = temp_dir + '/langs'

        if not path.isdir(instdir): mkdir(instdir)
        f = path.normpath(instdir + '/softclass.' + category + '.' + software + '.%s' % lang)
        if deleteFile and path.isfile(f):
            from os import remove
            remove(f)
        if not path.isfile(f):doHeader=True
        _fdhelp = open(f, 'a')

    if doHeader:_fdhelp.write(intro1 + '\n\n')
    if isNewSoftClass:
        s = intro2.replace('<ctg>', category).replace('<sfw>', software).replace('<softclass>', softclass)
        _fdhelp.write('\n#' + (len(s) - 2) * '-' + '#\n')
        _fdhelp.write(s + '\n')
        _fdhelp.write('#' + (len(s) - 2) * '-' + '#\n\n\n')


    vhelp = help
    if lhelp != None:
        if lhelp.find('.') <= 0:
            vlhelp = lhelp
        else:
            vlhelp = '.\\\n'.join(''.join(lhelp.strip().split('\n')).split('.'))[:-2]
    else:vlhelp=None

    if tagfil!=None:
        tagfil = tagfil.strip()
        if tagfil == '':tagfil=None
    if tagfil!=None:n = tagfil + '.'
    else:n=''
    if attr!=None:n = n + attr

    if vhelp!=None:_fdhelp.write(n + '.help' + '=' + vhelp + '\n')
    if vlhelp!=None:_fdhelp.write(n + '.lhelp' + '=' + vlhelp + '\n\n\n')

    if vhelp!=None:wkhelp = '%lang/softclass.' + category + '.' + software + '.%s/' % lang + n + '.help'
    else:wkhelp = None
    if vlhelp!=None:wklhelp = '%lang/softclass.' + category + '.' + software + '.%s/' % lang + n + '.lhelp'
    else:wklhelp=None

    return wkhelp, wklhelp, _fdhelp



def kSearch(node, attr, ksearch_wks, verbose=0):
    """
    - Type Command: {'type': 'command', 'parms': {'parm1': 'value1', 'parm2': 'value2'}, 'command': 'mycommand $attr1$ $attr2$ $parm1$ $parm2$', 'resultKey': 'tag0/tag1/tag2'}
    keys: type, parms, command
    The search for that field is using the command: mycommand.
    - Type OptStruct: {'type': 'otstruct', 'attrs': [<tag2/tag1/tag02@attr1>, <tag2@attr2>, ...], 'parms': [{'parm1': 'value1', 'parmn': 'valuen'}], 'operation': 'read', 'bsl': [<otherSoftClassBal>], 'appinst': <appinst>, 'machine': [<machine>], 'resultKey': 'tag0/tag1/tag2'}
    keys: type, attrs, operation, read
    """
    self_funct = 'ksearch'
    from kwadlib import default, wk
    import json as modjson

    """ Sample Test:
    # Test1:
    #  --domain t --env r    
    # 'parms': {'parm1': 'value1', 'parm2': 'value2'}
    wks = {'type': 'optstruct', 'attrs': tags, 'operation': 'read', 'bsl':  None, 'resultKey': 'Machines/Machine'}
    softclass.ksearch(node_read, 'machine', wks, 'kcontrol', machine='trabaabd', verbose=30)

    # Test2:
    v = """ '{"Machines": {"Machine": [{"machine": "trabaabd", "digits": 1, "name": "myname0", "title": "mytitle", "description": "mydesc", "host": "myhost", "ipv4": "127.0.0.1", "ipv6": "127.0.0.2", "sshport": 2020}]}}'  """
    wks = {'type': 'command', 'command': 'echo %s' % v, 'resultKey': 'Machines/Machine'}
    softclass.kSearch(node_read, 'machine', wks, 'kcontrol', machine=None, verbose=30)

    # Real ex in middleware§oss softclass.xml:    
    name="{'*value': 'my_srv','*required':True, '*help': '%lang/softclass.oss.en/ssl.name.help',\
        '*ksearch': {'type': 'optstruct', 'parms': {'domain': 't', 'env': 'r',  'doSubtree': 'r'}, 'operation': 'read', 'section': 'mac', 'bsl':  'middleware§kwad.Machine', 'appinst': 'kcontrol', 'resultKey': 'Machines/Machine'}}"
    """
    wk.isWKDefinition({'*ksearch': ksearch_wks}, class_exit='Main', method_exit='ksearch')
    if 'resultKey' in ksearch_wks:resultKey = ksearch_wks['resultKey']
    else:resultKey = None
    prefix = 'Error running *ksearch: %s for Attribute: %s, ' % (str(ksearch_wks), attr)
    doShell = False

    # todo
    try:
        # attrs:
        attrs = {}
        if 'attrs' in ksearch_wks:
            bus = ksearch_wks['attrs']
            for bu in bus:
                attr = bu.split('@')[-1]
                value = node.pxq_bu(bu)
                attrs[attr] = value

        # parms:
        if 'parms' in ksearch_wks:parms = ksearch_wks['parms']
        else:parms = {}

        if ksearch_wks['type'] == 'command':
            # keys: type, parms, command, resultKey
            command = ksearch_wks['command']

            for attr in attrs:command = command.replace ('$%s$' % attr, str(attrs[attr]))
            for parm in parms:command = command.replace ('$%s$' % parm, str(parms[parm]))

            # commands = ('bash', '-c', command)
            doShell = True

        elif ksearch_wks['type'] == 'optstruct':
            pass
            """
            type: *ksearch: is not supported by stdandalone KastMenu but by dkwad/KastMenu.
            """

        ## json_str = check_output(commands)
        #1:!
        p = Popen(command, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=doShell)
        stdout, stderr = p.communicate()
        ret = p.wait()
        stdout_stderr = stdout
        if stderr != None: stdout_stderr = stdout + '\n' + stderr
        if ret != 0:
            raise Exception("Unable to run command: %s ! %s" % (command, stdout_stderr))


        json_str = stdout_stderr

        try:
            json = modjson.loads(json_str)
        except Exception as e:
            raise Exception ('Error trying to parse json: %s ! subexception is: %s' % (json_str, str(e)))

        new_json = json
        if resultKey != None:
            spl = resultKey.split('/')
            if not isinstance(new_json, dict): raise xception.kwadSystemException('Main', self_funct, 'For *ksearch with resultKey: %s ! Unable to find resultKey into json response: %s' %(resultKey, str(json)))

            for tag in spl:
                if not isinstance(new_json, dict) and isinstance(new_json, list) and len(new_json) == 1:new_json=new_json[0] # jump in list if this level appens to be a list not a dict.
                if not isinstance(new_json, dict) or tag not in new_json: raise xception.kwadSystemException('Main', self_funct, 'For *ksearch with resultKey: %s ! Unable to find resultKey into json response: %s' %(resultKey, str(json)))
                new_json = new_json[tag]
            json = new_json

        return json

    except Exception as e:
        raise xception.kwadSystemException('Main', self_funct, prefix + 'SubException is: %s' % str(e))
