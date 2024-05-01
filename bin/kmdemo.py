## Copyright (c) 2007-2008, Patrick Germain Placidoux
## All rights reserved.
##
## Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
## associated documentation files (the “Software”), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
##
## The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited
## to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall
## the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract,
## tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
##
## Except as contained in this notice, the name of the Patrick Germain Placidoux shall not be used in advertising or otherwise
## to promote the sale, use or other dealings in this Software without prior written authorization from the Patrick Germain Placidoux.
##
## Home: http://www.dkwad.org
## Contact: dkwad@dkwad.org


SELF_MODULE = 'kmdemo'
KINIT_TEMP_DIR = None


def runMenu(kast_options, verbose=0):
    selfMethod='runMenu'
    from kwadlib.kastmenup import Menu, IMenu, Option
    from kwadlib.kastmenup import Config, VIDEO_COLOR

    # - Config
    config=Config(default_fct_menu,
        title='KastMenu Api Demo',
        temp_dir=None,
        help="""
Kmdemo shows how to use the KastMenu APi
to dynamically produce menus on the flow.

This program can be simply called:
kmdemo
- or if you want verbose:
kmdemo -v 30
- or if you want bigbrother logging into /tmp:
kmdemo -l -L /tmp -O
(then you can tail -f on the log while using the menu on the other side)
You can take an mpath from the log and automate the call with:
- A mpath is a walkthrough a KastMenu marked by <input><dot>[<input><dot>]
you can replay with a pause (in seconds) by screen. 
kmdemo -g <mpath> -p 2
or 
kmdemo -b <mpath>

Any time you can integrate your program (here kmdemo)
in another KastMenu Menu simply using the --follow_menu option.

Using this option to call your program will transparently integrate 
your custom menu in a larger KastMenu.
For instance if you put: 
    "kmdemo --follow_menu" into the command attribute of any option 
or imenu of a kastmenu xml file;
This would transparently integrate your indidual menu to a larger menu.
        """,
        option_upper=False, skip_line=True,
        screen_max_lines=18,
        lang_dir='/tmp',
        batch=kast_options['batch'],
        pause=kast_options['pause'],
        noclear=kast_options['noclear'],
        port=kast_options['port'],
        secid=kast_options['secid'],
        # is_listening=kast_options['is_listening'],
        show_shortcut=kast_options['show_shortcut'],
        log=kast_options['log'], log_output=kast_options['log_output'], log_dir=kast_options['log_dir'], log_rotate=kast_options['log_rotate'],
        record=kast_options['record'], go=kast_options['go'], go_menu=kast_options['go_menu'], debug=kast_options['debug'],
        verbose=verbose)

    # - FirstMenu
    firstMenu=Menu('Programming KastMenu', 'FirstMenu Subtitle', lhelp="""
- The KastMenu API supports the following components:\\n
Menu, Option and\\n
IMenu, IOption.\\n
\\n
- And the following calls:\\n
ioraise\\n
iowait\\n
iodialog\\n
ioprocess\\n
\\n
1) Components Menu, Option and IMenu, IOption:\\n
- A Menu is a container of Options, other Menu and IMenu.\\n
An Option is associated to a shell command;\\n
Selected this Option would run this command.\\n
\\n
- An IMenu is a container of IOptions, Options, other Menu or IMenu.\\n
(I is for Interactive)\\n
An IMenu is associated to a shell command.\\n
Submitted this IMenu would run this command.\\n
\\n
An IOption has a name and would accept an input value.\\n
IOption's value can be used into the IMenu's shell command as variable\\n
preceded by $.\\n
For instance "echo $<ioption_name>".\\n
\\n
2) calls:\\n
- ioraise: is the way to manage exception and raise in you code.\\n
Exposed code must be enclosed by try/except and explicitly use ioraise to\\n
properly raise the exception to KastMenu.\\n
- iowait: is the way to properly send a message alert box to KastMenu.\\n
- iodialog: is the way to properly send a dialog box to KastMenu.\\n
- ioprocess: is the way to properly run a shell command into KastMenu.\\n
\\n
3) Exits:\\n 
The KastMenu API also provides exits.\\n
exits are callback functions called during the lifecycle of a KastMenu.\\n
    """)
    firstMenu.setConfig(config)

    """    
    We can statically feed this Menu:
    Feeding a Menu means to populate its with other Children Menus, IMenus or Options.
    """

    # Menu1:
    # ------
    # For this Menu Title we'll use color and background colors.
    # The color sheme is the same either the client interface is a Terminal consol or Web/Mobile.
    # VIDEO_COLOR for colors and background are ('BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE','PURPLE', 'CYAN', 'WHITE')
    # confirm_exit: True, Means it will require confirmation to leave this Menu.
    menu = Menu('Menu.1', sub_title='Menu.1 subtile !', help='Using Menu', lhelp='Menu.1 long Help', contents=['use','contents','to add some', 'vertical text'], fct_exit_command=menu1_fct_exit, confirm_exit=True, fct_enter=menu1_fct_enter, fct_leave_forward=menu_fct_leave_forward, fct_leave_backward=None, set_color=True, police_bold=True, police_color=VIDEO_COLOR.WHITE, police_bgcolor=VIDEO_COLOR.GREEN)
    firstMenu.add(menu)

    """
    Menu.1 will be dynamically fed by exits.
    Using Exits allows to build Menus dynamically on the flow.
    A Menu can have Options, other Menus or IMenus children.
    Exits are: fct_exit_command, fct_enter, fct_leave_forward, and fct_leave_backward
    Here we only use: 
        fct_enter=menu1_fct_enter -> this will fed Menu1. 
        fct_leave_forward=menu_fct_leave_forward
    """

    # IMenu1:
    # -------
    # An IMenu (Interactive Menu) is a Menu that allows IOptions.
    # Interactive Opions allows to set values to this IMenu.
    # Then these values can be used by the IMenu's command as variable e.g.: "mycommand $<ioption1>  $<ioption1>"
    # confirm: True, Means it will require before exution of the command.
    imenu = IMenu('IMenu.2', help='Using Interactive Menu (IMenu)', lhelp='IMenu.2 long Help', command='printf "Fields value are fieldStr: $fieldStr, fieldInt: $fieldInt and fieldBool: $fieldBool !\n\nThey can be used in shell commands."', fct_command=None, fct_enter=imenu2_fct_enter, fct_leave_forward=menu_fct_leave_forward, fct_leave_backward=None, set_color=True, police_bold=True, police_color=VIDEO_COLOR.PURPLE, police_bgcolor=VIDEO_COLOR.NONE, confirm=False)
    firstMenu.add(imenu)

    """
    IMenu1 will be dynamically fed by exits.
    An IMenu can have IOptions, Options, other IMenus or Menus children.
    command indicates the command to run, one could also use fct_command.
    Here we only use: 
        fct_enter=imenu1_fct_enter -> this will fed Menu1.
        fct_leave_forward=imenu1_fct_leave_forward
    """

    firstMenu.add(Option('Option.3', help='Using Option', lhelp='Option.3 long Help', command='echo "Hi !"', contents=['More', 'vertical', 'text but on Option this', 'time !'], set_color=True, police_bold=True, police_color=VIDEO_COLOR.BLACK, police_bgcolor=VIDEO_COLOR.NONE))

    firstMenu.add(Option('Option.4', help='Using ioraise to gracefully raise !', lhelp='Option.4 long Help', fct_command=option4_fct_ioraise, set_color=True, police_bold=True, police_color=VIDEO_COLOR.GREEN, police_bgcolor=VIDEO_COLOR.NONE))
    firstMenu.add(Option('Option.5', help='Using iowait simple alert box !', lhelp='Option.5 long Help', fct_command=option5_fct_iowait))
    firstMenu.add(Option('Option.6', help='Using iodialog simple dailog box !', lhelp='Option.6 long Help', fct_command=option6_fct_iodialog))

    firstMenu.add(Option('Option.7', help='Using ioprocess to run command !', lhelp='Option.7 long Help', fct_command=option7_fct_ioprocess, set_color=True, police_bold=True, police_color=VIDEO_COLOR.BLUE, police_bgcolor=VIDEO_COLOR.NONE))

    from kwadlib.tools import getInstallDir
    firstMenu.add(Option('See code', help='See Api code', lhelp=None, command='cat /%s/bin/kmdemo.py' % getInstallDir()))

    config.go(firstMenu)
    # -- wait to Join :

# ---------------------- #
# Menu Feeder/Dispatcher #
# ---------------------- #
def default_fct_menu(config, menu):
    if menu.isFed():return False
    """    
    Each time ApiMenu needs to build a new Menu this function (or method) is called with an unique parameter the parent Menu instance.
    - We can finish to setup the Menu content: for ex we can add this Option to every menus:
    
    from kwadlib.kastmenup import Option, VIDEO_COLOR
    menu.add(Option('Common Option', help='Common Option short Help', lhelp='Common Option long Help', contents=['aaa','bb','cccc', 'ddddd'], command='ls -ltr', set_color=True, police_bold=True, police_color=VIDEO_COLOR.GREEN, police_bgcolor=None))
    
    But we wont use it here because: fct_menu is the first exit to be called,
    If we fill something here the next exit to be called e.g fct_enter will see the menu fed and wont run. 
    """

def menu1_fct_enter(config, menu1, id=None, id_type=None):
    selfMethod='menu1_fct_enter'
    if menu1.isFed():return False
    from kwadlib.kastmenup import Menu, Option
    menu1.clear() # This will clear all childs

    try:
        menu1_1 = Menu('Menu.1.1', sub_title='Menu.1.1 subtile !', help='Menu.1.1 short Help', lhelp='Menu.1.1 long Help', fct_exit_command=None, confirm_exit=True, fct_enter=menu1_fct_enter, fct_leave_forward=menu_fct_leave_forward, fct_leave_backward=None)
        menu1.add(menu1_1)

        menu1_1.add(Option('Option.1.1.1', help='Option.1.1.1 short Help', lhelp='Option.1.1.1 long Help', command='ls -ltr'))
        menu1_1.add(Option('Option.1.1.2', help='Option.1.1.2 short Help', lhelp='Option.1.1.2 long Help', command='ls -ltr', contents=['More','vertical','text but on Option this', 'time !']))
        menu1_1.add(Option('Option.1.1.3', help='Option.1.1.3 short Help', lhelp='Option.1.1.3 long Help', command='ls -ltr'))

        menu1.add(Option('Option.1.2', help='Option.1.2 short Help', lhelp='Option.1.2 long Help', command='ls -ltr'))

    except Exception as e:
        if config.getVerbose()>=200:raise # Debug purpose only
        config.ioraise(str(e), menu=menu1, id=id, id_type=id_type, fct_name=selfMethod, except_type='MenuEnterFailed')


def imenu2_fct_enter(config, imenu2, id=None, id_type=None):
    selfMethod='menu2_fct_enter'
    if imenu2.isFed():return False
    from kwadlib.kastmenup import Menu, Option, IOption
    imenu2.clear() # This will clear all childs
    try:
        menu2_1 = Menu('Menu.2.1', sub_title='Menu.2.1 subtile !', help='Menu.2.1 short Help', lhelp='Menu.2.1 long Help', fct_exit_command=None, confirm_exit=True, fct_enter=menu1_fct_enter, fct_leave_forward=menu_fct_leave_forward, fct_leave_backward=None)
        imenu2.add(menu2_1)

        menu2_1.add(Option('Option.2.1.1', help='Option.2.1.1 short Help', lhelp='Option.2.1.1 long Help', command='ls -ltr'))
        menu2_1.add(Option('Option.2.1.2', help='Option.2.1.2 short Help', lhelp='Option.2.1.2 long Help', command='ls -ltr'))
        menu2_1.add(Option('Option.2.1.3', help='Option.2.1.3 short Help', lhelp='Option.2.1.3 long Help', command='ls -ltr'))

        imenu2.add(IOption('fieldStr', value=None, wkvalue={'*type': 'str', '*value': 'hi'}, help='IOption.2.2 short Help', lhelp='Option.2.2 long Help', command='ls -ltr'))
        imenu2.add(IOption('fieldInt', value=5, wkvalue={'*type': 'int', '*value': 123}, help='IOption.2.3 short Help', lhelp='Option.2.3 long Help', command='ls -ltr'))
        imenu2.add(IOption('fieldBool', value=None, wkvalue={'*type': 'bool', '*value': True}, help='IOption.2.4 short Help', lhelp='Option.2.4 long Help', command='ls -ltr'))
        imenu2.add(Option('Option.2.2', help='Option.2.2 short Help', lhelp='Option.2.2 long Help', command='ls -ltr'))

    except Exception as e:
        if config.getVerbose()>=200:raise # Debug purpose only
        config.ioraise(str(e), menu=imenu2, id=id, id_type=id_type, fct_name=selfMethod, except_type='MenuEnterFailed')


def menu_fct_leave_forward(config, menu, id=None, id_type=None):
    menu.setNotFed()

def menu1_fct_exit(config, menu, id=None, id_type=None):
    selfMethod='menu1_fct_exit'
    config.ioprint('You are leaving KAstMenu Demo Api, Hope you enjoyed it !', menu=menu, id=id, id_type=id_type, fct_name=selfMethod)

def option4_fct_ioraise(config, menu, option_index, command, id=None, id_type=None):
    selfMethod = 'option4_fct_ioraise'
    message = 'Example using ioraise to gracefully raise !'
    config.ioraise(message, menu=menu, option_index=option_index, id=id, id_type=id_type, fct_name=selfMethod, except_type='ExecOperationInjectFailed')

def option5_fct_iowait(config, menu, option_index, command, id=None, id_type=None):
    selfMethod = 'option5_fct_iowait'
    message = 'Example using iowait simple alert box !'
    config.iowait(message, menu=menu, option_index=option_index, id=id, id_type=id_type, fct_name=selfMethod)

def option6_fct_iodialog(config, menu, option_index, command, id=None, id_type=None):
    selfMethod = 'option6_fct_iodialog'
    message = 'Example using iodialog simple dailog box ! Do you agree (y/n) ?'
    doAgree = False

    val = config.iodialog(message, menu=menu, option_index=option_index, id=id, id_type=id_type)
    if val == 'y': doAgree = True

def option7_fct_ioprocess(config, menu, option_index, command, id=None, id_type=None):
    selfMethod='option7_fct_ioprocess'
    from kwadlib import wk, xception
    cde = 'echo your input was: %s'
    try:
        val = config.iodialog('You may use a dialog box to get some (integer) input from the user ?', menu=menu, is_value=True, option_index=option_index, id=id, id_type=id_type)
        p = wk.WantedKeywords()
        setattr(p, 'myvar', {'*type':'int', '*required': True, '*withEval': True})
        wk.getKeywords(wantedKeywords=p, keywords={'myvar': val})

        system_command_ret, cde_output=config.ioprocess(cde % str(p.myvar), menu=menu, option_index=option_index, id=id, id_type=id_type, fct_name=selfMethod, useshell=False)

    except Exception as e:
        if config.getVerbose()>=200:raise
        message=str(xception.kwadInformation('Main', selfMethod, str(e))) + '\nExecution failed !\n'
        config.ioraise(message, menu=menu, option_index=option_index, id=id, id_type=id_type, fct_name=selfMethod, except_type='ExecOperationInjectFailed')


##########
## Main ##
##########

def usage():
    return """
Kmdemo shows how to use the KastMenu APi
to dynamically produce menus on the flow.

This program can be simply called:
kmdemo
- or if you want verbose:
kmdemo -v 30
- or if you want bigbrother logging into /tmp:
kmdemo -l -L /tmp -O
(then you can tail -f on the log while using the menu on the other side)
You can take an mpath from the log and automate the call with:
- A mpath is a walkthrough a KastMenu marked by <input><dot>[<input><dot>]
you can replay with a pause (in seconds) by screen. 
kmdemo -g <mpath> -p 2
or 
kmdemo -b <mpath>

Any time you can integrate your program (here kmdemo)
in another KastMenu Menu simply using the --follow_menu option.

Using this option to call your program will transparently integrate 
your custom menu in a larger KastMenu.
For instance if you put: 
    "kmdemo --follow_menu" into the command attribute of any option 
or imenu of a kastmenu xml file;
This would transparently integrate your indidual menu to a larger menu.
"""


def main(args):
    self_funct = 'main'
    import optparse
    from kwadlib import xception

    parser = optparse.OptionParser(usage())
    parser.add_option('-v', "--verbose", dest="verbose", type=int, default=0, help="Verbose level, int value.")
    parser.add_option("--debug", dest="debug", action="store_true", default=False, help="Raises and Fails at first issue.")

    # [Kastmenu Option (Begin)]
    """
    This part enclosed into "Kastmenu Option" deserves only to pass the KastMenu's options directly to 
    the Kastmenu Config Api. With no action on them.
    So you can directly copy this block as it is.
    """
    # -- advanced Menu options:
    og = optparse.OptionGroup(parser, 'Advanced Menu options', description='')
    parser.add_option_group(og)
    og.add_option('-b', "--batch", dest="batch", help="This option requires a value:<mpath>.\n\
        mpath is the value for the menu, e.g.: path:1.abc.2.3.\n\
        The menu path syntax is <option number|option name>.[option number|option name>].")
    og.add_option('-p', "--pause", dest="pause", type=int, help="Works in conjunction with the --batch (-b) option. Pause every screen for the amount of seconds provided.")
    og.add_option('-c', "--noclear", dest="noclear", action="store_true", default=False, help="Works in conjunction with the --batch (-b) option. If set the terminal wont be cleared between each option.")
    og.add_option("--secid", dest="secid", help="(Internal only). Works in conjunction with the kdealer (--kdealer) option. An md5 on the kdealer listener session.")
    og.add_option("--follow_menu", dest="follow_menu", action="store_true", default=False, help='Use this option, if you want to pipe this standalone Menu process with another.\n\
        If, within a Menu Option command you are calling another Manu process, use this option (--follow_menu) to allow them to glue together.\n\
        This would allow the listener and batch options to work as if they were called in the same Menu process.')
    parser.add_option("--show_shortcut", dest="show_shortcut", action="store_true", default=False, help="When kupd is called with option: show_shortcut, It will show At the same menu's level sublink for sub menus.")
    og.add_option('-l', "--log", action="store_true", default=False, dest="log", help="Do log console ?")
    og.add_option('-L', "--log_dir", dest="log_dir", help="The log directory path. Required when log (-l) is provided.")
    og.add_option('-R', "--log_rotate", dest="log_rotate", type=int, default=20, help="(Default 20) How many log files to keep into the log directory.")
    og.add_option('-O', "--log_output", action="store_true", default=False, dest="log_output", help="By default system commands output is not retrieved into the log, this option allows it.")
    og.add_option('-r', "--record", dest="record", action="store_true", default=False, help="Will record all entries to a string ready to use for remote execution mode.")
    og.add_option('-g', "--go", dest="go", help='Same as --batch (-b) but will left the Menu at interactive mode !')
    og.add_option('-G', "--GO", dest="go_menu", help='Same as --go (-g) but will disallow system commands !')

    (options, args) = parser.parse_args(args=args)

    if len(args) >= 1: raise xception.kwadSystemException('Main', self_funct, 'No Argument is supported !')

    # --console: Kdealer support. Try to get secrets from input: Reads Kdealer secid and port from Stdin. The expected Syntax is: kealer:<secid>,<port>
    from kwadlib.security.crypting import getOptSecidFromFile
    from kwadlib import default
    secid, port = getOptSecidFromFile(options.secid, temp_dir=default.getKastTempDir())

    if port==None:
        if options.secid != None: raise xception.kwadSystemException('Main', self_funct, 'Otpion --secid cannot be provided when port is not !')
    else:
        if options.secid==None or not isinstance(options.secid, str):raise xception.kwadParameterException('Main', self_funct, 'Otpion --secid must be provided  as str when port is provided !')
        if options.follow_menu:raise xception.kwadParameterException('Main', self_funct, 'Option --follow_menu cannot be provided when secid provided !')

    # -- advanced Menu options:
    kast_options = {
        'batch': options.batch,
        'pause': options.pause,
        'noclear': options.noclear,
        'port': port,
        'secid': secid,
        'show_shortcut': options.show_shortcut,
        'log': options.log, 'log_output': options.log_output, 'log_dir': options.log_dir, 'log_rotate': options.log_rotate,
        'record': options.record, 'go': options.go, 'go_menu': options.go_menu, 'debug': options.debug,
        }
    # [Kastmenu Option (End)]

    runMenu(kast_options=kast_options, verbose=options.verbose)



if __name__ == '__main__':
    from os import path
    import utils
    import sys

    apimenu_home = utils.getInstallDir()

    ## Set paths
    for _path in ('core',):
        _path = path.normpath(apimenu_home + '/' + _path)
        if not _path in sys.path: sys.path.append(_path)

    main(sys.argv[1:])
