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


SELF_MODULE='kdealer'

import random
random.seed()


if __name__ == '__main__':
    from optparse import OptionParser
    from os import path, makedirs
    import utils, sys

    apimenu_home = utils.getInstallDir()

    ## Set paths
    for _path in ('core',):
        _path=path.normpath(apimenu_home + '/' + _path)
        if not _path in sys.path:sys.path.append(_path)
    from kwadlib.security.crypting import getOptSecidFromFile
    from kwadlib import kdealerp
    from kwadlib import default
    from kwadlib import tools

    parser = OptionParser()
    parser.add_option("-s", "--secid", dest="secid", help="secid")
    parser.add_option("-m", "--queue_max", dest="queue_max", type=int, help="queue_max")
    parser.add_option("-v", "--verbose", dest="verbose", default =0, type=int, help="verbose")
    (options, args) = parser.parse_args()

    if len(args) != 0 :parser.error("Accept no arguments")
    if not isinstance(options.secid, str)  or options.secid=='':raise Exception('secid', 'str', str(options.secid))


    ## Retreives temp_dir:
    KDEALER_TEMP_DIR =  default.getKastTempDir() + '/kdealer/' + tools.genUid()
    if not path.isdir(KDEALER_TEMP_DIR):makedirs(KDEALER_TEMP_DIR)

    tools.verbose(SELF_MODULE + ': Temporary dir is: ' + KDEALER_TEMP_DIR + '.', level=options.verbose, ifLevel=50, indent='', logFile=options.verbose)

    secid, port = getOptSecidFromFile(options.secid, temp_dir=default.getKastTempDir())

    kdealerp.main(secid, port, options.queue_max, KDEALER_TEMP_DIR, options.verbose)
