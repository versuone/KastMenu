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



class Visitor:

    def __init__(self, childFirst = True, treatAncestor=True, recursiveMenu=True):
        self.childFirst = childFirst
        # Imbricated classes Treat the caller ?
        self.treatAncestor=treatAncestor
        # Imbricated classes recursivity ?
        self.recursiveMenu = recursiveMenu
       # End Imbricated classes recursivity.

    def visitBaseMenu(self, element):
        pass                       
    
    def visitMenu(self, element):
        pass
    
    def visitIMenu(self, element):       
        pass
        
    def visitBaseOption(self, element):
        pass           
        
    def visitOption(self, element):
        pass   

    def visitIOption(self, element):
        pass   

    def visitImbricatedMenus(self, element):
        """Recursivite sur les classes inbriquees."""
        for c in element.listNodeBases:                                       
            c.accept(self)
