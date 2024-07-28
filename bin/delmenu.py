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


SELF_MODULE = 'addkuser'
KINIT_TEMP_DIR = None


##########
## Main ##
##########

def usage():
    return """
delmenu -m myhost -u myuser
    """


def main(args):
    self_funct = 'main'
    from kwadlib.security.crypting import sanitize_kastmenu
    from kwadlib import tools, xception
    from kwadlib import default
    from kwadlib import db
    db.initdb()
    import optparse
    global KINIT_TEMP_DIR
    KINIT_TEMP_DIR = default.getUserKastTempDir()
    global VERBOSE
    VERBOSE = None

    parser = optparse.OptionParser(usage())
    parser.add_option('-v', "--verbose", dest="verbose", type=int, default=0, help="Verbose level, int value.")
    parser.add_option('-m', "--machine", dest="machine", help="Machine Host. Dont provide IP but FQDN as possible.")
    parser.add_option('-u', "--user", dest="user", help="User name")
    parser.add_option('-n', "--name", dest="name", help="This is a logical name for the menu file for this user on the machine !")
    parser.add_option('-p', "--path", dest="path", help="This is the Path for the menu file on the machine !")

    (options, args) = parser.parse_args(args=args)
    VERBOSE = options.verbose

    try:
        if len(args) > 0:
            print(usage())
            raise xception.kwadSystemException('Main', self_funct, 'Arguments: %s are not supported but options yes !' % str(args))

        kwad_attrs = tools.getKastConfs()
        tools.verbose(SELF_MODULE + ': Temporary dir is: ' + KINIT_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='',
                      logFile=VERBOSE)

        if options.machine == None: raise xception.kwadSystemException('Main', self_funct, 'Option --machine (-m) is required !')
        if options.user == None: raise xception.kwadSystemException('Main', self_funct, 'Option --user (-u) is required !')
        if options.path == None: raise xception.kwadSystemException('Main', self_funct, 'Option --path (-u) is required !')

        # Check MenuPath E:
        menufile = db.MenuFile(host=options.machine, name=options.name, user=options.user, path=options.path)
        if not menufile.load():
            xception.kwadInformation('Main', self_funct, "Option --path (-p): %s Do not Exist for Machine: %s and User: %s ! Nothing to do." % (options.path, options.machine, options.user)).warn()
            return

        menufile.delete()
        print ("Menu Path: %s for Machine: %s and User: %s Deleted." % (options.path, options.machine, options.user))
        return

    except Exception as e:

        if VERBOSE == None:
            try:
                VERBOSE = int(options.verbose)
            except:
                VERBOSE = 0
        if VERBOSE >= 10: raise

        import sys
        if not hasattr(e, 'short1') or not hasattr(e, 'short2'):
            message = e.__class__.__name__ + ': ' + str(e)
        elif VERBOSE < 5:
            message = e.short1()
        elif VERBOSE >= 5:
            message = e.short2()
        sys.stderr.write(message + '\n')
        sys.exit(2)


if __name__ == '__main__':
    from os import path
    import utils
    import sys

    addkuser_home = utils.getInstallDir()

    ## Set paths
    for _path in ('core',):
        _path = path.normpath(addkuser_home + '/' + _path)
        if not _path in sys.path: sys.path.append(_path)

    main(sys.argv[1:])
