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



##########
## Main ##
##########

SELF_MODULE = 'kastweb'
INSTALL_DIR = None
KASTWEB_TEMP_DIR = None
IS_QUITING = False

from kwadlib import kastwebp
MODULE_KASTWEBP = kastwebp

def call(menufile, host=None, debug=None, record=None, show=None, log=None, log_dir=None, log_rotate=None, log_output=None, show_shortcut=None, batch=None, go=None, go_menu=None, pause=None, tmpl_kws=None, temp_dir=None, keep_temp_dir=False, verbose=0):
    self_funct='main'
    from kwadlib.security.crypting import sanitize_hostorip
    from kwadlib import kastmenuxception
    from kwadlib import default
    from os import path
    global VERBOSE, KASTWEB_TEMP_DIR
    VERBOSE=None

    # kastweb_server_crt:
    KASTWEB_SERVER_CRT = default.getKastConfs()['kastweb_server_crt']
    if not KASTWEB_SERVER_CRT.startswith('/'):KASTWEB_SERVER_CRT = default.KAST_CONF_DIR + '/' + KASTWEB_SERVER_CRT
    # kastweb_server_key:
    KASTWEB_SERVER_KEY = default.getKastConfs()['kastweb_server_key']
    if not KASTWEB_SERVER_KEY.startswith('/'):KASTWEB_SERVER_KEY = default.KAST_CONF_DIR + '/' + KASTWEB_SERVER_KEY
    # kastweb_caclients:
    KASTWEB_CLIENTS_CACLIENTS = default.getKastConfs()['kastweb_caclients']
    if not KASTWEB_CLIENTS_CACLIENTS.startswith('/'):KASTWEB_CLIENTS_CACLIENTS = default.KAST_CONF_DIR + '/' + KASTWEB_CLIENTS_CACLIENTS

    from kwadlib.tools import RedirectStd
    import sys, datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    RedirectStd(stdout=sys.stdout, stderr=sys.stderr, nostdout=False, nostderr=False, log_dir=default.getKastTempDir(), log_file='kastmenu-%s.log' % ts)
    VERBOSE=verbose


    if not path.isfile(menufile): raise kastmenuxception.kastmenuSystemException('main', 'main', 'File: %s should Exist !' % menufile)

    import tornado.ioloop, tornado.web
    from os import path, makedirs
    from kwadlib import tools

    kast_attrs = tools.getKastConfs()

    ## aliases:
    aliases = dict(kast_attrs)

    ## Retreives temp_dir:
    if temp_dir != None:KASTWEB_TEMP_DIR = temp_dir
    else:
        current_user = default.getUser()
        if current_user == 'root':home = '/root'
        else:home = '/home/' + current_user
        KASTWEB_TEMP_DIR = '/%s/.kastmenu/temp/' % home + tools.genUid()
        if not path.isdir(KASTWEB_TEMP_DIR):makedirs(KASTWEB_TEMP_DIR)

    tools.verbose(SELF_MODULE + ': kastweb Temporary dir is: ' + KASTWEB_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='', logFile=VERBOSE)

    MODULE_KASTWEBP.initWebFacade(menufile, is_listening=True, show_shortcut=show_shortcut,
        log=log, log_output=log_output, log_dir=log_dir, log_rotate=log_rotate,
        temp_dir = KASTWEB_TEMP_DIR, keep_temp_dir = keep_temp_dir,
        aliases=aliases, tmpl_kws=tmpl_kws,
        record = record, show=show, batch = batch, go = go, go_menu = go_menu, pause = pause, debug = debug, verbose = verbose)
    MODULE_KASTWEBP.startWebFacade()

    HOST = default.getKastConfs()['kast_host']
    PORT = MODULE_KASTWEBP.MENU_WEB_FACADE.getPort()
    TEMP_DIR = MODULE_KASTWEBP.MENU_WEB_FACADE.getTempDir()
    SHASECID = MODULE_KASTWEBP.MENU_WEB_FACADE.getShaSecid()


    # Local KManager:
    # ---------------
    # a) Ssl Management:
    import ssl
    # See: https://www.tornadoweb.org/en/stable/httpserver.html
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(certfile=KASTWEB_SERVER_CRT, keyfile=KASTWEB_SERVER_KEY, password=MODULE_KASTWEBP.getPasswordLocal('4c23615cf2b9986b1e47dc28e64c89da9b4d'))

    ssl_ctx.load_verify_locations(capath=KASTWEB_CLIENTS_CACLIENTS)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    settings = {}
    # http://127.0.0.1:8888/webmenu/webmenu.html
    application = tornado.web.Application([
        (r"/kmenu/do_menu", MODULE_KASTWEBP.MainPageHandler),
        (r"/kmenu/oo_websocket_get", MODULE_KASTWEBP.OOWebSocketGet),
        (r"/kmenu/menu_websocket_get", MODULE_KASTWEBP.MenuWebSocketGet)
    ], **settings)

    from os import getpid
    if host != None:
        sanitize_hostorip(do_hide=False, class_exit='Main', method_exit=self_funct, **{'host': host})
        host = host
    else:host = HOST

    if host == 'localhost': # if host is localhost grab a new port not to conflict with the kdealer port:
        PORT = default.getFreePortOnLocalHost()

    # The following two lines are Expected by kastserver:
    print("""Launching Kastweb on host/port {host}:{port} with pid: {pid}
{{"host":"{host}","port":{port},"pid":{pid},"shasecid":"{shasecid}", "temp_dir": "{temp_dir}"}}
Kastweb Launched finished.""".format(host=host, port=PORT, pid=getpid(), shasecid=SHASECID, temp_dir=TEMP_DIR))

    http_server = application.listen(PORT, address=host, ssl_options=ssl_ctx)
    MODULE_KASTWEBP.IO_LOOP = tornado.ioloop.IOLoop.current()
    MODULE_KASTWEBP.IO_LOOP.start()
