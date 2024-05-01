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
    SSLCrypting for small messages (signatures, passwords):
    
    Crypt:
    sslcrypt  --pubKey  --message --dob64
    UnCrypt:
    sslcrypt  --privkey --cmessage --dob64
    """

def main(args=None):
    self_funct='main'
    import sys, optparse

    ## Set paths
    for _path in (KAST_HOME + '/core',):
        if not _path in sys.path:sys.path.append(_path)
    doImport()
    from kwadlib.security.crypting import SSLCrypt

    parser = optparse.OptionParser(usage())
    parser.add_option("--pubkey", dest="pubkey", help="Public SSL key path. If provided operation encode will be selected.")
    parser.add_option("--privkey", dest="privkey", help="Private SSL key path. If provided operation decode will be selected.")
    parser.add_option("-m", "--message", dest="message", help="Message to encrypt or decryt.")
    parser.add_option("--dob64", dest="dob64", action="store_true", default=False, help="Do b64 before or after crypting/uncrypting ?")
    (options, args) = parser.parse_args()

    if (options.pubkey and options.privkey): raise Exception('Options --pubkey and privkey cannot be selected together !')
    if (options.pubkey==None and options.privkey==None): raise Exception('Options one of --pubkey or privkey must be selected !')
    if options.message == None: raise Exception('Option message is required !')
    if options.b64 == None: raise Exception('Option message is required !')


    try:
        if options.pubkey:
            print(SSLCrypt.encode(options.pubkey, options.message, doB64=options.dob64))
        else:
            print(SSLCrypt.encode(options.privkey, options.message, doB64=options.dob64))

    except Exception as e:
        raise
    except:
        raise

if __name__ == '__main__':
    main()
