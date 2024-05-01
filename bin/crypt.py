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

def main(args=None):
    self_funct='main'
    import sys, optparse

    ## Set paths
    for _path in (KAST_HOME + '/core',):
        if not _path in sys.path:sys.path.append(_path)
    doImport()
    from kwadlib.security.crypting import Crypt

    # cmd, passfile, kfile, message="assword:", twice=False
    parser = optparse.OptionParser(usage())
    parser.add_option("-s", "--salt", dest="salt", help="A 32 bit length salt.")
    parser.add_option("-k", "--key", dest="key", help="A 32 bit length key. In conjuntion with -f (--file).")
    parser.add_option("-f", "--file", dest="file", help="file to encrypt or decryt. In conjuntion with -k (--key).")
    parser.add_option("--passfile", dest="passfile", help="A file containing the key. In conjuntion with --kfile.")
    parser.add_option("--kfile", dest="kfile", help="A key to read the passfile. In conjuntion with --passfile.")
    parser.add_option("-D", "--decrypt", dest="decrypt", action="store_true", default=False, help="decryt this file.")
    parser.add_option("-E", "--encrypt", dest="encrypt", action="store_true", default=False, help="encryt this file.")

    (options, args) = parser.parse_args()

    if (options.salt and not options.key) or (options.key and not options.salt): raise Exception('Parameter Error, If one of -s (--salt) or -k (--key) is provided both must be !')
    if (options.passfile and not options.kfile) or (options.kfile and not options.passfile): raise Exception('Parameter Error, If one of --kfile or --passfile is provided both must be !')
    if options.salt and options.passfile: raise Exception('Parameter Error, --salt and --key cannot be provided together !')
    if not options.salt and not options.passfile: raise Exception('Parameter Error, One of: --salt, --key or --passfile, --kfile must be provided !')

    if options.file == None:raise Exception('Option file is required !')
    if (not options.encrypt and not options.decrypt) or (options.encrypt and options.decrypt):
        raise Exception('One of Option -E (--encrypt) or -D (--decrypt) is required !')

    try:
        c=Crypt(salt=options.salt, key=options.key, passfile=options.passfile, kfile =options.kfile)
        if options.encrypt: print(c.encryptFile(options.file))
        elif options.decrypt: print(c.decryptFile(options.file))
        else:raise

    except Exception as e:
        raise
    except:
        raise

if __name__ == '__main__':
    main()
