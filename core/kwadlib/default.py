TEMP_DIR = None
KAST_LANGS_DIR = None
KAST_SAMPLES_DIR = None
KAST_DBPATH='/var/kastmenu-server/db/kastmenu-server.db'
KASTSERVER_LOG='kastserver.log'

KAST_USER="kastmenu"

class FILE_ORIGIN:
    STDIN = 'STDIN'
    SOURCE= 'SOURCE'
    FILE = 'FILE'


ACTION_OUTPUT_MARK = '@koutref-'
ACTION_INPUT_MARK = '@kinref'
ACTION_INPUT_MARK_SEP = '---'
OUTPUT_LINK_FORMAT =  """
Syntax:
@koutref-<name>/<tdc> (Prefered)
e.g.: 
@koutref-myact1/tag1/tag2[@attr1=val1,@attr1=val1,@attr1=val1]@attr4
@koutref-myact1@id
@koutref-myact1/Machines/Node@id

Where:
name: is either the value of the attribute name of the target softclass or value of the attribute name defined 
into the special konfig tag.
This name value is unique into mixe of softclasses files or the combined file.

tdc: is a kind of xpath into the cobmined file:
e.g.: @koutref-myact1/tag1/tag2[@attr1=val1,@attr2=val2,@attr2=val2,]@attr
It must end by the target attribute: @attr from with the value must be retreived.

An Output link refers to an output value produced by an softclass or a template.
SoftClasses may produce output it will always be an extra tag output defined into the softclass's descriptor file.
At execution time an output for softclass jss.ssl may look like this:
...
<ssl>
  <keystore created='False' path='/tmp/kwad/my_srv_keystore.jks'/>
  <p12 created='True' path='/tmp/kwad/my_clt_keystore.p12'/>
<ssl>

You should may also use the special tag <Konfig name='your_name'>
to set your SoftClass config name instead of directly setting an Attribute ssl/name.
e.g.: 
<ssl type ='softclass' bsl='middleware§jss.ssl' dir='$[temp_dir]>
    <Konfig name = 'blabla'/>
</ssl>

And later in the config file another softclass could refer to this output
@koutref-blabla/keystore@path
"""

# AG001:
OUTPUTS_SRC_BEGIN = '[OUTPUTS:BEGIN]'
OUTPUTS_SRC_END = '[OUTPUTS:END]'
OUTPUTS_CRYPTED_BEGIN = '[OUTPUTS:C:BEGIN]'
OUTPUTS_CRYPTED_END = '[OUTPUTS:C:END]'



class Dummy:pass
def getInstallDir():
    """
    Retreives the kwad installation directory.
    """
    global INSTALL_DIR
    if INSTALL_DIR!=None:return INSTALL_DIR

    from os import path

    import inspect
    c=Dummy()
    p=inspect.getabsfile(c.__class__)
    for i in range(0, 3):p=path.split(p)[0]
    INSTALL_DIR=p

    return INSTALL_DIR


def setInstallDir(value):
    """
    Internal use only
    """
    from os import path
    global INSTALL_DIR

    INSTALL_DIR=path.normpath(value)


# -----------------#
# Init/Kwad.conf #
# -----------------#
def getKastConfs():
    selfMethod='getKastConfs'
    global KAST_CONFS
    if KAST_CONFS!=None:return dict(KAST_CONFS)
    from kwadlib.attrmaker import AttrMaker
    from os import path

    file_desc = KAST_DESC_CONF
    file_source = KAST_CONF

    ar=AttrMaker()
    desc_alias=ar.addAttrDesc(file_desc, alias=None)

    alias=ar.addFile(file_source, alias=None, attrDesc=desc_alias)
    KAST_CONFS=ar.getAttrs(alias)

    # Aliases:
    todels = []
    toadds = {}
    for entry in KAST_CONFS:
        if not entry.startswith('alias_'):continue
        toadds[entry[6:]] = KAST_CONFS[entry]
        todels.append(entry)
    for entry in todels:del KAST_CONFS[entry]
    KAST_CONFS.update(toadds)

    # kwad_home
    KAST_CONFS['kwad_home'] = getInstallDir()

    return dict(KAST_CONFS)

def getProcessTimeOut():
    global PROCESS_TIMEOUT
    if PROCESS_TIMEOUT!=None:return PROCESS_TIMEOUT

    PROCESS_TIMEOUT = getKastConfs()['process_timeout']
    return PROCESS_TIMEOUT

def getLangsDir():
    global KAST_LANGS_DIR
    from os import path, mkdir, listdir
    import shutil
    if KAST_LANGS_DIR!=None:return KAST_LANGS_DIR

    KAST_LANGS_DIR = getUserKastDir() + '/langs'
    if not path.isdir(KAST_LANGS_DIR):
        mkdir(KAST_LANGS_DIR)
        ld = listdir(getInstallDir() + '/langs')
        for file in ld:
            if file == 'macuuid.key':continue
            shutil.copy(getInstallDir() + '/langs/' + file, getUserKastDir() + '/langs')

    return KAST_LANGS_DIR

def getSamplesDir():
    global KAST_SAMPLES_DIR
    if KAST_SAMPLES_DIR!=None:return KAST_SAMPLES_DIR

    KAST_SAMPLES_DIR = getKastConfs()['samples_dir']

    return KAST_SAMPLES_DIR


def getTempDir():
    global TEMP_DIR
    if TEMP_DIR!=None:return TEMP_DIR
    from os import path, makedirs, chmod

    TEMP_DIR = getUserKastTempDir()

    if not path.isdir(TEMP_DIR):makedirs(TEMP_DIR)
    chmod(TEMP_DIR, 0o770)

    return TEMP_DIR

def getKastTempDir():
    global TEMP_DIR
    from os import path, makedirs, chmod
    tmp = getUserKastDir() + '/temp'

    if not path.isdir(tmp):
        makedirs(tmp)
        chmod(tmp, 0o770)

    return tmp

def getUserKastDir(user = None):
    return '{home_dir}/.kastmenu'.format(home_dir=getUserHomeDir(user=user))

def getUserKastTempDir(user = None):
    from os import path, makedirs, chmod
    thisuser = getUser()
    if user == None:user = thisuser
    temp_dir = getUserKastDir(user = user) + '/temp'
    if not path.isdir(temp_dir):
        makedirs(temp_dir)
        chmod(temp_dir, 0o770)
    return temp_dir

def getUserHomeDir(user = None):
    import pwd

    # Get Current User home dir:
    # os.path.expanduser('~kwad'
    # e.g.: /home/kwad'
    p = pwd.getpwuid(getUserId(user=user))
    return p.pw_dir


def getUser():
    import os, pwd
    p = pwd.getpwuid(os.getuid())
    return  p.pw_name

def getUserId(user = None):
    self_funct = 'getUserId'
    from kwadlib import xception
    import os, pwd

    if not user:
        p = pwd.getpwuid(os.getuid())
        user = p.pw_name

    try:
        uid = pwd.getpwnam(user).pw_uid
    except Exception as e:
        raise xception.kwadParameterException('Main', self_funct, 'User: %s do not Exist ! SubException is: %s.' % (user, str(e)))

    return uid

def getUserGid(user = None):
    self_funct = 'getUserGid'
    from kwadlib import xception
    import os, pwd

    if not user:
        p = pwd.getpwuid(os.getuid())
        user = p.pw_name

    try:
        gid = pwd.getpwnam(user).pw_gid
    except Exception as e:
        raise xception.kwadParameterException('Main', self_funct, 'User: %s do not Exist ! SubException is: %s.' % (user, str(e)))

    return gid


# See: https://en.wikipedia.org/wiki/File-system_permissions
# And https://docs.python.org/3/library/os.html#os.chmod
def fsRemoveAccessForOtherToFiles(dir):
    from os import lstat, walk, chmod, path
    import stat
    for dirpath, dirnames, filenames in walk(dir):
        for fname in filenames:
            file = path.join(dirpath, fname)
            # Preserv previous rigths:
            # See: https://stackoverflow.com/questions/25988471/remove-particular-permission-using-os-chmod
            # https://stackoverflow.com/questions/28492685/change-file-to-read-only-mode-in-python
            current = stat.S_IMODE(lstat(file).st_mode)
            current = current & ~stat.S_IROTH
            current = current & ~stat.S_IWOTH
            current = current & ~stat.S_IXOTH
            chmod(file, current)

def fsGuiveOtherExecToDir(dir):
    from os import chmod, path
    spl = dir.split(path.sep)

    while len(spl)!=0:
        if path.sep + path.join(*spl)=='/home':break

        chmod(path.sep + path.join(*spl), 0o751)
        spl.pop()

def fsChownToDir(dir, uid, gid):
    from kwadlib.security.crypting import sanitize_int
    from kwadlib.tools import check_output
    #1:
    check_output(('sudo', 'chown', '-R', str(sanitize_int(uid)) + ':' + str(sanitize_int(gid)), dir))


def getFreePortOnLocalHost():
    # Get kdealer_port_range:
    port_min, port_max = KAST_CONFS['kdealer_port_range']

    # Check free port:
    for port in (list(range(port_min, port_max))):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('localhost', port))
            s.close()
        except:
            return port

def getSSLPassword():
    pass



INSTALL_DIR = None
getInstallDir()
KAST_CONF_DIR='/etc/kastmenu'
KAST_CONF=KAST_CONF_DIR +  '/kast.conf'
KAST_DESC_CONF=KAST_CONF_DIR + '/descs/kast.desc.conf'
KAST_CONFS = None
getKastConfs()
PROCESS_TIMEOUT = None
getProcessTimeOut()

KASTWEB_PATH = getInstallDir() + '/bin/kastweb'
