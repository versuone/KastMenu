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

# 2023/06/01 | 001 | Implementation of cvdemo: allow no user/password connection on localhost default Menu when comming from an hidden url.
#                    The following resources are created on the flow:
#                    - new unix user
#                    - K8S specific NameSpace for this user
#                    - a dkwad user

DEBUG = True
VERBOSE = 0
CONNECTION_TIMEOUT = 7
CVDEMO = "63e8d05112b016e611c17b0eb40aa120bc8f8446268d235e71f2c93551537fe1"


from kwadlib.security.crypting import sanitize_kastmenu, sanitize_hostorip, sanitize_int, sanitize_mail, sanitize_path, sanitize
from kwadlib import kastmenuxception
# Patch for cookie samesite support:
from http.cookies import Morsel

Morsel._reserved["samesite"] = "SameSite"
from tornado.httpclient import HTTPRequest
import tornado.websocket
from kwadlib import db
import tornado.gen
import tornado.web
import json
import time
db.initwebdb()
db.initdb()
""" Note about random:
It is deterministic, and the sequence it generates is dictated by the seed value you pass 
into random.seed. 
Typically you just invoke random.seed(), and it uses the current time as the seed value
"""
import random
random.seed()

""" Dynamic AES KEY:
Works but would force reject the browser's already opened tab 
when restarting the kastserver.
from os import urandom
AES256_KEY = urandom(32)
AES256_IV = urandom(16)
"""

from kwadlib import default
GUEST_USER = default.getKastConfs()['guestuser']
GENERATED_USER_LINUX_PREFIX = default.getKastConfs()['generated_user_linux_prefix']
from kwadlib.tools import getInstallDir
KAST_HOME = getInstallDir()
KAST_CONFS = default.getKastConfs()
KAST_HOST=KAST_CONFS['kast_host']
KAST_PORT=KAST_CONFS['kast_port']
SERVER_CRT = KAST_CONFS['server_crt']
SERVER_KEY = KAST_CONFS['server_key']
SESSION_TIMEOUT = 1800
SESSION_PART_PREFIX='session-part-'

DEFAULT_PAGE='/kastmenu/machine/'
INDEX_PAGE_ABS_PATH = KAST_HOME + "/core/kwadlib/web/kastmenu/index.html"

MENU_WEB_FACADE = None
WEB_FACADE_KWS = None
IO_LOOP = None
POLICY_CONSTRAINTS = None

def setVerbose(verbose):
    global VERBOSE
    VERBOSE = verbose
    db.VERBOSE = VERBOSE

def printlog(fromf, message, request=None, level=0):
    from kwadlib.tools import printlog as plog
    plog(fromf, message, request=request, level=level, verbose=VERBOSE)

def genKeys(fqdn=None, force=False):
    """
    This will generate kastserver ssl keys:
    ---------------------------------------
    """
    self_funct='genKeys'
    from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
    from kwadlib.security.crypting import sanitize_hostorip
    from kwadlib import default
    from os import path, remove
    import re

    etc_keys = '/etc/kastmenu/keys'

    temp_dir = default.getUserKastTempDir()
    passfile = temp_dir + '/fpass.txt'

    envs = {
        'TEMP_DIR': temp_dir
    }

    kast_host = default.getKastConfs()['kast_host']
    if fqdn!=None:
        if not force and kast_host==fqdn:
            print (self_funct + ' New fqdn == previous kast_host: %s into %s, nothing to do ! Use force to overpass.' % (kast_host, default.KAST_CONF_DIR))
            return
        sanitize_hostorip(do_hide=False, class_exit='Main', method_exit=self_funct, **{'fqdn': fqdn})
        kast_host_new = fqdn
        envs['FULL_FRONT_HOSTNAME'] = fqdn
    else:
        import socket
        kast_host_new = socket.gethostname()

    cmd = default.getInstallDir() + '/core/kwadlib/security/sslkeygen/sslkeygen_kastserver.sh'
    try:
        p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
        output, errmsg = p.communicate()
        ret = p.wait()
    except:
        raise
    finally:
        if path.isfile(passfile): remove(passfile)

    print (output)

    if p.returncode != 0:
        more=''
        if len(output)!=0: more = ' SubException is: %s' % output
        raise Exception ('Unable to run command: %s !%s' % (cmd, more))

    # Rename:  kastweb.kastmenu.myhostname.key, kastweb.kastmenu.myhostname.crt to real name:
    with open(default.KAST_CONF) as fread:
        src = fread.read()
        # kast_host:
        src = re.sub(r"kast_host\s*=\s*.*", 'kast_host = ' + kast_host_new, src)
        # server_key:
        src = re.sub(r"\nserver_key\s*=\s*.*", '\nserver_key = ' + etc_keys + '/' + kast_host_new + '.key', src)
        # server_crt:
        src = re.sub(r"\nserver_crt\s*=\s*.*", '\nserver_crt = ' + etc_keys + '/' + kast_host_new + '.crt', src)

        with open(default.KAST_CONF, 'w') as fwrite:
            fwrite.write(src)


# Encrypting password into /etc/kastmenu/kast.conf:
# - kastserverp has the responsability to encrypt ciritcal value into /etc/kastmenu/kast.conf:
def encryptKastConf():
    from kwadlib.security.crypting import CRYPT_PREFIX
    mail_password = default.getKastConfs()['mail_password']
    if mail_password in ('', None) or mail_password.startswith(CRYPT_PREFIX):return

    import re
    from kwadlib.security.crypting import encryptLocal
    mail_password = CRYPT_PREFIX + encryptLocal(mail_password + CRYPT_PREFIX)
    with open(default.KAST_CONF) as fr:
        s = fr.read()
        s = re.sub(r'mail_password=.+', 'mail_password=%s' % mail_password, s)
        with open(default.KAST_CONF, 'w') as fw:fw.write(s)


# Encrypting password into /etc/kastmenu/kast.conf:
# - kastserverp has the responsability to encrypt ciritcal value into /etc/kastmenu/kast.conf:
def encryptKastServerSSLKeyPassword():
    from kwadlib.security.crypting import encryptLocal
    from os import remove
    from os import path
    file_from = '/etc/kastmenu/keys/fpass.txt'
    if not path.isfile(file_from):return

    file_to = '/etc/kastmenu/keys/fpass.dat'
    if not path.isfile(file_from):return

    file = '/etc/kastmenu/keys/fpass.txt'
    with open(file_from) as fr:
        v=fr.read()
        with open(file_to, 'w') as fw:
            fw.write(encryptLocal(v))
    remove(file_from)

# ======================
# Init: Integrity Check:
# ======================


class ACTIVATION:
    DATE_EXPIRATION_PERIOD_1MONTH_ALERT = 2629800
    DATE_EXPIRATION_PERIOD_2MONTH_ALERT = 5259600
    ALERT_EXPIRATION_IN_1MONTH = False
    ALERT_EXPIRATION_IN_2MONTH = False
    DATE_EXPIRATION = None
    NB_MACHINES = None
    NB_USERS = None
    NB_BROWSERS = None
    NB_TAB_PER_BROWSERS = None
    ERROR_SUFFIX='\nAdvise the KastMenu Administrator !'

    @staticmethod
    def checkMaxMachine():
        sql = 'select count(*) from machine;'
        nb_hosts = db.DATABASE_CURSOR.execute(sql).fetchall()
        if nb_hosts == None or len(nb_hosts) == 0: nb_hosts = 0
        nb_hosts = nb_hosts[0][0]

        ACTIVATION.NB_MACHINES = 5
        if nb_hosts >= ACTIVATION.NB_MACHINES:
            error = "Maximum Number: %d of Machines allowed by License reached: %d." % (ACTIVATION.NB_MACHINES, nb_hosts)
            raise LicenceKastException(450, reason=error, log_message=error)

    @staticmethod
    def checkMaxUser():
        sql = 'select count(*) from user;'
        nb_users = db.DATABASE_CURSOR.execute(sql).fetchall()
        if nb_users == None or len(nb_users) == 0: nb_users = 0
        nb_users = nb_users[0][0]

        sql = 'select count(*) from ses_user;'
        nb_ses_users = db.WEB_DATABASE_CURSOR.execute(sql).fetchall()
        if nb_ses_users == None or len(nb_ses_users) == 0: nb_ses_users = 0
        nb_ses_users = nb_ses_users[0][0]

        ACTIVATION.NB_USERS = 500
        if nb_users >= ACTIVATION.NB_USERS or nb_ses_users >= ACTIVATION.NB_USERS:
            error = "Maximum Number: %d of Users allowed by License reached: %s." % (ACTIVATION.NB_USERS, str(nb_users) + '/' + str(nb_ses_users))
            raise LicenceKastException(450, reason=error, log_message=error)

    @staticmethod
    def checkMaxSession(): # Nb Browser
        sql = 'select sessionid from ses_session;'
        all_sessions = db.WEB_DATABASE_CURSOR.execute(sql).fetchall()
        if all_sessions == None or len(all_sessions) == 0: return
        all_sessions = set([s[0].split('-session-part-')[0] for s in all_sessions[0]])

        if len(all_sessions) >= ACTIVATION.NB_BROWSERS:
            error = "Maximum Number: %d of Browsers allowed by License reached: %d." % (ACTIVATION.NB_BROWSERS, len(all_sessions))
            raise LicenceKastException(450, reason=error, log_message=error)

    @staticmethod
    def checkMaxSessionPart(sessionid): # Nb Browser Tab
        new_session = sessionid.split('-session-part-')[0]

        sql = 'select sessionid from ses_session;'
        all_sessions = db.WEB_DATABASE_CURSOR.execute(sql).fetchall()
        if all_sessions == None or len(all_sessions) == 0: return

        all_sessions_dict = {}
        for s in all_sessions:
            ses, part = s[0].split('-session-part-')
            part = 'session-part-' + part
            if ses not in all_sessions_dict:all_sessions_dict[ses] = []
            all_sessions_dict[ses].append(part)

        if new_session not in all_sessions_dict:return
        if len(all_sessions_dict[new_session]) >= ACTIVATION.NB_TAB_PER_BROWSERS + 1:
            cleanThisSession(sessionid)
            error = "Maximum Number: %d of Browser Tabs allowed by Restriction rule reached: %d.\nThe full session has been destroyed ! So you will have to refresh your tabs, by Clearing your Browser History and eventually restarting it.\nNext time try not to overpass the maximum allowed." % (ACTIVATION.NB_TAB_PER_BROWSERS, len(all_sessions_dict[new_session]))

            raise LicenceKastException(450, reason=error, log_message=error)

def integrityCheck():
    global POLICY_CONSTRAINTS

    ACTIVATION.NB_MACHINES = default.getKastConfs()['nb_machines'] # 4
    ACTIVATION.NB_USERS = default.getKastConfs()['nb_users'] # 500
    ACTIVATION.NB_BROWSERS = default.getKastConfs()['nb_browsers'] # 4
    ACTIVATION.NB_TAB_PER_BROWSERS = default.getKastConfs()['nb_tab_per_browsers'] # 4

    encryptKastConf()
    encryptKastServerSSLKeyPassword()
integrityCheck()

def genUid():
    rand=random.randint(1, 10000000)
    return "%07i" % rand

def genSessionId():
    from kwadlib.security.crypting import sha256
    return 'session-' + sha256("%s-%s" % (str(time.time() * 1000), genUid()))

def genSessionPart():
    from kwadlib.security.crypting import padTo16
    v = padTo16(SESSION_PART_PREFIX + "%s-%s" % (str(int(time.time() * 1000)), genUid()))
    from kwadlib.security.crypting import encryptLocal
    return  encryptLocal(v)

def exitAll():
    # process:Terminate SSH Sessions:
    sql = 'select host, kastagent_ssh_pid from ses_menufile;'
    host_pids = db.WEB_DATABASE_CURSOR.execute(sql).fetchall()

    for host, pid in host_pids:
        killHost(host, pid)

def killHost(host, pid):
    import os, signal
    printlog('killHost', 'Kill host: %s with pid: %s.' % (host, pid), level=50)

    if host == 'localhost':
        # This will kill local bash and childs:
        import psutil

        parent_pid = pid
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):  # or parent.children() for recursive=False
            child.kill()
        parent.kill()
        parent.wait()

    else:
        # This will kill ssh session (and ssh manages well to propagate the signal to childs)
        os.kill(pid, signal.SIGTERM)  # or signal.SIGKILL

def cleanSession():
    from time import time
    ts = time()

    # process:Terminate SSH Sessions:
    sql = 'select host, kastagent_ssh_pid from ses_menufile where (%d - lastused) > %d;' % (ts, SESSION_TIMEOUT)
    host_pids = db.WEB_DATABASE_CURSOR.execute(sql).fetchall()
    if len(host_pids)>0:printlog('cleanSession', 'Found the following pid: %s to kill !' % ', '.join([p[0] for p in host_pids]), level=50)
    for host, pid in host_pids:
        killHost(host, pid)

    # db:Specific Remove:
    sql = 'delete from ses_menufile where (%d - lastused) > %d;' % (ts, SESSION_TIMEOUT)
    db.WEB_DATABASE_CURSOR.execute(sql)
    # db:All cascade chain Remove:
    sql = 'delete from ses_session where (%d - lastused) > %d;' % (ts, SESSION_TIMEOUT)
    db.WEB_DATABASE_CURSOR.execute(sql)


def cleanThisSessionPart(session):
    if session == None:return False
    from time import time
    ts = time()

    # process:Terminate SSH Sessions:
    sql = 'select host, kastagent_ssh_pid from ses_menufile where sessionid = "%s";' % session
    host_pids = db.WEB_DATABASE_CURSOR.execute(sql).fetchall()
    if len(host_pids)>0:printlog('cleanSession', 'Found the following pid: %s to kill !' % ', '.join([p[0] for p in host_pids]), level=50)
    for host, pid in host_pids:
        killHost(host, pid)

    # db:Specific Remove:
    sql = 'delete from ses_menufile where sessionid = "%s";' % session
    db.WEB_DATABASE_CURSOR.execute(sql)

    # db:All cascade chain Remove:
    sql = 'delete from ses_session where sessionid = "%s";' % session
    db.WEB_DATABASE_CURSOR.execute(sql)

def cleanThisSession(short_session):
    if short_session == None:return False
    from time import time
    ts = time()

    # process:Terminate SSH Sessions:
    sql = 'select host, kastagent_ssh_pid from ses_menufile where sessionid like "{session}%";'.format(session=short_session)
    host_pids = db.WEB_DATABASE_CURSOR.execute(sql).fetchall()
    if len(host_pids)>0:printlog('cleanSession', 'Found the following pid: %s to kill !' % ', '.join([p[0] for p in host_pids]), level=50)
    for host, pid in host_pids:
        killHost(host, pid)

    # db:Specific Remove:
    sql = 'delete from ses_menufile where sessionid like "{session}%";'.format(session=short_session)
    db.WEB_DATABASE_CURSOR.execute(sql)

    # db:All cascade chain Remove:
    sql = 'delete from ses_session where sessionid like "{session}%";'.format(session=short_session)
    db.WEB_DATABASE_CURSOR.execute(sql)

def getBlankMachineDefaultUserMenu(go_pages, validations, request=None):
    go_pages, validations = dict(go_pages), dict(validations)
    done = False
    # has machine:
    if go_pages['parms'] == None or not 'machine' in go_pages['parms'] or go_pages['parms']['machine'] == None:pass
    else: return done, go_pages, validations
    if go_pages['parms']==None:go_pages['parms']={}

    printlog('WebMenuDispatchHandler:post', '/Machine: Machine was blank looking for default machine (with flag isdefault=True)...', request=request)

    positive_message = None
    dfthost = None
    dftuser = None
    dftmenu = None
    # Chek KastMenu has Machine has default:
    sql = 'select host from machine where isdefault=1;'
    hosts = db.DATABASE_CURSOR.execute(sql).fetchall()
    if hosts != None and len(hosts) > 0:
        dfthost = hosts[0][0]
        tb_machine = db.Machine(host=dfthost)
        tb_machine.load()

    # Chek Machine has guest user:
    if dfthost != None:
        printlog('WebMenuDispatchHandler:post', '/Machine: Found default machine: %s.' % dfthost, request=request)
        printlog('WebMenuDispatchHandler:post', '/Machine: Looking for default user...', request=request)

        sql = 'select user from user where host="%s" and user="%s" and xnopassword = 1;' % (dfthost, GUEST_USER)
        users = db.DATABASE_CURSOR.execute(sql).fetchall()
        # Chek guest user has menu:
        if users != None and len(users) > 0:
            printlog('WebMenuDispatchHandler:post', '/Machine: %s: Found default user: %s.' % (dfthost, dftuser), request=request)
            printlog('WebMenuDispatchHandler:post', '/Machine: %s/User: %s: Looking for default menu...', request=request)

            dftuser = GUEST_USER
            validations['authenticated'] = True
            dftuser = GUEST_USER
            sql = 'select name from menufile where host="{host}" and user="{user}" and name="{name}";'.format(host=dfthost, user=GUEST_USER, name=tb_machine.default_menu)
            menus = db.DATABASE_CURSOR.execute(sql).fetchall()
            dftmenu = None
            if menus != None and len(menus) > 0:
                dftmenu = tb_machine.default_menu
                positive_message = 'Validate again to access to menu !'
                printlog('WebMenuDispatchHandler:post', '/Machine: %s/User: %s: Found default menu: %s.' % (dfthost, dftuser, dftmenu), request=request)

    done = True
    # validations:
    validations['field'] = 'machine'
    if positive_message == None:
        validations['message'] = 'Machine is required !'
    else:
        validations['+message'] = positive_message
    validations['succeed'] = False
    go_pages['parms']['machine'] = dfthost  # If KastMenu has default machine.
    go_pages['parms']['user'] = dftuser  # If Machine has guest user.
    go_pages['parms']['menu'] = dftmenu  # If Machine/guest user has default menu.

    return done, go_pages, validations

def getMachineDefaultUserMenu(machine, request=None):
    self_funct='getMachineDefaultUserMenu'
    if machine==None:raise Exception('Parameter machine cannot be None !')
    sanitize_hostorip(do_hide=False, class_exit='Main', method_exit=self_funct, **{'machine': machine})
    printlog ('getMachineDefaultUserMenu', 'getMachineDefaultUserMenu/Machine: %s: Searching for default User with associated menus...' % machine, level=60)

    # Chek Machine has guest user:
    sql = 'select user from user where host="%s" and user="%s" and xnopassword = 1;' % (machine, GUEST_USER)
    users = db.DATABASE_CURSOR.execute(sql).fetchall()
    # Chek guest user has menu:
    if users == None or len(users) == 0:return False, None, None
    printlog('getMachineDefaultUserMenu', '/Machine: %s: Found default User: %s (named: %s and with xnopassword=True).' % (machine, ', '.join([e[0] for e in users]), GUEST_USER), request=request, level=60)
    printlog('getMachineDefaultUserMenu', '/Machine: %s/User: %s: Searching for default User associated menus (will only pick the first one)...' % (machine, GUEST_USER), request=request, level=60)
    tb_machine = db.Machine(host=machine)
    tb_machine.load()

    dftuser = GUEST_USER
    sql = 'select name from menufile where host="{host}" and user="{user}" and name="{name}";'.format(host=machine, user=GUEST_USER, name=tb_machine.default_menu)
    menus = db.DATABASE_CURSOR.execute(sql).fetchall()
    dftmenu=None
    if menus != None and len(menus) > 0:
        dftmenu = tb_machine.default_menu
        printlog('getMachineDefaultUserMenu', '/Machine: %s/User: %s: Found default menu: %s.' % (machine, GUEST_USER, dftmenu), request=request, level=60)

    # dftuser:If Machine has guest user.
    # dfmenu: If Machine/guest user has default menu.
    return True, dftuser, dftmenu

def getMachineDefaultUser(machine, request=None):
    self_funct='getMachineDefaultUser'
    if machine==None:raise Exception('Parameter machine cannot be None !')
    sanitize_hostorip(do_hide=False, class_exit='Main', method_exit=self_funct, **{'machine': machine})
    printlog('getMachineDefaultUser', '/Machine: %s: Searching for default User.' % machine, request=request, level=60)
    # Chek Machine has guest user:
    sql = 'select user from user where host="%s" and user="%s" and xnopassword = 1;' % (machine, GUEST_USER)
    users = db.DATABASE_CURSOR.execute(sql).fetchall()
    # Chek guest user has menu:
    if users == None or len(users) < 0:return False, None
    dftuser = GUEST_USER
    printlog('getMachineDefaultUser', '/Machine: %s: Found default User: %s (named: %s and with xnopassword=True).' % (machine, ', '.join(users), GUEST_USER), request=request, level=60)

    # dftuser:If Machine has guest user.
    return True, dftuser

def getPublicMachines(request=None):
    self_funct='getPublicMachines'

    printlog('getPublicMachines', 'Searching for public Machines (with flag ispublic=True)...', request=request, level=60)
    sql = 'select host from machine where ispublic = 1;'
    result = db.DATABASE_CURSOR.execute(sql)
    if result == None:return None
    printlog('getPublicMachines', 'Searching for public Machines (with flag ispublic=True)...', request=request, level=60)
    results = result.fetchall()
    printlog('getPublicMachines', 'Found the following Public machine: %s.' % str(results), request=request, level=60)

    return results

def getPublicUsers(machine, request=None):
    self_funct='getPublicUsers'
    sanitize(do_hide=False, class_exit='Main', method_exit=self_funct, **{'user': machine})

    printlog('getPublicUsers', 'Searching for public Users (with flag ispublic=True)...', request=request, level=60)
    sql = 'select user, host from user where host ="{host}" and ispublic = 1;'.format(host=machine)
    result = db.DATABASE_CURSOR.execute(sql)
    if result == None:return None
    rs = result.fetchall()

    return rs

def getUserMenus(machine, user):
    self_funct='getUserMenus'
    sanitize_hostorip(do_hide=False, class_exit='Main', method_exit=self_funct, **{'machine': machine})
    sanitize(do_hide=False, class_exit='Main', method_exit=self_funct, **{'user': user})

    sql = 'select name, path from menufile where host ="{machine}" and user ="{user}";'.format(machine=machine, user=user)
    results = db.DATABASE_CURSOR.execute(sql)
    if results != None: results = results.fetchall()
    if results == None or len(results)==0:return None

    return results

def shortException(e):
    if e==None:return None

    # if not hasattr(e, 'short1') or not hasattr(e, 'short2'):
    if not hasattr(e, 'short1'):return e.__class__.__name__ + ': ' + str(e)
    else:return e.short1()


async def sshcall(host, cmd, user=None, sudo_user=None, port=22, isLocal=False, isMenu=False, doTTY=False, request=None, verbose=0):
    self_funct='sshcall'
    from subprocess import CalledProcessError
    from tornado.process import Subprocess
    # Dont go outside if host is this host:
    if host == KAST_HOST:host='localhost'

    SSH_PORT = ''
    if not isLocal:
        sanitize_hostorip(host)
        sanitize_int(port)
        if port != 22:SSH_PORT = ' -p %s' % str(port)
    ret=0

    if isLocal:
        printlog('sshcall', 'is Locally calling the following command: %s.' % cmd, request=request, level=80)

    else:
        # INFO: Prefer bash -E (instead of bash -c): propagate error outside bash
        #  + eventually "set -o pipefail && <cmd>" propagate error through pipe: |
        # when using pipe into command.

        sanitize(user)
        connection_user = user if sudo_user == None else sudo_user
        more='' if sudo_user == None else ' sudo -u %s ' % user

        if doTTY:
            # See: https://www.man7.org/linux/man-pages/man1/ssh.1.html
            # Multiple -t options force tty allocation, even if has no local tty. => Works with nohup !!
            cmd = 'ssh -tttt -o ConnectTimeout=%d %s %s@%s ' % (CONNECTION_TIMEOUT, SSH_PORT, connection_user, host) + more + cmd
        else:
            cmd = 'ssh -o ConnectTimeout=%d %s %s@%s ' % (CONNECTION_TIMEOUT, SSH_PORT, connection_user, host) + more + cmd

        printlog('sshcall', 'is Remotly calling the following command: %s.' % cmd, request=request, level=80)

    p = Subprocess(cmd, stdout=Subprocess.STREAM, stderr=Subprocess.STREAM, universal_newlines=True, shell=True, executable='/bin/bash')
    if not p.stdout.closed():
        try:
            ## isMenu = False
            if not isMenu:
                content = await p.stdout.read_until_close()
            else:
                reg = 'Launched finished.'
                # content = await p.stdout.read_until_regex(bytes(reg, 'utf-8'))
                content = await p.stdout.read_until(bytes(reg, 'utf-8'))

            stdout = content.decode('utf-8')

        except tornado.iostream.StreamClosedError as e:
            if isMenu: # Now try without regex:
                isMenu = False
                content = await p.stdout.read_until_close()
                stdout = content.decode('utf-8')
        except:
            ret=1

    if not isMenu and not p.stderr.closed():
        try:
            content = await p.stderr.read_until_close()
            stderr = content.decode('utf-8')
        except tornado.iostream.StreamClosedError as e:
            pass
    else:stderr=''

    if stdout==None:stdout=''
    if stderr==None:stderr=''
    content = stdout + stderr

    if not isMenu:
        try:
            await p.wait_for_exit()
            ret = p.returncode
        except CalledProcessError as e:
            ret = p.returncode
            if ret != 0:
                printlog('sshcall', 'Error Running Command: \n%s\n   Process Failed with this Return Code: %s' % (cmd, p.returncode), request=request)

    """
    if doTTY:
        from subprocess import check_output
        # Switch Terminal back to stty echo:
        check_output(('stty', 'echo'))
    """
    return ret, content, p.pid


class AcceptMail:

    @staticmethod
    def checkIsMail(name, mail):
        self_funct = 'checkIsMail'
        sanitize_mail(class_exit='AcceptMail', method_exit=self_funct, **{'name': mail})

    @staticmethod
    async def mailValidationCodeToUser(mail=None, validation_code=None, machine=None, request=None):
        sanitize_mail(mail)
        sanitize_int(validation_code)
        sanitize_hostorip(machine)
        HTML = """<html>
<body style='margin:0;padding:0;'>
<div style='background-color:blue;height:7vmin;margin:0;padding:0;'>
<img id="settings-running_img" border=0 src="https:[kast_host]:[kast_port]/kastmenu/images/list-ol-white.png"  
            style="margin-top:0.3vmin;width:7vmin;height:7vmin;float:left;"/>

<span style="font-size:5vmin;">&nbsp;&nbsp;&nbsp;KastMenu User Registration Validation</span>
</div>
<br>
<span style="font-size:3vmin;">
[bcc]Your new user needs the following validation code: [code] to be registred into KastMenu and on machine: [machine].
<br><br>
Please go back to your KastMenu session and enter the validation code.
<br>
Dont forget to save your new user and password for further use.
</span>

</body>
</html>
        """
        TEXT = """[bcc]Your new user needs the following validation code: [code] to be registred into KastMenu and on machine: [machine].

Please go back to your KastMenu session and enter the validation code.
Dont forget to save your new user and password for further use.
        """
        kast_host = default.getKastConfs()['kast_host']
        kast_port = default.getKastConfs()['kast_port']

        mail_username, mail_password, mail_smtp_host, mail_smtp_port, mail_bcc = AcceptMail.getMailCredential()
        print ('mailValidationCodeToUser/Mail: {mail}/Machine: {machine}/ValidationCode: {vcode}: Sending Validation code mail...'.format(mail=mail, machine=machine, vcode=validation_code))

        from email.message import EmailMessage
        msg = EmailMessage()
        msg_bcc = EmailMessage()
        msg['Subject'] = msg_bcc['Subject'] = 'KastMenu Account Registration Confirmation'
        msg['From'] = msg_bcc['From'] = 'noreply@kastmenu.org'
        msg['To'] = msg_bcc['To'] = ','.join([mail])

        text = TEXT.replace('[bcc]', '').replace('[code]', validation_code).replace('[machine]', machine).replace('[kast_host]', kast_host).replace('[kast_port]', str(kast_port))
        html = HTML.replace('[bcc]', '').replace('[code]', validation_code).replace('[machine]', machine).replace('[kast_host]', kast_host).replace('[kast_port]', str(kast_port))
        msg.set_content(text)
        msg.add_alternative(html, subtype='html')

        if mail_bcc != None:
            text = TEXT.replace('[bcc]', 'The following mail was sent to: %s.\n' % mail).replace('[code]', validation_code).replace('[machine]', machine).replace('[kast_host]', kast_host).replace('[kast_port]', str(kast_port))
            html = HTML.replace('[bcc]', 'The following mail was sent to: %s.<br>' % mail).replace('[code]', validation_code).replace('[machine]', machine).replace('[kast_host]', kast_host).replace('[kast_port]', str(kast_port))
            msg_bcc.set_content(text)
            msg_bcc.add_alternative(html, subtype='html')
        else:msg_bcc=None

        # AcceptMail.__do_send_mail(mail=mail, mail_username=mail_username, mail_password=mail_password, mail_bcc=mail_bcc, msg=msg, mail_smtp_host=mail_smtp_host, mail_smtp_port=mail_smtp_port)
        import functools
        await IO_LOOP.run_in_executor(None, functools.partial(AcceptMail.__do_send_mail, **{'mail': mail, 'mail_bcc': mail_bcc, 'mail_username': mail_username, 'mail_password': mail_password, 'msg': msg, 'msg_bcc': msg_bcc, 'mail_smtp_host': mail_smtp_host, 'mail_smtp_port': mail_smtp_port}))
        # yield IO_LOOP.run_in_executor(None, MENU_WEB_FACADE.getCommandOutput)

        print('mailValidationCodeToUser/Mail: Mail sent.'.format(mail=mail, machine=machine, vcode=validation_code))

    @staticmethod
    def __do_send_mail(mail=None, mail_bcc=None, mail_username=None, mail_password=None, msg=None, msg_bcc=None, mail_smtp_host=None, mail_smtp_port=None):
        import smtplib
        """
Note about: Mettre lecture de la python Q ds un threadExecutor qui se libere a get:
See:multithreading - Python queue linking object running asyncio coroutines with main thread input - Stack Overflow.html

This isn't going to work quite right, because the call to stdin_q.get()
is going to block your event loop. This means that if your server has multiple clients,
all of them will be completely blocked by whichever one happens to get to stdin_q.get() first,
until you send data into the queue.
The simplest way to get around this is use BaseEvent.loop.run_in_executor to run the stdin_q.get
in a background ThreadPoolExecutor, which allows you to wait for it without blocking the event loop:

@asyncio.coroutine
def get_input():
    loop = asyncio.get_event_loop()
    return (yield from loop.run_in_executor(None, stdin_q.get))  # None == use default executor.

Si besoins d'arguments:
    Voir tornado.pdf

    IOLoop.run_in_executor(executor, func, *args)
    Use functools.partial to pass keyword arguments to func.
    New in version 5.0.
"""
        server = smtplib.SMTP_SSL(mail_smtp_host, mail_smtp_port)
        if VERBOSE>80:server.set_debuglevel(1)
        server.login(mail_username, mail_password)
        ## server.sendmail(touser,  (ccuser1, ccuser2), msg)
        server.send_message(msg, to_addrs=[mail])
        if msg_bcc != None:
            server.send_message(msg_bcc, to_addrs=[mail_bcc])
        server.quit()


    @staticmethod
    async def generateUniqueUserFromMail(machine=None, mail=None, ssh_user=None, ssh_port=None, request=None, verbose=0):
        try:
            name = await AcceptMail.os_generateUniqueUserFromMail(machine=machine, mail=mail, ssh_user=ssh_user, ssh_port=ssh_port, request=request, verbose=verbose)
        except:
            raise

        return name

    @staticmethod
    def checkPasswordValidity(password):
        from kwadlib.security.crypting import checkPasswordValidity
        return checkPasswordValidity(password)

    @staticmethod
    async def os_generateUniqueUserFromMail(machine=None, mail=None, ssh_user=None, ssh_port=22, request=None, verbose=0):
        selfMethod = 'os_generateUniqueUserFromMail'
        sanitize_hostorip(machine)
        sanitize_mail(mail)
        if machine == 'localhost':
            localhost = ' -H localhost '
        else:
            localhost = ''
        found = False

        # Get All users on this machine:
        # ------------------------------
        # bash -E: propagate error outside bash, set -o pipefail &&  propagate error through pipe: |
        printlog('os_generateUniqueUserFromMail', '/Machine: {machine}/Mail: {mail}: Generating unique user for mail: {mail} on machine: {machine}...'.format(mail=mail, machine=machine), request=request)
        cmd = """ "getent passwd | awk -F: '{ print $1}'" """
        ret, output, ssh_pid = await sshcall(machine, cmd, user=ssh_user, port=ssh_port, isLocal=False, isMenu=True, doTTY=True, request=request, verbose=verbose)
        if ret!=0:raise Exception('Unable to get list of users of machine: %s !' % machine)
        users = output.split('\n')
        users = [user.split(':')[0] for user in users if user.startswith(GENERATED_USER_LINUX_PREFIX)]

        printlog('os_generateUniqueUserFromMail', '/Machine: {machine}/Mail: {mail}: Found this preexisting list of users: {users} on machine: {machine}.'.format(mail=mail, users=', '.join(users), machine=machine), request=request, level=80)

        # Guess a name from mail:
        # -----------------------
        left = mail.split('@')[0]
        spl = left.split('.')
        a=spl[0]
        if len(spl)>1:b=spl[1]
        else:b=None
        if b!=None:name = a[0] + b
        else:name=a

        if len(name)>5:name = name[0:5]
        pad = 5 - len(name)
        count = 0

        while count < 99:
            new_name = GENERATED_USER_LINUX_PREFIX + name + pad*'0' + (str(count) if count>9 else ('0' + str(count)))
            if new_name not in users:
                found = True
                break
            count+=1
            continue

        if not found:raise Exception('Unable to find a unique name for mail: %s on machine: %s !' % (mail, machine))

        printlog('os_generateUniqueUserFromMail', '/Machine: {machine}/Mail: {mail}: Generated user name is: {name}.'.format(mail=mail, machine=machine, name=new_name), request=request)

        return new_name

    # A001:
    @staticmethod
    async def os_generateUniqueUser(machine=None, ssh_user=None, ssh_port=22, request=None, verbose=0):
        selfMethod = 'os_generateUniqueUser'
        sanitize_hostorip(machine)
        if machine == 'localhost':
            localhost = ' -H localhost '
        else:
            localhost = ''
        found = False

        # Get All users on this machine:
        # ------------------------------
        # bash -E: propagate error outside bash, set -o pipefail &&  propagate error through pipe: |
        printlog('os_generateUniqueUser', '/Machine: {machine}: Generating unique user on machine: {machine}...'.format(machine=machine), request=request)
        cmd = """ "getent passwd | awk -F: '{ print $1}'" """
        ret, output, ssh_pid = await sshcall(machine, cmd, user=ssh_user, port=ssh_port, isLocal=False, isMenu=True, doTTY=True, request=request, verbose=verbose)
        if ret!=0:raise Exception('Unable to get list of users of machine: %s !' % machine)
        users = output.split('\n')
        users = [user.split(':')[0] for user in users if user.startswith(GENERATED_USER_LINUX_PREFIX)]

        printlog('os_generateUniqueUserFromMail', '/Machine: {machine}: Found this preexisting list of users: {users} on machine: {machine}.'.format(users=', '.join(users), machine=machine), request=request, level=80)

        # Guess a name from mail:
        # -----------------------
        rand = random.randint(1, 100000)
        name = "%05i" % rand
        count = 0

        while count < 99:
            # GENERATED_USER_LINUX_PREFIX
            new_name = 'x' + name + (str(count) if count>9 else ('0' + str(count)))
            if new_name not in users:
                found = True
                break
            count+=1
            continue

        if not found:raise Exception('Unable to find a unique name: %s on machine: %s !' % machine)

        printlog('os_generateUniqueUserFromMail', '/Machine: {machine}: Generated user name is: {name}.'.format(machine=machine, name=new_name), request=request)

        return new_name

    @staticmethod
    async def os_createUser(password=None, machine=None, user=None, ssh_user=None, ssh_port=22, nologin=False, request=None, verbose=0):
        from kwadlib.security.crypting import expect, NoneZeroRCException, TimeOutException
        sanitize_kastmenu(password)
        sanitize_hostorip(machine)
        sanitize(user)
        # Dont go outside if host is this host:
        if machine == KAST_HOST: host = 'localhost'
        else:host=machine
        if ssh_port == 22:SSH_PORT = ''
        else:SSH_PORT = ' -p %s' % str(ssh_port)

        printlog('os_createUser', '/Machine: {machine}/User: {user}: Creating user: {user} on Machine: {machine}...'.format(machine=machine, user=user), request=request)

        # first sudo chmod o+rwx /home/{user} is to be allowed to change .profile:
        if nologin:_nologin = ";sudo chmod o+rwx /home/{user};sudo echo 'exit 0' > /home/{user}/.profile;sudo chmod o-w /home/{user};sudo chmod ug+x /home/{user}/.bash_profile".format(user=user)
        else:_nologin = ""
        cmd = 'ssh -ttt  -o ConnectTimeout={ct} {ssh_port} {ssh_user}@{host} "sudo useradd --shell /bin/sh {user};sudo passwd {user} && sudo mkdir /home/{user}{nologin};sudo chown -R {user}:{user} /home/{user}"'.format(ct=str(CONNECTION_TIMEOUT), ssh_port=SSH_PORT, ssh_user=ssh_user, user=user, host=host, nologin=_nologin)

        ret=0
        error = None
        try:
            data = expect(cmd, password, message="assword:", twice=True, verbose=verbose)
        except NoneZeroRCException as e:
            ret = 1
            error = e.data
        except TimeOutException as e:
            ret = 1
            error=e
        except Exception as e:
            ret = 1
            error=e

        if error!=None:error = 'Error trying to create User: %s on Machine: %s ! SubException is: %s.' % (user, machine, str(error))
        if ret!=0:raise Exception(error)


        printlog('os_createUser', '/Machine: {machine}/User: {user}: Creating Kwad user: {user} on Machine: {machine}...'.format(machine=machine, user=user), request=request)
        cmd = """ "sudo -u kwad /opt/kwad-server/current/bin/knewuser %s -v 30 -F" """ % user
        ret, output, ssh_pid = await sshcall(machine, cmd, user=ssh_user, port=ssh_port, isLocal=False, isMenu=True, doTTY=True, request=request, verbose=verbose)
        if ret!=0:raise Exception('Unable to Create Kwad user: %s on Machine: %s !' % (user, machine))

        ## YUKA ONLY: ON CREE UN NAMESPACE POUR LE USER:
        # printlog('os_createUser', "/Machine: {machine}/User: {user}: Creating K8S user's NameSpace: ns-{user} on Machine: {machine}...".format(machine=machine, user=user), request=request)
        # cmd = """ sudo -u patrick kubectl create ns ns-%s """ % user
        # ret, output, ssh_pid = await sshcall(machine, cmd, user=ssh_user, port=ssh_port, isLocal=False, isMenu=True, doTTY=True, request=request, verbose=verbose)
        # if ret!=0:raise Exception("Unable to Create  K8S user's NameSpace: %s on Machine: %s !" % (user, machine))

        printlog('os_createUser', '/Machine: {machine}/User: {user}: User created.', request=request)

        return ret, error

    @staticmethod
    def createDbUser(sessionid=None, machine=None, user=None, mail=None, default_menu=None, default_menu_fpath=None, request=None, verbose=0):
        sanitize_hostorip(machine)
        sanitize(user)
        mail_store_sha = default.getKastConfs()['mail_store_sha']
        if mail!=None and mail_store_sha:
            from kwadlib.security.crypting import sha256
            mail = sha256(mail)

        printlog('createDbUser', '/Machine: {machine}/User: {user}/Mail :{mail}: Creating Tables for user: {user} on machine: {machine}.'.format(machine=machine, user=user, mail=mail), request=request )

        # tb_user:
        tb_user = db.User(host=machine, user=user, title=None, mail=mail)
        if tb_user.load():tb_user.delete()
        tb_user.lastused = time.time()
        tb_user.save()

        # tb_ses_user:
        tb_ses_user = db.ses_User(sessionid=sessionid, host=machine, user=user, authenticated=True)
        if tb_ses_user.load():tb_user.delete()
        tb_ses_user.authenticated = True
        tb_ses_user.lastused = time.time()
        tb_ses_user.save()

        # tb_menu:
        tb_menu = db.MenuFile(host=machine, user=user, name=default_menu, path=default_menu_fpath, tsupdated=time.time())
        if tb_menu.load():tb_menu.delete()
        tb_menu.save()

    @staticmethod
    def checkUserMailExists(machine=None, mail=None, request=None):
        sanitize_hostorip(machine)
        sanitize_mail(mail)

        mail_store_sha = default.getKastConfs()['mail_store_sha']
        if mail_store_sha:
            from kwadlib.security.crypting import sha256
            mail = sha256(mail)

        printlog('checkUserMailExists', '/Machine: {machine}/Mail: {mail}: Checking if this mail: {mail} is already registred in table: user ?'.format(machine=machine, mail=mail), request=request)
        sql = 'select mail from user where host="%s" and mail="%s";' % (machine, mail)
        mails = db.DATABASE_CURSOR.execute(sql).fetchall()

        sql = 'select * from user where host="%s";' % machine
        ALLS = db.DATABASE_CURSOR.execute(sql).fetchall()
        printlog('checkUserMailExists', 'FOUND: %s MAIL: %s' % (str(mails), mail), request=request)
        printlog('checkUserMailExists', 'ALL: %s' % str(ALLS), request=request)

        return mails!=None and len(mails)>0

    @staticmethod
    def getMailCredential():
        mail_username = default.getKastConfs()['mail_username']
        mail_password = default.getKastConfs()['mail_password']
        mail_smtp_host = default.getKastConfs()['mail_smtp_host']
        mail_smtp_port = default.getKastConfs()['mail_smtp_port']
        mail_bcc = default.getKastConfs()['mail_bcc']

        if mail_username == None:raise Exception('Entry: mail_username is required into the file: %s ! Advice the KastMenu administrator.' % default.KAST_CONF)
        if mail_password == None:raise Exception('Entry: mail_password is required into the file: %s ! Advice the KastMenu administrator.' % default.KAST_CONF)
        if mail_smtp_host == None:raise Exception('Entry: mail_smtp_host is required into the file: %s ! Advice the KastMenu administrator.' % default.KAST_CONF)
        if mail_smtp_port == None:raise Exception('Entry: mail_smtp_port is required into the file: %s ! Advice the KastMenu administrator.' % default.KAST_CONF)
        if mail_bcc!=None:
            try:
                AcceptMail.checkIsMail('mail_bcc', mail_bcc)
            except Exception as e:
                raise Exception('The field: "mail_bcc" of the config file: %s is not correct ! A mail address is expected. Advice the KastMenu administrator.' % default.KAST_CONF)
        try:
            from kwadlib.security.crypting import CRYPT_PREFIX
            from kwadlib.security.crypting import decryptLocal
            if mail_password.startswith(CRYPT_PREFIX):
                mail_password = decryptLocal(mail_password[len(CRYPT_PREFIX):])
                mail_password = mail_password.split(CRYPT_PREFIX)[0]
        except Exception as e:
            raise Exception('Value for entry: mail_password of %s is not correct ! Advice the KastMenu administrator.' % default.KAST_CONF)

        return mail_username, mail_password, mail_smtp_host, mail_smtp_port, mail_bcc


class KastException(tornado.web.HTTPError):

    def __init__(self, status_code=0, log_message=None, reason=None, do_page=False,
        *args,
        **kwargs
    ):
        self.og_reason = reason
        self.do_page = do_page

        # reason: do not support \n => would cause content-length error !
        if reason!=None:reason = reason.replace('\n', '<br>')
        tornado.web.HTTPError.__init__(self, *args, status_code=status_code, log_message=log_message, reason=reason, do_page=do_page, **kwargs)

class LicenceKastException(KastException):

    def __init__(self, *args, **kwargs):
        KastException.__init__(self, *args, ** kwargs)

# ------------------------------------------------------------------------------------------------------ #
# Static Handler:                                                                                        #
# ------------------------------------------------------------------------------------------------------ #
class KStaticFileHandler(tornado.web.StaticFileHandler):

    def sendError(self, error_code, error_message = None, log_message = None):
        # See: https://www.kite.com/python/docs/tornado.web.HTTPError
        raise KastException(error_code, reason=error_message, log_message=error_message)

    # @tornado.web.authenticated
    def prepare(self):
        if not self.get_secure_cookie("ident"):
            pass
            # if self.request.path.startswith('/kmanager'):self.redirect("/login")
            # else:self.sendError(470, error_message='Authenticaton Error !')

        tornado.web.StaticFileHandler.prepare(self)


# ------------------------------------------------------------------------------------------------------ #
# Bases Handlers:                                                                                        #
# ------------------------------------------------------------------------------------------------------ #
class PrepareHandler:
    __SSLClientCtx =None

    @staticmethod
    def getSSLClientCtx():
        if PrepareHandler.__SSLClientCtx!=None:return PrepareHandler.__SSLClientCtx
        # Ssl Management:
        # ---------------
        import ssl
        # See: https://www.tornadoweb.org/en/stable/httpserver.html
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        # Retreive SSL Pass:
        from kwadlib.security.crypting import decryptLocal
        file = '/etc/kastmenu/keys/fpass.dat'
        with open(file) as f:
            ssl_password = f.read()
            ssl_password = decryptLocal(ssl_password.strip())
        ssl_ctx.load_cert_chain(certfile=SERVER_CRT, keyfile=SERVER_KEY, password=ssl_password)
        ssl_ctx.check_hostname = False

        PrepareHandler.__SSLClientCtx = ssl_ctx

        return PrepareHandler.__SSLClientCtx

    @staticmethod
    async def do_prepare(self, session_part):
        # Check if session_part was generated by kastserver ?
        message = 'Invalid SessionPart ! Found: %s.' % session_part
        try:
            from kwadlib.security.crypting import decryptLocal
            session_part = decryptLocal(session_part)
        except Exception as e:
            raise KastException(500, reason=message, log_message=message + '\nSubException is: %s' % str(e))
        if not session_part.startswith(SESSION_PART_PREFIX):
            raise KastException(500, reason=message, log_message=message + '\nSubException is: SessionPart sould startwith expected prefix ! %s' + session_part)

        self.field_session_part = session_part
        # if self.__class__.__name__ == 'WebMenuProxyHandler':return
        cleanSession()

        if not self.get_secure_cookie("session"):
            ACTIVATION.checkMaxMachine()
            ACTIVATION.checkMaxUser()
            ACTIVATION.checkMaxSession()
            session_id = genSessionId()

            printlog('PrepareHandler/do_prepare', 'Creating New Browser Session: %s.' % session_id, request=self.request)

            self.flag_new_session = True
            self.set_secure_cookie("session", session_id, samesite='strict')
            self.field_ses_session = session_id + '-' + session_part
            tb_ses_session = db.ses_Session(sessionid=self.field_ses_session, lastused=time.time())
            tb_ses_session.save()
            printlog('PrepareHandler/do_prepare', 'Creating New Browser Tab Session: %s.' % self.field_ses_session, request=self.request)
        else:
            ACTIVATION.checkMaxMachine()
            ACTIVATION.checkMaxUser()
            self.field_ses_session = self.get_secure_cookie('session').decode("utf-8") + '-' + session_part
            ACTIVATION.checkMaxSessionPart(self.field_ses_session)

            # check Session Exist:
            tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
            if not tb_ses_session.load():
                if VERBOSE>=50: printlog('PrepareHandler/do_prepare', 'All Sessions: ' + str(db.WEB_DATABASE_CURSOR.execute('SELECT sessionid, go_pages FROM ses_session').fetchall()), request=self.request, level=50)

                self.flag_new_session = True
                tb_ses_session = db.ses_Session(sessionid=self.field_ses_session, lastused=time.time())
                tb_ses_session.save()
                printlog('PrepareHandler/do_prepare', 'Creating New Browser Tab Session: %s.' % self.field_ses_session, request=self.request)
            else:
                printlog('PrepareHandler/do_prepare', 'Re-Entering Browser Tab Session: %s.' % self.field_ses_session, request=self.request)
                self.flag_new_session = False

class BaseHandler(tornado.web.RequestHandler):

    async def do_prepare(self):

        # Query String:
        # -------------
        printlog('PrepareHandler/do_prepare', "Parsing query arguments: %s." % str(self.request.query_arguments), request=self.request, level=50)
        printlog('PrepareHandler/do_prepare', "Found the following uri: %s, %s." % (self.request.path, self.request.full_url()), request=self.request, level=50)
        self.query_arguments = {k:self.request.query_arguments[k][0] for k in self.request.query_arguments}
        for k in self.query_arguments:
            if self.query_arguments[k] == '':self.query_arguments[k] = None

    def write_error(self, status_code, **kwargs):
        import traceback

        kastexception = kwargs['exc_info'][1]

        if hasattr(kastexception, 'do_page') and kastexception.do_page:
            self.set_header('Content-Type', 'text/html')

            error_page = self.settings.get('static_path') + '/kastmenu/index-error.tmpl'
            with open(error_page, 'r') as f:error_src=f.read()
            error_src=error_src.replace('[[[ERROR_MESSAGE]]]', 'Error code: %d  Message: %s' % (status_code, kastexception.og_reason.replace('\n', '<br>')))
            error_src=error_src.replace('[[[HELP_TITLE]]]', 'KastMenu')
            error_src=error_src.replace('[[[HELP]]]', 'Some short Help !')
            error_src=error_src.replace('[[[LHELP]]]', 'Some long Help !')

            self.finish(error_src)
        else:
            self.set_header('Content-Type', 'application/json')

            if self.settings.get("serve_traceback") and "exc_info" in kwargs:
                # in debug mode, try to send a traceback
                lines = []
                for line in traceback.format_exception(*kwargs["exc_info"]):
                    lines.append(line)
                self.finish(json.dumps({
                    'error': {
                        'code': status_code,
                        'message': self._reason,
                        'traceback': lines,
                    }
                }))
            else:
                self.finish(json.dumps({
                    'error': {
                        'code': status_code,
                        'message': self._reason,
                    }
                }))


# http:
class BaseRemoteAuthHandler(PrepareHandler, BaseHandler):
    async def do_prepare(self, session_part):
        await PrepareHandler.do_prepare(self, session_part)
        await BaseHandler.do_prepare(self)

    def reply(self, jsonstr):
        self.set_header('Content-Type', 'application/json')
        self.write(jsonstr)

# WebSocket:
class BaseWebSocketHandler(PrepareHandler, tornado.websocket.WebSocketHandler):
    async def do_prepare(self, session_part):
        await PrepareHandler.do_prepare(self, session_part)


# ------------------------------------------------------------------------------------------------------ #
# Web Handlers:                                                                                          #
# ------------------------------------------------------------------------------------------------------ #
class WebMenuAdminHandler(BaseRemoteAuthHandler):
    SUPPORTED_URL_REQUEST = """
    /kastmenu/admin
    /kastmenu/admin/[user]
    """
    async def prepare(self):

        # Post not allowed:
        # -----------------
        if self.request.method.upper() == 'POST':
            m = 'Method: POST is not allowed !'
            raise KastException(405, reason=m, log_message=m)

    async def get(self, path):
        import json as modjson
        printlog('WebMenuAdminHandler:get',  '(uri /kastmenu/admin/*): Trying to Parse: %s' % self.request.path, request=self.request)

        # Make go_pages:
        spl = self.request.path.split('/')
        del spl[0]  # del blank
        del spl[0]  # del kastmenu
        KEYS = ('admin',)
        page_parms = {}
        go_pages = {
            'page': 'admin',
            'parms' : page_parms
        }

        failed = False

        for i in range(len(KEYS)):
            key = KEYS[i]
            if len(spl) < 1: break
            if key != spl[0]:
                failed = True
                break

            if len(spl) < 2:
                del spl[0]
                break

            value = spl[1]
            if value.strip()=='':value=None
            page_parms[key] = value
            del spl[0]
            del spl[0]

        if failed:
            message = 'Unsupported Url Request: %s ! Expected url request for /kastmenu/admin is one of:\n%s' % (self.request.path, WebMenuAdminHandler.SUPPORTED_URL_REQUEST)
            raise KastException(500, reason=message, log_message=message, do_page=True)

        if 'admin' in page_parms: # Actually admin in url is user in parms:
            page_parms['user'] = page_parms['admin']
            del page_parms['admin']

        # Return:
        # -------
        go_pages_json = modjson.dumps({'go_pages': go_pages})

        with open(INDEX_PAGE_ABS_PATH) as f:
            content = f.read()

        content = content.replace('//[1321321321]', 'loadvalue = %s;' % go_pages_json)

        self.set_header('Content-Type', 'text/html')
        self.write(content)



class WebMenuMachineHandler(BaseRemoteAuthHandler):
    ## // https://192.168.0.13:9000/kastmenu/machine/aaaaa/user/bbbbbb/password/cccccc/menufile/dddddd/menupath/eeeeee

    SUPPORTED_URL_REQUEST = """
    /kastmenu/machine
    /kastmenu/machine/[machine]
    /kastmenu/machine/[machine]/user/[user]
    /kastmenu/machine/[machine]/user/[user]/menu/[menu]
    /kastmenu/machine/[machine]/user/[user]/menu/[menu]/menupath/[menupath]
    """
    async def prepare(self):

        # Post not allowed:
        # -----------------
        if self.request.method.upper() == 'POST':
            m = 'Method: POST is not allowed !'
            raise KastException(405, reason=m, log_message=m, do_page=True)

    async def get(self, path):
        printlog('WebMenuMachineHandler:get', '(uri /kastmenu/machine/*): Trying to Parse: %s' % self.request.path, request=self.request)
        import json as modjson

        # Make go_pages:
        spl = self.request.path.split('/')
        del spl[0] # del blank
        del spl[0] # del kastmenu
        KEYS = ('machine', 'user', 'menu', 'menupath')
        page_parms = {}
        go_pages = {
            'page': 'machine',
            'parms' : page_parms
        }

        failed = False

        for i in range(len(KEYS)):
            key = KEYS[i]
            if len(spl) < 1: break
            if key != spl[0]:
                failed = True
                break

            if len(spl) < 2:
                del spl[0]
                break

            value = spl[1]
            if value.strip()=='':value=None
            page_parms[key] = value
            del spl[0]
            del spl[0]

        if failed:
            message = 'Unsupported Url Request: %s ! Expected url request for /kastmenu/machine is one of:\n%s' % (self.request.path, WebMenuMachineHandler.SUPPORTED_URL_REQUEST)
            raise KastException(500, reason=message, log_message=message, do_page=True)


        # Return:
        # -------
        go_pages_json = modjson.dumps({'go_pages': go_pages})

        with open(INDEX_PAGE_ABS_PATH) as f:
            content = f.read()

        content = content.replace('//[1321321321]', 'loadvalue = %s;' % go_pages_json)

        self.set_header('Content-Type', 'text/html')
        self.write(content)



# A001:
class WebMenuCVDEMO(BaseRemoteAuthHandler):
    # // https://192.168.0.13:9000/kastmenu/cvdemo/63e8d05112b016e611c17b0eb40aa120bc8f8446268d235e71f2c93551537fe1

    # @tornado.gen.coroutine
    async def prepare(self):
        self.crypt_session_part = genSessionPart()
        await BaseRemoteAuthHandler.do_prepare(self, self.crypt_session_part)
        if self.flag_new_session:
            pass

    async def get(self, path):
        if path == CVDEMO:return await self.getWelcomePage()
        elif path == 'get-view-token':return await self.getViewToken()

    # https://kastmenu.com:9000/kastmenu/cvdemo/63e8d05112b016e611c17b0eb40aa120bc8f8446268d235e71f2c93551537fe1
    async def getWelcomePage(self):
        import json as modjson
        prefix = 'Session: %s ' % self.field_ses_session
        validations = {'succeed': True, 'field': None, 'message': None, 'do_MenuSwitch': False}
        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        tb_ses_session.load()
        cvdemo_menu = "cvdemo"
        cvdemo_menu_path = "/opt/kastmenu/current/conf/welcome/cvdemo.xml"

        # 'parms': {'user':None, 'menu':None, 'menupath':None}
        go_parms = {"machine": "localhost", "user": None, "menu": cvdemo_menu}
        go_pages = {"page": "machine", "parms": go_parms, "do_submit": False}
        ses_machine = go_parms["machine"]

        # self.field_session_part
        tb_machine = db.Machine(host=ses_machine)
        tb_machine.load()
        # 2 {"go_pages":{"page":"machine","parms":{"machine":"localhost","mail":"fffff@aaa.com","mail_vcode":"8027603"},"do_submit":true,"type":"signin","password":"dfwdsfT-_7Y"}}

        # os_genUser :
        # ---------------
        try:
            printlog('WebMenuCVDEMO:', prefix + 'Try to generate User on Machine: %s.' % ses_machine, request=self.request)

            ses_user = await AcceptMail.os_generateUniqueUser(machine=ses_machine, ssh_user=tb_machine.sudo_user, ssh_port=tb_machine.ssh_port, request=self.request, verbose=VERBOSE)
        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            # validations:
            validations['field'] = 'mail'
            validations['message'] = 'Machine: {machine}: KastMenu was unable to generate an unique user on machine: {machine} ! Advise the KastMenu administrator. SubException is: {e}'.format(machine=ses_machine, e=shortException(e))
            validations['type'] = 'cvdemo'
            validations['succeed'] = False
            return

        go_parms['user'] = ses_user
        # os_createUser :
        # ---------------
        try:
            printlog('WebMenuCVDEMO:', prefix + 'Try to create User: %s on Machine: %s.' % (ses_user, ses_machine), request=self.request)
            await AcceptMail.os_createUser(password=ses_user, machine=ses_machine, user=ses_user, ssh_user=tb_machine.sudo_user, ssh_port=tb_machine.ssh_port, nologin=tb_machine.default_nologin, request=self.request, verbose=VERBOSE)
        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            # validations:
            validations['field'] = 'user'
            validations['message'] = 'Machine: {machine}: KastMenu was unable to create user: {user} on machine: {machine} ! Advise the KastMenu administrator with the following error. SubException is: {e}'.format(machine=ses_machine, user=ses_user, e=shortException(e))
            validations['type'] = 'cvdemo'
            validations['succeed'] = False
            return

        # createDbUser :
        # --------------
        try:
            printlog('WebMenuCVDEMO:', prefix + 'Trying to db/create User: %s on Machine: %s...' % (ses_user, ses_machine), request=self.request)
            AcceptMail.createDbUser(sessionid=self.field_ses_session, machine=ses_machine, user=ses_user, default_menu=cvdemo_menu, default_menu_fpath=cvdemo_menu_path, request=self.request, verbose=VERBOSE)
            printlog('WebMenuCVDEMO:', prefix + 'Record generated for User: %s on Machine: %s.' % (ses_user, ses_machine), request=self.request)
        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            # validations:
            validations['field'] = 'user'
            validations['message'] = 'Machine: {machine}/User: {user}: KastMenu was unable to db/create an unique user on machine: {machine} ! Advise the KastMenu administrator. SubException is: {e}'.format(machine=ses_machine, user=ses_user, e=shortException(e))
            validations['type'] = 'cvdemo'
            validations['succeed'] = False
            return

        tb_ses_user = db.ses_User(sessionid=self.field_ses_session, host=ses_machine, user=ses_user)
        tb_ses_user.load()
        tb_menufile = db.MenuFile(host=ses_machine, user=ses_user, name=cvdemo_menu)
        tb_menufile.load()

        # do_submit: Create New Menu Session:
        # -----------------------------------
        # launch Menu:
        while True:
            # Go Menu:
            # Delete Previous Menu Session:
            tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
            if tb_ses_menufile.load():
                printlog('WebMenuCVDEMO:', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Making room for this new Entry:\n'
                                                                 'Deleting Previous Menu: {pmenu}: for Machine: {pmachine} and User: {puser}.'.format(machine=ses_machine, user=ses_user, menu=tb_menufile.name, menupath=tb_menufile.path, pmachine=tb_ses_menufile.host, puser=tb_ses_menufile.user, pmenu=tb_ses_menufile.name), request=self.request)
                killHost(tb_ses_menufile.host, tb_ses_menufile.kastagent_ssh_pid)
                tb_ses_menufile.delete()

            try:
                printlog('WebMenuCVDEMO:', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Launching this new Menu at {menufile}...'.format(machine=ses_machine, user=ses_user, menu=tb_menufile.name, menufile=tb_menufile.path), request=self.request)
                ## kastweb_host, kastweb_port, kastweb_pid, shasecid, ssh_pid = await WebMenuDispatchHandler.os_launchMenu(machine=ses_machine, user=ses_user, sudo_user=tb_machine.sudo_user, ssh_port=tb_machine.ssh_port, menufile=tb_menufile.path, menupath=None, verbose=VERBOSE)
                kastweb_pid, kastweb_ssh_pid, kastagent_port, kastagent_shasecid, kastagent_pid, kastagent_ssh_pid = await WebMenuDispatchHandler.launchMenu(machine=ses_machine, kastagent_dir=tb_machine.kastagent_dir, kastweb_port=tb_machine.kastweb_port, kastagent_user=tb_machine.kastagent_user, menu_user=ses_user, menufile=tb_menufile.path, menupath=None, sudo_user=tb_machine.sudo_user, ssh_port=tb_machine.ssh_port, verbose=0)
                from kwadlib.security.crypting import sha256

                if (kastweb_pid, kastweb_ssh_pid) != (None, None):
                    tb_machine = db.Machine(host=ses_machine)
                    tb_machine.load()
                    tb_machine.kastweb_pid=kastweb_pid
                    tb_machine.kastweb_ssh_pid=kastweb_ssh_pid
                    tb_machine.save()
                tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session, host=ses_machine, user=ses_user, name=tb_menufile.name, kastagent_port=kastagent_port, kastagent_shasecid=kastagent_shasecid, kastagent_pid=kastagent_pid, kastagent_ssh_pid=kastagent_ssh_pid)
                tb_ses_menufile.lastused = time.time()
                tb_ses_menufile.save()
                printlog('WebMenuCVDEMO:', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Menu Launched.'.format(machine=ses_machine, user=ses_user, menu=tb_menufile.name), request=self.request)

            except Exception as e:
                import sys, traceback
                traceback.print_exc(file=sys.stdout)

                validations['field'] = 'menu'
                validations['message'] = 'Failed trying to launch Menu Name: %s on Machine: %s for User: %s ! SubException is: %s' % (tb_menufile.name, ses_machine, ses_user, shortException(e))
                validations['succeed'] = False
                break

            validations['do_MenuSwitch'] = True
            validations['succeed'] = True
            break

        tb_ses_user.lastused = time.time()
        tb_ses_user.save()
        validations['succeed'] = True

        # Return:
        # -------
        message = """The following resources was generated for you:
- A Temporary linux user: {user} on machine: localhost.
- A Specific Kubernetes K8S NameSpace for this user: ns-{user} was generated for this user.
- a Dkwad user.
        """.format(user=ses_user)
        # go_pages_json = modjson.dumps({'go_pages': go_pages, 'validations': validations})

        with open(INDEX_PAGE_ABS_PATH) as f:
            content = f.read()
        content = content.replace('//[1321321321]', 'sessionStorage.setItem("session_part", "{session_part}");DISPATCHER._CURRENT_ADMIN_GO_PARMS={go_parms};launchMenu({go_parms});doDispatch=false;'.format(session_part=self.crypt_session_part, message=message, go_parms=modjson.dumps(go_parms)) )
        # content = content.replace('//[1321321321]', 'sessionStorage.setItem("session_part", "{session_part}");/*alert("{message}");*/switchSettingScreen(false);feedFields(["machine", "user", "menu", "menupath"], {go_parms});launchMenu({go_parms});doDispatch=false;'.format(session_part=self.crypt_session_part, message=message, go_parms=modjson.dumps(go_parms)) )
        self.set_header('Content-Type', 'text/html')
        self.write(content)

        tb_ses_session.lastused = time.time()
        tb_ses_session.go_pages = modjson.dumps(go_pages)
        tb_ses_session.save()
        return


    # https://kastmenu.com:9000/kastmenu/cvdemo/get-view-token
    async def getViewToken(self):
        prefix = 'Session: %s ' % self.field_ses_session
        validations = {'succeed': True, 'field': None, 'message': None, 'do_MenuSwitch': False}
        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        tb_ses_session.load()
        from os import path

        ses_machine = 'localhost'
        tb_machine = db.Machine(host='localhost')
        tb_machine.load()
        output = None

        try:
            printlog('WebMenuCVDEMO:', prefix + '/Machine: {machine}/User: {user}: Generating SA view Token...'.format(machine=ses_machine, user='patrick'), request=self.request)
            output = await WebMenuCVDEMO.os_genToken(sudo_user=tb_machine.sudo_user, ssh_port=tb_machine.ssh_port, verbose=VERBOSE)
            printlog('WebMenuCVDEMO:', prefix + '/Machine: {machine}/User: {user}: Generated.'.format(machine=ses_machine, user='patrick'), request=self.request)

        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            validations['field'] = 'menu'
            validations['message'] = 'Failed trying to Generating SA view Token on Machine: %s by User: %s ! SubException is: %s' % (ses_machine, 'patrick', shortException(e))
            validations['succeed'] = False

        file = path.split((INDEX_PAGE_ABS_PATH))[0] + '/cvdemo/get-view-token.tmpl'
        with open(file) as f:
            content = f.read()
        self.set_header('Content-Type', 'text/html')
        self.write(content.replace('[TOKEN]', output))

        return


    @staticmethod
    async def os_genToken(sudo_user=None, ssh_port=None, verbose=0):
        selfMethod='os_genToken'
        machine = 'yuka'
        user = 'patrick'

        cmd = 'ssh -tttt -o ConnectTimeout=7  kwad@localhost  "sudo -u patrick kubectl -n kubernetes-dashboard create token  kubernetes-dashboard-viewonly-sa" '

        ret, output, ssh_pid =  await sshcall('localhost', cmd, user=None, sudo_user=None, port=ssh_port, isLocal=True, isMenu=True, doTTY=True, verbose=verbose)

        if ret != 0:
            raise kastmenuxception.kastmenuSystemException('WebMenuDispatchHandler', selfMethod, 'Failed trying to generate View Token on Machine: {machine} by User: {user} ! RemoteException is:\n{subex}'.format(machine=machine, user=user, subex=output))

        return output

class WebMenuDispatchHandler(BaseRemoteAuthHandler):

    # @tornado.gen.coroutine
    async def prepare(self):
        if 'Session-Part' not in self.request.headers:
            message='Request should support the following header: Session-Part !'
            raise KastException(500, reason=message, log_message=message)
        session_part = self.request.headers['Session-Part']
        await BaseRemoteAuthHandler.do_prepare(self, session_part)
        if self.flag_new_session:
            pass

        import json as modjson

        # Paremeters Management Get/Post: Query String and json field:
        # ------------------------------------------------------------
        if self.request.method.upper() == 'GET':
            m = 'Method: GET is not allowed !'
            raise KastException(405, reason=m, log_message=m, do_page=True)

        h = self.request.headers.get("Content-Type", None)
        if h == None:
            m = 'Unsupported Request: Should support Header: "Content-Type" !'
            raise KastException(500, reason=m, log_message=m, do_page=True)
        if not h.lower().startswith("application/json"):
            m = 'Unsupported Request Header: "Content-Type": Should be: "application/json" ! Found: %s.' % h
            raise KastException(500, reason=m, log_message=m, do_page=True)
        # self.json_args = json.loads(self.request.body)

        body = self.request.body
        body = body.strip()
        if len(body) != '':self.json_queries = modjson.loads(self.request.body)
        else:self.json_queries = None

        if self.json_queries!=None:printlog ('WebMenuDispatchHandler', 'WebMenuDispatchHandler:prepare: Found the following json parameters: %s.' % str(self.json_queries))

    async def post(self, uri):
        self_funct = 'post'
        import json as modjson
        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        tb_ses_session.load()
        prefix = 'Session: %s ' % self.field_ses_session

        # go_pages:
        go_pages = None
        if len(self.json_queries) == None or not 'go_pages' in self.json_queries:
            if tb_ses_session.go_pages != None:go_pages = modjson.loads(tb_ses_session.go_pages)
            else:go_pages = None
        else:go_pages = self.json_queries['go_pages']


        while True:
            if go_pages == None:
                go_pages = {'page': 'machine', 'parms': None}
                validations = {'succeed': True, 'field': None, 'message': None, 'do_MenuSwitch': False}
                break

            # do_submit:
            if 'do_submit' in go_pages and go_pages['do_submit']:
                do_submit = go_pages['do_submit']
            else:
                do_submit = False
            validations = {'succeed': True, 'field': None, 'message': None, 'do_MenuSwitch': False}

            go_page = go_pages['page']
            go_type = go_pages['type'] if 'type' in go_pages else None

            # Go Machine:
            # -----------
            if go_page == 'machine':
                printlog('WebMenuDispatchHandler:post', prefix + 'Entering Machine.', request=self.request)
                # parms keys: 'machine', 'user', 'menu', 'menupath'

                # has machine:
                done, go_pages, validations = getBlankMachineDefaultUserMenu(go_pages, validations, request=self.request)
                if done: break

                ses_machine = go_pages['parms']['machine']
                printlog('WebMenuDispatchHandler:post', prefix + 'Found Machine: %s.' % ses_machine, request=self.request)

                # sanitize machine:
                try:
                    sanitize_hostorip(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'machine': ses_machine})
                except Exception as e:
                    validations['field'] = 'machine'
                    validations['message'] = 'Invalid Machine: %s ! %s' % (ses_machine, shortException(e))
                    validations['succeed'] = False
                    go_pages['parms'] = {}
                    break

                # Check tb_machine still Exist otherwise delete machine:
                tb_machine = db.Machine(host=ses_machine)

                if not tb_machine.load():
                    # Delete tb_ses_machine:
                    sql = 'delete from ses_user where sessionid="%s" and host="%s";' % (self.field_ses_session, ses_machine)
                    db.WEB_DATABASE_CURSOR.execute(sql)
                    # validations:
                    validations['field'] = 'machine'
                    validations['message'] = 'Machine: %s do not Exist into KastMenu store !' % ses_machine
                    validations['succeed'] = False
                    go_pages['parms'] = {}
                    break
                ssh_port = tb_machine.ssh_port

                if go_page == 'machine' and go_type == 'signin':
                    printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}: Found Machine: {machine}.'.format(machine=ses_machine), request=self.request)
                    await self.acceptMailManagement(ses_machine, go_pages, validations)
                    tb_ses_session.load()
                    break

                # Has user:
                if go_pages['parms'] == None or not 'user' in go_pages['parms'] or go_pages['parms']['user']==None:
                    if do_submit:
                        # validations:
                        validations['field'] = 'user'
                        validations['message'] = 'User for Machine: %s is required !' % ses_machine
                        validations['succeed'] = False
                        go_pages['parms']['user'] = None
                        go_pages['parms']['menu'] = None
                        go_pages['parms']['menupath'] = None
                    break

                ses_user = go_pages['parms']['user']

                # sanitize user:
                try:
                    sanitize(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'ses_user': ses_user})
                except Exception as e:
                    # Accept mail users only if machine is xaccept_mail: True + sudo_user != None + user not found in tb_user:
                    doRaise = True
                    if tb_machine.sudo_user != None and tb_machine.xaccept_mail:
                        try:
                            if ses_user in ('', None): raise Exception()
                            AcceptMail.checkIsMail('mail', ses_user)
                            tb_user = db.User(host=ses_machine, user=ses_user)
                            if not tb_user.load():doRaise = False
                        except Exception as e:
                            pass

                    if doRaise:
                        validations['field'] = 'user'
                        validations['message'] = 'Invalid User: %s ! %s' % (ses_user, shortException(e))
                        validations['succeed'] = False
                        go_pages['parms']['user'] = None
                        go_pages['parms']['menu'] = None
                        go_pages['parms']['menupath'] = None
                        break

                printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}: Found User: {user}.'.format(machine=ses_machine, user=ses_user), request=self.request)

                # Check tb_user still Exist otherwise delete user:
                tb_user = db.User(host=ses_machine, user=ses_user)
                if not tb_user.load():
                    del go_pages['parms']['user']
                    if 'menu' in go_pages['parms']:del go_pages['parms']['menu']
                    if 'menupath' in go_pages['parms']:del go_pages['parms']['menupath']
                    # Delete tb_ses_user:
                    tb_ses_user = db.ses_User(sessionid=self.field_ses_session, host=ses_machine, user=ses_user)
                    if tb_ses_user.load():
                        tb_ses_user.delete()
                    # validations:
                    validations['field'] = 'user'
                    validations['message'] = 'Machine: %s/User: %s do not Exist into KastMenu store !' % (ses_machine, ses_user)
                    validations['succeed'] = False
                    go_pages['parms']['mail_vcode'] = None
                    go_pages['parms']['user'] = None
                    go_pages['parms']['menu'] = None
                    go_pages['parms']['menupath'] = None
                    break

                # Check if user is enabled:
                if not tb_user.enabled:
                    # validations:
                    validations['field'] = 'user'
                    validations['message'] = "Machine: %s/User: %s is disabled into KastMenu store ! Advise the KastMenu's manager to enable it." % (ses_machine, ses_user)
                    validations['succeed'] = False
                    go_pages['parms']['mail_vcode'] = None
                    go_pages['parms']['user'] = None
                    go_pages['parms']['menu'] = None
                    go_pages['parms']['menupath'] = None
                    break

                ses_authenticated = False
                # Check user already Exist in Session and Is Authenticated:
                tb_ses_user = db.ses_User(sessionid=self.field_ses_session, host=ses_machine, user=ses_user)
                if tb_ses_user.load():
                    tb_ses_user.lastused = time.time()
                    ses_authenticated = tb_ses_user.authenticated

                # X:Guest user Management:
                if tb_machine.sudo_user!=None and tb_user.xnopassword and ses_user == GUEST_USER:
                    ses_authenticated = True
                    if 'menu' not in go_pages['parms'] or go_pages['parms']['menu'] == None:
                        go_pages['parms']['menu'] = tb_machine.default_menu

                tb_ses_user.authenticated = ses_authenticated
                tb_ses_user.save()

                validations['authenticated'] = ses_authenticated
                if ses_authenticated and not do_submit: printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}: User is already authenticated.', request=self.request)

                # do_submit: Is already Authenticated ?
                # -------------------------------------
                if do_submit:
                    # Auth:
                    if ses_authenticated:pass
                    elif 'password' in go_pages and go_pages['password']!=None:
                        password = go_pages['password']
                        del go_pages['password']

                        try:
                            sanitize_kastmenu(do_hide=True, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'password': password})
                        except Exception as e:
                            validations['field'] = 'password'
                            validations['message'] = 'Invalid Password ! %s' % shortException(e)
                            validations['succeed'] = False
                            break

                        # X:Machine/sudo_user Management: ssh_user=ses_user if tb_machine.sudo_user==None else tb_machine.sudo_user
                        ret, output = self.os_authenticate(machine=ses_machine, user=ses_user, ssh_user=ses_user if tb_machine.sudo_user==None else tb_machine.sudo_user, ssh_port=ssh_port, password=password, request=self.request, verbose=VERBOSE)
                        if ret!=0:
                            validations['field'] = 'password'
                            validations['message'] = 'Invalid User/Password !'
                            validations['succeed'] = False
                            break
                    else:
                        validations['field'] = 'password'
                        validations['message'] = 'Password is required !'
                        validations['succeed'] = False
                        break

                    ses_authenticated = True
                    tb_ses_user.authenticated = ses_authenticated
                    tb_ses_user.lastused = time.time()
                    tb_ses_user.save()
                    validations['authenticated'] = ses_authenticated

                if ses_authenticated: printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}: is authenticated.', request=self.request)
                if 'password' in go_pages and go_pages['password']!=None:del go_pages['password']

                # Has MenuFile:
                if 'menu' not in go_pages['parms'] or go_pages['parms']['menu']==None:
                    # validations:
                    validations['field'] = 'menu'
                    validations['message'] = 'Menu for Machine: %s and User: %s is required !' % (ses_machine, ses_user)
                    validations['succeed'] = False
                    go_pages['parms']['menu'] = None
                    go_pages['parms']['menupath'] = None
                    break

                menu = go_pages['parms']['menu']

                # sanitize menu:
                try:
                    sanitize(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'menu': menu})
                except Exception as e:
                    validations['field'] = 'menu'
                    validations['message'] = 'Invalid Menu Name: %s ! %s' % (menu, shortException(e))
                    validations['succeed'] = False
                    go_pages['parms']['menu'] = None
                    go_pages['parms']['menupath'] = None
                    break

                # Check menu Exist:
                tb_menufile = db.MenuFile(host=ses_machine, user=ses_user, name=menu)
                if not tb_menufile.load():
                    validations['field'] = 'menu'
                    validations['message'] = 'Menu Name: %s on Machine: %s for User: %s do not Exist in db store !' % (menu, ses_machine, ses_user)
                    validations['succeed'] = False
                    go_pages['parms']['menu'] = None
                    go_pages['parms']['menupath'] = None
                    break

                printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Found Menu: {menu}, for user: {user} on Machine: {machine}.'.format(machine=ses_machine, user=ses_user, menu=menu), request=self.request)

                # Prepare javascript menufile list:
                # Has MenuPath:
                menupath = None
                if 'menupath' in go_pages['parms'] and go_pages['parms']['menupath'] not in ('', None):
                    menupath = go_pages['parms']['menupath']

                    # sanitize menupath :
                    try:
                        sanitize_kastmenu(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'menupath ': menupath })
                    except Exception as e:
                        validations['field'] = 'menupath'
                        validations['message'] = 'Invalid MenuPath : %s ! %s' % (menupath , shortException(e))
                        validations['succeed'] = False
                        go_pages['parms']['menupath'] = None
                        break

                printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Menupath: {menupath} was passed.'.format(machine=ses_machine, user=ses_user, menu=menu, menupath=menupath), request=self.request)

                # do_submit: Create New Menu Session:
                # -----------------------------------
                # launch Menu:
                if do_submit:
                    # Go Menu:
                    # Delete Previous Menu Session:
                    tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
                    if tb_ses_menufile.load():
                        printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Making room for this new Entry:\n'
                                 'Deleting Previous Menu: {pmenu}: for Machine: {pmachine} and User: {puser}.'.format(machine=ses_machine, user=ses_user, menu=menu, menupath=menupath, pmachine=tb_ses_menufile.host, puser=tb_ses_menufile.user, pmenu=tb_ses_menufile.name), request=self.request)
                        killHost(tb_ses_menufile.host, tb_ses_menufile.kastagent_ssh_pid)
                        tb_ses_menufile.delete()

                    try:
                        printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Launching this new Menu...'.format(machine=ses_machine, user=ses_user, menu=tb_menufile.name, menufile=tb_menufile.path), request=self.request)
                        # kastweb_host, kastweb_port, kastweb_pid, shasecid, ssh_pid = await self.os_launchMenu(machine=ses_machine, user=ses_user, sudo_user=tb_machine.sudo_user, ssh_port=ssh_port, menufile=tb_menufile.path, menupath=menupath, verbose=VERBOSE)
                        kastweb_pid, kastweb_ssh_pid, kastagent_port, kastagent_shasecid, kastagent_pid, kastagent_ssh_pid = await WebMenuDispatchHandler.launchMenu(machine=ses_machine, kastagent_dir=tb_machine.kastagent_dir, kastweb_port=tb_machine.kastweb_port, kastagent_user=tb_machine.kastagent_user, menu_user=ses_user, menufile=tb_menufile.path, menupath=menupath, sudo_user=tb_machine.sudo_user, ssh_port=ssh_port, verbose=VERBOSE)

                        from kwadlib.security.crypting import sha256

                        tb_machine = db.Machine(host=ses_machine)
                        tb_machine.load()
                        tb_machine.kastweb_pid = kastweb_pid
                        tb_machine.kastweb_ssh_pid = kastweb_ssh_pid
                        tb_machine.save()
                        tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session, host=ses_machine, user=ses_user, name=menu, kastagent_port=kastagent_port, kastagent_shasecid=kastagent_shasecid, kastagent_pid=kastagent_pid, kastagent_ssh_pid=kastagent_ssh_pid)
                        tb_ses_menufile.lastused = time.time()
                        tb_ses_menufile.save()
                        printlog('WebMenuDispatchHandler:post', prefix + '/Machine: {machine}/User: {user}/Menu: {menu}: Menu Launched.', request=self.request)

                    except Exception as e:
                        import sys, traceback
                        traceback.print_exc(file=sys.stdout)

                        validations['field'] = 'menu'
                        validations['message'] = 'Failed trying to launch Menu Name: %s on Machine: %s for User: %s ! SubException is: %s' % (menu, ses_machine, ses_user, shortException(e))
                        validations['succeed'] = False
                        break

                    validations['do_MenuSwitch'] = True
                    validations['succeed'] = True
                    break

                tb_ses_user.lastused = time.time()
                tb_ses_user.save()
                validations['succeed'] = True
                break


            # Go Admin:
            # ---------
            elif go_page == 'admin':
                printlog('WebMenuDispatchHandler:post', prefix + 'Entering Admin.', request=self.request)
                # parms keys: 'user'

                # Has user:
                if go_pages['parms'] == None or not 'user' in go_pages['parms'] or go_pages['parms']['user']==None:
                    if do_submit:
                        # validations:
                        validations['field'] = 'user'
                        validations['message'] = 'KastMenu Admin User is required !'
                        validations['succeed'] = False
                    break

                ses_user = go_pages['parms']['user']

                # sanitize user:
                try:
                    sanitize(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'ses_user': ses_user})
                except Exception as e:
                    validations['field'] = 'user'
                    validations['message'] = 'Invalid User: %s ! %s' % (ses_user, shortException(e))
                    validations['succeed'] = False
                    break

                # Check tb_user still Exist otherwise delete user:
                tb_user = db.AdminUser(user=ses_user)
                if not tb_user.load():
                    del go_pages['parms']['user']
                    # Delete tb_ses_adminuser:
                    tb_ses_adminuser = db.ses_AdminUser(sessionid=self.field_ses_session, user=ses_user)
                    if tb_ses_adminuser.load():
                        tb_ses_adminuser.delete()
                    # validations:
                    validations['field'] = 'user'
                    validations['message'] = 'KastMenu Admin: %s do not Exist into KastMenu store !' % ses_user
                    validations['succeed'] = False
                    break

                printlog('WebMenuDispatchHandler:post', prefix + 'Found user: %s.' % ses_user, request=self.request)

                ses_authenticated = False
                # Check user already Exist in Session and Is Authenticated:
                tb_ses_adminuser = db.ses_AdminUser(sessionid=self.field_ses_session, user=ses_user)
                if tb_ses_adminuser.load():
                    tb_ses_adminuser.lastused = time.time()
                    ses_authenticated = tb_ses_adminuser.authenticated

                tb_ses_adminuser.authenticated = ses_authenticated
                validations['authenticated'] = ses_authenticated

                # do_submit: Is already Authenticated ?
                # -------------------------------------
                if do_submit:
                    # Auth:
                    if ses_authenticated:pass
                    elif 'password' in go_pages and go_pages['password']!=None:
                        password = go_pages['password']
                        del go_pages['password']

                        try:
                            sanitize_kastmenu(do_hide=True, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'password': password})
                        except Exception as e:
                            validations['field'] = 'password'
                            validations['message'] = 'Invalid Password ! %s' % shortException(e)
                            validations['succeed'] = False
                            break

                        from kwadlib.security.crypting import sha256

                        if tb_user.password != sha256(password):
                            validations['field'] = 'password'
                            validations['message'] = 'Invalid User/Password !'
                            validations['succeed'] = False
                            break
                    else:
                        validations['field'] = 'password'
                        validations['message'] = 'Password is required !'
                        validations['succeed'] = False
                        break

                    printlog('WebMenuDispatchHandler:post', prefix + 'User: %s is authenticated.' % ses_user, request=self.request)

                    # Create into ses_adminuser:
                    ses_authenticated = True
                    tb_ses_adminuser.authenticated = ses_authenticated
                    tb_ses_adminuser.lastused = time.time()
                    tb_ses_adminuser.save()
                    validations['authenticated'] = ses_authenticated
                    # Create into ses_user:
                    # Create an instance of this user into ses_User (in order to allow foreign key check when using ses_menufile),
                    # But never authenticate admin user on local machine.
                    tb_ses_user = db.ses_User(sessionid=self.field_ses_session, host='localhost', user=ses_user)
                    tb_ses_user.authenticated = False
                    tb_ses_user.lastused = time.time()
                    tb_ses_user.save()

                if 'password' in go_pages and go_pages['password']!=None:del go_pages['password']

                # do_submit: Create New Menu Session:
                # -----------------------------------
                # launch Menu:
                if do_submit:
                    # Go Menu:
                    # Delete Previous Menu Session:
                    tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
                    if tb_ses_menufile.load():
                        killHost(tb_ses_menufile.host, tb_ses_menufile.kastagent_ssh_pid)
                        tb_ses_menufile.delete()

                    try:
                        printlog('WebMenuDispatchHandler:post', prefix + 'Trying to Launch Admin Menu for User: %s...' % ses_user, request=self.request)
                        kastweb_pid, kastweb_ssh_pid, kastagent_port, kastagent_shasecid, kastagent_pid, kastagent_ssh_pid = await self.launchAdminMenu(verbose=VERBOSE)
                        from kwadlib.security.crypting import sha256

                        if (kastweb_pid, kastweb_ssh_pid) != (None, None):
                            tb_machine = db.Machine(host='localhost')
                            tb_machine.load()
                            tb_machine.kastweb_pid = kastweb_pid
                            tb_machine.kastweb_ssh_pid = kastweb_ssh_pid
                            tb_machine.save()
                        tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session, host='localhost', user=ses_user, name='KastAdmin', kastagent_port=kastagent_port, kastagent_shasecid=kastagent_shasecid, kastagent_pid=kastagent_pid, kastagent_ssh_pid=kastagent_ssh_pid)
                        tb_ses_menufile.lastused = time.time()
                        tb_ses_menufile.save()
                        printlog('WebMenuDispatchHandler:post', prefix + 'Admin Menu Launched.', request=self.request)

                    except Exception as e:
                        import sys, traceback
                        traceback.print_exc(file=sys.stdout)

                        validations['field'] = 'menu'
                        validations['message'] = 'Failed trying to launch Menu KastAdmin for User: %s ! SubException is: %s' % (ses_user, shortException(e))
                        validations['succeed'] = False
                        break

                    validations['do_MenuSwitch'] = True
                    validations['succeed'] = True
                    break

                tb_ses_adminuser.lastused = time.time()
                tb_ses_adminuser.save()
                validations['succeed'] = True
                break


            # Other goPage:
            # -------------
            else:
                raise (222222222)

        if 'message' in validations:
            printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Finish sendind this message to client: %s.' % validations['message'], request=self.request)
        go_pages_json = modjson.dumps({'go_pages': go_pages, 'validations': validations})

        # Return:
        # -------
        self.reply(go_pages_json)
        if 'do_submit' in go_pages:del go_pages['do_submit']
        if 'password' in go_pages:del go_pages['password']
        tb_ses_session.lastused = time.time()
        tb_ses_session.go_pages = modjson.dumps(go_pages)
        tb_ses_session.save()
        return


    async def acceptMailManagement(self, ses_machine, go_pages=None, validations=None):
        """
        Accept Mail Management [Begin]:                                                                            #
        """
        prefix = 'Session: %s ' % self.field_ses_session
        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        tb_ses_session.load()
        tb_machine = db.Machine(host=ses_machine)
        tb_machine.load()

        if tb_machine.sudo_user != None and tb_machine.xaccept_mail:pass
        else:
            # validations:
            validations['field'] = None
            validations['type'] = 'mail.out'
            validations['succeed'] = False
            go_pages['parms']['mail'] = None
            go_pages['parms']['mail_vcode'] = None
            return

        printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Entering AcceptMail Management.', request=self.request)

        # Check has mail:
        if go_pages['parms'] == None or not 'mail' in go_pages['parms']:
            ## if do_submit:
            # validations:
            validations['field'] = 'mail'
            validations['message'] = 'Mail for Machine: %s is required !' % ses_machine
            validations['succeed'] = False
            go_pages['parms']['user'] = None
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        ses_mail = go_pages['parms']['mail']

        # Check mail:
        message = None
        try:
            AcceptMail.checkIsMail('mail', ses_mail)
        except Exception as e:
            message = 'Unsupported Mail: %s for Machine: %s ! SubException is: %s' % (ses_mail, ses_machine, shortException(e))
            # validations:
            validations['field'] = 'mail'
            validations['message'] = message
            validations['type'] = 'mail'
            validations['succeed'] = False
            go_pages['parms']['mail'] = ses_mail
            go_pages['parms']['user'] = None
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        # Check is already registred:
        if AcceptMail.checkUserMailExists(machine=ses_machine, mail=ses_mail, request=self.request):
            message = 'Unsupported Mail: %s ! This mail is already registred, if you have forgotten your associated user for machine: %s, Advise the KastMenu administrator.' % (ses_mail, ses_machine)
            # validations:
            validations['field'] = 'mail'
            validations['message'] = message
            validations['type'] = 'mail'
            validations['succeed'] = False
            go_pages['parms']['mail'] = ses_mail
            go_pages['parms']['user'] = None
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Found Mail: %s.' % ses_mail, request=self.request)

        # Check has validation code 1:
        # ----------------------------
        if go_pages['parms'] == None or not 'mail_vcode' in go_pages['parms']:
            # Send Validation Code to user:
            # -----------------------------
            try:
                rand = random.randint(1, 10000000)
                vcode = "%05i" % rand
                await AcceptMail.mailValidationCodeToUser(mail=ses_mail, validation_code=vcode, machine=ses_machine)
                tb_ses_session.vcode = vcode
                tb_ses_session.lastused = time.time()
                tb_ses_session.save()
            except Exception as e:
                import sys, traceback
                traceback.print_exc(file=sys.stdout)

                # validations:
                validations['field'] = 'mail'
                validations['message'] = 'Unable to send Validation Code to mail: %s ! SubException is: %s. Advice the KastMenu administrator.' % (ses_mail, shortException(e))
                validations['type'] = 'mail'
                validations['succeed'] = False
                go_pages['parms']['user'] = None
                go_pages['parms']['menu'] = None
                go_pages['parms']['menupath'] = None
                return

            # validations:
            validations['field'] = 'mail_vcode'
            validations['message'] = 'Validation Code is required ! Please check your mail to retreive the validation code.'
            validations['type'] = 'mail+vcode'
            validations['succeed'] = False
            go_pages['parms']['user'] = None
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        ses_vode = go_pages['parms']['mail_vcode']
        printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Checking received Validation Code: %s with expected: %s.' % (str(ses_vode), str(tb_ses_session.vcode)), request=self.request)

        # Check has validation code 2:
        if go_pages['parms']['mail_vcode'] == None or go_pages['parms']['mail_vcode'] != tb_ses_session.vcode:
            if go_pages['parms']['mail_vcode'] == None:
                message = 'Validation Code is required ! Please check your mail to retreive the validation code.'
            else:
                message = 'This Validation Code is not correct ! Please check your mail to retreive the validation code.'
            # validations:
            validations['field'] = 'mail_vcode'
            validations['message'] = message
            validations['type'] = 'mail+vcode'
            validations['succeed'] = False
            go_pages['parms']['user'] = None
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Validation Code checked !', request=self.request)

        # Has password:
        # -------------
        if 'password' in go_pages and go_pages['password'] != None:
            password = go_pages['password']
            del go_pages['password']

            errors = AcceptMail.checkPasswordValidity(password)
            succeed = errors['password_ok']
            if not succeed:
                from io import  StringIO
                sb =StringIO()
                firstime=True
                for err in ('length_error', 'digit_error', 'uppercase_error', 'lowercase_error', 'symbol_error', 'exclude_error'):
                    if errors[err]==None:continue
                    if firstime:firstime=False
                    else:sb.write(', ')
                    sb.write(str(errors[err]))

                validations['field'] = 'password'
                validations['message'] = 'Invalid Password ! %s' % sb.getvalue()
                validations['type'] = 'mail-vcode'
                go_pages['parms']['user'] = None
                go_pages['parms']['menu'] = None
                go_pages['parms']['menupath'] = None
                validations['succeed'] = False
                return
        else:
            validations['field'] = 'password'
            validations['message'] = 'Password is required !'
            validations['type'] = 'mail-vcode'
            validations['succeed'] = False
            go_pages['parms']['user'] = None
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Password is Valid.', request=self.request)

        # generate unique user name from mail:
        # ------------------------------------
        try:
            printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Try to generate User from Mail: %s on Machine: %s.' % (ses_mail, ses_machine), request=self.request )
            ses_user = await AcceptMail.generateUniqueUserFromMail(machine=ses_machine, mail=ses_mail, ssh_user=tb_machine.sudo_user, ssh_port=tb_machine.ssh_port, request=self.request, verbose=VERBOSE)
        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            # validations:
            validations['field'] = 'mail'
            validations['message'] = 'Machine: {machine}/Mail: {mail}: KastMenu was unable to generate an unique user on machine: {machine} for mail: {mail} ! Advise the KastMenu administrator. SubException is: {e}'.format(machine=ses_machine, mail=ses_mail, e=shortException(e))
            validations['type'] = 'mail-vcode'
            validations['succeed'] = False
            go_pages['parms']['mail-vcode'] = None
            go_pages['parms']['user'] = None
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'User: %s generated for Mail: %s on Machine: %s.' % (ses_user, ses_mail, ses_machine), request=self.request)

        # os_createUser :
        # ---------------
        try:
            await AcceptMail.os_createUser(password=password, machine=ses_machine, user=ses_user, ssh_user=tb_machine.sudo_user, ssh_port=tb_machine.ssh_port, nologin=tb_machine.default_nologin, request=self.request, verbose=VERBOSE)
        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            # validations:
            validations['field'] = 'user'
            validations['message'] = 'Machine: {machine}/User: {user}: KastMenu was unable to create an unique user on machine: {machine} for mail: {mail} ! Advise the KastMenu administrator with the following error. SubException is: {e}'.format(machine=ses_machine, user=ses_user, mail=ses_mail, e=shortException(e))
            validations['type'] = 'mail-vcode'
            validations['succeed'] = False
            go_pages['parms']['user'] = ses_user
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return

        # createDbUser :
        # --------------
        try:
            printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Trying to db/create User: %s on Machine: %s...' % (ses_user, ses_machine), request=self.request)
            AcceptMail.createDbUser(sessionid=self.field_ses_session, machine=ses_machine, user=ses_user, mail=ses_mail, default_menu=tb_machine.default_menu, default_menu_fpath=tb_machine.default_menu_fpath, request=self.request, verbose=VERBOSE)
            printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Record generated for User: %s on Machine: %s.' % (ses_user, ses_machine), request=self.request)
        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            # validations:
            validations['field'] = 'user'
            validations['message'] = 'Machine: {machine}/User: {user}: KastMenu was unable to db/create user on machine: {machine} for mail: {mail} ! Advise the KastMenu administrator. SubException is: {e}'.format(machine=ses_machine, user=ses_user, mail=ses_mail, e=shortException(e))
            validations['type'] = 'mail-vcode'
            validations['succeed'] = False
            go_pages['parms']['user'] = ses_user
            go_pages['parms']['menu'] = None
            go_pages['parms']['menupath'] = None
            return


        # validations:
        if 'message' in validations:
            printlog('WebMenuDispatchHandler:acceptMailManagement', prefix + 'Finish sendind this message to client: %s.' % validations['message'], request=self.request)
        validations['field'] = None
        validations['+message'] = """User: {user} for Machine: {machine} and Mail: {mail} is created ! Validate again to switch to Menu.
The following resources was created for this user:
    - an unix user on machine: {machine}
    - a K8S NameSpace: ns-{user}
    - a dkwad user.
Save your user and password, kastmenu cannot recover them !
        """.format(user=ses_user, machine=ses_machine, mail=ses_mail)
        validations['type'] = 'mail.out'
        validations['succeed'] = False
        go_pages['parms']['mail_vcode'] = None
        go_pages['parms']['user'] = ses_user
        go_pages['parms']['menu'] = tb_machine.default_menu
        go_pages['parms']['menupath'] = None

        ## tb_ses_session.vcode = None
        tb_ses_session.save()

    @staticmethod
    async def os_launchMachine(machine=None, kastagent_dir=None, kastweb_port=None, kastagent_user=None, sudo_user=None, ssh_port=None, verbose=0):
        selfMethod='os_launchMachine'
        from kwadlib import default
        # ===>
        kagent_bin = default.getKastAgentBinPath()
        version = default.getVersion()
        bintar = 'kastagent-' + version + '.tar.gz'
        suffix = '/kastagent/kastagent-' + version

        if kastagent_user==None:raise kastmenuxception.kastmenuParameterException('WebMenuDispatchHandler', selfMethod, 'kastagent_user is required for machine: %s !' % machine)
        sanitize(class_exit='WebMenuDispatchHandler', method_exit=selfMethod, **{'kastagent_user': kastagent_user})

        if kastagent_dir == '*home':kastagent_dir = '/home/%s'
        else:sanitize_path(class_exit='WebMenuDispatchHandler', method_exit=selfMethod, **{'kastagent_dir': kastagent_dir})
        kastweb = kastagent_dir + suffix + '/bin/kastweb'
        bininst = kastagent_dir + suffix + '/bin/kastagent-install.sh'
        caclients = kastagent_dir + suffix + '/conf/keys/kastweb/caclients'
        target_dir = kastagent_dir + '/kastagent'

        # Check Kastweb Remote connection:
        # --------------------------------
        printlog('WebMenuDispatchHandler:os_launchMachine', 'Checking Kastweb availability on Machine: %s and Port: %d ...' % (machine, kastweb_port), request=None, level=80)
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((machine, kastweb_port))
            s.close()

            printlog('WebMenuDispatchHandler:os_launchMachine', '... Kastweb is Listening on Machine: %s and Port: %d. Nothing to do.' % (machine, kastweb_port), request=None, level=80)
            return None, None
        except:
            pass

        printlog('WebMenuDispatchHandler:os_launchMachine', "Kastweb is not Listening on Machine: %s and Port: %d, we'll have to Launch it !" % (machine, kastweb_port), request=None, level=80)

        SSH_PORT = ''
        if machine == 'localhost':
            isLocal = True
            localhost = ' -H localhost '
        else:
            isLocal = False
            localhost = ''
            sanitize_hostorip(machine)
            sanitize_int(ssh_port)
            if ssh_port != 22: SSH_PORT = ' -p %s' % str(ssh_port)


        # Check kastagent-x.x remote directory:
        # -------------------------------------
        printlog('WebMenuDispatchHandler:os_launchMachine', 'Checking Kastweb directory: %s presence on Machine: %s ...' % (kastweb, machine), request=None, level=80)
        cmd = "ls %s" % kastweb
        #1:
        ret, output, ssh_pid = await sshcall(machine, cmd, user=kastagent_user, sudo_user=sudo_user, port=ssh_port, isLocal=False, isMenu=True, doTTY=True, verbose=verbose)
        if ret != 0:
            connection_user = kastagent_user if sudo_user == None else sudo_user

            printlog('WebMenuDispatchHandler:os_launchMachine', 'Kastweb directory: %s is not present on Machine: %s will have to install Kastagent !' % (kastweb, machine), request=None, level=80)

            # Intall kastagent-x.x binary:
            # ----------------------------
            printlog('WebMenuDispatchHandler:os_launchMachine', 'Installing Kastagent: %s on Machine: %s at %s ...' % (kagent_bin, machine, kastagent_dir), request=None, level=80)
            ## scp:
            """
            if isLocal:
            {version} {kast_agent_dir} {kast_web_host}  {kast_web_port} 
                cmd = 'set -x;set -e;ls {kastagent_dir} && mkdir {target_dir} && cp {kagent_bin} {target_dir} && cd {target_dir} && tar -zxvf ./{bintar} && {bininst}'.format(kastagent_dir=kastagent_dir, kagent_bin=kagent_bin, target_dir=target_dir, bintar=bintar, bininst=bininst)
            else:
            """
            if connection_user!=kastagent_user:sudo='sudo'
            else:sudo=''

            ## cmd = """set -x;set -e;ssh {port} {user}@{machine} {sudo} bash -c 'ls {kastagent_dir} && mkdir -p {target_dir}' && scp {port} {kagent_bin} {user}@{machine}:/tmp && ssh {port} {user}@{machine} {sudo} bash -c 'mv /tmp/{bintar} {target_dir} && cd {target_dir} && tar -zxvf ./{bintar} | tail -3' && {sudo} bash -c 'cd {target_dir} && {bininst} {version} {kast_agent_dir} {kast_web_host} {kast_web_port}' && {sudo} bash -c 'chown -R {real_user}:{real_user} {target_dir}'""".format(port=SSH_PORT, kagent_bin=kagent_bin, user=connection_user, machine=machine, kastagent_dir=kastagent_dir, sudo=sudo, target_dir=target_dir, bintar=bintar, real_user=kastagent_user, bininst=bininst, version=version, kast_agent_dir=kastagent_dir, kast_web_host=machine,  kast_web_port=kastweb_port)
            """
            scp /etc/kastmenu/keys/caclients/to_kastweb/caclients.tar {caclients}
            scp {port} /etc/kastmenu/keys/caclients/to_kastweb/caclients.tar {user}@{machine}:/tmp
sudo ls -ltr /etc/kastmenu/keys/caclients/to_kastweb/*.crt
cd /etc/kastmenu/keys/caclients;tar -cvf caclients.tar *.crt
e.g.:
serenity.crt
kastmenu.serenity.ca.crt
            """
            cmd = """cd /etc/kastmenu/keys/caclients/to_kastweb;tar -cvf caclients.tar *.crt;cd -;ssh {port} {user}@{machine} 'set -x;set -e;{sudo} bash -c "ls {kastagent_dir} && mkdir -p {target_dir}"' && scp {port} {kagent_bin} {user}@{machine}:/tmp && ssh {port} {user}@{machine} 'set -x;set -e;{sudo} bash -c "mv /tmp/{bintar} {target_dir} && cd {target_dir} && tar -zxvf ./{bintar} | tail -3" && {sudo} bash -c "cd {target_dir} && {bininst} {version} {kast_agent_dir} {kast_web_host} {kast_web_port}"' && scp {port} /etc/kastmenu/keys/caclients/to_kastweb/caclients.tar {user}@{machine}:/tmp && set -x;set -e;ssh {port} {user}@{machine} '{sudo} bash -c "tar -xvf /tmp/caclients.tar -C {caclients} && rm /tmp/caclients.tar && c_rehash {caclients} && chown -R {real_user}:{real_user} {target_dir}"' """.format(port=SSH_PORT, kagent_bin=kagent_bin, user=connection_user, machine=machine, kastagent_dir=kastagent_dir, sudo=sudo, target_dir=target_dir, bintar=bintar, real_user=kastagent_user, caclients=caclients, bininst=bininst, version=version, kast_agent_dir=kastagent_dir, kast_web_host=machine, kast_web_port=kastweb_port)
            printlog('popen', 'is Remotly calling the following command: %s.' % cmd, request=None, level=80)
            from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
            p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True, executable='/bin/bash')
            # live read/print instead of: stdout, stderr = p.communicate():
            for stdout_line in iter(p.stdout.readline, ""):
                print(stdout_line)

            p.stdout.close()
            ret = p.wait()
            if ret!=0:
                raise Exception('Unable to Install Kastagent: %s on Machine: %s at %s !' % (kagent_bin, machine, kastagent_dir))

        printlog('WebMenuDispatchHandler:os_launchMachine', '... Kastweb directory: %s is present on Machine: %s.' % (kastweb, machine), request=None, level=80)


        # Runing Kastweb:
        # ---------------
        printlog('WebMenuDispatchHandler:os_launchMachine', 'Launching Kastagent/kastweb on Machine: %s ...' % (machine,), request=None, level=80)
        cmd = '{kastweb} --host {machine} --port {kastweb_port} -v{verbose}'.format(kastweb=kastweb, localhost=localhost, machine=machine, kastweb_port=kastweb_port, verbose=str(verbose))
        ret, output, ssh_pid =  await sshcall(machine, cmd, user=kastagent_user, sudo_user=sudo_user, port=ssh_port, isLocal=False, isMenu=True, doTTY=True, verbose=verbose)

        """ e.g.:
kastweb: kastweb Temporary dir is: /home/kastmenu/.kastmenu/temp.
Launching Kastweb on host/port localhost:9100 with pid: 25811
{"host":"localhost","port":9100,"pid":25811"}
Kastweb Launched finished.
"""
        # Expected content:
        EXPECTED_KASTWEB_OUTPUT="""{pid:[pid]}
Kastweb Launched finished."""
        try:
            import json as modjson
            spl = output.split('\n')
            json = spl[-2].strip()
            if json == '':raise Exception()
            d = modjson.loads(json)
            kastweb_pid = d['pid']
        except:
            raise Exception('Bad pattern from kastweb !\nExpected: %s !\n   Found: %s and %s' % (EXPECTED_KASTWEB_OUTPUT, output.split('\n')[-2], output))

        if ret != 0:
            raise kastmenuxception.kastmenuSystemException('WebMenuDispatchHandler', selfMethod, 'Failed trying to launch Kastweb at path: {kastagent_dir}, on Machine: {machine} For User: {user} ! RemoteException is:\n{subex}'.format(kastagent_dir=kastagent_dir, machine=machine, user=kastagent_user, subex=output))
        printlog('WebMenuDispatchHandler:os_launchMachine', 'Kastagent/kastweb Launched with Endpoints: %s' % output, request=None, level=80)

        return kastweb_pid, ssh_pid

    @staticmethod
    async def launchMenu(machine=None, kastagent_dir=None, kastweb_port=None, kastagent_user=None, menu_user=None, menufile=None, menupath=None, sudo_user=None, ssh_port=None, verbose=0):
        kastweb_pid, kastweb_ssh_pid = await WebMenuDispatchHandler.os_launchMachine(machine=machine, kastagent_dir=kastagent_dir, kastweb_port=kastweb_port, kastagent_user=kastagent_user, sudo_user=sudo_user, ssh_port=ssh_port, verbose=verbose)
        kastagent_port, kastagent_shasecid, kastagent_pid, kastagent_ssh_pid = await WebMenuDispatchHandler.os_launchMenu(machine=machine, kastagent_dir=kastagent_dir, user=menu_user, sudo_user=sudo_user, ssh_port=ssh_port, menufile=menufile, menupath=menupath, verbose=verbose)

        return kastweb_pid, kastweb_ssh_pid, kastagent_port, kastagent_shasecid, kastagent_pid, kastagent_ssh_pid
    @staticmethod
    async def os_launchMenu(machine=None, kastagent_dir=None, user=None, sudo_user=None, ssh_port=None, menufile=None, menupath=None, verbose=0):
        selfMethod='os_launchMenu'
        if kastagent_dir == '*home':kastagent_dir = '/home/%s/current'
        else:sanitize_path(class_exit='WebMenuDispatchHandler', method_exit=selfMethod, **{'kastagent_dir': kastagent_dir})
        suffix = '/kastagent/kastagent-' + default.getVersion()
        kastagent = kastagent_dir + suffix + '/bin/kastagent'

        if menupath not in (None, ''):more = " -g %s -p 3 " % menupath
        else:more=''
        if machine == 'localhost': localhost = ' -H localhost '
        else:localhost = ''

        printlog('WebMenuDispatchHandler:os_launchMenu', 'Launching Kastagent on Machine: %s ...' % (machine,), request=None, level=80)
        cmd = '{kastagent} {menufile} {localhost} -l -O -v{verbose}{more}'.format(kastagent=kastagent, menufile=menufile, localhost=localhost, verbose=str(verbose), more=more)
        ret, output, ssh_pid =  await sshcall(machine, cmd, user=user, sudo_user=sudo_user, port=ssh_port, isLocal=False, isMenu=True, doTTY=True, verbose=verbose)

        # Expected content:
        EXPECTED_KASTAGENT_OUTPUT="""{"host":"{host}","port":{port},"pid":{pid},"shasecid":"{shasecid}", "temp_dir": "{temp_dir}"}
Kastagent Launched finished."""
        try:
            import json as modjson
            spl = output.split('\n')
            json = spl[-2].strip()
            if json == '':raise Exception()
            d = modjson.loads(json)
            ## kastagent_host, kastagent_port, kastagent_pid, shasecid = d['host'], d['port'], d['pid'], d['shasecid']
            kastagent_port, kastagent_shasecid, kastagent_pid, temp_dir = d['port'], d['shasecid'], d['pid'], d['temp_dir']
        except:
            raise Exception('Bad pattern from kastagent !\nExpected: %s !\n   Found: %s and %s' % (EXPECTED_KASTAGENT_OUTPUT, output.split('\n')[-2].strip(), output))

        if ret != 0:
            raise kastmenuxception.kastmenuSystemException('WebMenuDispatchHandler', selfMethod, 'Failed trying to launch Menu Name: {menufile} on Machine: {machine} For User: {user} ! RemoteException is:\n{subex}'.format(menufile=menufile, machine=machine, user=user, subex=output))
        printlog('WebMenuDispatchHandler:os_launchMenu', 'Kastagent Launched with Endpoints: %s' % output, request=None, level=80)

        return kastagent_port, kastagent_shasecid, kastagent_pid, ssh_pid


    @staticmethod
    async def launchAdminMenu(verbose=0):
        kastagent_dir = getInstallDir()
        kastweb_port = default.getKastConfs()['kastweb_port']
        kastagent_user = default.getKastConfs()['kastagent_user']

        kastweb_pid, kastweb_ssh_pid = await WebMenuDispatchHandler.os_launchMachine(machine='localhost', kastagent_dir=kastagent_dir, kastweb_port=kastweb_port, kastagent_user=kastagent_user, sudo_user=None, ssh_port=None, verbose=verbose)
        kastagent_port, kastagent_shasecid, kastagent_pid, kastagent_ssh_pid = await WebMenuDispatchHandler.os_launchAdminMenu(kastagent_dir=kastagent_dir, user=kastagent_user, verbose=verbose)

        return kastweb_pid, kastweb_ssh_pid, kastagent_port, kastagent_shasecid, kastagent_pid, kastagent_ssh_pid
    @staticmethod
    async def os_launchAdminMenu(kastagent_dir=None, user=None, verbose=0):
        selfMethod='os_launchAdminMenu'
        if kastagent_dir == '*home':kastagent_dir = '/home/%s/current'
        else:sanitize_path(class_exit='WebMenuDispatchHandler', method_exit=selfMethod, **{'kastagent_dir': kastagent_dir})
        kastagent = kastagent_dir + '/bin/kastagent'
        menufile = kastagent_dir + '/conf/kastadmin.xml'

        printlog('WebMenuDispatchHandler:os_launchAdminMenu', 'Launching Kastagent on Machine: localhost ...', request=None, level=80)
        cmd = '{kastagent} {menufile} -H localhost -l -O -v{verbose}'.format(kastagent=kastagent, menufile=menufile, verbose=str(verbose))
        verbose = 100
        ret, output, ssh_pid =  await sshcall('localhost', cmd, user=None, port=None, isLocal=True, isMenu=True, doTTY=True, verbose=verbose)

        # Expected content:
        EXPECTED_KASTAGENT_OUTPUT = """{"host":"{host}","port":{port},"pid":{pid},"shasecid":"{shasecid}", "temp_dir": "{temp_dir}"}
        Kastagent Launched finished."""
        try:
            import json as modjson
            spl = output.split('\n')
            json = spl[-2].strip()
            if json == '': raise Exception()
            d = modjson.loads(json)
            ## kastagent_host, kastagent_port, kastagent_pid, shasecid = d['host'], d['port'], d['pid'], d['shasecid']
            kastagent_port, kastagent_shasecid, kastagent_pid, temp_dir = d['port'], d['shasecid'], d['pid'], d['temp_dir']
        except:
            raise Exception('Bad pattern from kastagent !\nExpected: %s !\n   Found: %s and %s' % (EXPECTED_KASTAGENT_OUTPUT, output.split('\n')[-2].strip(), output))

        if ret != 0:
            raise kastmenuxception.kastmenuSystemException('WebMenuDispatchHandler', selfMethod, 'Failed trying to launch Menu Name: {menufile} on Machine: {machine} For User: {user} ! RemoteException is:\n{subex}'.format(menufile=menufile, machine='localhost', user=user, subex=output))
        printlog('WebMenuDispatchHandler:os_launchAdminMenu', 'Kastagent Launched with Endpoints: %s' % output, request=None, level=80)

        return kastagent_port, kastagent_shasecid, kastagent_pid, ssh_pid

    @staticmethod
    def os_authenticate(machine=None, user=None, ssh_user=None, ssh_port=22, password=None, request=None, verbose=0):
        from kwadlib.security.crypting import expect, NoneZeroRCException, TimeOutException
        sanitize_kastmenu(password)
        sanitize_hostorip(machine)
        sanitize(user)
        # Dont go outside if host is this host:
        if machine == KAST_HOST: host = 'localhost'
        else:host=machine
        if ssh_port == 22:SSH_PORT = ''
        else:SSH_PORT = ' -p %s' % str(ssh_port)

        printlog('WebMenuDispatchHandler:os_authenticate', 'Trying to authenticate user: %s on machine: %s...' % (user, machine), request=request)
        cmd = 'ssh  -o ConnectTimeout={ct} {ssh_port} {ssh_user}@{host} su {user} -c hostname'.format(ct=str(CONNECTION_TIMEOUT), ssh_port=SSH_PORT, ssh_user=ssh_user, user=user, host=host)
        printlog('WebMenuDispatchHandler:os_authenticate', 'Running command: %s.' % cmd, request=request, level=80)

        ret=0
        error = None
        try:
            data = expect(cmd, password, message="assword:", twice=False, verbose=verbose)
        except NoneZeroRCException as e:
            ret = 1
            error = e.data
        except TimeOutException as e:
            ret = 1
            error=TimeOutException
        except Exception as e:
            ret = 1
            error=e

        if error!=None:error = 'Error trying to check User: %s on Machine: %s ! SubException is: %s.' % (user, machine, str(error))

        printlog('WebMenuDispatchHandler:os_authenticate', 'User: %s authenticated on Machine: %s.' % (user, machine), request=request)
        return ret, error


class WebMenuUtilsHandler(BaseRemoteAuthHandler):

    # @tornado.gen.coroutine
    async def prepare(self):
        if 'Session-Part' not in self.request.headers:
            if self.request.uri == '/kastmenu/utils/genSessionPart':return
            message='Request should support the following header: Session-Part !'
            raise KastException(500, reason=message, log_message=message)
        session_part = self.request.headers['Session-Part']
        if session_part in (None, '', 'null') and self.request.uri == '/kastmenu/utils/genSessionPart':
            return

        await BaseRemoteAuthHandler.do_prepare(self, session_part)
        if self.flag_new_session:
            pass

        import json as modjson

        # Paremeters Management Get/Post: Query String and json field:
        # ------------------------------------------------------------
        if self.request.method.upper() == 'GET':
            m = 'Method: GET is not allowed !'
            raise KastException(405, reason=m, log_message=m, do_page=True)

        h = self.request.headers.get("Content-Type", None)
        if h == None:
            m = 'Unsupported Request: Should support Header: "Content-Type" !'
            raise KastException(500, reason=m, log_message=m, do_page=True)
        if not h.lower().startswith("application/json"):
            m = 'Unsupported Request Header: "Content-Type": Should be: "application/json" ! Found: %s.' % h
            raise KastException(500, reason=m, log_message=m, do_page=True)
        # self.json_args = json.loads(self.request.body)

        body = self.request.body
        body = body.strip()
        if len(body) != '':self.json_queries = modjson.loads(self.request.body)
        else:self.json_queries = None

        if self.json_queries != None: printlog('WebMenuUtilsHandler:prepare', 'Found the following json parameters: %s.' % str(self.json_queries), request=self.request)

    async def post(self, uri):
        self_funct = 'post'
        import json as modjson
        level = 50

        if uri == 'genSessionPart':
            session_part = genSessionPart()
            self.reply(modjson.dumps({'session-part': session_part}))
            return

        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        values = None
        validations = {'succeed': True, 'field': None, 'message': None}

        while True:
            if not tb_ses_session.load():break


            if uri == 'getSupportXAcceptMail':
                if 'machine' not in self.json_queries: break
                machine = self.json_queries['machine']
                try:
                    sanitize_hostorip(machine)
                except:break
                printlog('WebMenuUtilsHandler:post', 'Uri:getSupportXAcceptMail: Checking if Machine: %s AcceptMail Signin...' % machine, level=level, request=self.request)

                tb_machine = db.Machine(host=machine)
                if not tb_machine.load():break
                if tb_machine.sudo_user==None:break
                if not tb_machine.xaccept_mail:break
                values = {'xacceptmail':True}
                printlog('WebMenuUtilsHandler:post',  'Uri:getSupportXAcceptMail: Found Machine: %s AcceptMail Signin.' % machine, level=level, request=self.request)
                break


            elif uri == 'getPublicMachines':
                try:
                    printlog('WebMenuUtilsHandler:post', 'Uri:getPublicMachines: Checking for Public Machines...', level=level, request=self.request)
                    datas = getPublicMachines(request=self.request)
                    if datas == None or len(datas) == 0:break
                    values = datas
                except:
                    values = []
                break

            elif uri == 'getPublicUsers':
                try:
                    if 'machine' not in self.json_queries:break
                    ses_machine = self.json_queries['machine']
                    try:
                        sanitize(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'ses_machine': ses_machine})
                    except:break
                    printlog('WebMenuUtilsHandler:post', 'Uri:getPublicMachines: Checking for Public Machines...', request=self.request, level=level)

                    datas = getPublicUsers(machine = ses_machine, request=self.request)
                    if datas == None or len(datas) == 0:break
                    values = datas
                except:
                    values = []
                break

            elif uri == 'getUserMenus':
                try:
                    if 'machine' not in self.json_queries or self.json_queries['machine'] == None: break
                    ses_machine = self.json_queries['machine']
                    try:
                        sanitize_hostorip(ses_machine)
                    except:break
                    printlog('WebMenuUtilsHandler:post', "Uri:getUserMenus: Checking for User's Menus...", request=self.request, level=level)

                    if 'user' not in self.json_queries or self.json_queries['user'] == None:
                        done, dftuser, dftmenu = getMachineDefaultUserMenu(ses_machine, request=self.request)
                        if not done:
                            values = []
                        else:
                            values = [[dftmenu]]
                            validations['user'] = dftuser
                        break

                    ses_user = self.json_queries['user']

                    sanitize(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'ses_user': ses_user})
                    sanitize_hostorip(do_hide=False, class_exit='WebMenuDispatchHandler', method_exit=self_funct, **{'ses_machine': ses_machine})

                    tb_ses_user = db.ses_User(sessionid=self.field_ses_session, host=ses_machine, user=ses_user)
                    if not tb_ses_user.load():
                        break

                    datas = getUserMenus(user=ses_user, machine=ses_machine)
                    if datas == None or len(datas) == 0: break
                    values = datas
                except:
                    raise
                    values = []
                break

            elif uri == 'terminateMenu':
                printlog('WebMenuUtilsHandler:post', 'Uri:terminateMenu: Terminating current Menu...', request=self.request)
                tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
                if not tb_ses_menufile.load():return
                killHost(tb_ses_menufile.host, tb_ses_menufile.kastagent_ssh_pid)
                tb_ses_menufile.delete()
                break

            break

        go_pages_json = modjson.dumps({'values': values, 'validations': validations})

        # Return:
        # -------
        self.reply(go_pages_json)
        tb_ses_session.lastused = time.time()
        tb_ses_session.save()
        return


# ------------------------------------------------------------------------------------------------------ #
# PROXIES:                                                                                               #
# ------------------------------------------------------------------------------------------------------ #

class WebMenuProxyHandler(BaseRemoteAuthHandler):

    # @tornado.gen.coroutine
    async def prepare(self):
        if 'Session-Part' not in self.request.headers:
            message='Request should support the following header: Session-Part !'
            raise KastException(500, reason=message, log_message=message)
        session_part = self.request.headers['Session-Part']
        await BaseRemoteAuthHandler.do_prepare(self, session_part)
        if self.flag_new_session:
            pass

    async def get(self):
        # Try to load Current Session:
        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
        if not tb_ses_session.load() or not tb_ses_menufile.load():
            return
        tb_machine = db.Machine(host=tb_ses_menufile.host)
        tb_machine.load()
        host, port = tb_ses_menufile.host, tb_machine.kastweb_port

        # See: https://www.tornadoweb.org/en/stable/httpclient.html
        from tornado.httpclient import AsyncHTTPClient
        http_client = AsyncHTTPClient()
        try:
            """
            http_client = httpclient.AsyncHTTPClient() 
            http_client.fetch(url, method='POST', body=urllib.parse.urlencode(data))
            """

            # Removing parasite headers from browser:
            headers = self.request.headers
            if 'If-None-Match' in headers: del headers['If-None-Match']
            if 'If-Modified-Since' in headers: del headers['If-Modified-Since']

            url = 'https://%s:%s' % (host, port) + self.request.uri + '&port=%d&shasecid=%s' % (tb_ses_menufile.kastagent_port, tb_ses_menufile.kastagent_shasecid)
            printlog('WebMenuProxyHandler:', 'Opening WebMenuProxyHandler on this backend url: %s ...' % (url,), request=self.request, level=100)
            response = await http_client.fetch(url, connect_timeout=7, request_timeout=120,
                headers=headers, follow_redirects=False,
                ssl_options= PrepareHandler.getSSLClientCtx())
        except Exception as e:
            m="Error: %s" % e
            raise KastException(500, reason=m, log_message=m, do_page=True)

        keys = list(response.headers.keys())
        for header in keys:self.set_header(header, response.headers[header])

        self.write(response.body)


class OOWebMenuProxyWebSocketGet(BaseWebSocketHandler):

    async def prepare(self):
        # /kmenu/menu_websocket_get/session-part/JesNAtelv6SRSnzqtQaa6LgW+wEmRpw4kFf+OHAbv//N5DkIAyyq1Y3y2XDY+Xn
        session_part = self.request.uri.split('/session-part/')[-1]
        await BaseWebSocketHandler.do_prepare(self, session_part)
        if self.flag_new_session:
            pass

    async def open(self):
        from tornado.websocket import websocket_connect

        # Try to load Current Session:
        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
        if not tb_ses_session.load() or not tb_ses_menufile.load():
            self.close()
            return
        tb_machine = db.Machine(host=tb_ses_menufile.host)
        tb_machine.load()
        host, port = tb_ses_menufile.host, tb_machine.kastweb_port


        # Open:
        # -----
        url = 'wss://%s:%s/kmenu/oo_websocket_get' % (host, port) + '?port=%d&shasecid=%s' % (tb_ses_menufile.kastagent_port, tb_ses_menufile.kastagent_shasecid)
        printlog('OOWebMenuProxyWebSocketGet:', 'Opening WebMenu Output WebSocket on this backend url: %s ...' % (url,), request=self.request, level=100)
        wss_req = HTTPRequest(url,
            validate_cert=False, ssl_options=PrepareHandler.getSSLClientCtx())

        # ws = await websocket_connect(wss_req) support of: connect_timeout:
        import asyncio
        ws = await asyncio.wait_for(websocket_connect(wss_req), timeout=CONNECTION_TIMEOUT)

        ws.on_message = self.on_message
        ws.on_close = self.on_close

        printlog("Main", "OOMenuWebSocket opened", request=self.request)

    def on_message(self, message):
        try:self.write_message(message.replace('<', '&lt;').replace('>', '&gt;'))
        except:
            raise

    def on_close(self):
        # Delete Current Session:
        tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
        if tb_ses_menufile.load():
            killHost(tb_ses_menufile.host, tb_ses_menufile.kastagent_ssh_pid)
            tb_ses_menufile.delete()

        self.close()

class MenuWebMenuProxyWebSocketGet(BaseWebSocketHandler):

    async def prepare(self):
        # /kmenu/menu_websocket_get/session-part/JesNAtelv6SRSnzqtQaa6LgW+wEmRpw4kFf+OHAbv//N5DkIAyyq1Y3y2XDY+Xn
        session_part = self.request.uri.split('/session-part/')[-1]
        await BaseWebSocketHandler.do_prepare(self, session_part)
        if self.flag_new_session:
            pass

    async def open(self):
        from tornado.websocket import websocket_connect

        # Try to load Current Session:
        tb_ses_session = db.ses_Session(sessionid=self.field_ses_session)
        tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
        if not tb_ses_session.load() or not tb_ses_menufile.load():
            self.close()
            return

        tb_machine = db.Machine(host=tb_ses_menufile.host)
        tb_machine.load()
        host, port = tb_ses_menufile.host, tb_machine.kastweb_port

        # Open:
        # -----
        url = 'wss://%s:%s/kmenu/menu_websocket_get' % (host, port) + '?port=%d&shasecid=%s' % (tb_ses_menufile.kastagent_port, tb_ses_menufile.kastagent_shasecid)
        printlog('MenuWebMenuProxyWebSocketGet:', 'Opening WebMenu WebSocket on this backend url: %s ...' % (url,), request=self.request, level=100)
        wss_req = HTTPRequest(url,
            validate_cert=False, ssl_options=PrepareHandler.getSSLClientCtx())

        # ws = await websocket_connect(wss_req) support of: connect_timeout:
        import asyncio
        ws = await asyncio.wait_for(websocket_connect(wss_req), timeout=CONNECTION_TIMEOUT)

        ws.on_message = self.on_message
        ws.on_close = self.on_close

        printlog("Main", "MenuWebSocket opened", request=self.request)


    def on_message(self, message):
        try:self.write_message(message)
        except:
            raise

    def on_close(self):
        # Delete Current Session:
        tb_ses_menufile = db.ses_MenuFile(sessionid=self.field_ses_session)
        if tb_ses_menufile.load():
            killHost(tb_ses_menufile.host, tb_ses_menufile.kastagent_ssh_pid)
            tb_ses_menufile.delete()

        self.close()




