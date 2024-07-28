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



##########
## Main ##
##########

SELF_MODULE = 'kastserver'
INSTALL_DIR = None
WEB_TEMP_DIR = None
MODULE_KASTSERVERP = None
IS_EXITING = False

# - Protect everything created:
from os import umask
oldmask = umask(0o077)



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

from signal import signal, SIGTSTP, SIGINT, SIGHUP, SIGTERM, SIGQUIT
def signal_handler(signal_received, frame):
    global IS_EXITING
    if IS_EXITING:return
    IS_EXITING = True

    MODULE_KASTSERVERP.exitAll()

    import os
    import psutil
    this_pid = os.getpid()
    this = psutil.Process(this_pid)
    for child in this.children(recursive=True):  # or parent.children() for recursive=False
        child.kill()

    MODULE_KASTSERVERP.IO_LOOP.current().stop()

    import sys
    sys.stdout = None
    sys.exit(0)


def usage():
    return """ e.g.:
     sudo -u kastserver /opt/kastmenu/current/bin/kastserver -v100
"""

def main(args):
    self_funct='main'
    import optparse
    global VERBOSE, MODULE_KASTSERVERP
    VERBOSE=None

    parser = optparse.OptionParser(usage())
    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level a number. e.g.: -v10. (beware >= 200 will cause some raise exceptions not be caught)")
    parser.add_option("--temp_dir", dest="temp_dir", help="Temporary.")
    parser.add_option("--keep_temp_dir", dest="keep_temp_dir", action="store_true", help="This will keep the temporary dir ! Allowing to see all the intermediate state will parsing the file. e.g: from mako, jinja, yaml, hcl to xml.\n Beware Parsing is usually done in memory, keeping the resulting files into temp_dir could be a security breach.")

    (options, args) = parser.parse_args(args=args)
    VERBOSE=options.verbose
    
    try:
        from os import path, makedirs
        from kwadlib import kastservers
        MODULE_KASTSERVERP = kastservers.MODULE_KASTSERVERP

        kastservers.call(keep_temp_dir=options.keep_temp_dir, temp_dir=options.temp_dir, verbose=options.verbose)
        
    except Exception as e:
        
        if VERBOSE==None:
            try:VERBOSE=int(options.verbose)
            except:VERBOSE=0
        if VERBOSE>=10:raise

        import sys
        if not hasattr(e, 'short1') or not hasattr(e, 'short2'):
            message=e.__class__.__name__ + ': ' + str(e)
        elif VERBOSE<5:
            message=e.short1()
        elif VERBOSE>=5:
            message=e.short2()
        sys.stderr.write(message + '\n')
        sys.exit(2)
        
        
if __name__ == '__main__':
    from os import path
    import utils
    import sys

    signal(SIGTSTP, signal_handler)
    signal(SIGINT, signal_handler)
    signal(SIGHUP, signal_handler)
    signal(SIGTERM, signal_handler)
    signal(SIGQUIT, signal_handler)

    INSTALL_DIR = utils.getInstallDir()
    
    ## Set paths
    for _path in ('core',):
        _path=path.normpath(INSTALL_DIR + '/' + _path)
        if not _path in sys.path:sys.path.append(_path)

    storepid()

    main(sys.argv[1:])