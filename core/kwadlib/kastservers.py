#!/usr/bin/python3
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

##########
## Main ##
##########

SELF_MODULE = 'kastserver'
INSTALL_DIR = None
WEB_TEMP_DIR = None
IS_EXITING = False

# - Protect everything created:
from os import umask
oldmask = umask(0o077)

from kwadlib.tools import getKastConfs

KAST_CONFS = getKastConfs()
KASTSERVER_LOG='kastserver.log'
KAST_LOG_DIR = KAST_CONFS['log_dir']
SERVER_CRT = KAST_CONFS['server_crt']
SERVER_KEY = KAST_CONFS['server_key']
from kwadlib import kastserverp
MODULE_KASTSERVERP = kastserverp

import secrets

def storepid():
    from subprocess import check_output
    from os import path, makedirs, getpid
    dir_run = "/var/log/kastmenu"
    if not path.isdir(dir_run):
        makedirs(dir_run)
        check_output("chown -R  kastmenu:kastmenu %s" % dir_run)

    with open("%s/kast.pid" % dir_run, 'w') as f:
        f.write(str(getpid()))


def printlog(fromf, message, level=0):
    from kwadlib.tools import printlog as plog
    plog(fromf, message, level=level, verbose=VERBOSE)


def call(keep_temp_dir=False, temp_dir=None, verbose=0):
    self_funct='main'
    global VERBOSE, WEB_TEMP_DIR
    VERBOSE=None
    from kwadlib.tools import RedirectStd
    import sys
    RedirectStd(stdout=sys.stdout, stderr=sys.stderr, nostdout=False, nostderr=False, log_dir=KAST_LOG_DIR, log_file=KASTSERVER_LOG)

    VERBOSE=verbose

    from os import path, makedirs
    from kwadlib import tools
    import tornado.ioloop, tornado.web

    kastserverp.setVerbose(VERBOSE)

    ## Retreives temp_dir:
    if temp_dir != None:WEB_TEMP_DIR = temp_dir
    else:
        WEB_TEMP_DIR = tools.getTempDir() + '/web/' + tools.genUid()
        if not path.isdir(WEB_TEMP_DIR):makedirs(WEB_TEMP_DIR)

    tools.verbose(SELF_MODULE + ': web Temporary dir is: ' + WEB_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='', logFile=VERBOSE)


    # Remote KManager:
    # ---------------
    # a) Ssl Management:
    import ssl
    # See: https://www.tornadoweb.org/en/stable/httpserver.html
    ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    # ssl_ctx = ssl.create_default_context()

    # Retreive SSL Pass:
    from kwadlib.security.crypting import decryptLocal
    file = '/etc/kastmenu/keys/fpass.dat'
    with open(file) as f:
        password = f.read()
        password = decryptLocal(password.strip())


    ssl_ctx.load_cert_chain(certfile=SERVER_CRT, keyfile=SERVER_KEY, password=password)
    ssl_ctx.check_hostname = False
    # ssl_ctx.verify_mode = ssl.CERT_NONE
    # ssl_ctx.hostname_checks_common_name = False

    ## ssl_ctx.load_verify_locations(capath=CLIENTS_CA_CRT)
    """ Info:
        -----
    Supported by: ${ETC_KEYS}/caclients (c_rehash already run by: kwad-5.5.6/core/kwadlib/security/sslkeygen/sslkeygen_user.sh)
    See: 
    https://forum.opnsense.org/index.php?topic=6679.0
    https://pythontic.com/ssl/sslcontext/load_verify_locations
    https://pythontic.com/ssl/sslcontext/verify_mode
    https://www.peterspython.com/en/blog/using-python-s-pyopenssl-to-verify-ssl-certificates-downloaded-from-a-host
    See: ls -ltr /etc/ssl/certs
    total 548
    lrwxrwxrwx 1 root root     59 déc.   9 17:12 1636090b.0 -> Hellenic_Academic_and
    _Research_Institutions_RootCA_2011.pem
    lrwxrwxrwx 1 root root     27 déc.   9 17:12 14bc7599.0 -> emSign_ECC_Root_CA_-_G3.pem
    """
    ## ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.verify_mode = ssl.CERT_OPTIONAL


    # b) Statics
    settings = {
        "static_path": path.join(tools.getInstallDir(), "core/kwadlib/web"),
    }
    # c) Application:
    application = tornado.web.Application([
        #-> Root is Login:

        # (r"/", kastserverp.LoginHandler),
        tornado.web.url(r"/", tornado.web.RedirectHandler, {"url": kastserverp.DEFAULT_PAGE, "permanent": False}),
        tornado.web.url(r"/kastmenu", tornado.web.RedirectHandler, {"url": kastserverp.DEFAULT_PAGE, "permanent": False}),
        tornado.web.url(r"/kastmenu/machine", tornado.web.RedirectHandler, {"url": kastserverp.DEFAULT_PAGE, "permanent": False}),
        tornado.web.url(r"/kastmenu/admin", tornado.web.RedirectHandler, {"url": kastserverp.DEFAULT_PAGE, "permanent": False}),
        tornado.web.url(r"/kastmenu/index.html", tornado.web.RedirectHandler, {"url": kastserverp.DEFAULT_PAGE, "permanent": False}),
        #-> webui:
        # (r"/webui/(.*)", kastserverp.KStaticFileHandler, dict(path=settings['static_path'] + '/webui')),
        (r"/kastmenu/machine/(.*)", kastserverp.WebMenuMachineHandler),
        (r"/kastmenu/admin/(.*)", kastserverp.WebMenuAdminHandler),
        (r"/kastmenu/dispatch/(.*)", kastserverp.WebMenuDispatchHandler),
        (r"/kastmenu/utils/(.*)", kastserverp.WebMenuUtilsHandler),
        # A001:
        (r"/kastmenu/cvdemo/(%s)" % kastserverp.CVDEMO, kastserverp.WebMenuCVDEMO),
        (r"/kastmenu/cvdemo/(get-view-token)", kastserverp.WebMenuCVDEMO),
        #+tard: (r"/kmenu/dispatch", kastserverp.WebDispatch),
        (r"/kastmenu/(.*)", kastserverp.KStaticFileHandler, dict(path=settings['static_path'] + '/kastmenu')),
        #-> webmenu Proxy:
        (r"/kmenu/do_menu", kastserverp.WebMenuProxyHandler),
        (r"/kmenu/oo_websocket_get/.*", kastserverp.OOWebMenuProxyWebSocketGet),
        (r"/kmenu/menu_websocket_get/.*", kastserverp.MenuWebMenuProxyWebSocketGet),
        #-> Frameworks:
        (r"/cdn_icons/(.*)", kastserverp.KStaticFileHandler, dict(path=settings['static_path'] + '/cdn_icons')),
        (r"/bootstrap5/(.*)", kastserverp.KStaticFileHandler, dict(path=settings['static_path'] + '/bootstrap5')),
        # A001:
        (r"/kastmenu/cvdemo/new-%s.html" % kastserverp.CVDEMO, kastserverp.KStaticFileHandler, dict(path=settings['static_path'] + '/cvdemo')),
        (r"/kastmenu/cvdemo/graph.jpg", kastserverp.KStaticFileHandler, dict(path=settings['static_path'] + '/cvdemo')),
    ], cookie_secret=secrets.token_hex(), **settings)
    import socket
    printlog('Main', 'Launching KManager and KMenu WebServer ! on %s(%s):%s' % (kastserverp.KAST_HOST,  socket.gethostbyname(kastserverp.KAST_HOST), kastserverp.KAST_PORT))
    # With listen extra arg goes to: server = HTTPServer(self, ssl_options=ssl_ctx)

    httpServer = application.listen(port=kastserverp.KAST_PORT, address=kastserverp.KAST_HOST, ssl_options=ssl_ctx)

    """ Must be Isolated into a separated process !! """

    kastserverp.IO_LOOP = tornado.ioloop.IOLoop.current()
    kastserverp.IO_LOOP.start()


    """ MultiProcess e.g.:
https://www.tornadoweb.org/en/stable/httpserver.html

sockets = bind_sockets(8888)
tornado.process.fork_processes(0)
async def post_fork_main():
    server = HTTPServer()
    server.add_sockets(sockets)
    await asyncio.Event().wait()
asyncio.run(post_fork_main())
"""
