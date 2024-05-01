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
MODULE_KASTWEBP = None
IS_QUITING = False


from signal import signal, SIGINT, SIGHUP, SIGTERM, SIGQUIT
def signal_handler(signal_received, frame):
    global IS_QUITING
    if IS_QUITING:return
    IS_QUITING = True
    import os
    import psutil

    if MODULE_KASTWEBP.MENU_WEB_FACADE != None: MODULE_KASTWEBP.MENU_WEB_FACADE.stop()
    if MODULE_KASTWEBP.IO_LOOP!=None:MODULE_KASTWEBP.IO_LOOP.current().stop()

    parent_pid = os.getpid()
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):  # or parent.children() for recursive=False
        child.kill()
    parent.kill()


def usage():
    return ''

def main(args):
    self_funct='main'
    import optparse
    global VERBOSE, KASTWEB_TEMP_DIR, MODULE_KASTWEBP
    VERBOSE=None
    from kwadlib import kastmenuxception
    from kwadlib import kastwebs
    from kwadlib import default

    MODULE_KASTWEBP = kastwebs.MODULE_KASTWEBP

    parser = optparse.OptionParser(usage())
    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level a number. e.g.: -v10. (beware >= 200 will cause some raise exceptions not be caught)")
    parser.add_option("-H", "--host", dest="host", help="Optional host, By default take it from %s." % default.KAST_CONF)
    parser.add_option("--temp_dir", dest="temp_dir", help="Temporary.")
    parser.add_option("--keep_temp_dir", dest="keep_temp_dir", action="store_true", help="This will keep the temporary dir ! Allowing to see all the intermediate state will parsing the file. e.g: from mako, jinja, yaml, hcl to xml.\n Beware Parsing is usually done in memory, keeping the resulting files into temp_dir could be a security breach.")

    parser.add_option("--debug", dest="debug", action="store_true", default=False, help="Raises and Fails at first issue.")
    parser.add_option("-r", "--record", dest="record", action="store_true", default=False, help="Will record all entries to a string ready to use for remote execution mode.")
    parser.add_option("--show", dest="show", action="store_true", default=False, help="Apimenu (now supports Mako www.makotemplates.org and palletsprojects.com/p/jinja) will do nothing but show the resulting xml file after mako|jinja2 parsing if your menu file ends with .mako or .jinja (e.g. menu.xml.mako instead of menu.xml).")
    parser.add_option("--tmpl_kws", dest="tmpl_kws", help="(optional) A set of parameters (a CoolTyped dict) to feed mako or jinja with, when the file argument rather than beeing an .xml file is a .xml.mako file or a  .xml.jinja file.")
    parser.add_option("-l", "--log", action="store_true", default=False, dest="log", help="Do log console ?")
    parser.add_option("-L", "--log_dir", dest="log_dir", help="The log directory path. Required when log (-l) is provided.")
    parser.add_option("-R", "--log_rotate", dest="log_rotate", type=int, default=20, help="(Default 20) How many log files to keep into the log directory.")
    parser.add_option("-O", "--log_output", action="store_true", default=False, dest="log_output", help="By default system commands output is not retrieved into the log, this option allows it.")
    parser.add_option("--show_shortcut", dest="show_shortcut", action="store_true", default=False, help="Only usefull for kupd showing SoftClasses as Menu.\n"
                                                                                                        "When kupd is called with option: show_shortcut, It will show At the same menu's level sublink for sub menus.")
    # -- advanced Menu options:
    og = optparse.OptionGroup(parser, 'Advanced Menu options', description='')
    parser.add_option_group(og)
    og.add_option("-b", "--batch", dest="batch", help="This option requires a value:<mpath>.\n\
        mpath is the value for the menu, e.g.: path:1.abc.2.3.\n\
        The menu path syntax is <option number|option name>.[option number|option name>].")
    og.add_option("-g", "--go", dest="go", help='Same as --batch (-b) but will left the Menu at interactive mode !')
    og.add_option("-G", "--GO", dest="go_menu", help='Same as --go (-g) but will disallow system commands !')
    og.add_option("-p", "--pause", dest="pause", type=int, help="Works in conjunction with the --batch (-b) option. Pause every screen for the amount of seconds provided.")

    (options, args) = parser.parse_args(args=args)
    VERBOSE=options.verbose

    if len(args) == 0:raise kastmenuxception.kastmenuSystemException('main', 'main', 'The menufile argument is required !')
    if len(args) != 1:raise kastmenuxception.kastmenuSystemException('main', 'main', 'Only one argument is supported: the menufile argument is required !')
    menufile = args[0]
    from os import path
    menufile = path.normpath(menufile)
    if not path.isfile(menufile): raise kastmenuxception.kastmenuSystemException('main', 'main', 'File: %s should Exist !' % menufile)
    
    try:   
        kastwebs.call(menufile, host=options.host, debug=options.debug, record=options.record, show=options.show, log=options.log, log_dir=options.log_dir, log_rotate=options.log_rotate, log_output=options.log_output, show_shortcut=options.show_shortcut, batch=options.batch, go=options.go, go_menu=options.go_menu, pause=options.pause, tmpl_kws=options.tmpl_kws, temp_dir=options.temp_dir, keep_temp_dir=options.keep_temp_dir, verbose=options.verbose)

    except Exception as e:

        if VERBOSE==None:
            try:VERBOSE=int(options.verbose)
            except:VERBOSE=0
        if VERBOSE>200:raise

        import sys
        if not hasattr(e, 'short1') or not hasattr(e, 'short2'):
            message=e.__class__.__name__ + ': ' + str(e)
        elif VERBOSE<=100:
            message=e.short1()
        elif VERBOSE>100:
            message=e.short2()
        sys.stderr.write(message + '\n')
        sys.exit(2)


if __name__ == '__main__':
    from os import path
    import utils
    import sys

    signal(SIGINT, signal_handler)
    signal(SIGHUP, signal_handler)
    signal(SIGTERM, signal_handler)
    signal(SIGQUIT, signal_handler)

    INSTALL_DIR = utils.getInstallDir()

    ## Set paths
    for _path in ('core',):
        _path=path.normpath(INSTALL_DIR + '/' + _path)
        if not _path in sys.path:sys.path.append(_path)

    main(sys.argv[1:])