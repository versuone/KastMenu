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


# 001: 2023/09/05 : Replacing JQuery bu Bootsrap5
# Html5 Fetch is far slower then JQuery Ajax, so we can no more loop on get.
# oo WebSocket is renamed oo_websocket_get
# menu_websocket_get is Added to replace all get()

"""
# 20230905: 001: Replacing JQuery bu Bootsrap5
# Html5 Fetch is far slower then JQuery Ajax, so we can no more loop on get.
# oo WebSocket is renamed OOWebSocketGet
# MenuWebSocketGet is Added to replace all get()
"""

import tornado.web
import tornado.websocket
import tornado.gen
from kwadlib import kastmenup

MENU_WEB_FACADE = None
WEB_FACADE_KWS = None
IO_LOOP = None


def initWebFacade(menu_file, is_listening=True, show_shortcut=False,
        log=False, log_output=False, log_dir=None, log_rotate=None,
        temp_dir=None, keep_temp_dir=False,
        aliases= None, tmpl_kws={},
        record=False, show=False, batch=None, go=None, go_menu=None, pause=None, debug = False, verbose = 0
    ):
    global WEB_FACADE_KWS
    WEB_FACADE_KWS = {'menu_file': menu_file, 'is_listening': is_listening, 'show_shortcut': show_shortcut,
        'log': log, 'log_output': log_output, 'log_dir': log_dir, 'log_rotate': log_rotate,
        'temp_dir': temp_dir, 'keep_temp_dir': keep_temp_dir,
        'aliases': aliases, 'tmpl_kws':tmpl_kws,
        'record': record, 'showResultingSourceOnly': show, 'batch': batch, 'go': go, 'go_menu': go_menu, 'pause': pause, 'debug': debug, 'verbose': verbose,
    }

"""
MODULE_KASTWEBP.initWebFacade(path.normpath(SAMPLE), is_listening=True,
log=True, log_output=True, log_dir=KASTWEB_TEMP_DIR + '/log',
temp_dir = KASTWEB_TEMP_DIR, keep_temp_dir = options.keep_temp_dir,
aliases=aliases, tmpl_kws={},
record = False, go = None, debug = False)
"""
def startWebFacade():
    import time
    global MENU_WEB_FACADE

    kastmenu = True
    if kastmenu:
        w = kastmenup.digest(**WEB_FACADE_KWS)
    else:
        # Test kupd:
        from kwadlib import kupdp
        file_source = None
        file_desc = None
        file_rest = None
        kact = 'middleware§jss.ssl.by.kwad'
        kact = None
        """ e.g.:
        /opt/kastmenu/current/bin/kupd   --kact middleware§jss.ssl.by.kwad -v 300 --console
        /opt/kastmenu/current/bin/kupd --kcac mycac.xml -o -v 300  --noclear  --debug
        /opt/kastmenu/current/bin/kupd --kcac mymanage.xml -o -v 300  --noclear  --debug
        """
        kcac = '/opt/kastmenu/current/samples/softclasses/mycac.xml'
        # debug=WEB_FACADE_KWS['debug']
        # verbose=WEB_FACADE_KWS['verbose'],
        w = kupdp.call([], debug=True, HELP=False, console=True, is_listening=True,
            update=False, create=False, force=False, remove=False,
            kact=kact, kcac=kcac, file_source=file_source,
            attr_separator=None, node_separator=None, text_separator=None, picpath_attr_separator=None, picpath_text_separator=None,
            oprint=False, oprint_json=False, info=None, web=False, plugins=False, aplugin=None,
            keep_temp_dir=WEB_FACADE_KWS['keep_temp_dir'], detail=False, show_shortcut=WEB_FACADE_KWS['show_shortcut'],
            # -- advanced options:
            overwrite=False, to_file=None, no_dft=False,
            file_desc=file_desc, file_rest=file_rest,
            cap_sensitive=True,
            xforce=False, dont_show_files=False, dont_show_new_softclass=False,
            # -- advanced Menu options: A005
            batch=None, pause=None, noclear=True,
            port=None, secid=None, follow_menu=False,
            log=WEB_FACADE_KWS['log'], log_dir=WEB_FACADE_KWS['log_dir'], log_rotate=WEB_FACADE_KWS['log_rotate'], log_output=WEB_FACADE_KWS['log_output'],
            record=WEB_FACADE_KWS['record'], go=WEB_FACADE_KWS['go'], go_menu=WEB_FACADE_KWS['go_menu'],
            # kwad_generic_options:
            # -- kact extended generic options:
            cattrs=None, dattrs=None, cacdir=None, crst=None, tmpl_kws=WEB_FACADE_KWS['tmpl_kws'],
            verbose=300)

    MENU_WEB_FACADE = w

    time.sleep(3)  # wait for the process be launched.



class MainPageHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.query_arguments = {k:self.request.query_arguments[k][0] for k in self.request.query_arguments}
        for k in self.query_arguments:
            if self.query_arguments[k] == '':self.query_arguments[k] = None

    def get(self):
        operation = self.query_arguments['operation'].decode("utf-8")
        if 'value' in self.query_arguments: value = self.query_arguments['value'].decode("utf-8")
        else: value = None

        datas = None
        # D001: if operation == 'get': datas = getattr(MENU_WEB_FACADE, 'get')(smartwait=True, nowait=False)
        if operation in ('put', 'puts'):
            getattr(MENU_WEB_FACADE, operation)(value)
            return


# @tornado.asyncio.coroutine
@tornado.gen.coroutine
def get_input():

    r = yield IO_LOOP.run_in_executor(None, MENU_WEB_FACADE.getCommandOutput)  # None == use default executor.
    raise tornado.gen.Return(r)



class OOWebSocketGet(tornado.websocket.WebSocketHandler):

    @tornado.gen.coroutine
    def open(self):
        print("OOWebSocket opened")

        while True:
            message = yield IO_LOOP.run_in_executor(None, MENU_WEB_FACADE.getCommandOutput)
            self.write_message(message)

    def on_message(self, message): # Not Supported
        raise

    def on_close(self):
        print("OOWebSocket closed")


class MenuWebSocketGet(tornado.websocket.WebSocketHandler):

    @tornado.gen.coroutine
    def open(self):
        import json
        print("MenuWebSocket opened")

        while True:
            datas = yield IO_LOOP.run_in_executor(None, getLock)
            if datas == None:continue

            self.write_message(json.dumps([datas]))

    def on_message(self, message): # Not Supported
        raise

    def on_close(self):
        print("MenuWebSocket closed")


def getLock():
    return getattr(MENU_WEB_FACADE, 'get')(nowait=False, smartwait=False, lock=True)

def genKastwebKeys(fqdn=None, force=False):
    """
    This will generate kastweb ssl keys:
    ------------------------------------
    """
    self_funct='genKastwebKeys'
    from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
    from kwadlib.security.crypting import sanitize_hostorip
    from kwadlib import default
    from os import path, remove
    import re

    etc_keys = path.split(default.getKastConfs()['kastweb_server_crt'])[-2]
    if not etc_keys.startswith('/'):etc_keys = default.KAST_CONF_DIR + '/' + etc_keys

    temp_dir = default.getUserKastTempDir()
    passfile = temp_dir + '/fpass.txt'

    envs = {
        'ETC_KEYS': etc_keys,
        'KAST_DIR': default.getInstallDir(),
        'PASSWORD': getPasswordLocal('4c23615cf2b9986b1e47dc28e64c89da9b4d'), # todo: will be replaced by random value by BUILD:::
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

    with open(passfile, 'w') as f:
        f.write(getPasswordLocal('4c23615cf2b9986b1e47dc28e64c89da9b4d'))

    cmd = default.getInstallDir() + '/core/kwadlib/security/sslkeygen/sslkeygen_kastweb.sh'
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
        # kastweb_server_key:
        src = re.sub(r"kastweb_server_key\s*=\s*.*", 'kastweb_server_key = ' + etc_keys + '/' + kast_host_new + '.key', src)
        # kastweb_server_crt:
        src = re.sub(r"kastweb_server_crt\s*=\s*.*", 'kastweb_server_crt = ' + etc_keys + '/' + kast_host_new + '.crt', src)

        with open(default.KAST_CONF, 'w') as fwrite:
            fwrite.write(src)

def getPasswordLocal(ctxkastweb):
    from kwadlib.security.crypting import sha256
    CTX_KASTWEB = '4c23615cf2b9986b1e47dc28e64c89da9b4d'  # todo: will be replaced by random value by BUILD:::
    if ctxkastweb != CTX_KASTWEB:raise Exception('encryptLocal is not callable in this context !')

    return sha256(CTX_KASTWEB + '17380277749631') # 17380277749631 is fixed can be anything