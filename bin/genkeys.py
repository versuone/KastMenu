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



SELF_MODULE = 'genkeys'
APMENU_TEMP_DIR = None


def usage():
    return """
Syntax:
-------
genkeys [<fqdn>]
genkeys myfqdn
genkeys

fqdn is the only argument allowed if not provided will deduce it for the local machine hostname.

Genkeys: Will generate server certificates for the kastmenu kastweb web interface server.
This can be done at any time (and likely at the first installation).

Note: The kastweb interface program (kastweb.py) is only remotly run by the kastmenu, 
launching a menu on this machine and under the user it was called for.

The following tree entries are defined into the configuration file 
at : <kastmenu_dir>/conf/kast.conf:
kastweb_server_crt = kastweb.kastmenu.myhostname.crt
kastweb_server_key = kastweb.kastmenu.myhostname.key
kastweb_caclients = keys/caclients

If the entry starts with no /: this means a relative path from
the <kastmenu_install_dir>.
genkeys will deduced the keys directory from there.
e.g. the keys directory is: <kastmenu_install_dir>/keys.

Genkeys will generate all keys into this keys directory.

Genkeys will: 
    Aslo generates clients certificated into 
    - keys/caclients/to_kastservers.
    For futur releases, this may be used by the kastserver to restraign the kastmenu
    partners it can communicate with.

    Expect kastserver's certificates directly under:
    - keys/caclients
    Dump here all kastserver certifcate you want to allow communication
    with this kastmenu installation.
    This is done this way, by copying:
    cp /etc/kastmenu/keys/caclients/to_kastweb/.   <kastmenu_install_dir>/keys/caclients
"""


if __name__ == '__main__':
    import sys
    import utils
    import optparse
    from os import path
    import optparse

    parser = optparse.OptionParser(usage())
    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option("--force", dest="force", action="store_true", default=False, help="By default will not generate SSL Keys if same fqndn as previous. Use force to overpass this.")

    (options, args) = parser.parse_args(args=sys.argv)

    GENKEYS_HOME = utils.getInstallDir()

    # Set paths
    for _path in ('core',):
        _path = path.normpath(GENKEYS_HOME + '/' + _path)
        if not _path in sys.path: sys.path.append(_path)

    fqdn = None
    if len(args) > 2: raise Exception('Only one argument is allowed the fqdn !')
    if len(args) == 2: fqdn = args[-1]

    from kwadlib import kastserverp

    kastserverp.genKeys(fqdn=fqdn, force=options.force)
