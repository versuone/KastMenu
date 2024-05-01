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


INSTALL_DIR=None

class Dummy:pass

def getInstallDir():
    """
    Retreives the kwad installation directory.
    """
    global INSTALL_DIR
    if INSTALL_DIR!=None:return INSTALL_DIR
    
    from os import path 

    import inspect
    c=Dummy()
    p=inspect.getabsfile(c.__class__)
    
    for i in range(0, 2):p=path.split(p)[0]
    INSTALL_DIR=p
    
    return INSTALL_DIR
