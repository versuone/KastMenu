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


KASTWEBP_FILE = '/opt/kastmenu/current/core/kwadlib/kastwebp.tmpl.py'
KASTWEBS_FILE = '/opt/kastmenu/current/core/kwadlib/kastwebs.tmpl.py'
KASTWEBP_TO_FILE = '/opt/kastmenu/current/core/kwadlib/kastwebp.py'
KASTWEBS_TO_FILE = '/opt/kastmenu/current/core/kwadlib/kastwebs.py'
DEFAULT_KEY = '4c23615cf2b9986b1e47dc28e64c89da9b4d'

import sys
import time
import random
random.seed()
import fnmatch
import sysconfig
from hashlib import sha256
from os import path, remove
from Cython.Build import cythonize
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py

def usage():
    return """
Setup.py:
=========
# Run: 
cd /opt/kastmenu/current
/opt/kastmenu/current/bin/.venv/bin/python3 setup.py build_ext --inplace

# What:
Where {deftkey} value is the current value for CTX_KASTWEB in the file: {file} (and {file2}).
(The line to be replaced are usually commented with: "# todo: will be replaced by random value by BUILD:::")
This value in file: {file} (and {file2}) will be replace by a new sha256(random value) before the build.

Because kastmenu run under any user.
- The /opt/kastmenu/* code need to be readable by the python run by the user so readable by anyone.
- The same for the conf directory at /etc/kastmenu/*.

We need to hide the generated ssl private's key for the kastweb server.
The way we found is (As anyone can read the code and the conf store) is to allow
the building of the file and hard hide the key in it.
""".format(deftkey=DEFAULT_KEY, file=KASTWEBP_FILE, file2=KASTWEBS_FILE)

def randKey():
    id = str(int(time.time() * 100))
    rand256 = random.randint(1, 100000000)
    rand256 = "%08i" % rand256
    rand256 = sha256(rand256.encode('utf-8')).digest().hex()
    
    return rand256

print (usage())


index=1
randkey = randKey()
for file, to_file in ((KASTWEBP_FILE, KASTWEBP_TO_FILE),  (KASTWEBS_FILE, KASTWEBS_TO_FILE)):
    print( "%d. Creating file: %s, From file: %s, By replacing: %s by new random secret key !" % (index, to_file, file, DEFAULT_KEY)) 
    index+=1
    with open(file) as f:
        src = f.read()
        src = src.replace(DEFAULT_KEY, randkey)
        
        with open(to_file, 'w') as f:
            src = f.write(src)
            done = True


print( "%d. Compiling files: %s.\n" % (index, ','.join((KASTWEBS_FILE, KASTWEBS_TO_FILE))) ) 

INCLUDE_FILES = [
    KASTWEBP_TO_FILE.split('/opt/kastmenu/current/')[-1],
    KASTWEBS_TO_FILE.split('/opt/kastmenu/current/')[-1]
]


def get_ext_paths():
    """get filepaths for compilation"""
    return list(INCLUDE_FILES)

class build_py(_build_py):

    def find_package_modules(self, package, package_dir):
        ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')
        modules = super().find_package_modules(package, package_dir)
        filtered_modules = []
        for (pkg, mod, filepath) in modules:
            if os.path.exists(filepath.replace('.py', ext_suffix)):
                continue
            filtered_modules.append((pkg, mod, filepath, ))
        return filtered_modules  
    
setup(
    name='kastmenu',
    version='1.0',
    packages=find_packages(),
    ext_modules=cythonize(
        get_ext_paths(),
        compiler_directives={'language_level': 3}
    ),
    cmdclass={
        'build_py': build_py
    }
)

index+=1
print( "\n%d. Removing files: %s." % (index, ','.join((KASTWEBP_TO_FILE, KASTWEBS_TO_FILE))) ) 
remove(KASTWEBP_TO_FILE)
remove(KASTWEBS_TO_FILE)
remove(KASTWEBP_TO_FILE.split('.py')[0] + '.c' )
remove(KASTWEBS_TO_FILE.split('.py')[0] + '.c' )

index+=1
print( "\n%d. kastweb SSL Keys must be re-generated with script: %s." % (index, '/opt/kastmenu/kastmenu-1.0/bin/genkastwebkeys') ) 
