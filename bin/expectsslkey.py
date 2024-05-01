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


SELF_MODULE='expectpass'

tools = None
xception = None
def doImport():
    global tools
    global xception
    global KAST_HOME

    from kwadlib import tools as _tools
    from kwadlib import xception as _xception

    tools = _tools
    xception = _xception

import utils
KAST_HOME=utils.getInstallDir()
PARAMETERS = ["--kpassfile", "--kfile", "--ktwice", "--kmessage"]

def usage():
    return """
    expectpass some command with parms  -p kpassfile -k kfile -m kmessage -t ktwice
    """

def getThisArgs():
    import sys, shlex
    # Intercept expecsslkey's Options
    this_args = []
    todels = []

    sub_args = shlex.split(' '.join(sys.argv[1:]))
    found = False
    j=0
    for i in range(len(sub_args)):
        j+=1
        option = sub_args[i]
        if not option.startswith('--'):
            # If found args mixed into expectsslkey's options suite.
            if found and j>=2:raise Exception("Found extra: %s arg into expectsslkey's options suite ! expectsslkey's options: should be all align at the end of the command expression and not be mixed." % option)
            continue
        elif found and option not in PARAMETERS:raise Exception(
                "Found extra: %s option arg into expectsslkey's options suite ! expectsslkey's options: should be all align at the end of the command expression and not be mixed." % option)

        if option in PARAMETERS:
            if option == '--ktwice':
                this_args.extend([option])
                todels.extend([i])
                j=1 # bypass next arg
            else:
                if len(sub_args) <= i + 1: continue
                value = sub_args[i + 1]
                if value.startswith('-'):raise Exception("Unsupported value: %s for option: %s !" % (value, option))
                this_args.extend([option, value])
                todels.extend([i, i+1])
                j=0
            found = True

    l = []
    for i in range(len(sub_args)):
        if i in todels:continue
        l.append(sub_args[i])

    sub_args = l

    return sub_args, this_args

def main(args=None):
    self_funct='main'
    import sys, optparse

    ## Set paths
    for _path in (KAST_HOME + '/core',):
        if not _path in sys.path:sys.path.append(_path)
    doImport()
    from kwadlib.security.crypting import expectSSlKey

    # cmd, passfile, kfile, message="assword:", twice=False
    parser = optparse.OptionParser(usage())
    parser.add_option("-p", "--kpassfile", dest="kpassfile", help="file containing the crypted password.")
    parser.add_option("-k", "--kfile", dest="kfile", help="kfile")
    parser.add_option("-t", "--ktwice", dest="ktwice", action="store_true", default=False, help="Command spawn same input twice. Aka passwword confirmation.")
    parser.add_option("-m", "--kmessage", dest="kmessage", help="message of the command input line.")

    sub_args, this_args = getThisArgs()
    (options, _) = parser.parse_args(args=this_args)
    if len(this_args) <= 0: raise Exception('The expect options are expected !')
    # +20230715:
    if len(sub_args) <= 0: raise Exception('The Command argument is expected !')

    try:
        if options.kpassfile == None:raise Exception('options kpassfile is required !')
        if options.kfile == None:raise Exception('options kfile is required !')
        # cmd, passfile, kfile, message="assword:", twice=False
        expectSSlKey(' '.join(sub_args), options.kpassfile, options.kfile, message=options.kmessage, twice=options.ktwice)

    except Exception as e:
        raise
    except:
        raise

if __name__ == '__main__':
    main()
