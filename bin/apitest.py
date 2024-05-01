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



"""
To afford to program menus, first you have to understand the Menu lifecycle into ApiMenu :
menus are build on the fly from the information retreived from each level either for the xml or the programatic interface.
And destroyed on rollback to the origine when the user strikes the <ENTER> key with no option.
"""


# 20120306:A001


HELP='Help for %s'
LHELP='This a long help for %s.\nSay something, say something, say something.'
EXEC_COMMAND=None # Maybe "dir" for windows or "ls" for unixes or whatever command the local os supports.


import utils
APIMENU_HOME=utils.getInstallDir()



##########
## Main ##
##########


    
def feedMenu(config, menu):
    
    if isinstance(menu, kastmenup.Menu):feedMenuChilds(menu)
    else:feedIMenuChilds(menu)

def feedMenuChilds(menu):
    """
    Instanciates and add Childs to the menu received in parameter.
    Childs can be :
        a new Menu
        a new IMenu (Interactive Menu)
        an Option
    """    
    if menu.isFed():return False # Track if this menu is already fed.
    
    menuid = menu.getTitle()
    
    
    ## Making and adding Childs to this menu
        
    # - Child is a Menu
    title = menuid + '.m1'
    child = kastmenup.Menu(title, help=HELP % title)
    menu.add(child)


    # - Child is an IMenu
    title = menuid + '.im2'
    
    """
    The following line prepares the command for this IMenu.
    For IMenu only, input fields can be reused to format the command argument line associated to this IMenu.
    e.g.: 
       if  input fields for this IMenu are : m1.im2.io3 and m1.im2.io4
       And the command is formatted like this : "dir $m1.im2.io3 $m1.im2.io4" or ("ls $m1.im2.io3 $m1.im2.io4")
       If the user enter 
            m1.im2.io3 = 'myfile1'
            m1.im2.io4 = 'myfile2'
        The executed command when typing "s" (submit) on the IMenu would be : dir myfile1 myfile2
    """
    command=EXEC_COMMAND + ' $' + title + '.io3' + ' $' + title + '.io4'
    
    child=kastmenup.IMenu(title, help=HELP % title, command=command, verbose_exec_command=True)
    menu.add(child)


    # - Child is an Option
    title = menuid + '.o3'
    child=kastmenup.Option(title, help=HELP % title, command=EXEC_COMMAND, contents=['This option shows', 'information', 'in many', 'lines !'], verbose_exec_command=True)
    menu.add(child)
    title = menuid + '.o4'
    child=kastmenup.Option(title, help=HELP % title, command=EXEC_COMMAND, verbose_exec_command=True)
    menu.add(child)    
        
    return True

def feedIMenuChilds(menu):
    """
    Instanciates and add Childs to the menu received in parameter.
    Childs can be :
        a new Menu
        a new IMenu (Interactive Menu)
        an Option
    """
    if menu.isFed():return False # Track if this menu is already fed.
    
    menuid = menu.getTitle()
    
    ## Making and adding Childs to this menu

    # - Child is a Menu
    title=menuid + '.m1'
    child=kastmenup.Menu(title, help=HELP % title)
    menu.add(child)

    # - Child is an IMenu
    title=menuid + '.im2'
    command=EXEC_COMMAND + ' $' + title + '.io3' + ' $' + title + '.io4'
    child=kastmenup.IMenu(title, help=HELP % title, command=command, verbose_exec_command=True)
    menu.add(child)
        
    # - Child is an IOption :
    #   because parent Menu is an IMenu, IOption can be added in it.
    #   Note: IMenu also accept classical Option (see below).
    title=menuid + '.io3'
    child=kastmenup.IOption(title, help=HELP % title, lhelp=LHELP % title, value='myfile1', wkvalue={'*type': 'str', '*required': True})
    menu.add(child)
    title=menuid + '.io4'
    child=kastmenup.IOption(title, help=HELP % title, lhelp=LHELP % title, value='myfile2', wkvalue={'*checkIn': ('myfile2', 'myfile3', 'myfile4'), '*required': True})
    menu.add(child)
    
    # - Child is an Option
    title=menuid + '.o5'
    child=kastmenup.Option(title, help=HELP % title, command=EXEC_COMMAND, verbose_exec_command=True)
    menu.add(child)

    return True

def usage():
    return """ """




if __name__ == '__main__':
    self_funct='main'

    ## Set paths
    # - This just set the rigth path to reach the module apimenup.
    from os import path
    import sys
    for _path in ('core',):
        _path=path.normpath(APIMENU_HOME + '/' + _path)
        if not _path in sys.path:sys.path.append(_path)
        
    from kwadlib.tools import getOsType
    if getOsType()=='windows':
        EXEC_COMMAND='dir'
        #A001:+temp_dir
        TEMP_DIR='c:\windows'
    else:
        EXEC_COMMAND='ls'
        #A001:+temp_dir
        TEMP_DIR='/tmp'

    from kwadlib import kastmenup

    # - Config
    #M001:+temp_dir
    config=kastmenup.Config(feedMenu, title='My Menu', temp_dir=TEMP_DIR, skip_line=True, screen_max_lines=30, lang_dir=APIMENU_HOME + '/langs', check_all_car='s', check_all_message='Submit')
    """
    The key point to understand is that : the function feedMenu passed as first parameter to Config, will be called every time Apimenu
    need to display a menu.
    """

    # - Make first Menu
    menu = kastmenup.Menu('m1', help=HELP % 'm1', confirm_exit=True)
    feedMenuChilds(menu)

    # - Run ApiMenu
    config.go(menu)