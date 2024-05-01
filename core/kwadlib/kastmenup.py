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



# 001: 2018/08/08 : Do not use pexpect, every where a dispatch is made  on --follow_menu.
#                   Because pexpect watch the output for the whole new menu and the output would be writen twice into the log.
# 003:20220826: Securing the kdealer secid
# 035: 2023/07/21 Node.getTexts was replaced by:Node.getText. (epicxmlp modif 035). May afefect behaviour of self.__content.
# 036: Bug Correction set_config must be called at init.
# 037:20230929: contents switched from list to free wk
# 038:20230929: allow --noclear anytime
# 039:20240109: add session_dir: a temp dir passed per env variable and force Popen, subprocess2, pexpect to use bash.
# 040:20240109: add input sanitize
# 041:20240111: Now command can be provided not only as attribute command but also as text.
# 042:20240115: Add ? will show help and lhelp
# 043:20240116: Bug correction avoid get stuck on input() while running from web.
# 044:20240116: Remove pexpect_spawn as pexpect truncate shell command that not terminate with EOF (e.g.: cat, ls ...).
# 045:20240118: Replace space by _ in Menu's title and Option's name: In order to support Names -b and -g searchs.
# 047:20240221: Allow stopGoing into web.
# 048:20240224: On exit no bottom up update of QConfig (to avoid overriding) !
# 049:20240229: Support of {*password:True,*password_file_option:<fname>}
# 050:20240309: Support of boolean option.
#   By default support for command interpolation is to replace $<value>:
#       mycmd --option1 $value1 --option2 $value1
#   But some langages like python do not support value for boolean option:
#       mycmd --mybool True or mycmd --mybool False.
#   So we add support for --$<option> for boolean type only.
#   This means if we find this into the command (and the option1 type is boolean):
#       mycmd --$option1 --option2 $value1
#   This will be replaced by: mycmd --option1 --option2 $value1 if value for option1 is true,
#   Otherwise we remove it:
#       mycmd --option2 $value1
# 051:20240325: Support for command_enter and command_exit
#               the xml equivalent for programatic: fct_enter, fct_leave_forward and fct_leave_backward

SELF_MODULE='apimenup'
CONFIG = None


from . import tools
KAST_CONFS = tools.getKastConfs()
APIMENU_HOME=tools.getInstallDir()
Logger=tools.Logger
from . import kastmenuxception
import types
from . import kastweblib
from .multilangue import MULTILANG
import threading
from kwadlib import default

SHOW_HOST=True
UP_CAR='+'
UP_MESSAGE='%lang/menu.en/up_message'
DOWN_CAR='-'
DOWN_MESSAGE='%lang/menu.en/down_message'
EXIT_CAR='0'
EXIT_MESSAGE='%lang/menu.en/exit_message'
CHECK_ALL_CAR='c'
CHECK_ALL_MESSAGE='%lang/menu.en/check_all_message'
CONFIRM_MESSAGE='%lang/menu.en/confirm_message'
CONFIRM_EXIT_MESSAGE='%lang/menu.en/confirm_exit_message'
CHOICE_MESSAGE='%lang/menu.en/choice_message'
WAIT_MESSAGE='%lang/menu.en/wait_message'
OPTION_UPPER=True
OPTION_CHECK_MESSAGE1='%lang/menu.en/option_check_message1'
OPTION_CHECK_MESSAGE2='%lang/menu.en/option_check_message2'
INPUT_FIELD_MESSAGE1='%lang/menu.en/input_field_message1'
INPUT_FIELD_MESSAGE2='%lang/menu.en/input_field_message2'
INPUT_FIELD_DEFAULT_MESSAGE='%lang/menu.en/input_field_default_message'
INPUT_FIELD_CHECKIN_MESSAGE='%lang/menu.en/input_field_checkin_message'
COMMAND_LABEL='%lang/menu.en/command_label'
SCREEN_MAX_LINES=10
INDENT=10
LINE_LENGTH=40
OPTION_INDENT=2
OPTION_HELP_INDENT=20
CHOICE_INDENT=OPTION_INDENT + 10
OPTION_VALUE_INDENT=20
SKIP_LINE=True
LANG_DIR='$install_dir/conf'
USE_UNIX_COLORS=True
DONT_USE_UNIX_COLOR=False
UNIX_VIDEO_UNDERLINE="\033[4m"
UNIX_VIDEO_NOUNDERLINE="\033[24m"
UNIX_VIDEO_BACK_NORMAL="\033[m"
##UNIX_VIDEO_REVERS="\033[7m"
VIDEO_COLORS=('BLACK','RED','GREEN','YELLOW','BLUE','PURPLE', 'CYAN', 'WHITE', 'NONE')
class VIDEO_COLOR:
    BLACK='BLACK'
    RED='RED'
    GREEN='GREEN'
    YELLOW='YELLOW'
    BLUE='BLUE'
    PURPLE='PURPLE'
    CYAN='CYAN'
    WHITE='WHITE'
    NONE='NONE'

# See: https://unix.stackexchange.com/questions/124407/what-color-codes-can-i-use-in-my-bash-ps1-prompt
UNIX_VIDEO_COLORS = {\
'frColors':\
	{
		'BLACK' : '30',
		'RED': '31',
		'GREEN': '32',
		'YELLOW': '33',
		'BLUE': '34',
		'PURPLE': '35',
		'CYAN': '36',
		'WHITE': '37'
	},
'bgColors':\
	{
		'BLACK': '40',
		'RED': '41',
		'GREEN': '42',
		'YELLOW': '43',
		'BLUE': '44',
		'PURPLE': '45',
		'CYAN': '46',
		'WHITE': '47',
        'NONE': '99'
	}
    # None: will make white.
}

UNIX_VIDEO_TEMPLATE="\033[{bold};{frColor};{bgColor}m"
UNIX_VIDEO_DEFAULT_BOLD=True
UNIX_VIDEO_DEFAULT_FRCOLOR='BLACK'
UNIX_VIDEO_DEFAULT_BGCOLOR='WHITE'
UNIX_VIDEO_DEFAULT_MENU="\033[1;30;47m"
UNIX_VIDEO_DEFAULT_IOPTION="\033[1;30;44m"


# Remote excution defaults
DEFAULT_PAUSE=5

# Grabed from kdealer
# QUEUE_INPUT=None
# QUEUE_WEB_OUTPUT=None
# ROLES=None
# GROUPS=None

from .kdealerp import QUEUE_MAX
# QUEUE_MAX = 1000

## type: menu,// print,command_result,warn,raise,command_result // input_field, // dialog, // (data_input)
WEB_OUTPUTS={'type': None, 'contents': None}
WEB_ESCAPES=(('/', '&#47;'), ('\\', '&#92;'), ('<', '&lt;'), ('>', '&gt;'), ('@', '&#64;'), (':', '&#58;'), (',', '&#44;'), ("'", '&#39;'), ('"', '&quot;'), ('~', '&#126;'))
# menu/contents: {'id': 'IMENU_' + tools.genUid(), 'is_locked': False, 'sub_type': 'Menu', 'title': title, 'sub_titles': sub_titles, 'items': web_ouput_items}
ROLES_AUTZ=('r', 'x')

SECID_SYNTAX='<string>[//<string>]'

from multiprocessing.managers import BaseManager
class QueueManager(BaseManager):pass
QueueManager.register('get_config')
QueueManager.register('new_api_menu_instance')
QueueManager.register('set_config')
QueueManager.register('get_queue_input')
QueueManager.register('get_queue_output')
QueueManager.register('get_queue_command_output')
QueueManager.register('setKdealerCaller')
QueueManager.register('getKdealerCaller')
QueueManager.register('stop')



def checkRolesAutzSyntax(roles_autz=None, message=None):
    selfMethod='checkRolesAutzSyntax'        
    
    if roles_autz!=None:
        from . import wk
        p=wk.WantedKeywords()
        p.roles_autz={'*rolesAutz': roles_autz}
        
        try:
            wk.getKeywords(wantedKeywords=p, keywords={'roles_autz': roles_autz}, class_exit='Main', method_exit=selfMethod)
        except Exception as e:
            raise kastmenuxception.kastmenuSystemException('Main', selfMethod, 'Incorect syntaxe for attribute:' + message + '. SubException is:' + str(e))
        roles_autz=p.roles_autz

    return roles_autz


def sanitize_input(value, allow_cars=None):
    from kwadlib.security.crypting import sanitize_kastmenu
    if allow_cars!=None and value in allow_cars:return value
    try:
        sanitize_kastmenu(value)
        return value
    except:
        return ''


class Config(threading.Thread):

    # A003: + kdealer option:
    def __init__(self, fct_menu, title, temp_dir, help=None, show_host=SHOW_HOST, up_car=UP_CAR, up_message=UP_MESSAGE, 
        down_car=DOWN_CAR, down_message=DOWN_MESSAGE, exit_car=EXIT_CAR, exit_message=EXIT_MESSAGE, 
        check_all_car=CHECK_ALL_CAR, check_all_message=CHECK_ALL_MESSAGE, choice_message=CHOICE_MESSAGE, 
        confirm_message=CONFIRM_MESSAGE, confirm_exit_message=CONFIRM_EXIT_MESSAGE, wait_message=WAIT_MESSAGE, 
        option_upper=OPTION_UPPER, option_check_message1=OPTION_CHECK_MESSAGE1, option_check_message2=OPTION_CHECK_MESSAGE2, 
        input_field_message1=INPUT_FIELD_MESSAGE1, input_field_message2=INPUT_FIELD_MESSAGE2, 
        input_field_default_message=INPUT_FIELD_DEFAULT_MESSAGE, input_field_checkin_message=INPUT_FIELD_CHECKIN_MESSAGE, 
        command_label=COMMAND_LABEL, screen_max_lines=SCREEN_MAX_LINES, indent=INDENT, option_help_indent=OPTION_HELP_INDENT, 
        option_value_indent=OPTION_VALUE_INDENT, skip_line=SKIP_LINE, dont_use_unix_color=DONT_USE_UNIX_COLOR, lang_dir=LANG_DIR,
        record=False, go_menu=None, go=None, batch=None, pause=None, noclear=False, kdealer=True, port=None, secid=None, is_listening=False, roles_autz_dft=None, roles_mappings=None,
        log=False, log_output=False, log_dir=None, log_rotate=None, call_cde=None, debug=False, show_shortcut=True, verbose=0):
        """
fct_menu : A function to build Menus
    Menu are build on the flow.
    Each time ApiMenu nedds to build a new Menu this function (or method) is called with an unique parameter the parent Menu instance.

title : The main menu title.

temp_dir : Temporary directory

show_host : True/False : If True shows the localhost name on the rigth.

When ApiMenu is called with an xml file, the values of the coming list of parameter
are retreived from the xml file.
Most of these parameters are defined within the xml file througth the menu lang dictionary
into <APIMENU_INSTALL_DIR>/langs.
    
screen_max_lines : If not guiven takes it value from the global variable: SCREEN_MAX_LINES
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@screen_max_lines.
    Number of lines. This the maximum size allowed for a Menu screen.
    
up_car : If not guiven takes it value from the global variable: UP_CAR.
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@up_car.
    Page Up charater.When a Menu screen exceed the screen_max_lines this character symbol is shown.
    Typing this character on the Menu will PageUp.
    
up_message : If not guiven takes it value from the global variable: UP_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@up_message.
    Page Up message. When a Menu screen exceed the screen_max_lines this message is shown.

down_car : If not guiven takes it value from the global variable: DOWN_CAR
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@down_car.
    Page Down charater. When a Menu screen has been paged Up this character Appear.
    Typing this character on the Menu will PageDown.

down_message : If not guiven takes it value from the global variable: DOWN_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@down_message.
    Page Down message. When a Menu screen has been paged Up this message shown.

exit_car : If not guiven takes it value from the global variable: EXIT_CAR
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@exit_car.
    Exit message. Some menu may need an softclass for the user to exit. In this case character Appear.
    Typing this character on the Menu will Exit.    
    
exit_message : If not guiven takes it value from the global variable: EXIT_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@exit_message.
    Exit message. Some menu may need an softclass for the user to exit. In this case this message is shown.
        
check_all_car : If not guiven takes it value from the global variable: CHECK_ALL_CAR
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@check_all_car.
    For Input Menu only. 
    An Input Menu screen lists a set of Input fields.
    These Input fields are proposed for validation (validation softclass may be to run a command)
    througth the check_all_car character.
    Typing this character will validate the IMenu.
    
check_all_message : If not guiven takes it value from the global variable: CHECK_ALL_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@check_all_message.
    An Input Menu screen lists a set of Input fields.
    These Input fields are proposed for validation (validation softclass may be to run a command)
    througth the check_all_car character.
    This message is shown to invite the user to run Validation.
        
choice_message : If not guiven takes it value from the global variable: CHOICE_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@choice_message.
    
confirm_message : If not guiven takes it value from the global variable: CONFIRM_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@confirm_message.
    Confirmation message. Before to run a command some menu may require acceptance.
    This message is the acceptance invitation message.
    
confirm_exit_message : If not guiven takes it value from the global variable: CONFIRM_EXIT_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@confirm_exit_message.
    Exit message. Before to exit, some menu may require acceptance.
    This message is the exit invitation message.
    
wait_message : If not guiven takes it value from the global variable: WAIT_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@wait_message.
    Wait message. Running a command, some menu may need a wait message.
    This message is the way message.
        
option_upper : If not guiven takes it value from the global variable: OPTION_UPPER
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@up_car.
    If True, Menu title are shown in Upper Cases.
    
option_check_message1 : If not guiven takes it value from the global variable: OPTION_CHECK_MESSAGE1
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@option_check_message1.
    This message may be shown into the validation sequence of the value typed by the user.
    
option_check_message2 : If not guiven takes it value from the global variable: OPTION_CHECK_MESSAGE2
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@option_check_message2.
    This message may be shown into the validation sequence of the value typed by the user.
    
input_field_message1 : If not guiven takes it value from the global variable: INPUT_FIELD_MESSAGE1
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@input_field_message1.
    This message may be shown into the input sequence for an Input field (from an IMenu screen).
    
input_field_message2 : If not guiven takes it value from the global variable: INPUT_FIELD_MESSAGE2
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@input_field_message2.
    This message may be shown into the input sequence for an Input field (from an IMenu screen).
    
input_field_default_message : If not guiven takes it value from the global variable: INPUT_FIELD_DEFAULT_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@input_field_default_message.
    This message is displayed showing the default value for an Input field (from an IMenu screen).
    
input_field_checkin_message : If not guiven takes it value from the global variable: INPUT_FIELD_CHECKIN_MESSAGE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@input_field_checkin_message.
    The message is shown when an entry for an Input field (from an IMenu screen) must be chossen beteewn 
    an arbitrary list of predefined values.
    
command_label : If not guiven takes it value from the global variable: COMMAND_LABEL
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@command_label.
    This label is displayed at the begining of the output of the Running Command.
    
option_help_indent : If not guiven takes it value from the global variable: OPTION_HELP_INDENT
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@option_help_indent.
    Integer, how much to indent the help information on the Menu screen.
    
option_value_indent : If not guiven takes it value from the global variable: OPTION_VALUE_INDENT
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@option_value_indent.
    This label is displayed at the begining of the output of the Running Command.
    Integer, how much to indent the value information on the Menu screen.
    
skip_line : If not guiven takes it value from the global variable: SKIP_LINE
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@skip_line.
    If True, will skip a line between each child composing the Menu screen.
    
lang_dir : If not guiven takes it value from the global variable: LANG_DIR
    Called with an xml file, Apimenu passes the value from the Tag/Attribute: config@lang_dir.
    Where is the lang dictionary.
    Generally into : <APIMENU_INSTALL_DIR>/lang
    
    -------------------------------
    | Remote execution parameters |
    -------------------------------
    
record : Will record all entries to a string ready to use for remote execution mode.
    
batch : This option requires a value:<mpath>.
    mpath is the value for the menu path:1.abc.2.3.
    The menu path syntax is <option number|option name>.[option number|option name>].

go : as batch but navigates througth menus.

pause : Works in conjunction with the --batch (-b) option. Pause every screen for the amount of seconds provided.

noclear : Works in conjunction with the --batch (-b) option. I set the terminal wont be cleared between each option.

kdealer : (True by default) Works in conjunction with batch or is_listening.
          kdealer True, run the kdealer menu input/output dispatcher and allows :
          - to follow another independent menus processes, launched by some menu command like if it was the same unique menu.
               These menu command use: --follow_menu.
          - the support of webMenu.
          - the support of batch commands
          - the support of full history for batch commands

port : (Internal only). Works in conjunction with batch or is_listening.
secid : (Internal only). Works in conjunction with the kdealer (--kdealer) option. An md5 on the unique ID of the kdealer listener session.

verbose : Default 0.
    Integer, the verbose level.
        """

        selfMethod='Config'
        # A003: + kdealer option:
        if title==None or not isinstance(title, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'title', 'str', str(title))
        if temp_dir!=None:
            if not isinstance(temp_dir, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'temp_dir', 'temp_dir', str(temp_dir))
        else:
            from kwadlib import default
            temp_dir = default.getKastTempDir()

        if not isinstance(fct_menu, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_menu. The type expected is: ether a function or a method ! Received:' + str(fct_menu) + ' !')
        if not isinstance(show_host, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'show_host', 'bool', str(show_host))
        if up_car==None or not isinstance(up_car, str) or len(up_car)!=1:raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'up_car', 'str/len 1', str(up_car))
        if up_message==None or not isinstance(up_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'up_message', 'str', str(up_message))
        if down_car==None or not isinstance(down_car, str) or len(up_car)!=1:raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'down_car', 'str/len 1', str(down_car))
        if down_message==None or not isinstance(down_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'down_message', 'str', str(down_message))
        if exit_car==None or not isinstance(exit_car, str) or len(up_car)!=1:raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'exit_car', 'str/len 1', str(exit_car))
        if exit_message==None or not isinstance(exit_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'exit_message', 'str', str(exit_message))
        if check_all_car==None or not isinstance(check_all_car, str) or len(up_car)!=1:raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'check_all_car', 'str/len 1', str(check_all_car))
        if check_all_message==None or not isinstance(check_all_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'check_all_message', 'str', str(check_all_message))
        if choice_message==None or not isinstance(choice_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'choice_message', 'str', str(choice_message))
        if confirm_message==None or not isinstance(confirm_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'confirm_message', 'str', str(confirm_message))
        if confirm_exit_message==None or not isinstance(confirm_exit_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'confirm_exit_message', 'str', str(confirm_exit_message))
        if wait_message==None or not isinstance(wait_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'wait_message', 'str', str(wait_message))
        if not isinstance(option_upper, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_upper', 'bool', str(option_upper))
        if option_check_message1==None or not isinstance(option_check_message1, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_check_message1', 'str', str(option_check_message1))
        if option_check_message2==None or not isinstance(option_check_message2, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_check_message2', 'str', str(option_check_message2))
        if input_field_message1==None or not isinstance(input_field_message1, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'input_field_message1', 'str', str(input_field_message1))
        if input_field_message2==None or not isinstance(input_field_message2, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'input_field_message2', 'str', str(input_field_message2))
        if input_field_default_message==None or not isinstance(input_field_default_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'input_field_default_message', 'str', str(input_field_default_message))
        if input_field_checkin_message==None or not isinstance(input_field_checkin_message, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'input_field_checkin_message', 'str', str(input_field_checkin_message))
        if command_label==None or not isinstance(command_label, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command_label', 'str', str(command_label))
        if screen_max_lines==None or not isinstance(screen_max_lines, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'screen_max_lines', 'int', str(screen_max_lines))
        if indent==None or not isinstance(indent, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'indent', 'int', str(indent))
        if option_help_indent==None or not isinstance(option_help_indent, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_help_indent', 'int', str(option_help_indent))
        if option_value_indent==None or not isinstance(option_value_indent, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_value_indent', 'int', str(option_value_indent))
        if not isinstance(skip_line, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'skip_line', 'bool', str(skip_line))
        if not isinstance(dont_use_unix_color, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'dont_use_unix_color', 'bool', str(dont_use_unix_color))
        if lang_dir==None or not isinstance(lang_dir, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'lang_dir', 'str', str(lang_dir))
        if not isinstance(record, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'record', 'bool', str(record))
        if go_menu!=None and not isinstance(go_menu, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'go_menu', 'str', str(go_menu))
        if go!=None and not isinstance(go, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'go', 'str', str(go))
        if batch!=None and not isinstance(batch, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'batch', 'str', str(batch))
        if not isinstance(noclear, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'noclear', 'bool', str(noclear))
        if not isinstance(debug, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'debug', 'bool', str(debug))
        if not isinstance(show_shortcut, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'show_shortcut', 'bool', str(show_shortcut))
        if pause!=None and not isinstance(pause, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'pause', 'int', str(pause))
        if kdealer != None and not isinstance(kdealer, bool): raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'kdealer', 'bool', str(kdealer))
        if port!=None and not isinstance(port, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'port', 'int', str(port))
        if secid!=None and not isinstance(secid, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'secid', 'str', str(secid))
        if is_listening!=None and not isinstance(is_listening, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'is_listening', 'bool', str(is_listening))
        if verbose!=None and not isinstance(verbose, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'verbose', 'int', str(verbose))
        if not isinstance(log, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'log', 'bool', str(log))
        if not isinstance(log_output, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'log_output', 'bool', str(log_output))
        from os import path, mkdir, chmod
        from kwadlib import default
        from hashlib import md5

        if log:
            if log_dir==None:log_dir = default.getKastTempDir()
            log_dir=path.normpath(log_dir)
            if not path.isdir(log_dir):
                if not path.isdir(path.split(log_dir)[0]):raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'The base directory:' + path.split(log_dir)[0] + ' (for log_dir:' + log_dir + ') must exist !')
                mkdir(log_dir)
                chmod(log_dir, 0o777)
        else:log_output=False

        from . import wk
        
        # Set log first
        self.__log_output=log_output
        self.__do_record_for_log_only=False
        self.__log=log
        if self.__log:
            if not record:self.__do_record_for_log_only=True
            record=True
            import time
            import datetime
            import random
            from getpass import getuser
            random.seed()
            id=str(int(time.time()*100))
            rand=random.randint(1, 1000)
            self.__log_file=path.normpath(log_dir + '/smkmenu_' + getuser() + '_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d.%H.%M.%S') + '_random' + str(rand) + Logger.SUFFIX)
            Logger(self.__log_file, log_rotate)
            print('* Call_cde:', call_cde)
        else:self.__log_file=None
        
        if roles_autz_dft==None:roles_autz_dft={'*anyone':'+all'}
        self.__roles_autz_dft=checkRolesAutzSyntax(roles_autz_dft, message='roles_autz_dft')
        if '*anyone' in self.__roles_autz_dft and '+all' in self.__roles_autz_dft['*anyone'].split(';'):optimistic='+*optimistic'
        else:optimistic='-*optimistic'
        if '*anyone' not in self.__roles_autz_dft:self.__roles_autz_dft['*anyone']=optimistic
        elif self.__roles_autz_dft['*anyone'].find('*optimistic')<0:self.__roles_autz_dft['*anyone']+=';' + optimistic        
        
        if go!=None or go_menu!=None:
            if go!=None:batch=go
            else:batch=go_menu
            self.__is_going=True
        else:
            self.__is_going=False
            
        if go_menu!=None:self.__is_menu_going=True
        else:self.__is_menu_going=False
        
        # roles_mappings:
        if roles_mappings!=None:
            for role in roles_mappings:
                roles=roles_mappings[role]
                p=wk.WantedKeywords()
                p.roles={'*type': 'dict', '*dtype': {'users': {'*type': 'list'}, 'groups': {'*type': 'list'}}}
                wk.getKeywords(wantedKeywords=p, keywords={'roles': roles}, class_exit=self.__class__.__name__, method_exit=selfMethod)
            self.__roles_mappings=roles_mappings
            
        else:self.__roles_mappings={}
        
        # - reversed roles_mappings:
        self.__reversed_roles_mappings_groups={}
        self.__reversed_roles_mappings_users={}
        
        for role in self.__roles_mappings:
            roles=roles_mappings[role]
            for user in roles['users']:
                if user not in self.__reversed_roles_mappings_users:self.__reversed_roles_mappings_users[user]=[]
                self.__reversed_roles_mappings_users[user].append(role)
            for group in roles['groups']:
                if group not in self.__reversed_roles_mappings_groups:self.__reversed_roles_mappings_groups[group]=[]
                self.__reversed_roles_mappings_groups[group].append(role)
        
        self.__verbose=verbose
        
        ##  Remote execution parameters
        
        if batch==None:
            if pause!=None:raise kastmenuxception.kastmenuSystemException('Main', selfMethod, 'Parameter --pause(-P) cannot be provided when batch is not !')
            # A038: if noclear:raise apimenuxception.kastmenuSystemException('Main', selfMethod, 'Parameter --noclear(-C) cannot be provided when batch is not !')

        # DSisabled to try to allow go from webMenu:
        ## if batch!=None and is_listening:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Parameters --batch (-b), --go (-g), --GO (-G) and is_listening are exlusive !')
        # A003:
        if (secid!=None and port==None) or (secid == None and port != None): raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Parameters --secid (-s) and --port (-p) work together ! When one is provided the other one must be as well.')
        # D003: if (batch!=None or secid!=None or is_listening) and port==None:raise apimenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Parameter --port(-p) is required when --batch(-b), --secid(-s) or is_listening is provided !')
        if batch!=None and not kdealer:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Parameter --kdealer (True) is required when --batch(-b) is provided !')
        if is_listening and not kdealer:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Parameter --kdealer (True) is required when is_listening is provided !')


        # A kdealer can be shared amongst several menus on a partition, so it must be associated with a menu instance id.
        secid_menuid=None
        if secid!=None:
            spl=secid.split('//')
            if len(spl)>1:
                if len(spl)!=2 or spl[0].strip()=='' or spl[1].strip()=='':
                    raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Incorrect secid:' + secid + ', the secid syntax is:' + SECID_SYNTAX + ' !')
                secid, secid_menuid=spl[0].strip(), spl[1].strip()
        self.__secid=None
        self.__secid_md5 = None
        self.__secid_menuid = None

        # A003:
        if secid != None:
            self.__secid = secid
            m = md5()
            m.update(bytes(self.__secid, 'utf-8'))
            self.__secid_md5 = str(m.hexdigest())


            
        # - multilang support
        MULTILANG.init(verbose=verbose)
        title, help, up_message, down_message, exit_message, check_all_message, choice_message, confirm_message, confirm_exit_message, wait_message, web_wait_message, option_check_message1, option_check_message2, input_field_message1, input_field_message2, input_field_default_message, input_field_checkin_message, command_label=\
            MULTILANG.convert(title, help, up_message, down_message, exit_message, check_all_message, choice_message, confirm_message, confirm_exit_message, wait_message, '%lang/menu.en/wait_message', option_check_message1, option_check_message2, input_field_message1, input_field_message2, input_field_default_message, input_field_checkin_message, command_label)

        self.__isAlive=True
        self.__initialMenu=None
        self.__fct_menu=fct_menu
        self.__title=title
        self.__temp_dir=temp_dir
        self.__help=help
        self.__show_host=show_host
        self.__up_car=up_car
        self.__up_message=up_message
        self.__down_car=down_car
        self.__down_message=down_message
        self.__exit_car=exit_car
        self.__exit_message=exit_message
        self.__check_all_car=check_all_car
        self.__check_all_message=check_all_message        
        self.__choice_message=choice_message        
        self.__confirm_message=confirm_message
        self.__confirm_exit_message=confirm_exit_message
        self.__wait_message=wait_message
        self.__web_wait_message=web_wait_message
        self.__option_upper=option_upper
        self.__option_check_message1=option_check_message1
        self.__option_check_message2=option_check_message2
        self.__input_field_message1=input_field_message1
        self.__input_field_message2=input_field_message2
        self.__input_field_default_message=input_field_default_message
        self.__input_field_checkin_message=input_field_checkin_message
        self.__command_label=command_label
        self.__screen_max_lines=screen_max_lines
        self.__menu_pipes=[]
        self.__indent=indent
        self.__option_help_indent=option_help_indent
        self.__option_value_indent=option_value_indent
        self.__skip_line=skip_line
        self.__last_system_command_ret=0
        self.__isFirstMenuProcess=True
        
        if tools.getOsType()!='unix' or dont_use_unix_color:self.__use_unix_colors=False
        else:self.__use_unix_colors=True
        self.__do_record=record
        self.__records=[]
        self.__record_names=[]
        
        # batch
        self.__batch=batch
        if self.__batch==None:self.__is_batch=False
        else:
            self.__batch=str(self.__batch)
            if self.__batch.startswith('Names:'):self.__batch=self.__batch[6:]
            self.__is_batch=True
            
        self.__pause=pause          
        self.__noclear=noclear
        self.__debug=debug

        self.show_shortcut=show_shortcut

        # web (is_listening) or secid + port or batch:
        self.__port=port
        self.__is_listening=is_listening
        self.__kdealer_process_handler=None
        
        # Shared REsources
        self.__shared_queueInput=None
        self.__shared_queueWebOutput=None
        self.__shared_queueWebCommandOutput=None
        self.__shared_roles=None
        self.__shared_user=None
        self.__shared_groups=None

        # A036:
        doSectConfig = False

        ## Q Factory (Begin) ##
        # Note: The following: secid, port are passed to ext menu calls
        # M003: if self.isBatch() or self.isListening() or secid!=None or port!=None:
        if self.isBatch() or self.isListening() or secid!=None or kdealer:

            # Create a new kdealer process:
            if self.__port == None:
                # Get kdealer_port_range:
                from kwadlib.default import getFreePortOnLocalHost
                from os import path
                self.__port = getFreePortOnLocalHost()
                if self.__port == None: raise Exception('Unable to find a free port into the provided port range into kwad_conf !')

                self.__secid = 'SECID_' + tools.genUid()
                m = md5()
                m.update(bytes(self.__secid, 'utf-8'))
                self.__secid_md5 = str(m.hexdigest())
                self.__kdealer_process_handler = launchProcessKdealer(secid_md5=self.__secid_md5, secid=self.__secid, port=self.__port, queue_max=QUEUE_MAX, verbose=0)

            # Connect to Existing kdealer process:
            else:
                try:
                    import socket
                    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect(('localhost', self.__port))
                    s.close()
                except:
                    raise Exception('Unable to fin an Active kdealer on the provided port:' + str(self.__port) + ' !')

            self.__KMQ = QueueManager(address=('localhost', int(self.__port)), authkey=bytes(self.__secid, 'utf-8'))
            self.__KMQ.connect()
            # is kdealer Manager:
            if self.__kdealer_process_handler!=None:
                from os import getpid
                self.__KMQ.setKdealerCaller(getpid())

            if secid_menuid!=None:
                self.__secid_menuid=secid_menuid
                # Retreive CONFIG
                # todo: ACONFIGS may need to be converted to a BaseManager.dit() to pass ?
                ACONFIGS=self.__KMQ.get_config(api_menu_instance=self.__secid_menuid)
                try:ACONFIGS
                except:raise Exception('Unable to retreive Apimenu persistent Config !')
                ACONFIGS=ACONFIGS.copy() # Convert multiprocessing object to dict.
                if not is_listening:self.__is_listening=ACONFIGS['is_listening']
                self.__is_going=ACONFIGS['is_going']
                self.__is_menu_going=ACONFIGS['is_menu_going']
                self.__is_batch=ACONFIGS['is_batch']
                self.__pause=ACONFIGS['pause']
                self.__noclear=ACONFIGS['noclear']
                self.__debug=ACONFIGS['debug']
                self.show_shortcut=ACONFIGS['show_shortcut']
                self.__verbose=ACONFIGS['verbose']
                self.__do_record=ACONFIGS['do_record']
                self.__do_record_for_log_only=ACONFIGS['do_record_for_log_only']
                self.__records=ACONFIGS['records']
                self.__record_names=ACONFIGS['record_names']
                self.__shared_user=ACONFIGS['user']
                self.__shared_groups=ACONFIGS['groups']
                self.__isFirstMenuProcess=False
                # log
                self.__log=ACONFIGS['log']
                self.__log_output=ACONFIGS['log_output']
                self.__log_file=ACONFIGS['log_file']
                if self.__log:Logger(self.__log_file)
            else:
                # A036:
                doSectConfig=True
                # - Returned BaseManager string need to be stripped !
                self.__secid_menuid=self.__KMQ.new_api_menu_instance().strip()

            # Retreive QUEUE_INPUT
            if self.isBatch() or self.isListening():
                if not self.isListening():self.__use_unix_colors=False # todo: maybe uncheck this for self.isListening() only.
                self.__shared_queueInput=self.__KMQ.get_queue_input(api_menu_instance=self.__secid_menuid)
                try:self.__shared_queueInput
                except:raise Exception('Unable to retreive Input Queue !')
            
            # Retreive QUEUE_OUTPUT
            if self.isListening():
                self.__shared_queueWebOutput=self.__KMQ.get_queue_output(api_menu_instance=self.__secid_menuid)
                try:self.__shared_queueWebOutput
                except:raise Exception('Unable to retreive Output Queue !')

            # Retreive QUEUE_COMMAND_OUTPUT
            if self.isListening():
                self.__shared_queueWebCommandOutput=self.__KMQ.get_queue_command_output(api_menu_instance=self.__secid_menuid)
                try:self.__shared_queueWebCommandOutput
                except:raise Exception('Unable to retreive Command Output Queue !')
        ## Q Factory (End) ##
        
    
        ## Roles Mapping
        if self.__shared_roles==None and secid_menuid==None:
            if tools.getOsType()=='unix':
                import os, pwd, grp
                # Retreive system user/group (not effective)
                # - user
                self.__shared_user=pwd.getpwuid(os.getuid()).pw_name
                # - groups
                self.__shared_groups=[]
                gids=os.getgroups()
                for gid in gids:self.__shared_groups.append(grp.getgrgid(gid).gr_name)
            else:
                from getpass import getuser
                # Retreive system user/group (not effective)
                # - user
                self.__shared_user=getuser()
                # - groups
                self.__shared_groups=[]
        
        self.mapRoles()

        ## Q Feed
        if self.isBatch() and self.__batch!=None:
            packets=self.__batch.split('.')
            for packet in packets:
                # Note: '' are allowed : They mean [ENTER KEY] ! if packet=='' or packet.isspace():continue
                self.getSharedQueueInput().put(packet, False)
                
            self.getSharedQueueInput().put('suicide', False)

        if self.isListening():
            self.__queue_wait=True
            # self.__queue_buffer_output=Queue.Queue(QUEUE_MAX)
            # Initiate the batch stuff, cause will run in Thread
            threading.Thread.__init__(self)    
            self.setName('ConfigThread')
        elif self.isBatch():self.__queue_wait=False
            
        if self.isListening():self.__noclear=True

        # A036:
        if doSectConfig:self.__KMQ.set_config(api_menu_instance=self.__secid_menuid, roles=self.getSharedRoles(), user=self.getSharedUser(), groups=self.getSharedGroups(), is_listening=self.__is_listening, records=self.__records, record_names=self.__record_names, is_going=self.__is_going, is_menu_going=self.__is_menu_going, is_batch=self.__is_batch, pause=self.__pause, noclear=self.__noclear, do_record=self.__do_record, do_record_for_log_only=self.__do_record_for_log_only, log=self.__log, log_output=self.__log_output, log_file=self.__log_file, debug=self.__debug, show_shortcut=self.show_shortcut, verbose=self.__verbose)

    def getTempDir(self):
        return self.__temp_dir

    def getVerbose(self):
        return self.__verbose

    def stop(self):
        self.__isAlive=False
        import sys

        if self.__kdealer_process_handler!=None: # is kdealer manager
            if self.__KMQ!=None: self.__KMQ.stop()
            self.killKdealer()
            sys.exit(0)

        if not self.isListening():
            sys.exit(0)

    def isAlive(self):
        return self.__isAlive
    
    def isFirstMenuProcess(self):
        return self.__isFirstMenuProcess

    def getKdealerHandler(self):
        return self.__kdealer_process_handler

    def killKdealer(self):
        from os import kill, getpid
        from signal import SIGKILL
        if self.__kdealer_process_handler!=None:
            self.__kdealer_process_handler.terminate()  # send sigterm, or ...
            self.__kdealer_process_handler.kill()
            while self.__kdealer_process_handler.poll()==None:
                self.__kdealer_process_handler.kill()

        kill(getpid(), SIGKILL)

        # Note unix only: os.kill(self.__kdealer_process_handler, signal.SIGQUIT)

    def garbadge(self):
        # Update kdealer Set Config infos:
        self.__KMQ.set_config(api_menu_instance=self.__secid_menuid, records=self.__records, record_names=self.__record_names, is_going=self.__is_going, is_menu_going=self.__is_menu_going, is_batch=self.__is_batch, pause=self.__pause)
        """ D048: No bottom up update of QConfig:
        if self.__secid!=None:
            self.__KMQ.set_config(api_menu_instance=self.__secid_menuid, roles=self.getSharedRoles(), user=self.getSharedUser(), groups=self.getSharedGroups(), is_listening=self.__is_listening, records=self.__records, record_names=self.__record_names, is_going=self.__is_going, is_menu_going=self.__is_menu_going, is_batch=self.__is_batch, pause=self.__pause, noclear=self.__noclear, do_record=self.__do_record, do_record_for_log_only=self.__do_record_for_log_only, log=self.__log, log_output=self.__log_output, log_file=self.__log_file, debug=self.__debug, show_shortcut=self.show_shortcut, verbose=self.__verbose)
        """
    
    def getSecid(self):
        return self.__secid

    def _setInitialMenu(self, menu):
        self.__initialMenu=menu
    
    """    
    Shared Resources.
    """
    def getSharedQueueInput(self):
        return self.__shared_queueInput
    
    def getSharedQueueWebOutput(self):
        return self.__shared_queueWebOutput

    def getSharedQueueWebCommandOutput(self):
        return self.__shared_queueWebCommandOutput
    
    def getSharedRoles(self):
        return self.__shared_roles
    
    def getSharedUser(self):
        return self.__shared_user
    
    def getSharedGroups(self):        
        return self.__shared_groups
    
    """
    Programatic Menu Input/Output methods
    for support of both loccal and remote controled menu.
    """
    def iodialog(self, message, menu=None, is_value=False, option_index=None, id=None, id_type=None):
        selfMethod='iodialog'
        if not isinstance(message, str) or message.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'message', 'str', str(message))
        if not isinstance(menu, BaseMenu):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'menu', 'BaseMenu', str(menu))
        if self.getSharedQueueWebOutput()!=None:
            if option_index!=None and not isinstance(option_index, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_index', 'int', str(option_index))
            if not isinstance(id, str) or id.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id', 'str', str(id))
            if not isinstance(id_type, str) or id_type.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(id_type))

        ## return self.read(message, isChoice=True, id=id, id_type=id_type)
        # , doConfirm=False, doConfirmOk='y', doConfirmKo='n', isChoice=False, is_value=False
        if is_value:
            doConfirm=False
            is_value = True
        else:
            doConfirm = True
            is_value = False

        return self.read(message, doConfirm=doConfirm, doConfirmOk='y', doConfirmKo='n', isChoice=False, is_value = is_value, id=id, id_type=id_type)

    def iowait(self, message, menu=None, option_index=None, id=None, id_type=None, fct_name=None):
        selfMethod='iowait'
        if not isinstance(message, str) or message.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'message', 'str', str(message))
        if not isinstance(menu, BaseMenu):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'menu', 'BaseMenu', str(menu))
        if self.getSharedQueueWebOutput()!=None:
            if option_index!=None and not isinstance(option_index, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_index', 'int', str(option_index))
            if not isinstance(id, str) or id.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id', 'str', str(id))
            if not isinstance(id_type, str) or id_type.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(id_type))
            if not isinstance(fct_name, str) or fct_name.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(fct_name))

        if message!=self.__wait_message:
            """
            if self.getSharedQueueWebOutput()!=None:
                web_outputs=dict(WEB_OUTPUTS)
                web_outputs['keys']={'menu': menu.getPipeUid()}
                if option_index!=None:web_outputs['keys']['option']=str(option_index)
                web_outputs['type']='print'
                web_outputs['contents']={'stype': 'io', 'fct_name': fct_name, 'id': id, 'id_type': id_type, 'messages': message.split('\n')}
                self.printweb(web_outputs)
            """
            if self.getSharedQueueWebCommandOutput() != None:
                coid = tools.genUid()
                self.getSharedQueueWebCommandOutput().put(coid + '[[COID]][[NEW_PROCESS_OUTPUT]]', False)  # new ooid
                self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + message, False)

            self.println(line=message)
            self.println()

        self.read(self.__wait_message, id=id, id_type=id_type)

    def ioprint(self, message, menu=None, option_index=None, id=None, id_type=None, fct_name=None):
        selfMethod='ioprint'
        if not isinstance(message, str) or message.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'message', 'str', str(message))
        if not isinstance(menu, BaseMenu):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'menu', 'BaseMenu', str(menu))
        if self.getSharedQueueWebOutput()!=None:
            if option_index!=None and not isinstance(option_index, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_index', 'int', str(option_index))
            if not isinstance(id, str) or id.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id', 'str', str(id))
            if not isinstance(id_type, str) or id_type.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(id_type))
            if not isinstance(fct_name, str) or fct_name.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(fct_name))

        if self.getSharedQueueWebOutput()!=None:
            web_outputs=dict(WEB_OUTPUTS)
            web_outputs['keys']={'menu': menu.getPipeUid()}
            if option_index!=None:web_outputs['keys']['option']=str(option_index)
            web_outputs['type']='print'
            web_outputs['contents']={'stype': 'io', 'fct_name': fct_name, 'id': id, 'id_type': id_type, 'messages': message.split('\n')}
            self.printweb(web_outputs)

        self.println(line=message)

    def ioprocess(self, command, menu=None, option_index=None, id=None, id_type=None, fct_name=None, useshell=False):
        selfMethod='ioprocess'
        if not isinstance(command, str) or command.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command', 'str', str(command))
        if not isinstance(menu, BaseMenu):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'menu', 'BaseMenu', str(menu))
        if self.getSharedQueueWebOutput()!=None:
            if option_index!=None and not isinstance(option_index, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_index', 'int', str(option_index))
            if not isinstance(id, str) or id.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id', 'str', str(id))
            if not isinstance(id_type, str) or id_type.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(id_type))
            if not isinstance(fct_name, str) or fct_name.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(fct_name))
        cde_output=''
        if option_index!=None:option_or_menu=menu.getChild(option_index)
        else:option_or_menu=menu

        do_follow_menu = False

        if self.getSharedQueueWebOutput()!=None:
            web_outputs=dict(WEB_OUTPUTS)
            web_outputs['keys']={'menu': menu.getPipeUid()}
            if option_index!=None:web_outputs['keys']['option']=str(option_index)
            web_outputs['type']='command_result'
            web_outputs['contents']={'stype': 'io', 'fct_name': fct_name, id_type: id, 'raws': None, 'outputs': None, 'return_code': None}
        else:
            web_outputs=None
        self.println()

        if command.find('--follow_menu') > 0:
            # D003: do_follow_menu = True

            # - Alert --follow_menu
            if self.doRecord() and self.__port==None:
                if web_outputs==None:
                    # M003: apimenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'Option --follow_menu was found in this command. Please recall this menu with option --port(-p) when recording !').warn()
                    kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'Option --follow_menu was found in this command. Please recall the top menu with option --kdealer (True) when recording !').warn()
                else:
                    _web_outputs=dict(web_outputs)
                    _web_outputs['type']='warn'
                    # M003: _web_outputs['contents']={'stype': 'io', 'fct_name': fct_name, 'type': 'whenRecodingCallWithPort', 'id': id, 'id_type': id_type, 'messages': stripOutput('Option --follow_menu was found in this command. Please recall this menu with option --port(-p) when recording !')}
                    _web_outputs['contents']={'stype': 'io', 'fct_name': fct_name, 'type': 'whenRecodingCallWithPort', 'id': id, 'id_type': id_type, 'messages': stripOutput('Option --follow_menu was found in this command. Please recall the top menu with option --kdealer (True) when recording !')}
                    self.printweb(_web_outputs)

                self.read(self.__wait_message, id=id, id_type=id_type)


        # - Replace --follow_menu and push caracteristics
        # A002:
        if self.__secid != None:
            if command.find('--follow_menu') > 0:
                do_follow_menu = True
                # Prepare stdin for next MenuMaker process:
                from kwadlib.security.crypting import setSecidToFile
                setSecidToFile(self.__secid_md5, self.__secid + '//' + self.__secid_menuid,  self.__port, temp_dir=default.getKastTempDir())
                ## Replace parameter:
                command = command.replace('--follow_menu', '--secid ' + self.__secid_md5)

            ## Set Config:
            # Update kdealer Set Config infos:
            # kmq = QueueManager(address=('localhost', int(self.__port)), authkey=self.__secid)
            # kmq.connect()
            self.__KMQ.set_config(api_menu_instance=self.__secid_menuid, roles=self.getSharedRoles(),
                                  user=self.getSharedUser(), groups=self.getSharedGroups(),
                                  is_listening=self.__is_listening, records=self.__records,
                                  record_names=self.__record_names, is_going=self.__is_going,
                                  is_menu_going=self.__is_menu_going, is_batch=self.__is_batch, pause=self.__pause,
                                  noclear=self.__noclear, do_record=self.__do_record,
                                  do_record_for_log_only=self.__do_record_for_log_only, log=self.__log,
                                  log_output=self.__log_output, log_file=self.__log_file,
                                  debug=self.__debug, show_shortcut=self.show_shortcut, verbose=self.__verbose)



            """ D003:                
            command = command.replace('--follow_menu', '--secid ' + self.__secid + '//' + self.__secid_menuid + ' --port ' + str(self.__port))
            # Update kdealer Set Config infos:
            # kmq = QueueManager(address=('localhost', int(self.__port)), authkey=self.__secid)
            # kmq.connect()
            self.__KMQ.set_config(api_menu_instance=self.__secid_menuid, roles=self.getSharedRoles(), user=self.getSharedUser(), groups=self.getSharedGroups(), is_listening=self.__is_listening, records=self.__records, record_names=self.__record_names, is_going=self.__is_going, is_menu_going=self.__is_menu_going, is_batch=self.__is_batch, pause=self.__pause, noclear=self.__noclear, do_record=self.__do_record, do_record_for_log_only=self.__do_record_for_log_only, log=self.__log, log_output=self.__log_output, log_file=self.__log_file)
            """

        # - Show command:
        if web_outputs != None:
            web_outputs['contents']['raws'] = [command]

        self.println(line=command)
        self.println()

        # A039:
        sd = menu.getSessionDir(self)
        if sd != None:
            envs = {'KSESSION_DIR': sd}
            if self.__log_file != None: envs['KLOG_FILE'] = self.__log_file
        else:
            envs = None

        # - Execute command
        if web_outputs==None:
            if useshell:cde=command
            else:cde=command.split()

            # A001:
            if (not (self.doLog() and  self.doLogOutput()) ) or do_follow_menu:
                system_command_ret, stdout, stderr=tools.subprocess2(cde, doPrint=True if option_or_menu.getVerbose_exec_command() else False, stdout=None, stderr=None, wait=True, verbose_zero_temp_dir=None, useshell=useshell, envs=envs )
            else:
                # A044
                try:
                    from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
                    from subprocess import CalledProcessError
                    from io import StringIO
                    import sys
                    sb = StringIO()

                    popen = Popen(command, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                    for stdout_line in iter(popen.stdout.readline, ""):
                        sys.stdout.write(stdout_line) # write to log file
                        sb.write(stdout_line)

                    popen.stdout.close()
                    system_command_ret = popen.wait()

                except CalledProcessError as e:
                    system_command_ret = e.returncode
                    message = 'Execution Error: %s' % str(e.output)
                    sys.stdout.write(message) # write to log file
                    sb.write(message)

                except Exception as e:
                    system_command_ret = 1
                    message = 'Execution Error: %s' % str(e)
                    sys.stdout.write(message) # write to log file
                    sb.write(message)

                cde_output = sb.getvalue()

                """ D044
                # Allow output retreiving straigth from the TTY (pexpect known bug write more than once last line)
                try:
                    # M039
                    system_command_ret, cde_output=pexpect_spawn(command, envs = envs) # M039
                except KeyboardInterrupt:
                    import sys
                    sys.exit(1)
                """

        else:
            # Announcing long task with a preceding event !
            _web_outputs=dict(web_outputs)
            _web_outputs['type']='raise'
            _web_outputs['contents']={'type': 'APIMENU_NEXT_GET_MAY_BE_LONG'}
            self.printweb(_web_outputs)

            # A012:
            """
            fileout = path.normpath(self.__temp_dir + '/' + 'process_output_' + id + '_' + tools.genUid() + '.dat')
            c = Popen(command, stderr=fileout, stdout=fileout, shell=True)
            """
            system_command_ret, cde_output =self.execWebCommand(command, envs=envs, do_follow_menu=do_follow_menu)


        # A002:
        # - Retreive caracteristics
        if self.__secid!=None:
            ACONFIGS=self.__KMQ.get_config(api_menu_instance=self.__secid_menuid)
            try:ACONFIGS
            except:raise Exception('Unable to retreive Apimenu persistent Config !')
            ACONFIGS=ACONFIGS.copy() # Convert multiprocessing object to dict.
            was_going=self.__is_going
            self.__is_going=ACONFIGS['is_going']
            self.__is_menu_going=ACONFIGS['is_menu_going']
            self.__is_batch=ACONFIGS['is_batch']
            self.__records=ACONFIGS['records']
            self.__record_names=ACONFIGS['record_names']
            # log: Removed:
            ## self.__log=ACONFIGS['log']
            ## self.__log_file=ACONFIGS['log_file']
            ## if self.__log:Logger(self.__log_file)
            if was_going and not self.__is_going:self.__shared_queueInput=None

        # A001:
        if not do_follow_menu  or system_command_ret!=0: # No if was following !
            if web_outputs!=None:
                pass
                """ D012:
                web_outputs['contents']['outputs']=stripOutput(cde_output)
                web_outputs['contents']['return_code']=system_command_ret
                self.printweb(web_outputs)
                """
            else:
                if system_command_ret!=0:
                    self.println()
                    self.println(line='Echec running command ! Return code is:' + str(system_command_ret))
            self.println()

            self.read(self.__wait_message, id=id, id_type=id_type)

        return system_command_ret, cde_output

    def ioraise(self, message, menu=None, option_index=None, id=None, id_type=None, fct_name=None, except_type=None):
        selfMethod='ioraise'
        if not isinstance(message, str) or message.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'message', 'str', str(message))
        if not isinstance(menu, BaseMenu):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'menu', 'BaseMenu', str(menu))
        if self.getSharedQueueWebOutput()!=None:
            if option_index!=None and not isinstance(option_index, int):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'option_index', 'int', str(option_index))
            if not isinstance(id, str) or id.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id', 'str', str(id))
            if not isinstance(id_type, str) or id_type.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(id_type))
            if not isinstance(fct_name, str) or fct_name.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(fct_name))
            if not isinstance(except_type, str) or except_type.strip()=='':raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'id_type', 'str', str(except_type))

        if self.getSharedQueueWebOutput()!=None:
            web_outputs=dict(WEB_OUTPUTS)
            web_outputs['keys']={'menu': menu.getPipeUid()}
            if option_index!=None:web_outputs['keys']['option']=str(option_index)
            web_outputs['type']='raise'
            web_outputs['contents']={'stype': 'io', 'fct_name': fct_name, 'type': 'io/' + fct_name + '/' + except_type, 'id': id, 'id_type': id_type, 'messages': stripOutput(message)}
            self.printweb(web_outputs)
        else:
            if self.__verbose >= 20:
                import traceback, sys
                traceback.print_stack(file=sys.stdout)
        kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, message).warn()
        self.println()

        self.read(self.__wait_message, id=id, id_type=id_type)

    def mapRoles(self):
        self.__shared_roles=['*anyone']

        if self.__shared_user in self.__reversed_roles_mappings_users:
            self.__shared_roles.extend(self.__reversed_roles_mappings_users[self.__shared_user])

        for group in self.__shared_groups:
            if group in self.__reversed_roles_mappings_groups:
                self.__shared_roles.extend(self.__reversed_roles_mappings_groups[group])

        if False: # todo: Never cause deprecated
            print('* Initial User:', self.__shared_user)
            print('* Groups:', str(self.__shared_groups)[1:-1].replace("'", ''))
            print('* Mapped roles:', str(self.__shared_roles)[1:-1].replace("'", ''))
            print()

    def getRolesAutzDft(self):
        return self.__roles_autz_dft

    def doRecord(self):
        return self.__do_record

    def doRecordForLogOnly(self):
        return self.__do_record_for_log_only

    def doLog(self):
        return self.__log

    def doLogOutput(self):
        return self.__log_output

    def isGoing(self):
        return self.__is_going

    def isMenuGoing(self):
        return self.__is_menu_going

    def stopGoing(self):
        self.__is_going=False
        self.__is_menu_going=False
        self.__batch=None
        self.__is_batch=False
        self.__pause=0
        # D047: self.__shared_queueInput=None

    def isBatch(self):
        return self.__is_batch

    def getBatchCde(self):
        return self.__batch

    def getTempDir(self):
        return self.__temp_dir

    def isListening(self):
        return self.__is_listening

    def getLastSystemCommandRet(self):
        return self.__last_system_command_ret

    def __clearPipe(self):
        self.__menu_pipes=[]

    def __addMenuToPipe(self, menu):
        menu._setPipeIndex(len(self.__menu_pipes))
        if len(self.__menu_pipes)!=0:self.__menu_pipes[-1].leave_forward(self, id='NEW_NOID', id_type='mid')
        self.__menu_pipes.append(menu)
        menu._setPipeUid(menu.getTitle())

    def __delMenuFromPipe(self, index):
        selfMethod='__delMenuFromPipe'
        if index >= len(self.__menu_pipes):raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'No menu found in the MenuPipe at index:' + str(index) + ' !')
        del self.__menu_pipes[index]

    def go(self, menu, wait=False):
        self._setInitialMenu(menu)
        menu.setConfig(self) # Interception of programatic menus.

        if self.isListening():
            self.start() # Start regular Menu.

            if wait:self.join()
            else:
                kastweblib.WEB_OUTPUTS = WEB_OUTPUTS
                webFacade=kastweblib.WebFacade(port=self.__port, secid=self.__secid, queue_input=self.getSharedQueueInput(), queue_output=self.getSharedQueueWebOutput(), queue_command_output=self.getSharedQueueWebCommandOutput(), config=self)
                return webFacade

        else:self.run()

    def run(self):
        selfMethod='run'
        from io import StringIO
        menu=self.__initialMenu
        web_outputs=None

        self.__clearPipe()
        menu._cantBeDeleted()
        self.__addMenuToPipe(menu)

        exit=False
        while not exit and self.isAlive():
            if len(self.__menu_pipes)==1:menu=self.__menu_pipes[0]
            else:
                menu=self.__menu_pipes[-1]

            menu.enter(self, id='ENTER_NOID', id_type='mid')

            try:
                menu.calcPages(self.__screen_max_lines, self.__skip_line)
            except Exception as e:
                if self.__debug: raise
                self.__delMenuFromPipe(menu.getPipeIndex())
                if self.getSharedQueueWebOutput()!=None:
                    web_outputs=dict(WEB_OUTPUTS)
                    web_outputs['keys']={'menu': menu.getPipeUid()}
                    web_outputs['type']='raise'
                    web_outputs['contents']={'type': 'MenuHasNoEntry', 'id': None, 'id_type': None, 'messages': stripOutput(str(e))}
                    self.printweb(web_outputs)

                self.println()
                self.drawLine()
                kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, str(e)).warn()
                self.println()

                self.read(self.__wait_message, id=id, id_type='mid')
                continue


            if not self.__noclear:tools.clearConsol()

            ## - Display base
            host=''
            if self.__show_host:
                import socket
                host='[' + socket.gethostname() + ']' + 5*' '

            title=self.__title.upper()
            self.__middle=self.__indent + int(len(host + title)/2)

            if self.getSharedQueueWebOutput()!=None:
                if host=='':host=None
                web_outputs=dict(WEB_OUTPUTS)
                web_outputs['type']='menu'
                web_outputs['contents']={'big_title': {'title': title.strip(), 'host': host.strip()[1:-1], 'user': default.getUser()}, 'choices': {'exit_car': None, 'up_car': None, 'down_car': None, 'check_all_car': None}}

            self.println(line=self.__indent*' ' + host + title)
            self.println()

            ## - Display menu
            if isinstance(menu, Menu):index=self.printMenu(menu, web_outputs=web_outputs)
            else:index=self.printIMenu(menu, web_outputs=web_outputs)

            ## - Display base
            self.println()
            self.println()

            sb=StringIO()
            sb.write((self.__indent + OPTION_INDENT+3)*' ' + '(' + self.__exit_message.strip() +':' + self.__exit_car)
            if menu.getHelp()!=None or menu.getHelp()!=None:
                sb.write(', Help:?')
            if self.getSharedQueueWebOutput()!=None:web_outputs['contents']['choices']['exit_car']=self.__exit_car
            if menu.getPageNumber()>1 and  menu.getCurrentPageIndex()!=menu.getPageNumber()-1:
                sb.write(' ' + self.__up_message +':' + self.__up_car)
                if self.getSharedQueueWebOutput()!=None:web_outputs['contents']['choices']['up_car']=self.__up_car
            if menu.getCurrentPageIndex()>0:
                sb.write(' ' + self.__down_message + ':' + self.__down_car)
                if self.getSharedQueueWebOutput()!=None:web_outputs['contents']['choices']['down_car']=self.__down_car
            if isinstance(menu,IMenu) and menu.doCheckAll():
                sb.write(' ' + self.__check_all_message + ':' + self.__check_all_car)
                if self.getSharedQueueWebOutput()!=None:web_outputs['contents']['choices']['check_all_car']=self.__check_all_car
            sb.write(')')

            if self.doRecord():mo_path='.'.join(self.__records) + '/Names:' + '.'.join(self.__record_names)
            else:mo_path=None

            self.println(line=sb.getvalue())
            if self.doRecord():
                if self.doLog():
                    import time, datetime, sys
                    ds=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d.%H.%M.%S')
                    sys.stdout.writef((self.__indent + OPTION_INDENT+3)*' ' + ' DS:' + ds + ' MO Path:' + mo_path)
                if not self.doRecordForLogOnly():
                    self.println(line=(self.__indent + OPTION_INDENT+3)*' ' + ' MO Path:' + mo_path)
                self.println()


            mid=None
            if self.getSharedQueueWebOutput() != None:
                web_outputs['contents']['mo_paths']={'indexes': '.'.join(self.__records), 'names': '.'.join(self.__record_names)}
                mid=web_outputs['contents']['mid']
                self.printweb(web_outputs)

            # - input
            val=self.read((self.__indent + CHOICE_INDENT)*' ' + self.__choice_message + ' ?', isChoice=True, id=mid, id_type='mid', _menu=menu, allow_cars=['?'])

            # Base options
            if val==self.__up_car:
                menu.pageUp()
                continue
            if val==self.__down_car:
                menu.pageDown()
                continue
            if val==self.__exit_car:
                self.drawLine()
                exit = self.__exit_command(menu)
                continue
            if val in ('', None, 'None'):
                if menu.getPipeIndex()==0:
                    self.drawLine()
                    exit=self.__exit_command(menu)
                    continue
                else:
                    success=self.__menu_pipes[-1].leave_backward(self, id='PREV_NOID', id_type='mid')
                    if success:del self.__menu_pipes[-1]
                    continue

            ## check_all on IMenu
            if isinstance(menu, IMenu) and menu.doCheckAll() and val==self.__check_all_car:
                self.println()
                self.drawLine()
                self.__command(menu)
                continue


            # A042:
            # Help:
            if val=='?':
                help = menu.getHelp()
                lhelp = menu.getLHelp()
                if help==None and lhelp==None:continue
                if help==None:help=''
                if lhelp!=None:help+='\n\n' + lhelp.replace('\\n', '\n')

                if self.getSharedQueueWebOutput()!=None:
                    # web_outputs['type']='command_result'
                    web_outputs['type']='warn'
                    web_outputs['keys']={'menu': menu.getPipeUid()}
                    web_outputs['contents']={'type': 'help', 'id': mid, 'id_type': 'mid', 'messages': stripOutput(help)}
                    self.printweb(web_outputs)

                self.println(line=help)

                self.read(self.__wait_message, id=mid, id_type='mid')
                continue


            # Check options
            if not val.isdigit():
                if self.getSharedQueueWebOutput()!=None:
                    web_outputs['type']='raise'
                    web_outputs['keys']={'menu': menu.getPipeUid()}
                    web_outputs['contents']={'type': 'InvalidEntryNotDigit', 'id': mid, 'id_type': 'mid', 'messages': stripOutput( self.__option_check_message1.replace('$1', ' ' + self.__up_car + ', ' +  self.__down_car + ', ' + self.__exit_car) )}
                    self.printweb(web_outputs)

                self.println()
                self.drawLine()
                kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, self.__option_check_message1.replace('$1', ' ' + self.__up_car + ', ' + self.__down_car + ', ' + self.__exit_car)).warn()
                self.println()

                self.read(self.__wait_message, id=mid, id_type='mid')
                continue

            index=int(val)

            if index<0 or index>menu.getChildNumber():
                option = menu.getChild(index)
                if self.getSharedQueueWebOutput()!=None:
                    web_outputs['type']='raise'
                    web_outputs['keys']={'menu': menu.getPipeUid()}
                    web_outputs['contents']={'type': 'InvalidEntryNotInRange', 'id': mid, 'id_type': 'mid', 'messages': stripOutput( self.__option_check_message2 )}
                    self.printweb(web_outputs)

                self.println()
                self.drawLine()
                kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, self.__option_check_message2).warn()
                self.println()

                self.read(self.__wait_message, id=mid, id_type='mid')
                continue

            # - Inputs

            ## Item is a Menu
            option=menu.getChild(index)
            if isinstance(option, BaseMenu):
                option._cantBeDeleted()
                self.__fct_menu(self, option)
                self.__addMenuToPipe(option)
                if option!=self.__menu_pipes[0]:option._canBeDeleted()
                continue


            ## Item is an IOption
            if isinstance(option, IOption):
                self.println()
                self.drawLine()

                self.__input_field(menu, index)
                continue


            ## Item is an Command
            self.println()
            self.drawLine()

            self.__command(menu, option_index=index)

        self.garbadge()

    def doColors(self, menu, value):
        frColor=bgColor=None
        # if not (self.__use_unix_colors or QUEUE_WEB_OUTPUT!=None):return value, frColor, bgColor
        if not (self.__use_unix_colors or menu.doSetColor()):return value, frColor, bgColor

        ## if self.__use_unix_colors or menu.doSetColor():
        # if self.__use_unix_colors or menu.doSetColor() or QUEUE_WEB_OUTPUT!=None:
        if menu.doSetBold():bold='1'
        else:bold='0'
        frColor=menu.getFrColor()
        if frColor==None:
            if self.getSharedQueueWebOutput()==None:frColor=UNIX_VIDEO_DEFAULT_FRCOLOR
            if isinstance(menu, IOption):frColor='WHITE'
        bgColor=menu.getBgColor()
        if bgColor==None:
            if self.getSharedQueueWebOutput()==None:bgColor=UNIX_VIDEO_DEFAULT_BGCOLOR
            if isinstance(menu, IOption):bgColor='BLUE'


        if self.__use_unix_colors and self.getSharedQueueWebOutput()==None:
            vtmpl=UNIX_VIDEO_TEMPLATE.replace('{bold}', bold).replace('{frColor}', UNIX_VIDEO_COLORS['frColors'][frColor]).replace('{bgColor}', UNIX_VIDEO_COLORS['bgColors'][bgColor])
            value = vtmpl + value + UNIX_VIDEO_BACK_NORMAL

        if frColor!=None:return value, frColor.lower(), bgColor.lower()
        else:return value, None, None

    def printMenu(self, menu, web_outputs=None): ## Menu

        # - Menu title
        title=menu.getTitle().upper()
        help = menu.getHelp()
        lhelp = menu.getLHelp()
        if menu.getSubTitle()!=None:sub_titles=menu.getSubTitle().split('\n')
        else:sub_titles=()

        self.__printMenuTitle(title, sub_titles)
        self.println()

        mid = None
        if web_outputs != None:
            web_ouput_items=[]
            if self.isFirstMenuProcess() and menu.getPipeIndex()==0:is_first_menu=True
            else:is_first_menu=False

            web_outputs['keys']={'menu': menu.getPipeUid(), 'menu_instance': 'M' + tools.genUid(), 'is_first_menu_process': self.isFirstMenuProcess(), 'is_first_menu': is_first_menu}
            mid='MENU-' + web_outputs['keys']['menu'] + '//MENU_INSTANCE-' + web_outputs['keys']['menu_instance']
            web_outputs['contents'].update({'mid': mid, 'is_locked': False, 'sub_type': 'Menu', 'title': title.strip(), 'sub_titles': sub_titles, 'help': help, 'lhelp': lhelp, 'items': web_ouput_items})

        # - Options
        page=menu.getCurrentPage()
        for child_index in page:
            child=menu.getChild(child_index)
            if web_outputs!=None:
                uid='O' + tools.genUid()
                oid=web_outputs['contents']['mid'] + '//OPTION-' + str(child_index) + '//OPTION_INSTANCE-' + uid

            name=child.getName()
            if self.__option_upper:name=name.upper()
            _name, frColor, bgColor=self.doColors(child, name)
            help=child.getHelp()
            if help==None:help=''
            else:help='[' + help + ']'
            lhelp=child.getLHelp()
            if lhelp==None:lhelp=''

            if isinstance(child, (Option, IOption )):sep=')' ## Child is an Option
            else:sep='/' ## Child a Menu

            line=(self.__indent + OPTION_INDENT)*' ' + str(child_index) + sep + ' %-' + str(self.__option_help_indent) +'s %s'
            self.println(line=line % (_name, help))

            if web_outputs!=None:
                _woo={'type': child.__class__.__name__, 'oid': oid, 'option': str(child_index), 'sep': sep, 'option-instance': uid, 'label': name, 'value': None, 'olegend': None, 'help': help[1:-1], 'lhelp': lhelp, 'frColor': frColor, 'bgColor': bgColor}
                web_ouput_items.append(_woo)

            # M035:
            # contents=child.getContents()
            contents=child.getContentsAsList()
            if len(contents)!=0:
                for line in contents:self.println(line=(self.__indent + OPTION_INDENT)*' ' + line.strip())
                if web_outputs != None:_woo['olegend']=contents

            if self.__skip_line:self.println()

        return child_index

    def printIMenu(self, menu, web_outputs=None): ## IMenu

        # - Menu title
        title=menu.getTitle().upper()
        if menu.getSubTitle()!=None:sub_titles=menu.getSubTitle().split('\n')
        else:sub_titles=()

        self.__printMenuTitle(title, sub_titles)
        self.println()

        mid = None
        if web_outputs != None:
            web_ouput_items=[]
            if self.isFirstMenuProcess() and menu.getPipeIndex()==0:is_first_menu=True
            else:is_first_menu=False

            web_outputs['keys']={'menu': menu.getPipeUid(), 'menu_instance': 'M' + tools.genUid(), 'menu_index': menu.getIndex(), 'is_first_menu_process': self.isFirstMenuProcess(), 'is_first_menu': is_first_menu}
            mid='MENU-' + web_outputs['keys']['menu'] + '//MENU_INSTANCE-' + web_outputs['keys']['menu_instance']
            web_outputs['contents'].update({'mid': mid, 'is_locked': False, 'sub_type': 'IMenu', 'title': title, 'sub_titles': sub_titles, 'items': web_ouput_items})

        # - IOptions
        firstOption = True
        page=menu.getCurrentPage()
        for child_index in page:
            child=menu.getChild(child_index)
            if web_outputs!=None:
                uid='O' + tools.genUid()
                oid=web_outputs['contents']['mid'] + '//OPTION-' + str(child_index) + '//OPTION_INSTANCE-' + uid

            if isinstance(child, (Option, IOption)):sep=')' ## Child is an Option
            else:sep='/' ## Child a Menu

            if isinstance(child, IOption):
                label=child.getLabel()
                if self.__option_upper:label=label.upper()
                if child.isValue() and self.getSharedQueueWebOutput()==None:label=label + abs(self.__option_value_indent - (len(label) + 2)) *'.' + ':'
                _label, frColor, bgColor=self.doColors(child, label)
                # help:
                help=child.getHelp()
                if help==None:help=''
                else:help='[' + help + ']'
                # lhelp:
                if isinstance(child, IOption): lhelp = child.getLHelp()
                else:lhelp = None

                if child.isValue():
                    is_password = False
                    line=(self.__indent + OPTION_INDENT)*' ' + str(child_index) + sep + ' %-' + str(self.__option_value_indent) +'s%-' + str(self.__option_help_indent) +'s %s'
                    if firstOption:line='\n' + line

                    # A049: Support of *password: <value show>: hide password:
                    show_value = child.getValue()
                    descs = child.getIODescs()
                    if child.isValue() and show_value!=None and '*password' in descs and descs['*password']:
                        is_password = True
                        show_value = len(show_value) * '*'
                    self.println(line=self.println(line=line % (_label, ' ' + ' ' + str(show_value), help)))

                    if web_outputs != None:
                        # A049: + is_password
                        _woo={'type': child.__class__.__name__, 'oid': oid, 'option': str(child_index), 'sep': sep, 'option_instance': uid, 'label': label, 'value': child.getValue(), 'is_password': is_password, 'olegend': None, 'help': help[1:-1], 'lhelp': lhelp, 'frColor': frColor, 'bgColor': bgColor}
                        web_ouput_items.append(_woo)
                else:
                    line=(self.__indent + OPTION_INDENT)*' ' + str(child_index) + sep + ' %-' + str(self.__option_value_indent + self.__option_help_indent) +'s %s'
                    self.println(line=line % (_label, help))

                    if web_outputs!=None:
                        _woo={'type': child.__class__.__name__, 'oid': oid, 'option': str(child_index), 'sep': sep, 'option_instance': uid, 'label': label, 'value': None, 'olegend' : None, 'help': help[1:-1], 'lhelp': lhelp, 'frColor': frColor, 'bgColor': bgColor}
                        web_ouput_items.append(_woo)
                firstOption=False

                if not child.isValue():
                    # ++
                    # contents=child.getContents()
                    contents = child.getContentsAsList()
                    if len(contents)!=0:
                        for line in contents:self.println(line=(self.__indent + OPTION_INDENT + 3)*' ' + str(line).strip())
                        self.println()
                        if web_outputs!=None:_woo['olegend']=contents

            else:
                # - Menu, IMenu

                name=child.getName()
                if self.__option_upper:name=name.upper()
                _name, frColor, bgColor=self.doColors(child, name)
                help=child.getHelp()
                if help==None:help=''
                else:help='[' + help + ']'
                lhelp=child.getLHelp()
                if lhelp==None:lhelp=''

                line=(self.__indent + OPTION_INDENT)*' ' + str(child_index) + sep + ' %-' + str(self.__option_help_indent) +'s %s'
                self.println(line=line % (_name, help))

                if web_outputs != None:
                    _woo={'type': child.__class__.__name__, 'oid': oid, 'option': str(child_index), 'sep': sep, 'option-instance': uid, 'label': name, 'value': None, 'olegend': None, 'help': help[1:-1], 'lhelp': lhelp, 'frColor': frColor, 'bgColor': bgColor}
                    web_ouput_items.append(_woo)

                # ++
                # contents=child.getContents()
                contents = child.getContentsAsList()
                if len(contents)!=0:
                    for line in contents:self.println(line=(self.__indent + OPTION_INDENT)*' ' + line)
                    self.println()

                    if web_outputs != None:
                        _woo['olegend']=contents


        return child_index

    def __printMenuTitle(self, title, sub_titles):

        self.println(line=(self.__middle - int((len(title)+4)/2))*' ' + (len(title)+4) *'_')
        self.println(line=(self.__middle - int((len(title)+4)/2))*' ' + '|' + (len(title)+2)*' ' + '|')
        self.println(line=(self.__middle - int((len(title)+4)/2))*' ' + '| ' + title + ' |')
        self.println(line=(self.__middle - int((len(title)+4)/2))*' ' + '|' + (len(title)+2) *'_' + '|')
        self.println()
        for sub_title in sub_titles:self.println(line=(self.__middle - int(len(sub_title)/2))*' ' + sub_title)

    def drawLine(self):
        if self.getSharedQueueWebOutput()==None:self.println(line=self.__indent*' ' + '_'*LINE_LENGTH)

    def __command(self, menu, option_index=None): ## Mixed (Menu/IMenu)
        selfMethod='__command'
        global LAST_SYSTEM_COMMAND_RET
        if option_index!=None:option_or_menu=menu.getChild(option_index)
        else:option_or_menu=menu
        from io import StringIO
        from kwadlib.tools import Popen
        do_follow_menu = False

        if self.getSharedQueueWebOutput()!=None:
            web_outputs=dict(WEB_OUTPUTS)
            web_outputs['type']='command_result'
            web_outputs['keys']={'menu': menu.getPipeUid(), 'option': str(option_index), 'command_instance': 'C' + tools.genUid()}
            cid='MENU-' + web_outputs['keys']['menu'] + '//OPTION-' + str(option_index) + '//COMMAND_INSTANCE-' + web_outputs['keys']['command_instance']
            web_outputs['contents']={'cid': cid, 'index': str(option_index), 'raws': None, 'outputs': None, 'return_code': None}
        else:
            cid=None
            web_outputs=None

        self.println()

        if isinstance(menu, Menu) or isinstance(option_or_menu, Option):
            doConfirm=option_or_menu.doConfirm()
        elif isinstance(menu, IMenu):doConfirm=menu.doConfirm()
        else:
            if self.getSharedQueueWebOutput()!=None:
                web_outputs['type']='raise'
                web_outputs['contents']={'type': 'InvalidMenu', 'cid': cid, 'id_type': 'cid', 'messages': stripOutput( 'Not managed Menu:' + menu.__class__.__name__ )}
                self.printweb(web_outputs)
            else:
                kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'Not managed Menu:' + menu.__class__.__name__ + ' !').warn()
            self.read(self.__wait_message, id=cid, id_type='cid')
            return

        # CheckAutz
        if isinstance(option_or_menu, Option): ## menu is a Menu (Or IMenu called for Option)
            title=option_or_menu.getName()

            if not option_or_menu.checkCommandAutz('execute'):
                mes='This Option (' + str(option_or_menu.getIndex()) + ', calling for a: ' + menu.__class__.__name__ + ') is not allowed for role(s):' + str(self.getSharedRoles())[1:-1].replace("'", '') + ' ! The "execute" autorization is needed !'
                if self.getSharedQueueWebOutput()!=None:
                    web_outputs['type']='raise'
                    web_outputs['contents']={'type': 'InvalidMenuOrOption', 'cid': cid, 'id_type': 'cid', 'messages': mes}
                    self.printweb(web_outputs)
                else:
                    kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, mes).warn()
                self.read(self.__wait_message, id=cid, id_type='cid')
                return

        if doConfirm:
            if isinstance(menu, Menu) or isinstance(option_or_menu, Option): ## menu is a Menu (Or IMenu called for Option)
                title=option_or_menu.getName()
            else:title=self.__check_all_message ## menu is an IMenu (Called fo check_all s)

            val=self.read(self.__indent*' ' + self.__confirm_message.replace('$1', title) + ' (y/n) ?', id=cid, doConfirm=True, id_type='cid')
            if val!='y':
                return

        self.println()

        if isinstance(menu, Menu) or isinstance(option_or_menu, Option): ## menu is a Menu (Or IMenu called for Option)

            if option_or_menu.getFct_command()==None and option_or_menu.getCommand()==None:
                mes='No command defined !'
                if web_outputs!=None:
                    web_outputs['contents']['raws']=[mes]
                    self.printweb(web_outputs)

                self.println(line=mes)

                self.read(self.__wait_message, id=cid, id_type='cid')
                return

            # Fct_command
            if option_or_menu.getFct_command()!=None:
                # todo: new_menu is to be removed cause:new_menu is likely binded to no menu at all or may be binded to the wrong one.
                try:
                    new_menu=option_or_menu.getFct_command()(self, menu, option_index, command=option_or_menu.getCommand(), id=cid, id_type='cid')
                except Exception as e:
                    if self.__debug: raise
                    from kwadlib.tools import tracebackToString
                    message = 'Exception running fct function: %s:%s\nTraceback is:%s' % (
                        option_or_menu.getFct_command(), str(e), tracebackToString(e))

                    if self.getSharedQueueWebOutput() != None:
                        web_outputs['type'] = 'raise'
                        web_outputs['contents'] = {'type': 'Exception', 'cid': cid, 'id_type': 'cid',
                                                   'messages': stripOutput(message)}
                        self.printweb(web_outputs)
                    else:
                        kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, str(e)).warn()
                    self.read(self.__wait_message, id=cid, id_type='cid')
                    return

                if new_menu!=None:
                    if not isinstance(new_menu, Menu):
                        if self.getSharedQueueWebOutput()!=None:
                            web_outputs['type']='raise'
                            web_outputs['contents']={'type': 'InvalidMenuReturned', 'cid': cid, 'id_type': 'cid', 'messages': stripOutput( 'An Option fct_command (:' + str(option_or_menu.getFct_command()) + ') can return nothing else than a Menu instance ! Received:' + str(new_menu) + '.' )}
                            self.printweb(web_outputs)
                        else:
                            kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'An Option fct_command (:' + str(option_or_menu.getFct_command()) + ') can return nothing else than a Menu instance ! Received:' + str(new_menu) + '.').warn()
                        self.read(self.__wait_message, id=cid, id_type='cid')
                        return

                    self.__addMenuToPipe(new_menu)
                if menu.doDelete():self.__delMenuFromPipe(menu.getPipeIndex())

            # System command
            else:

                try:
                    lock_uid=option_or_menu.lockAcquire(self.getTempDir(), command=str(option_or_menu.getCommand())) # Menu is a Menu/Option
                except Exception as e:
                    if self.__debug: raise
                    if self.getSharedQueueWebOutput()!=None:
                        web_outputs['type']='raise'
                        web_outputs['contents']={'type': 'CommandAlreadyLocked', 'cid': cid, 'id_type': 'cid', 'messages': stripOutput( str(e) )}
                        self.printweb(web_outputs)
                    else:
                        kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, str(e)).warn()
                    self.read(self.__wait_message, id=cid, id_type='cid')
                    return

                command=str(option_or_menu.getCommand())
                # A051
                command_enter=option_or_menu.getCommandEnter()
                command_exit=option_or_menu.getCommandExit()

                if command.find('--follow_menu') > 0:

                    # - Alert --follow_menu
                    if self.doRecord() and self.__port==None:
                        if web_outputs==None:
                            kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'Option --follow_menu was found in this command. Please recall this menu with option --port(-p) when recording !').warn()
                        else:
                            _web_outputs=dict(web_outputs)
                            _web_outputs['type']='warn'
                            _web_outputs['contents']={'type': 'whenRecodingCallWithPort', 'id': cid, 'id_type': 'cid', 'messages': stripOutput('Option --follow_menu was found in this command. Please recall this menu with option --port(-p) when recording !')}
                            self.printweb(_web_outputs)

                        self.read(self.__wait_message, id=cid, id_type='cid')

                # - isMenuGoing ?
                if self.isMenuGoing() and not command.find('--follow_menu')>0:
                    if web_outputs==None:
                        kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'When apimenu is called with option --GO (-G) system commands are disallowed ! Leaving GO mode.').warn()
                    else:
                        _web_outputs=dict(web_outputs)
                        _web_outputs['type']='warn'
                        _web_outputs['contents']={'type': 'whenRecodingCallWithPort', 'id': cid, 'id_type': 'cid', 'messages': stripOutput('When apimenu is called with option --GO (-G) system commands are disallowed ! Leaving GO mode.')}
                        self.printweb(_web_outputs)

                    self.stopGoing()
                    self.read(self.__wait_message, id=cid, id_type='cid')
                    return


                # - Replace --follow_menu and push caracteristics
                if self.__secid!=None:
                    if command.find('--follow_menu') > 0:
                        do_follow_menu = True
                        from kwadlib.security.crypting import setSecidToFile
                        # Prepare stdin for next MenuMaker process:
                        setSecidToFile(self.__secid_md5, self.__secid + '//' + self.__secid_menuid,  self.__port, temp_dir=default.getKastTempDir())
                        ## Replace parameter:
                        command = command.replace('--follow_menu', '--secid ' + self.__secid_md5)

                    # Update kdealer Set Config infos:
                    # kmq = QueueManager(address=('localhost', int(self.__port)), authkey=self.__secid)
                    # kmq.connect()
                    self.__KMQ.set_config(api_menu_instance=self.__secid_menuid, roles=self.getSharedRoles(), user=self.getSharedUser(), groups=self.getSharedGroups(), is_listening=self.__is_listening, records=self.__records, record_names=self.__record_names, is_going=self.__is_going, is_menu_going=self.__is_menu_going, is_batch=self.__is_batch, pause=self.__pause, noclear=self.__noclear, do_record=self.__do_record, do_record_for_log_only=self.__do_record_for_log_only, log=self.__log, log_output=self.__log_output, log_file=self.__log_file, debug=self.__debug, show_shortcut=self.show_shortcut, verbose=self.__verbose)

                # - Show command:
                mes=self.__command_label.replace('$1', command)
                # - Verbose level:
                if option_or_menu.getVerbose_exec_command():
                    verbose=10
                    doPrint=True
                else:
                    verbose=0
                    doPrint=False

                # A039:
                sd = option_or_menu.getSessionDir(self)
                if sd!=None:
                    envs = {'KSESSION_DIR': sd}
                    if self.__log_file != None:envs['KLOG_FILE']=self.__log_file
                else:envs=None

                # - Execute command
                # A002:
                if web_outputs==None:
                    # self.__last_system_command_ret, stdout, stderr=tools.subprocess(command, doPrint=doPrint, stdin=None, stdout=None, stderr=None, wait=True, verbose_zero_temp_dir=None, useshell=True)

                    if (not (self.doLog() and  self.doLogOutput()) ) or do_follow_menu:
                        try:
                            self.__last_system_command_ret = 0

                            # A051:
                            if command_enter != None:
                                self.println('Found Command enter: %s:' % command_enter)
                                p = Popen(command_enter, shell=True, stdout=None, stderr=None, executable='/bin/bash', env=envs)
                                p.wait()
                                self.println()
                                self.__last_system_command_ret = p.returncode

                            if self.__last_system_command_ret == 0:
                                self.println(line=mes)
                                self.println()

                                p = Popen(command, shell=True, stdout=None, stderr=None, executable='/bin/bash', env=envs) # M039
                                """ Removed would cause EOF trying to input() after stdin.read(). 
                                if process_stdin!=None:
                                    p.stdin.write(bytes(process_stdin.strip() + '\n', 'utf-8'))
                                    p.stdin.close()
                                """
                                p.wait()
                                self.__last_system_command_ret = p.returncode
                            # A051:
                            if self.__last_system_command_ret == 0:
                                if command_exit !=None:
                                    self.println()
                                    self.println('Found Command exit: %s:' % command_exit)
                                    p = Popen(command_exit, shell=True, stdout=None, stderr=None, executable='/bin/bash', env=envs)
                                    p.wait()
                                    self.__last_system_command_ret = p.returncode
                        except KeyboardInterrupt:
                            import sys
                            sys.exit(1)

                    else:
                        # A044
                        try:
                            from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
                            from subprocess import CalledProcessError
                            from io import StringIO
                            import sys
                            sb = StringIO()
                            system_command_ret = 0

                            # A051:
                            if command_enter != None:
                                sb.write ('Found Command enter: %s:\n' % command_enter)
                                popen = Popen(command_enter, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                                for stdout_line in iter(popen.stdout.readline, ""):
                                    sys.stdout.write(stdout_line)  # write to log file
                                    sb.write(stdout_line)
                                popen.stdout.close()
                                system_command_ret = popen.wait()
                                sb.write('\n')

                            if system_command_ret == 0:
                                if web_outputs != None:
                                    web_outputs['contents']['raws'] = [mes]
                                self.println(line=mes)
                                self.println()

                                popen = Popen(command, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                                for stdout_line in iter(popen.stdout.readline, ""):
                                    sys.stdout.write(stdout_line)  # write to log file
                                    sb.write(stdout_line)
                                popen.stdout.close()
                                system_command_ret = popen.wait()

                            # A051:
                            if system_command_ret == 0:
                                if command_exit != None:
                                    sb.write('\nFound Command exit: %s:\n' % command_exit)
                                    popen = Popen(command_exit, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                                    for stdout_line in iter(popen.stdout.readline, ""):
                                        sys.stdout.write(stdout_line)  # write to log file
                                        sb.write(stdout_line)
                                    popen.stdout.close()
                                    system_command_ret = popen.wait()
                                    sb.write('\n')

                        except CalledProcessError as e:
                            system_command_ret = e.returncode
                            message = 'Execution Error: %s' % str(e.output)
                            sys.stdout.write(message)  # write to log file
                            sb.write(message)

                        except Exception as e:
                            system_command_ret = 1
                            message = 'Execution Error: %s' % str(e)
                            sys.stdout.write(message)  # write to log file
                            sb.write(message)

                        stdout = sb.getvalue()

                        """ D044
                        # Allow output reteirving straigth from the TTY (pexpect known bug write more than once last line)
                        try:
                            self.__last_system_command_ret, stdout=pexpect_spawn(command, envs=envs) # M039
                        except KeyboardInterrupt:
                            import sys
                            sys.exit(1)
                        """
                else:
                    # Announcing long task with a preceding event !
                    _web_outputs=dict(web_outputs)
                    _web_outputs['type']='raise'
                    _web_outputs['contents']={'type': 'APIMENU_NEXT_GET_MAY_BE_LONG'}
                    self.printweb(_web_outputs)

                    """ D012:
                    output=check_output(command, stderr=SUBPROCESS_STDOUT, shell=True).replace('\t', ' ')
                    self.__last_system_command_ret=0
                    """

                    # A012:
                    self.__last_system_command_ret, stdout =self.execWebCommand(command, command_enter=command_enter, command_exit=command_exit, envs=envs, do_follow_menu=do_follow_menu)


                # A002:
                # - Retreive caracteristics
                if self.__secid!=None:
                    ACONFIGS=self.__KMQ.get_config(api_menu_instance=self.__secid_menuid)
                    try:ACONFIGS
                    except:raise Exception('Unable to retreive Apimenu persistent Config !')
                    ACONFIGS=ACONFIGS.copy() # Convert multiprocessing object to dict.
                    was_going=self.__is_going
                    self.__is_going=ACONFIGS['is_going']
                    self.__is_menu_going=ACONFIGS['is_menu_going']
                    self.__is_batch=ACONFIGS['is_batch']
                    self.__records=ACONFIGS['records']
                    self.__record_names=ACONFIGS['record_names']
                    # log
                    ## self.__log=ACONFIGS['log']
                    ## self.__log_file=ACONFIGS['log_file']
                    ## if self.__log:Logger(self.__log_file)
                    if was_going and not self.__is_going:self.__shared_queueInput=None


                option_or_menu.lockRelease(self.getTempDir(), uid=lock_uid)

                # A001:
                if not do_follow_menu or self.__last_system_command_ret!=0:  # No if was following !
                    if web_outputs!=None:
                        pass
                        """ D012:
                        web_outputs['contents']['outputs']=stripOutput(output)
                        web_outputs['contents']['return_code']=self.__last_system_command_ret
                        self.printweb(web_outputs)
                        """

                    if self.__last_system_command_ret!=0:
                        self.println()
                        self.println(line='Echec running command ! Return code is:' + str(self.__last_system_command_ret))
                    self.println()

                    self.read(self.__wait_message, id=cid, id_type='cid')

        elif isinstance(menu, IMenu): ## menu is an IMenu (Called fo check_all s)
            display_command = None  # A049

            if menu.getFct_command()==None and menu.getCommand()==None:
                mes='No command defined !'
                if web_outputs!=None:
                    web_outputs['contents']['raws']=[mes]
                    self.printweb(web_outputs)

                self.println(line=mes)

                self.read(self.__wait_message, id=cid, id_type='cid')
                return

            options=menu.getChilds()

            if menu.getFct_command()!=None:values={} # Fct_command
            else:
                command=menu.getCommand() # System command
                display_command=command
                # A051:
                command_enter = menu.getCommandEnter()  # System command
                command_exit = menu.getCommandExit()  # System command

            for option in options:
                if not isinstance(option, IOption):continue

                # Fct_command
                if option.getFct_command()!=None:
                    try:
                        success=option.getFct_command()(self, menu, option.getIndex(), value=option.getIOValue(), command=option.getCommand(), id=cid, id_type='cid')
                    except Exception as e:
                        if self.__debug: raise
                        from kwadlib.tools import tracebackToString
                        message = 'Exception running fct function: %s:%s\nTraceback is:%s' % (
                            option_or_menu.getFct_command(), str(e), tracebackToString(e))

                        if self.getSharedQueueWebOutput() != None:
                            web_outputs['type'] = 'raise'
                            web_outputs['contents'] = {'type': 'Exception', 'cid': cid, 'id_type': 'cid',
                                                       'messages': stripOutput(message)}
                            self.printweb(web_outputs)
                        else:
                            kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, str(e)).warn()
                        self.read(self.__wait_message, id=cid, id_type='cid')
                        return
                    if not success:return
                else:
                    if web_outputs!=None:fct_output=StringIO()
                    else:fct_output=None

                    if not option.checkIOValue(option.getIOValue(), verbose=self.__verbose, fct_output=fct_output):
                        if web_outputs!=None:
                            if fct_output.getvalue() not in ('', None):web_outputs['contents']['raws']=fct_output.getvalue().split('\n')
                            self.printweb(line=web_outputs)

                        self.println()

                        self.read(self.__wait_message, id=cid, id_type='cid')
                        return

                if menu.getFct_command()!=None:values[option.getName()]=option.getIOValue() # Fct_command
                elif menu.getCommand()!=None:

                    if option.isValue():value=str(option.getIOValue())
                    else:
                        # M035: value=';'.join([str(line) for line in option.getIOValue()])
                        value=option.getIOValue()

                    # M035:
                    if value!=None:
                        from kwadlib import ct
                        value = ct.unDress(value)
                    else:value='None'

                    # A049: Support of *password: <command>: hide password:
                    descs = option.getIODescs()
                    if option.isValue() and '*password' in descs and descs['*password']:
                        display_command = display_command.replace('$' + option.getName(), len(value)*'*') # System command
                        # if has password_file_option: rewrite command: with --<optionfile> fpath instead of --password value:
                        if '*password_file_option' in descs and descs['*password_file_option']!=None:
                            fpath = self.getTempDir() + '/' + tools.genUid() + '.dat'
                            command = command.replace('$' + option.getName(), ' --%s %s ' % (descs['*password_file_option'], fpath))  # System command
                    # 050: support of boolean option: not present if False:
                    elif '*type' in descs and descs['*type'] == 'bool' and command.find('--$' + option.getName()):
                        if value ==True:
                            display_command = display_command.replace('--$' + option.getName(), '--' + option.getName())
                            command = command.replace('--$' + option.getName(), '--' + option.getName())
                        else:
                            display_command = display_command.replace('--$' + option.getName(), '')
                            command = command.replace('--$' + option.getName(), '')
                    else:
                        display_command = display_command.replace('$' + option.getName(), value)
                        command = command.replace('$' + option.getName(), value)  # System command

            # Fct_command
            if menu.getFct_command()!=None:
                try:
                    new_menu=menu.getFct_command()(self, menu, option_index, values=values, command=menu.getCommand(), id=cid, id_type='cid')
                except Exception as e:
                    if self.__debug: raise
                    from kwadlib.tools import tracebackToString
                    message = 'Exception running fct function: %s:%s\nTraceback is:%s' % (
                        option_or_menu.getFct_command(), str(e), tracebackToString(e))

                    if self.getSharedQueueWebOutput() != None:
                        web_outputs['type'] = 'raise'
                        web_outputs['contents'] = {'type': 'Exception', 'cid': cid, 'id_type': 'cid',
                                                   'messages': stripOutput(message)}
                        self.printweb(web_outputs)
                    else:
                        kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, str(e)).warn()
                    self.read(self.__wait_message, id=cid, id_type='cid')
                    return

                if new_menu!=None:
                    if not isinstance(new_menu, Menu):
                        if self.getSharedQueueWebOutput()!=None:
                            web_outputs['type']='raise'
                            web_outputs['contents']={'type': 'InvalidMenuReturned', 'cid': cid, 'id_type': 'cid', 'messages': stripOutput( 'An Option fct_command (:' + str(option_or_menu.getFct_command()) + ') can return nothing else than a Menu instance ! Received:' + str(new_menu) + '.' )}
                            self.printweb(web_outputs)
                            return
                        else:
                            raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'A Menu fct_command (:' + str(option_or_menu.getFct_command()) + ') can return nothing else than a Menu instance ! Received:' + str(new_menu) + '.')

                    self.__addMenuToPipe(new_menu)
                if menu.doDelete():self.__delMenuFromPipe(menu.getPipeIndex())

            # System command
            else:

                if command.find('--follow_menu') > 0:

                    # - Alert --follow_menu:
                    if self.doRecord() and self.__port==None:
                        if web_outputs==None:
                            kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'Option --follow_menu was found in this command. Please recall this menu with option --port(-p) when recording !').warn()
                        else:
                            _web_outputs=dict(web_outputs)
                            _web_outputs['type']='warn'
                            _web_outputs['contents']={'type': 'whenRecodingCallWithPort', 'id': cid, 'id_type': 'cid', 'messages': stripOutput('Option --follow_menu was found in this command. Please recall this menu with option --port(-p) when recording !')}
                            self.printweb(_web_outputs)
                        self.read(self.__wait_message, id=cid, id_type='cid')

                # - isMenuGoing ?
                if self.isMenuGoing() and not command.find('--follow_menu')>0:
                    if web_outputs==None:
                        kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'When apimenu is called with option --GO (-G) system commands are disallowed ! Leaving GO mode.').warn()
                    else:
                        _web_outputs=dict(web_outputs)
                        _web_outputs['type']='warn'
                        _web_outputs['contents']={'type': 'whenRecodingCallWithPort', 'id': cid, 'id_type': 'cid', 'messages': stripOutput('When apimenu is called with option --GO (-G) system commands are disallowed ! Leaving GO mode.')}
                        self.printweb(_web_outputs)
                    self.stopGoing()
                    self.read(self.__wait_message, id=cid, id_type='cid')
                    return

                try:
                    lock_uid=menu.lockAcquire(self.getTempDir(), command=command)
                except Exception as e:
                    if self.__debug: raise
                    if self.getSharedQueueWebOutput()!=None:
                        web_outputs['type']='raise'
                        web_outputs['contents']={'type': 'CommandAlreadyLocked', 'cid': cid, 'id_type': 'cid', 'messages': stripOutput( str(e) )}
                        self.printweb(web_outputs)
                    else:
                        kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, str(e)).warn()
                    self.read(self.__wait_message, id=cid, id_type='cid')
                    return

                # - Replace --follow_menu and push caracteristics:
                # M003: if self.__secid!=None:
                if self.__secid != None:
                    if command.find('--follow_menu') > 0:
                        do_follow_menu = True
                        # Prepare stdin for next MenuMaker process:
                        from kwadlib.security.crypting import setSecidToFile
                        setSecidToFile(self.__secid_md5, self.__secid + '//' + self.__secid_menuid, self.__port, temp_dir=default.getKastTempDir())
                        ## Replace parameter:
                        command = command.replace('--follow_menu', '--secid ' + self.__secid_md5)
                        if display_command!=command: # A049: reflect this inot display_command as well
                            display_command=display_command.replace('--follow_menu', '--secid ' + self.__secid_md5)

                    # Update kdealer Set Config infos:
                    # kmq = QueueManager(address=('localhost', int(self.__port)), authkey=self.__secid)
                    # kmq.connect()
                    self.__KMQ.set_config(api_menu_instance=self.__secid_menuid, roles=self.getSharedRoles(), user=self.getSharedUser(), groups=self.getSharedGroups(), is_listening=self.__is_listening, records=self.__records, record_names=self.__record_names, is_going=self.__is_going, is_menu_going=self.__is_menu_going, is_batch=self.__is_batch, pause=self.__pause, noclear=self.__noclear, do_record=self.__do_record, do_record_for_log_only=self.__do_record_for_log_only, log=self.__log, log_output=self.__log_output, log_file=self.__log_file, debug=self.__debug, show_shortcut=self.show_shortcut, verbose=self.__verbose)

                # - Show command:
                # M049: +display_command:
                mes=self.__command_label.replace('$1', display_command)
                # - Verbose level:
                if menu.getVerbose_exec_command():
                    verbose=10
                    doPrint=True
                else:
                    verbose=0
                    doPrint=False

                # A039:
                sd = menu.getSessionDir(self)
                if sd!=None:
                    envs = {'KSESSION_DIR': sd}
                    if self.__log_file != None: envs['KLOG_FILE'] = self.__log_file
                else:envs=None

                # - Execute command:
                # A002:
                if web_outputs==None:
                    # self.__last_system_command_ret, stdout, stderr=tools.subprocess(command, doPrint=doPrint, stdin=None, stdout=None, stderr=None, wait=True, verbose_zero_temp_dir=None, useshell=True)

                    # A001:
                    if (not (self.doLog() and  self.doLogOutput()) ) or do_follow_menu:
                        self.__last_system_command_ret = 0

                        # A051:
                        if command_enter != None:
                            self.println('Found Command enter: %s:' % command_enter)
                            p = Popen(command_enter, shell=True, stdout=None, stderr=None, executable='/bin/bash', env=envs) # M039
                            try:
                                p.wait()
                            except KeyboardInterrupt:
                                import sys
                                sys.exit(1)
                            self.__last_system_command_ret=p.returncode
                            self.println()

                        if self.__last_system_command_ret == 0:  # M051
                            self.println(line=mes)
                            self.println()

                            p = Popen(command, shell=True, stdout=None, stderr=None, executable='/bin/bash', env=envs) # M039
                            try:
                                p.wait()
                            except KeyboardInterrupt:
                                import sys
                                sys.exit(1)
                            self.__last_system_command_ret=p.returncode

                        # A051:
                        if self.__last_system_command_ret == 0:  # M051
                            if command_exit != None:
                                self.println()
                                self.println ('Found Command exit: %s:' % command_exit)
                                p = Popen(command_exit, shell=True, stdout=None, stderr=None, executable='/bin/bash', env=envs) # M039
                                try:
                                    p.wait()
                                except KeyboardInterrupt:
                                    import sys
                                    sys.exit(1)
                                self.__last_system_command_ret=p.returncode
                                self.println()
                    else:
                        # A044
                        try:
                            from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
                            from subprocess import CalledProcessError
                            from io import StringIO
                            import sys
                            sb = StringIO()
                            system_command_ret = 0

                            # A051:
                            if command_enter!=None:
                                sb.write('Found Command enter: %s:\n' % command_enter)
                                popen = Popen(command_enter, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                                for stdout_line in iter(popen.stdout.readline, ""):
                                    sys.stdout.write(stdout_line)  # write to log file
                                    sb.write(stdout_line)
                                popen.stdout.close()
                                system_command_ret = popen.wait()
                                sb.write('\n')

                            if system_command_ret == 0: # M051
                                if web_outputs != None:
                                    web_outputs['contents']['raws'] = [mes]
                                self.println(line=mes)
                                self.println()

                                popen = Popen(command, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                                for stdout_line in iter(popen.stdout.readline, ""):
                                    sys.stdout.write(stdout_line)  # write to log file
                                    sb.write(stdout_line)

                                popen.stdout.close()
                                system_command_ret = popen.wait()

                            # A051:
                            if system_command_ret == 0:  # M051
                                if command_exit!=None:
                                    sb.write('\nFound Command exit: %s:\n' % command_exit)
                                    popen = Popen(command_exit, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                                    for stdout_line in iter(popen.stdout.readline, ""):
                                        sys.stdout.write(stdout_line)  # write to log file
                                        sb.write(stdout_line)
                                    popen.stdout.close()
                                    system_command_ret = popen.wait()
                                    sb.write('\n')

                        except CalledProcessError as e:
                            system_command_ret = e.returncode
                            message = 'Execution Error: %s' % str(e.output)
                            sys.stdout.write(message)  # write to log file
                            sb.write(message)

                        except Exception as e:
                            system_command_ret = 1
                            message = 'Execution Error: %s' % str(e)
                            sys.stdout.write(message)  # write to log file
                            sb.write(message)

                        stdout = sb.getvalue()

                        """ D044
                        # Allow output reteirving straigth from the TTY (pexpect known bug write more than once last line)
                        try:
                            self.__last_system_command_ret, stdout=pexpect_spawn(command, envs=envs) # M039
                        except KeyboardInterrupt:
                            import sys
                            sys.exit(1)
                        """
                else:
                    # Announcing long task with a preceding event !
                    _web_outputs=dict(web_outputs)
                    _web_outputs['type']='raise'
                    _web_outputs['contents']={'type': 'APIMENU_NEXT_GET_MAY_BE_LONG'}
                    self.printweb(_web_outputs)

                    """ D012:
                    output=check_output(command, stderr=SUBPROCESS_STDOUT, shell=True)
                    self.__last_system_command_ret=0
                    """
                    # A012:
                    # A049: +display_command:
                    system_command_ret, stdout = self.execWebCommand(command, command_enter=command_enter, command_exit=command_exit, display_command=display_command, envs=envs, do_follow_menu=do_follow_menu)

                # A002:
                # - Retreive caracteristics
                if self.__secid!=None:
                    ACONFIGS=self.__KMQ.get_config(api_menu_instance=self.__secid_menuid)
                    try:ACONFIGS
                    except:raise Exception('Unable to retreive Apimenu persistent Config !')
                    ACONFIGS=ACONFIGS.copy() # Convert multiprocessing object to dict.
                    was_going=self.__is_going
                    self.__is_going=ACONFIGS['is_going']
                    self.__is_menu_going=ACONFIGS['is_menu_going']
                    self.__is_batch=ACONFIGS['is_batch']

                    self.__records=ACONFIGS['records']
                    self.__record_names=ACONFIGS['record_names']
                    # log: Removed:
                    ## self.__log=ACONFIGS['log']
                    ## self.__log_file=ACONFIGS['log_file']
                    ## if self.__log:Logger(self.__log_file)
                    if was_going and not self.__is_going:self.__shared_queueInput=None
                option_or_menu.lockRelease(self.getTempDir(), uid=lock_uid)

                # A001:
                if not do_follow_menu or self.__last_system_command_ret!=0:
                    if web_outputs!=None:
                        pass
                        """ D012:
                        web_outputs['contents']['outputs']=stripOutput(output)
                        web_outputs['contents']['return_code']=self.__last_system_command_ret
                        self.printweb(web_outputs)
                        """
                    else:
                        if self.__last_system_command_ret!=0:
                            self.println()
                            self.println(line='Echec running command ! Return code is:' + str(self.__last_system_command_ret))
                        self.println()

                    self.read(self.__wait_message, id=cid, id_type='cid')

        else:
            if self.getSharedQueueWebOutput()!=None:
                web_outputs['type']='raise'
                web_outputs['contents']={'type': 'NotManagedMenu', 'cid': cid, 'id_type': 'cid', 'messages': stripOutput('Not managed Menu:' + menu.__class__.__name__ + ' !')}
                self.printweb(web_outputs)
            else:
                kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, 'Not managed Menu:' + menu.__class__.__name__ + ' !').warn()
            self.read(self.__wait_message, id=cid, id_type='cid')

    def __exit_command(self, menu): ## Mixed (Menu/IMenu)
        selfMethod='__exit_command'
        self.println()

        light_mid='MENU-' + menu.getPipeUid()

        if menu.doConfirmExit():
            val=self.read(self.__indent*' ' + self.__confirm_exit_message + ' (y/n) ?', id=light_mid, id_type='lmid', doConfirm=True)
            if val!='y':return False
            return True

        if menu.getFct_exit_command()!=None:
            # Fct_command
            isOk=menu.getFct_exit_command()(self, menu, id=light_mid, id_type='lmid')
            if isOk:return True

            val=self.read(self.__indent*' ' + self.__confirm_exit_message + ' (y/n) ?', id=light_mid, id_type='lmid', doConfirm=True)
            if val!='y':return False
            return True

        return True

    def __input_field(self, menu, option_index): ## IMenu
        selfMethod='__input_field'
        from io import StringIO
        from . import ct
        option=menu.getChild(option_index)

        if self.getSharedQueueWebOutput()!=None:
            web_outputs=dict(WEB_OUTPUTS)
            web_outputs['type']='input_field'
            web_outputs['keys']={'menu': menu.getPipeUid(), 'option': str(option_index), 'input_field_instance': 'I' + tools.genUid()}
            iid='MENU-' + web_outputs['keys']['menu'] + '//OPTION-' + str(option_index) + '//INPUT_FIELD_INSTANCE-' + web_outputs['keys']['input_field_instance']
            web_outputs['contents']={'iid': iid, 'raws': []}
        else:
            iid=None
            web_outputs=None

        if option.getLHelp()!=None:
            mes=option.getLHelp()
            if web_outputs!=None:web_outputs['contents']['lhelp']=mes.split('\n')

            self.println()
            self.println(line=mes)
            self.println()

        ## Echec Input locked
        if option.isLocked():
            message='input are Locked for this command !'
            if web_outputs!=None:
                web_outputs=dict(WEB_OUTPUTS)
                web_outputs['type']='raise'
                web_outputs['contents']={'type': 'InputLocked', 'id':iid, 'id_type': 'iid', 'messages': stripOutput( message )}
                self.printweb(web_outputs)

            kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, message).warn()
            self.println()

            self.read(self.__wait_message, id=iid, id_type='iid')
            return

        mes=self.__input_field_message1 + ':' + option.getLabel() + '.'
        if web_outputs!=None:web_outputs['contents']['raws'].append(mes)
        self.println(line=mes)

        if not option.isValue():
            mes='(' + self.__input_field_message2  + ':' + option.getList_separator_car() + ')'
            if web_outputs!=None:web_outputs['contents']['raws'].append(mes)

            self.println()
            self.println(line=mes)

        # Formatting default message
        default=_default=option.getIODftValue()
        # M035: if not option.isValue() and len(default)==0:default=None
        if isinstance(default, (list, tuple)):_default='\n' + '\n'.join([str(line) for line in default])
        if default!=None:_default=self.__input_field_default_message.capitalize() + ': ' +  str(_default)
        else:_default=''

        # Formatting type message
        _type='Type:str'
        _checkIn=''
        # - type
        descs=option.getIODescs()
        if not option.isValue():
            if '*ltype' in descs:
                descs=descs['*ltype']
                if '*type' in descs:_type='Type:' + descs['*type']
            # - checkXIn
            elif '*checkXIn' in descs:_checkIn=' ' + self.__input_field_checkin_message + ':' + str(descs['*checkXIn'])[1:-1]
            else:descs=None
        elif '*type' in descs:_type='Type:' + descs['*type']
        # - checkIn
        if descs!=None and '*checkIn' in descs:_checkIn=' ' + self.__input_field_checkin_message + ':' + str(descs['*checkIn'])[1:-1]

        if hasattr(self, 'xml_node') and '*ksearch' in descs:
            """
            For now if self has xml_node: was called by kupd --kact (or --kcac)
            """
            from io import StringIO
            import texttable as tt
            sb = StringIO()
            hasKSearch = True

            ksearchs = descs['*ksearch']
            from kwadlib.tools import kSearch
            node = self.xml_node.getTopParent().getQuickTunNode(menu.tun)

            rows = kSearch(node, 'name', ksearch_wks=ksearchs, verbose=self.__verbose)

            okey = ksearchs['okey']
            oattrs = list(ksearchs['oattrs'])
            if oattrs[0] != okey:
                del oattrs[oattrs.index(okey)]
                oattrs = oattrs.insert(0, okey)
            if 'okeys' in ksearchs:
                okeys = ksearchs['okeys']
            else:
                okeys = None

            # Blanks for missing fields:
            ksearch_keys = []
            for lattrs in rows:
                ksearch_keys.append(lattrs[okey])
                for attr in oattrs:
                    if attr not in lattrs:lattrs[attr] = ''
            ksearch_keys.sort()

            if web_outputs != None and hasattr(self, 'xml_node') and descs != None:
                option_list_rows = list(rows)
                option_list_oattrs = oattrs
                option_list_okey = okey
                option_list_okeys = okeys

                # Making indexes:
                option_list_indexes = { k:[] for k in okeys}
                for i in range(len(rows)):
                    d = rows[i]
                    for key in okeys:
                        option_list_indexes[key].append(d[key] + '_' + str(i))
                # Sorting indexes:
                for key in okeys:option_list_indexes[key].sort()

            else:
                tabs = tt.Texttable()
                tabs.header(oattrs)

                for lattrs in rows:
                    rows = []
                    for attr in oattrs:
                        v = lattrs[attr]
                        rows.append(v)
                    tabs.add_row(rows)

                """
                names = ['bar', 'chocolate', 'chips']
                weights = [0.05, 0.1, 0.25]
                costs = [2.0, 5.0, 3.0]
                unit_costs = [40.0, 50.0, 12.0]
                for row in zip(names, weights, costs, unit_costs):
                    tab.add_row(row)
                """

                s = tabs.draw()
                _checkIn += '\n' + s + '\n'
        else:
            hasKSearch = False

        # ----------- #
        # Read Value: #
        # ----------- #
        mes=_type + _checkIn + _default
        if web_outputs!=None:
            _v=option.getIOValue()
            try:ct.unDress(_v)
            except:_v=None
            web_outputs['contents']['value']=_v
            web_outputs['contents']['default']=_default
            web_outputs['contents']['is_value']=option.isValue()

            if hasKSearch:
                web_outputs['type']='option_list'
                ## web_outputs['contents']={'iid': iid, 'rows': {'k1': 'v1'}}
                web_outputs['contents']={'iid': iid, 'rows': option_list_rows, 'oattrs': option_list_oattrs, 'okey': option_list_okey, 'okeys': option_list_okeys, 'option_list_indexes': option_list_indexes}
                self.printweb(web_outputs)
            else:
                web_outputs['contents']['raws'].extend(mes.split('\n'))
                self.printweb(web_outputs)

        self.println()
        self.println(line=mes)
        self.println()

        # A049: Support of *password: <value read>: hide password:
        descs=option.getIODescs()
        if option.isValue() and '*password' in descs and descs['*password']:is_password=True
        else:is_password=False
        # A049: +is_password:
        value=ovalue=self.read(option.getLabel() + ' ?', is_value=True, is_password=is_password, id=iid, id_type='iid')

        if hasKSearch and value not in ksearch_keys:
            message = 'Should be one of: %s' % ', '.join(ksearch_keys)
            if web_outputs != None:
                web_outputs = dict(WEB_OUTPUTS)
                web_outputs['type'] = 'raise'
                web_outputs['contents'] = {'type': 'IncorectValue', 'id': iid, 'id_type': 'iid', 'messages': stripOutput(message)}
                self.printweb(web_outputs)

            self.println(line=message)
            self.println()

            self.read(self.__wait_message, id=iid, id_type='iid')
            return

        if value in ('', None, 'None'):value=None
        elif not option.isValue():
            from . import ct
            value=value.split(option.getList_separator_car())
            ## Echec on ct
            try:
                value=ct.unDress(value)
            except Exception as e:
                message=str(e)
                if web_outputs!=None:
                    web_outputs=dict(WEB_OUTPUTS)
                    web_outputs['type']='raise'
                    web_outputs['contents']={'type': 'IncorectValue', 'id':iid, 'id_type': 'iid', 'messages': stripOutput( message )}
                    self.printweb(web_outputs)

                self.println(line=message)
                self.println()

                self.read(self.__wait_message, id=iid, id_type='iid')
                return


        # ---------- #
        # Set Value: #
        # ---------- #
        # Fct_command
        if web_outputs!=None:fct_output=StringIO()
        else:fct_output=None

        if option.getFct_command()!=None:
            message=None
            try:
                success=option.getFct_command()(self, menu, option_index, value=value, command=option.getCommand(), id=iid, id_type='iid')
            except Exception as e:
                message=str(e)
                ## Echec on fct_command
                if web_outputs!=None:
                    web_outputs=dict(WEB_OUTPUTS)
                    web_outputs['type']='raise'
                    web_outputs['contents']={'type': 'IncorrectValue', 'id':iid, 'id_type': 'iid', 'messages': stripOutput( message )}
                    self.printweb(web_outputs)

                self.println(line=message)
                self.println()
                self.read(self.__wait_message, id=iid, id_type='iid')
                return

        ## Echec on input Value
        elif not option.setIOValue(value, verbose=self.__verbose, fct_output=fct_output):
            if web_outputs!=None:
                message=None
                if fct_output.getvalue() not in ('', None):message=fct_output.getvalue()
                web_outputs=dict(WEB_OUTPUTS)
                web_outputs['type']='raise'
                web_outputs['contents']={'type': 'IncorectValue', 'id':iid, 'id_type': 'iid', 'messages': stripOutput( message )}
                self.printweb(web_outputs)

            self.println()

            self.read(self.__wait_message, id=iid, id_type='iid')
            return

    # A049: +is_password:
    def read(self, info=None, doConfirm=False, doConfirmOk='y', doConfirmKo='n', isChoice=False, is_value=False, is_password=False, id=None, id_type=None, _menu=None, allow_cars=None):
        """
        Note: Option _menu is only allowed from read new option.
        """
        selfMethod='read'
        import sys
        if not self.isAlive():return 'suicide'

        # A045:
        def splitName(data):
            if data.startswith('name='):name=data[5:]
            if data.startswith('title='):name=data[6:]
            name=name.replace('_', ' ')
            index = str(_menu.getChildByTitle(name).getIndex())
            return index


        if self.getSharedQueueInput()==None:
            try:
                import os

                # A049:
                if is_password:
                    from getpass import getpass
                    getpass(info)
                else:data=input(info)

                # A040:
                data=sanitize_input(data, allow_cars=allow_cars)
                if self.__log:sys.stdout.writef(data)
            except KeyboardInterrupt:
                import sys
                sys.exit(1)


            # Record ids
            self.__record(data, menu=_menu) # record inputs
            return data

        # Put Info:
        if self.getSharedQueueWebOutput()!=None:
            if info==self.__wait_message:
                doConfirm=True
                doConfirmKo=''
                doConfirmKo=None
                info=self.__web_wait_message
            dialog_id='SECID_' + tools.genUid()
            web_outputs=dict(WEB_OUTPUTS)
            web_outputs['type']='dialog'
            # A049: +is_password:
            web_outputs['contents']={'dialog_id': dialog_id, 'is_choice': isChoice, 'is_to_confirm': doConfirm, 'is_value': is_value, 'is_password': is_password, 'confirm_ok': doConfirmOk, 'confirm_ko': doConfirmKo, id_type: id, 'id_type': id_type, 'messages': info.split('\n')}
            self.printweb(web_outputs)

        if info!=None:self.println(line=info, noln=True)

        # Get data:
        try:
            if self.getSharedQueueWebOutput()!=None:
                # Announcing stuck on read with a preceding event !
                web_outputs=dict(WEB_OUTPUTS)
                web_outputs['type']='raise'
                web_outputs['contents']={'type': 'APIMENU_STUKE_ON_READING'}
                self.printweb(web_outputs)

            data=self.getSharedQueueInput().get(self.__queue_wait)
            # A040:
            data=sanitize_input(data, allow_cars=allow_cars)
            # A044:
            if data.startswith('name=') or data.startswith('title='): data = splitName(data)
        except:  # Issue reading on q:
            # M043: if not (self.isBatch() and self.isGoing()):
            if (not (self.isBatch() and self.isGoing())) or self.getSharedQueueWebOutput()!=None:
                self.stop()
                return 'suicide'
            else:
                self.stopGoing()
                # Reread (real user input this time) <-- instead of --> batch inputs :

                try:
                    data=input()
                    # A040:
                    data=sanitize_input(data, allow_cars=allow_cars)
                    if self.__log:sys.stdout.writef(data)
                except KeyboardInterrupt:
                    import sys
                    sys.exit(1)

                # Record ids
                self.__record(data, menu=_menu) # record inputs
                return data

        if data=='suicide':
            if not (self.isBatch() and self.isGoing()):
                self.stop()
                return 'suicide'
            else:
                self.stopGoing()
                # Reread (real user input this time) <-- instead of --> batch inputs :
                try:
                    # A043: allow fail back on input for web:
                    if self.getSharedQueueWebOutput() != None:
                        # Announcing stuck on read with a preceding event !
                        web_outputs = dict(WEB_OUTPUTS)
                        web_outputs['type'] = 'raise'
                        web_outputs['contents'] = {'type': 'APIMENU_STUKE_ON_READING'}
                        self.printweb(web_outputs)
                        data = self.getSharedQueueInput().get(self.__queue_wait)
                        # A040:
                        data = sanitize_input(data, allow_cars=allow_cars)
                        # A044:
                        if data.startswith('name=') or data.startswith('title='):data=splitName(data)
                    else: # M043:
                        data=input()
                        # A040:
                        data = sanitize_input(data, allow_cars=allow_cars)
                    if self.__log:sys.stdout.writef(data)
                except KeyboardInterrupt:
                    import sys
                    sys.exit(1)

                # Record ids
                self.__record(data, menu=_menu) # record inputs
                return data

        data=str(data).strip()

        if self.getSharedQueueWebOutput()!=None:
            web_outputs=dict(WEB_OUTPUTS)
            web_outputs['type']='data_input'
            web_outputs['contents']={'dialog_id': dialog_id, 'data': data, id_type: id, 'id_type': id_type}
            self.printweb(web_outputs)

        self.println(line=data)
        
        # - work names paths
        if _menu!=None and (data.startswith('title=') or data.startswith('name=')):
            childs=_menu.getChilds()
            
            if data.startswith('title='):
                title=data.split('title=')[1]
                for child in childs:
                    if not isinstance(child, BaseMenu):continue
                    if child.getTitle()==title:
                        data=str(child.getIndex())
                        break
            else:
                name=data.split('name=')[1]
                for child in childs:
                    if not isinstance(child, BaseOption):continue
                    if child.getName()==name:
                        data=str(child.getIndex())
                        break
        
        if self.isBatch() and self.__pause!=None:
            from time import sleep
            sleep(self.__pause)
        
        # Record ids
        self.__record(data, menu=_menu) # record inputs
        
        return data
    
    def println(self, line=None, noln=False, nospace=False):
        selfMethod='println'
        if self.getSharedQueueWebOutput() != None and not self.doLog():return

        if self.getSharedQueueWebOutput() != None: # doLog is True
            import sys
            if line==None:line=''
            if not noln:sys.stdout.writef(line + '\n')
            else:sys.stdout.writef(line + ' ')
        else:
            if line==None:line=''
            if not noln:print(line)
            else:print(line, end=' ')
        return

    def printweb(self, line=None, noln=False, nospace=False, shared_queueWebOutput=None):
        selfMethod='printweb'

        return kastweblib.printweb(line=line, noln=noln, nospace=nospace, shared_queueWebOutput=self.getSharedQueueWebOutput())

    def webOptionList(self, line):
        if self.getSharedQueueWebOutput()==None:raise
        self.getSharedQueueWebCommandOutput().put("option-list[[COID]]{'a':Return Code is:'}")


    def ioprint_process_output(self, output=None, coid=None):
        selfMethod='print_process_output'
        if self.getSharedQueueWebOutput() == None:
            if output==None:return
            if not isinstance(output, str):
                if self.__verbose >= 20:
                    import traceback, sys
                    traceback.print_stack(file=sys.stdout)
                raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'output', 'str', str(output))
            self.println(line=output, noln=False, nospace=False)
            return

        if coid==None:
            coid = tools.genUid()
            self.getSharedQueueWebCommandOutput().put(coid + '[[COID]][[NEW_PROCESS_OUTPUT]]', False)  # new ooid

        if output!=None:
            self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + output.replace('\n', '<BR>'), False)
            self.println(line=output, noln=False, nospace=False)

        return coid

    # A049: +display_command:
    # A051: + command_enter, command_exit
    def execWebCommand(self, command, command_enter=None, command_exit=None, display_command=None, envs=None, stdin=None, do_follow_menu=False):
        from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
        from subprocess import CalledProcessError
        from io import StringIO
        import sys
        sb = StringIO()
        if display_command==None:display_command=command # A049
        """
        from base64 import b64encode, b64decode
        data = b64encode(buf)  # encode binary buffer to b64
        buf = b64decode(data)  # decode b64 to binary buffer
        """
        coid = tools.genUid()
        # A003: useshell is False and stdin is provided only when do_follow_menu is True !!

        self.getSharedQueueWebCommandOutput().put(coid + '[[COID]][[NEW_PROCESS_OUTPUT]]', False)  # new ooid
        self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]Execute command:' + display_command, False) # A049
        self.getSharedQueueWebCommandOutput().put(coid + '[[COID]] ', False)

        system_command_ret=0 #M051
        try:
            # A051:
            if command_enter != None:
                sb.write('Found Command enter: %s:\n' % command_enter)
                popen = Popen(command_enter, stdin=SUBPROCESS_PIPE if stdin != None else None, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                output, stderr = popen.communicate()
                system_command_ret = popen.wait()
                if stderr!=None:
                    if output==None:output=''
                    output+=stderr
                if output!=None:sb.write(output + '\n')

                if system_command_ret != 0:
                    self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + sb.getvalue(), False)
                    if (self.doLog() and self.doLogOutput()) and not do_follow_menu:  # write to log:
                        sys.stdout.writef(sb.getvalue())

            if system_command_ret==0:
                # M003: popen = Popen(command, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
                """
                import subprocess
    
                command = "awk '{print $4}'"
                popen = Popen(command, stdin=SUBPROCESS_PIPE, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
                popen.stdin.writelines('b c a z f')
                popen.stdin.close()
    
                for stdout_line in iter(popen.stdout.readline, ""):
                    print 'output:', stdout_line
                """

                popen = Popen(command, stdin=SUBPROCESS_PIPE if stdin != None else None, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                if stdin != None:
                    popen.stdin.write(bytes(stdin.strip(), 'utf-8'))
                    popen.stdin.close()

                """ M046: Bug correction: Hangs when Process may wait on stdin for trivial input:
                    This is only critical for web interface as the input prompt is tighted to the tty.
                for stdout_line in iter(popen.stdout.readline, ""):
                    self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + stdout_line.rstrip(), False)
                    sb.write(stdout_line)
                    if (self.doLog() and self.doLogOutput()) and not do_follow_menu: # write to log:
                        sys.stdout.writef(stdout_line)
                """

                if do_follow_menu:
                    for stdout_line in iter(popen.stdout.readline, ""):
                        self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + stdout_line.rstrip(), False)
                        sb.write(stdout_line)
                else:
                    """ M046: Bug correction: Hangs when Process may wait on stdin for trivial input:
                        This is only critical for web interface as the input prompt is tighted to the tty."""
                    from kwadlib.default import PROCESS_TIMEOUT
                    import time
                    start = time.time()

                    # Prepare non blocking read:
                    import fcntl
                    import os
                    fd = popen.stdout.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                    while popen.poll()==None:
                        try:
                            stdout_part = popen.stdout.read()
                            # make sure it returned data
                            if stdout_part:
                                start = time.time()
                                self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + stdout_part.rstrip(), False)
                                sb.write(stdout_part)
                                if (self.doLog() and self.doLogOutput()):  # write to log:
                                    sys.stdout.writef(stdout_part)
                                continue
                        except:
                            pass

                        time.sleep(2)
                        if time.time() - start > PROCESS_TIMEOUT:
                            raise Exception('\nProcess Timeout ! Advise run this command using kastmenu localy on the machine to debug.\nThere is much probability this command is misbehaving waiting for some input.\nIf you still want to increase the KastMenu Process Timeout (%s seconds), Advise the KastMenu administrator to increase the KastMenu config attribute: "process_timeout". ' % str(PROCESS_TIMEOUT))

                ## (xstdout, xstderr) = popen.communicate()
                # Read last:
                stdout_part = popen.stdout.read()
                # make sure it returned data
                if stdout_part:
                    self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + stdout_part.rstrip(), False)
                    sb.write(stdout_part)
                    if (self.doLog() and self.doLogOutput()) and not do_follow_menu:  # write to log:
                        sys.stdout.writef(stdout_part)
                popen.stdout.close()
                system_command_ret = popen.wait()

            # A051:
            if command_exit != None:
                sb.write('\nFound Command exit: %s:\n' % command_exit)
                popen = Popen(command_enter, stdin=SUBPROCESS_PIPE if stdin != None else None, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, executable='/bin/bash', universal_newlines=True, shell=True, env=envs)
                output, stderr = popen.communicate()
                system_command_ret = popen.wait()
                if stderr!=None:
                    if output==None:output=''
                    output+=stderr
                if output!=None:sb.write(output + '\n')

                if system_command_ret != 0:
                    self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + sb.getvalue(), False)
                    if (self.doLog() and self.doLogOutput()) and not do_follow_menu:  # write to log:
                        sys.stdout.writef(sb.getvalue())

        except CalledProcessError as e:
            system_command_ret = e.returncode
            self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + e.output, False)
            if (self.doLog() and self.doLogOutput()) and not do_follow_menu:  # write to log:
                sys.stdout.writef(e.output)
            sb.write(e.output)

        except Exception as e:
            self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + str(e), False)
            if (self.doLog() and self.doLogOutput()) and not do_follow_menu:  # write to log:
                sys.stdout.writef(str(e))
            sb.write(str(e))
            system_command_ret = 1
        except:
            system_command_ret = 1

        message = 'Return Code is:' + str(system_command_ret)
        self.getSharedQueueWebCommandOutput().put(coid + '[[COID]] ', False)
        self.getSharedQueueWebCommandOutput().put(coid + '[[COID]]' + message, False)
        if (self.doLog() and self.doLogOutput()) and not do_follow_menu:  # write to log:
            sys.stdout.writef(message)
        sb.write(message)

        return system_command_ret, sb.getvalue()



    def __record(self, data, menu=None):
        selfMethod='__record'
        optionIsNotAMenu=kastmenuxception.kastmenuOptionIsNotAMenu(self.__class__.__name__, selfMethod, 'Option:' + '.'.join(self.__records) + '.' + str(data) + ' is not a Menu. Advice:all Options must lead to a Menu when using the go argument.')
        
        # record entries
        if menu!=None:
            try:
                value=int(data)
                child=menu.getChild(value)
                if isinstance(child, BaseMenu):
                    value='title=' + child.getTitle()  # Menu
                else:
                    value='name=' + child.getName() # Option
            except:
                value=data
        else:value=data
            
        self.__records.append(data)
        # M045:
        self.__record_names.append(value.replace(' ', '_'))

def serialize(value):
    from . import ct
    return ct.unDress(value)

def stripOutput(output):
    # Converting multiple \n\n\n... to only one:
    output='\n'.join(output.split('\n')).replace('\n\n', '\n')
    # Replacing:
    output=output.replace('\n', '&&a1z2e34r&&')
    for rsc in WEB_ESCAPES:output=output.replace(rsc[0], rsc[1])
    
    return output.split('&&a1z2e34r&&')

class CommandLock:

    def __init__(self, name=None, timeout=None):
        selfMethod = '__init__'
        if timeout!=None and name==None:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'lock_timeout cannot be provided if name is not !')
        self.__name, self.__timeout=name, timeout
    
    def getLockName(self):
        return self.__name
    
    def getLockTimeOut(self):
        return self.__timeout
    
    def lockAcquire(self, temp_dir, command=None):
        selfMethod='lockAcquire'
        if self.getLockName()==None:return
        from os import path, remove
        from .tools import genUid
        import time
        lock=path.realpath(path.normpath(temp_dir + '/' + self.getLockName()))
        
        # Check lock TiemOut :
        if path.isfile(lock):
            delta = time.time() - path.getctime(lock)
            if delta >= self.getLockTimeOut():remove(lock)
            else:
                uid, command=self.getLockContent(lock)
                raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Unable to acquire command Lock:' + lock + '. The Lock is already used since:' + str(int(delta)) + 's by :' + command + ' ! Please wait up to: ' + str(int(self.getLockTimeOut() - delta)) + 's.')
            
        uid=genUid()
        fd=open(lock, 'wb')
        fd.write(bytes(uid + ',' + command, 'utf-8'))
        fd.close()
        
        return uid

    def lockRelease(self, temp_dir, uid=None):
        selfMethod='lockRelease'
        if self.getLockName()==None:return False
        from os import path, remove
        import time
        lock=path.realpath(path.normpath(temp_dir + '/' + self.getLockName()))
        if not path.isfile(lock):return False
        
        # Check lock TimemOut :
        if path.isfile(lock) and time.time() - path.getctime(lock) >= self.getLockTimeOut():
            remove(lock)
            return True
            
        # Get lock content
        _uid, command=self.getLockContent(lock)
        if uid!=_uid:return False
        
        remove(lock)
        
        return True
    
    def getLockContent(self, lock):
        fd=open(lock)
        r=fd.read()
        fd.close()
        spl=r.split(',')
        uid=spl[0].strip()
        command=','.join(spl[1:])
        return uid, command



class VideoColors:

    def __init__(self, set_color=False, police_bold=False, police_color=None, police_bgcolor=None):
        self.setColor(set_color=set_color)
        self.setBold(police_bold=police_bold)
        self.setFrColor(police_color)
        self.setBgColor(police_bgcolor)
    
    def doSetColor(self):
        return self.__do_set_color  
    
    def setColor(self, set_color=True):
        selfMethod='doSetColor'
        if not isinstance(set_color, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'set_color', 'bool', str(set_color))
        self.__do_set_color=set_color
        
    def doSetBold(self):
        return self.__do_set_bold
               
    def setBold(self, police_bold=True):
        selfMethod='doSetBold'
        if not isinstance(police_bold, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'police_bold', 'bool', str(police_bold))
        self.__do_set_bold=police_bold
        
    def getFrColor(self):
        return self.__frcolor
        
    def setFrColor(self, police_color):
        selfMethod='setFrColor'
        if police_color!=None and police_color not in VIDEO_COLORS:raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'police_color', 'In ' + str(VIDEO_COLORS), str(police_color))
        self.__frcolor=police_color
        
    def getBgColor(self):
        return self.__bgcolor 

    def setBgColor(self, police_bgcolor):
        selfMethod='setBgColor'
        if police_bgcolor!=None and police_bgcolor not in VIDEO_COLORS:raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'police_bgcolor', 'In ' + str(VIDEO_COLORS), str(police_bgcolor))
        selfMethod='setBgColor'
        self.__bgcolor=police_bgcolor 



class BaseMenu:
        
    def __init__(self, title, sub_title=None, roles_autz=None, except_roles=None, contents=None, help=None, lhelp=None, fct_exit_command=None, do_check_all=True, confirm_exit=False, fct_enter=None, fct_leave_forward=None, fct_leave_backward=None):
        """
title : This is the menu title

sub_title : This is the menu title

fct_exit_command : Default None.
    When called programatically. This function interceptor is called before exiting a Menu.

do_check_all : Default True.
    For IMenu (Input Menu) only.
    Will invite the user to check all the Input field and run the validation sequence.

confirm_exit : Default False.
    Does this Menu require an acceptance to Exit.

fct_enter : Default None.
    When called programatically. This function interceptor is called before entering a Menu.

fct_leave_forward : Default None.
    When called programatically. This function interceptor is called before leaving forward a Menu.

fct_leave_backward : Default None.
    When called programatically. This function interceptor is called before leaving backward a Menu.
"""
        selfMethod='__init__'

        if not isinstance(title, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'title', 'str', str(title))
        if sub_title!=None and not isinstance(sub_title, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'sub_title', 'str', str(sub_title))
        if contents!=None and not isinstance(contents, list):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'contents', 'list', str(contents))
        if help!=None and not isinstance(help, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'help', 'str', str(help))
        if lhelp!=None and not isinstance(lhelp, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'lhelp', 'str', str(lhelp))
        if fct_exit_command!=None and not isinstance(fct_exit_command, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_exit_command. The type expected is: ether a function or a method ! Received:' + str(fct_exit_command) + ' !')
        if confirm_exit and not do_check_all:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'IMenu:' + title + ', confirm_exit is not allowed when do_check_all is False ! Received for: confirm_exit:' + str(confirm_exit) + ' !')
        if fct_enter!=None and not isinstance(fct_enter, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_enter. The type expected is: ether a function or a method ! Received:' + str(fct_enter) + ' !')
        if fct_leave_forward!=None and not isinstance(fct_leave_forward, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_leave_forward. The type expected is: ether a function or a method ! Received:' + str(fct_leave_forward) + ' !')
        if fct_leave_backward!=None and not isinstance(fct_leave_backward, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_leave_backward. The type expected is: ether a function or a method ! Received:' + str(fct_leave_backward) + ' !')
        
        # - MultiLang support
        title, help, lhelp=MULTILANG.convert(title, help, lhelp)

        # M045: self.__title=title
        self.__title=title.replace('_', ' ').replace('.', ' ')
        self.__sub_title=sub_title

        # ++
        # self.__contents=()
        # if contents!=None:self.__contents=tuple(contents.split('\n'))
        # M035:
        self.__contents =None
        if contents!=None:self.__contents=contents

        self.__help=help
        self.__lhelp=lhelp
        self.__fct_exit_command=fct_exit_command
        self.__confirm_exit=confirm_exit
        self.__childs=[]
        self.__index=0
        self.__doDelete=False
        self.__pages=[]
        self.__pipeIndex=None
        self.__pipe_uid=None
        self.__currentPageIndex=0
        self.__canBeDeleted=True
        self.__isFed=False
        self.__fct_enter=fct_enter
        self.__fct_leave_forward=fct_leave_forward
        self.__fct_leave_backward=fct_leave_backward
        self._isFirstMenu=False
        self.aggregatParent=None        
        self.__config=None
        self.__roles_autz=checkRolesAutzSyntax(roles_autz, message='role_autz on tag: ' + str(self.getAggregatFiliation([])))
        if except_roles==None:except_roles=[]
        self.__except_roles=except_roles
        # A039:
        self.__session_dir = None  # Will be setup on setConfig()

    def isFirstMenu(self):
        return self._isFirstMenu

    def leave_forward(self, config, id=None, id_type=None):
        if self.__fct_leave_forward!=None:self.__fct_leave_forward(config, self, id=id, id_type=id_type)

    def leave_backward(self, config, id=None, id_type=None):
        doLeave=True
        if self.__fct_leave_backward!=None:doLeave=self.__fct_leave_backward(config, self, id=id, id_type=id_type)
        
        return doLeave
        
    def enter(self, config, id=None, id_type=None):
        if self.__fct_enter!=None:self.__fct_enter(config, self, id=id, id_type=id_type)
        
    def setNotFed(self):
        self.__isFed=False
        
    def clear(self):
        self.__childs=[]
        self.__currentPageIndex=0

    def getLinesCount(self):
        # M035:
        return len(self.getContentsAsList())
        
    def getTitle(self):
        return self.__title                
    
    def getSubTitle(self):
        return self.__sub_title        
    
    def getName(self):
        return self.__title
    
    def getContents(self):
        return self.__contents

    # M035:
    def getContentsAsList(self):
        if isinstance(self.__contents, (tuple, list)):return list(self.__contents)
        elif self.__contents!=None: return str(self.__contents).split('\n')
        return []
    
    def getHelp(self):
        return self.__help

    def getLHelp(self):
        return self.__lhelp
    
    def doConfirmExit(self):
        return self.__confirm_exit    
    
    def getFct_exit_command(self):
        return self.__fct_exit_command
    
    def isFed(self):
        return self.__isFed
    
    def getIndex(self):
        return self.__index    
    
    def _setIndex(self, index):
        self.__index=index
        
    def getPipeIndex(self):
        return self.__pipeIndex

    def _setPipeIndex(self, index):
        self.__pipeIndex=index        
        
    def getPipeUid(self):
        return self.__pipe_uid

    def _setPipeUid(self, uid):
        self.__pipe_uid=uid

    def calcPages(self, screen_max_lines, do_skip_line):
        selfMethod='calcPages'
        if len(self.__childs)==0:raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Menu:' + self.getTitle() + ', has no child !')
        if do_skip_line:more=1
        else:more=0
        
        self.__pages=[]
        page=[]
        maxPage=0
        self.__pages.append(page)
        for index in range(len(self.__childs)):
            child=self.__childs[index]
            child._setIndex(index + 1)

            # check Option max dont exeed screen_max_lines.
            if child.getLinesCount() > screen_max_lines:
                raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Menu:' + self.getTitle() + '/Option:' + child.getName() + '/' + str(index) + ', has a number of lines greater than the max number of lines:' + str(screen_max_lines) + ' allowed for a page. Your option value is:' + '\n' + child.getContents() + ' !')

            if maxPage + child.getLinesCount() + more > screen_max_lines:
                page=[]
                maxPage=0
                self.__pages.append(page)

            page.append(index + 1)
            maxPage+=child.getLinesCount() + more
            
        if self.__currentPageIndex>=len(self.__pages):self.pageZero()
        
        return tuple(self.__pages)
    
    def getChilds(self):
        return tuple(self.__childs)
    
    def getChildNumber(self):
        return len(self.__childs)
        
    def getChild(self, index):
        selfMethod='getChild'
        if index>len(self.__childs):raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Menu:' + self.getTitle() + ', unknown Menu child index:' + str(index) + ', max Menu child index is:' + str(len(self.__childs)) + ' !')
        return self.__childs[index - 1]
        
    def getChildByTitle(self, title):
        selfMethod='getChildByTitle'
        for child in self.__childs:
            if child.getName()==title:return child
        
    def delChild(self, index):
        selfMethod='delChild'
        if index>=len(self.__childs):raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Menu:' + self.getTitle() + ', unknown Menu child index:' + str(index) + ', max Menu child index is:' + str(len(self.__childs)) + ' !')
        del self.__childs[index]
        
    def _canBeDeleted(self):
        self.__canBeDeleted=True
        
    def _cantBeDeleted(self):
        self.__canBeDeleted=False

    def isDeletable(self):
        return self.__canBeDeleted
    
    def delete(self):
        selfMethod='delete'
        if not self.__canBeDeleted:raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Menu:' + self.getTitle() + ' cannot be deleted !')
        self.__doDelete=True            
        
    def doDelete(self):
        return self.__doDelete
        
    def isDeleted(self):
        return self.__isDeleted
    
    def getCurrentPageIndex(self):
        return self.__currentPageIndex
    
    def getCurrentPage(self):
        return tuple(self.__pages[self.__currentPageIndex])
    
    def getPageNumber(self):
        return len(self.__pages)    
    
    def getPages(self):
        return tuple(self.__pages)
        
    def pageUp(self):
        if self.__currentPageIndex < len(self.__pages) -1:
            self.__currentPageIndex+=1
            return True
        return False        

    def pageDown(self):
        if self.__currentPageIndex > 0:
            self.__currentPageIndex-=1
            return True
        return False
    
    def pageZero(self):
        if self.__currentPageIndex!=0:
            self.__currentPageIndex=0
            return True
        self.__currentPageIndex=0
        return False
        
    def accept(self, p_visitor, p_specificRecursive):                        
        selfMethod='accept'
        if  __debug__ and isinstance(p_specificRecursive, bool)!=True:
            raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'p_specificRecursive', 'bool', str(p_specificRecursive))
    
        if p_visitor.recursiveImbricatedMenus == True and p_specificRecursive == True:
            p_visitor.visitImbricatedMenus(self)

    def getAggregatParent(self):
        if self.aggregatParent!=None:return self.aggregatParent()
        else:return None
       
    def setAggregatParent(self, p_baseMenu):
        selfMethod='setAggregatParent'
        if  __debug__ and not isinstance(p_baseMenu, BaseMenu):
            raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'p_baseMenu', 'BaseMenu', str(p_baseMenu))
        import weakref
            
        self.aggregatParent=weakref.ref(p_baseMenu)

    def removeAggregatParent(self):
        self.aggregatParent=None

    def getAggregatFiliation(self, p_aggFiliation):
        selfMethod='getAggregatFiliation'
        if  __debug__ and not isinstance(p_aggFiliation, list):
            raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'p_aggFiliation', 'list', str(list))
        p_aggFiliation.append(self)

        if  self.getAggregatParent()!=None and not self.getAggregatParent().isFirstMenu():self.getAggregatParent().getAggregatFiliation(p_aggFiliation)                            
        
        return p_aggFiliation

    def getAggregatIndexFiliation(self):
        selfMethod='getAggregatIndexFiliation'
        l=[]
        self.getAggregatFiliation(l)
        l=[str(o.getIndex()) for o in l]
        
        return '/'.join(l)

    def getTopParent(self):
        if not self.isFirstMenu() and self.getAggregatParent()!=None:
            return self.getAggregatParent().getTopParent()
        return self

    def getTop(self):
        return self.getTopParent()
    
    def setConfig(self, config):
        selfMethod='setConfig'
        if not isinstance(config, Config):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'config', Config, str(config))
        import weakref
        self.__config=weakref.ref(config)

    def getSessionDir(self, config): # A039:
        from os import mkdir
        if self.__session_dir!=None:return self.__session_dir

        self.__session_dir = config.getTempDir() + '/' + tools.genUid()
        mkdir(self.__session_dir)
        return self.__session_dir

    def getConfig(self):
        selfMethod='getConfig'
        if (self.isFirstMenu() or self.getAggregatParent()==None) and self.__config==None:
            raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'You must use menu.setConfig(config) on the first Menu,  prior any add operation on a it !')
            
        if self.__config==None:
            import weakref
            self.__config=weakref.ref(self.getTop().getConfig())
            
        return self.__config()
        
    def add(self, child):
        selfMethod='addChild'
        if not isinstance(child, self.allowedChilds):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'child', self.allowedChilds, str(child))
        child.setAggregatParent(self)

        if not child.checkAutz('display'):
            child.removeAggregatParent()
            return
        self.__isFed=True

        self.__childs.append(child)
        
    #+roles support
    def checkAutz(self, autz='display'):
        self_funct='checkAutz'
        rolesAutzDft=self.getConfig().getRolesAutzDft()
        roles=self.getConfig().getSharedRoles()
        # AFAIRE: except_roles
        rolesAutz=self.__roles_autz
        if rolesAutz==None:rolesAutz=rolesAutzDft
        passed=False

        if '+*optimistic' in rolesAutzDft['*anyone'].split(';'):optimistic=True
        else:optimistic=False

        for role in roles:
            if role not in rolesAutz:continue
            if role in self.__except_roles:continue
            autzs=rolesAutz[role].split(';')
            if '-' + autz in autzs:continue
            if '+all' in autzs or '+' + autz in autzs:
                passed=True
                break
            if optimistic:
                passed=True
                break

        return passed

    def checkCommandAutz(self, autz='execute'):
        self_funct='checkCommandAutz'
        rolesAutzDft=self.getConfig().getRolesAutzDft()
        roles=self.getConfig().getSharedRoles()
        rolesAutz=self.__roles_autz
        if rolesAutz==None:rolesAutz=rolesAutzDft
        passed=False
        
        if '+*optimistic' in rolesAutzDft['*anyone'].split(';'):optimistic=True
        else:optimistic=False

        for role in roles:
            if role not in rolesAutz:continue
            if role in self.__except_roles:continue
            autzs=rolesAutz[role].split(';')
            if '-' + autz in autzs:continue
            if '+all' in autzs or '+' + autz in autzs:
                passed=True
                break
            if optimistic:
                passed=True
                break

        return passed



class Menu(BaseMenu, VideoColors):

    def __init__(self, title, sub_title=None, roles_autz=None, except_roles=None, contents=None, help=None, lhelp=None, fct_exit_command=None, confirm_exit=False, fct_enter=None, fct_leave_forward=None, fct_leave_backward=None, set_color=False, police_bold=False, police_color=None, police_bgcolor=None):
        """
title : This is the menu title

sub_title : This is the menu title

fct_exit_command : Default None.
    When called programatically. This function interceptor is called before exiting a Menu.

confirm_exit : Default False.
    Does this Menu require an acceptance to Exit.

fct_enter : Default None.
    When called programatically. This function interceptor is called before entering a Menu.

fct_leave_forward : Default None.
    When called programatically. This function interceptor is called before leaving forward a Menu.

fct_leave_backward : Default None.
    When called programatically. This function interceptor is called before leaving backward a Menu.
"""        
        selfMethod='__init__'
        self.allowedChilds=(Option, Menu, IMenu)
        
        BaseMenu.__init__(self, title, sub_title=sub_title, roles_autz=roles_autz, except_roles=except_roles, contents=contents, help=help, lhelp=lhelp, fct_exit_command=fct_exit_command, confirm_exit=confirm_exit, fct_enter=fct_enter, fct_leave_forward=fct_leave_forward, fct_leave_backward=fct_leave_backward)
        VideoColors.__init__(self, set_color=set_color, police_bold=police_bold, police_color=police_color, police_bgcolor=police_bgcolor)

    def accept(self, p_visitor):

        if (p_visitor.childFirst):
            BaseMenu.accept(self, p_visitor, p_visitor.recursiveMenu);
            if p_visitor.treatAncestor:
                p_visitor.visitBaseMenu(self)
                p_visitor.visitMenu(self) 
            else:
                p_visitor.treatAncestor=True
        else:
            if p_visitor.treatAncestor:
                p_visitor.visitBaseMenu(self)
                p_visitor.visitMenu(self)
            else:
                p_visitor.treatAncestor=True
            BaseMenu.accept(self, p_visitor, p_visitor.recursiveMenu)



class IMenu(BaseMenu, VideoColors, CommandLock):
    # A051: + command_enter, command_exit
    def __init__(self, title, sub_title=None, roles_autz=None, except_roles=None, contents=None, help=None, lhelp=None, command=None, command_enter=None, command_exit=None, fct_command=None, fct_exit_command=None, do_check_all=True, confirm=False, confirm_exit=False, verbose_exec_command=False, fct_enter=None, fct_leave_forward=None, fct_leave_backward=None, set_color=False, police_bold=False, police_color=None, police_bgcolor=None, lock_name=None, lock_timeout=None):
        """
title : This is the menu title

sub_title : This is the menu title

fct_exit_command : Default None.
    When called programatically. This function interceptor is called before exiting a Menu.

do_check_all : Default True.
    For IMenu (Input Menu) only.
    Will invite the user to check all the Input field and run the validation sequence.

confirm : Default False.
    Does the command associated with this IMenu needs Acceptance before to run the Validation sequence.

command : Default None
    This command is called running the Validation sequence.
    All variables within the command string are replaced with the corresponding Input field value.
    e.g.: if command is : ls $field1 $field2
    And the values for these 2 IOptions are field1 = 'myfile1' and field = 'myfile2'. 
    The command turns to : ls myfile1 myfile2.

command_enter: Default None
    In conjunction with command. Is executed before to run command.
command_exit: Default None
    In conjunction with command. Is executed after command has run.

fct_command : Default None.
    When called programatically. This function interceptor is called at the Validation sequence.

    >>  Rules for command and fct_command :
        ...................................
    if fct_command only is given: this fonction is called at the Validation sequence.
    if command only is given: This system command is called on check_all (default:s) key.
    if fct_command and command are given: The fonction fct_command is called, with the command parameter at the Validation sequence.

confirm_exit : Default False.
    Does this Menu require an acceptance to Exit.

fct_enter : Default None.
    When called programatically. This function interceptor is called before entering a Menu.

fct_leave_forward : Default None.
    When called programatically. This function interceptor is called before leaving forward a Menu.

fct_leave_backward : Default None.
    When called programatically. This function interceptor is called before leaving backward a Menu.
"""
        selfMethod='__init__'
        self.allowedChilds=(IOption, Option, Menu, IMenu)

        if not isinstance(do_check_all, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'do_check_all', 'bool', str(do_check_all))
        if (command, fct_command) == (None, None) and do_check_all:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'At least one of command or fct_command is required ! Your values are command:' + str(command) + ', fct_command:' + str(fct_command) + ' !')

        if command!=None:
            if not do_check_all:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'IMenu:' + title + ', command is not allowed when do_check_all is False ! Received for: command:' + str(command) + ' !')
            if not isinstance(command, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command', 'str', str(command))
        else:
            # A051:
            if command_enter != None: raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'command_enter is not allowed when command is not provided !')
            if command_exit != None: raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'command_exit is not allowed when command is not provided !')

        if fct_command!=None and not do_check_all:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'IMenu:' + title + ', fct_command is not allowed when do_check_all is False ! Received for: fct_command:' + str(fct_command) + ' !')
        if fct_command!=None and not isinstance(fct_command, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_command. The type expected is: ether a function or a method ! Received:' + str(fct_command) + ' !')
        # A051:
        if command_enter!=None and not isinstance(command_enter, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command_enter', 'str', str(command_enter))
        if command_exit!=None and not isinstance(command_exit, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command_exit', 'str', str(command_exit))

        if not isinstance(confirm, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'confirm', 'bool', str(confirm))
        if confirm and not do_check_all:raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'IMenu:' + title + ', confirm is not allowed when do_check_all is False ! Received for: confirm:' + str(confirm) + ' !')
        if not isinstance(verbose_exec_command, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'verbose_exec_command', 'bool', str(verbose_exec_command))

        BaseMenu.__init__(self, title, sub_title=sub_title, roles_autz=roles_autz, except_roles=except_roles, contents=contents, help=help, lhelp=lhelp, fct_exit_command=fct_exit_command, confirm_exit=confirm_exit, fct_enter=fct_enter, fct_leave_forward=fct_leave_forward, fct_leave_backward=fct_leave_backward)
        VideoColors.__init__(self, set_color=set_color, police_bold=police_bold, police_color=police_color, police_bgcolor=police_bgcolor)
        CommandLock.__init__(self, name=lock_name, timeout=lock_timeout)
        
        
        self.__do_check_all=do_check_all
        self.__command=command
        # A051
        self.__command_enter=command_enter
        self.__command_exit=command_exit
        self.__fct_command=fct_command
        self.__doConfirm=confirm
        self.__verbose_exec_command=verbose_exec_command
        
    def doCheckAll(self):
        return self.__do_check_all
        
    def checkCommand(self):
        selfMethod='checkCommand'
        
        if self.getCommand()==None:raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'IMenu:' + self.getTitle() + ', this Menu do not support any command !')
        options=self.getChilds()
        command=self.getCommand() # System command
            
        for option in options:
            if command.find(option.getName())<0:raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'IMenu:' + self.getTitle() + '/IOption:' + option.getName() + ' This IOption has no equivalent field:' + '$' + option.getName() + ' in command:' + command + ' !')

    def getCommand(self):
        return self.__command

    # A051:
    def getCommandEnter(self):
        return self.__command_enter
    def getCommandExit(self):
        return self.__command_exit

    def getVerbose_exec_command(self):
        return self.__verbose_exec_command
    
    def getFct_command(self):
        return self.__fct_command
    
    def doConfirm(self):
        return self.__doConfirm

    def accept(self, p_visitor):

        if (p_visitor.childFirst):
            BaseMenu.accept(self, p_visitor, p_visitor.recursiveNode);
            if p_visitor.treatAncestor:
                p_visitor.visitBaseMenu(self)
                p_visitor.visitIMenu(self) 
            else:
                p_visitor.treatAncestor=True
        else:
            if p_visitor.treatAncestor:
                p_visitor.visitBaseMenu(self)
                p_visitor.visitIMenu(self)
            else:
                p_visitor.treatAncestor=True
            BaseMenu.accept(self, p_visitor, p_visitor.recursiveNode)



class BaseOption:
    
    def __init__(self, roles_autz=None, except_roles=None):
        selfMethod='__init__'
        if except_roles!=None and not isinstance(except_roles, list):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'except_roles', 'list', str(except_roles))

        self.aggregatParent=None
        self._isFirstMenu=False
        self.__config=None
        
        self.__roles_autz=checkRolesAutzSyntax(roles_autz, message='role_autz on tag: ' + str(self.getAggregatFiliation([])))
        if except_roles==None:except_roles=[]
        self.__except_roles=except_roles
        # A039:
        self.__session_dir = None # Will be setup on setConfig()
        
    def isFirstMenu(self):
        return self._isFirstMenu
        
    def accept(self, p_visitor):
        p_visitor.visitOption(self)

    def getAggregatParent(self):          
        if self.aggregatParent!=None:return self.aggregatParent()
        else:return None
       
    def setAggregatParent(self, p):
        selfMethod='setAggregatParent'
        if  __debug__ and not isinstance(p, (BaseOption, BaseMenu)):
            raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'p', (BaseOption, BaseMenu), str(p))
        import weakref
            
        self.aggregatParent=weakref.ref(p)

    def removeAggregatParent(self):
        self.aggregatParent=None

    def getAggregatFiliation(self, p_aggFiliation):
        selfMethod='getAggregatFiliation'
        if  __debug__ and not isinstance(p_aggFiliation, list):
            raise kastmenuxception.kastmenuParameterTypeException('p_aggFiliation', 'list', str(list))

        if  self.getAggregatParent()!=None and not self.getAggregatParent().isFirstMenu():
            p_aggFiliation.append(self.getAggregatParent())
            self.getAggregatParent().getAggregatFiliation(p_aggFiliation)                            
        
        return p_aggFiliation

    def getAggregatIndexFiliation(self):
        selfMethod='getAggregatIndexFiliation'
        l=[]
        self.getAggregatFiliation(l)
        l=[o.getIndex() for o in l]
        
        return '/'.join(l)

    def getTopParent(self):
        if not (self.isFirstMenu() or self.getAggregatParent()==None):
            return self.getAggregatParent().getTopParent()
        return self

    def getTop(self):
        return self.getTopParent()

    def setConfig(self, config):
        import weakref
        from os import mkdir
        self.__config=weakref.ref(config)

    def getSessionDir(self, config):  # A039:
        from os import mkdir
        if self.__session_dir != None: return self.__session_dir

        self.__session_dir = config.getTempDir() + '/' + tools.genUid()
        mkdir(self.__session_dir)
        return self.__session_dir

    def getConfig(self):
        if self.__config==None:
            import weakref
            self.__config=weakref.ref(self.getTop().getConfig())

        return self.__config()    
    
    def checkAutz(self, autz='display'):
        self_funct='checkAutz'
        rolesAutzDft=self.getConfig().getRolesAutzDft()
        roles=self.getConfig().getSharedRoles()
        passed=self.getAggregatParent().checkAutz(autz=autz)
        if not passed:return False

        rolesAutz=self.__roles_autz
        if rolesAutz==None:rolesAutz=rolesAutzDft
        passed=False
        
        if '+*optimistic' in rolesAutzDft['*anyone'].split(';'):optimistic=True
        else:optimistic=False

        for role in roles:
            if role not in rolesAutz:continue
            if role in self.__except_roles:continue
            autzs=rolesAutz[role].split(';')
            if '-' + autz in autzs:continue
            if '+all' in autzs or '+' + autz in autzs:
                passed=True
                break
            if optimistic:
                passed=True
                break

        return passed

    def checkCommandAutz(self, autz='execute'):
        self_funct='checkCommandAutz'
        rolesAutzDft=self.getConfig().getRolesAutzDft()
        roles=self.getConfig().getSharedRoles()
        passed=self.getAggregatParent().checkCommandAutz(autz=autz)
        if not passed:return False

        rolesAutz=self.__roles_autz
        if rolesAutz==None:rolesAutz=rolesAutzDft
        passed=False

        if '+*optimistic' in rolesAutzDft['*anyone'].split(';'):optimistic=True
        else:optimistic=False

        for role in roles:
            if role not in rolesAutz:continue
            if role in self.__except_roles:continue
            autzs=rolesAutz[role].split(';')
            if '-' + autz in autzs:continue
            if '+all' in autzs or '+' + autz in autzs:
                passed=True
                break
            if optimistic:
                passed=True
                break

        return passed



class Option(BaseOption, VideoColors, CommandLock):
    # A051: command_enter, command_exit
    def __init__(self, name, help=None, lhelp=None, roles_autz=None, except_roles=None, contents=None, command=None, command_enter=None, command_exit=None, fct_command=None, confirm=False, verbose_exec_command=False, set_color=False, police_bold=False, police_color=None, police_bgcolor=None, lock_name=None, lock_timeout=None):
        """
title : This is the Option title

help :  Default None
    Short Help string for this Menu Option.
    
contents : Long text information for this Menu Option.

command : Default None
    This command is called when this Option is chosen.

command_enter: Default None
    In conjunction with command. Is executed before to run command.
command_exit: Default None
    In conjunction with command. Is executed after command has run.

fct_command : Default None.
    When called programatically. When this Option is chosen, this function interceptor is called.

confirm : Default False
    Does this Option requires Acceptance before to execute.

verbose_exec_command : Default False.
    If True the called command is explicitally shown on the command output display.
"""
        selfMethod='__init__'
        if not isinstance(name, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'name', 'str', str(name))
        if help!=None and not isinstance(help, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'help', 'str', str(help))
        if contents!=None and not isinstance(contents, list):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'contents', 'list', str(contents))
        if (command, fct_command) == (None, None):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'At least one of command or fct_command is required ! Your values are command:' + str(command) + ', fct_command:' + str(fct_command) + ' !')

        if command!=None:
            if not isinstance(command, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command', 'str', str(command))
        else:
            # A051:
            if command_enter != None: raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'command_enter is not allowed when command is not provided !')
            if command_exit != None: raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'command_exit is not allowed when command is not provided !')

        if fct_command!=None and not isinstance(fct_command, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_command. The type expected is: ether a function or a method ! Received:' + str(fct_command) + ' !')
        # A051:
        if command_enter!=None and not isinstance(command_enter, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command_enter', 'str', str(command_enter))
        if command_exit!=None and not isinstance(command_exit, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command_exit', 'str', str(command_exit))

        if not isinstance(confirm, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'confirm', 'bool', str(confirm))
        if not isinstance(verbose_exec_command, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'verbose_exec_command', 'bool', str(verbose_exec_command))

        BaseOption.__init__(self, roles_autz=roles_autz, except_roles=except_roles)
        VideoColors.__init__(self, set_color=set_color, police_bold=police_bold, police_color=police_color, police_bgcolor=police_bgcolor)
        CommandLock.__init__(self, name=lock_name, timeout=lock_timeout)
        
        # - MultiLang support
        self.__help, self.__lhelp=MULTILANG.convert(help, lhelp)
        ## if help!=None:help = help.replace('\\\\', '\n')

        # M045: self.__name=name
        self.__name=name.replace('_', ' ').replace('.', ' ')
        self.__help=help

        # M035:
        # self.__contents=()
        # if contents!=None:self.__contents=tuple(contents.split('\n'))
        self.__contents=None
        if contents!=None:self.__contents=contents

        self.__command=command
        # A051
        self.__command_enter=command_enter
        self.__command_exit=command_exit
        self.__fct_command=fct_command
        self.__doConfirm=confirm
        self.__index=None
        self.__verbose_exec_command=verbose_exec_command

    def getName(self):
        return self.__name
    
    def getHelp(self):
        return self.__help

    def getLHelp(self):
        return self.__lhelp
    
    def getContents(self):
        return self.__contents

    # A035:
    def getContentsAsList(self):
        if isinstance(self.__contents, (tuple, list)):return list(self.__contents)
        elif self.__contents!=None: return  str(self.__contents).split('\n')
        return []
    
    def getCommand(self):
        return self.__command
    # A051:
    def getCommandEnter(self):
        return self.__command_enter
    def getCommandExit(self):
        return self.__command_exit

    def getFct_command(self):
        return self.__fct_command
        
    def getVerbose_exec_command(self):
        return self.__verbose_exec_command
    
    def doConfirm(self):
        return self.__doConfirm

    def getLinesCount(self):
        # M035:
        return len(self.getContentsAsList())
    
    def getIndex(self):
        return self.__index    
    
    def _setIndex(self, index):
        self.__index=index

    def accept(self, p_visitor):
        p_visitor.visitBaseOption(self)
        p_visitor.visitOption(self)


class IOption(BaseOption, VideoColors):
    def __init__(self, name, roles_autz=None, except_roles=None, help=None, lhelp=None, value=None, wkvalue=None, contents=None, wkcontents=None, lock_input=False, command=None, fct_command=None, list_separator_car=';', set_color=False, police_bold=False, police_color=None, police_bgcolor=None):
        """
name : This is the Field Name

help : A short Help for this IMenu IOption.

lhelp : A short Help for this IMenu IOption.

value : Default None
    A default value for this IMenu IOption.

wkvalue : A default value for this IMenu IOption.

contents : Long text information for this IMenu IOption.

wkcontents : a wk expression to check the user Input value.
    This wk expression will be run on the Validation sequence of the parent IMenu.
    For more informatiojn about wk expression see the wk project at sourceforge.net
    or the wk book into the <APIMENU_INSTALL_DIR>/doc diretory.
    
lock_input : Default False
    If True this IOption wont be allowed for Input.

command : Default None
    This command is called when this Option is chosen.

fct_command : Default None.
    When called programatically. When this Option is chosen, this function interceptor is called.

list_separator_car : When the Input value can be a list, this is the line break separator character.
"""

        selfMethod='__init__'
        from . import wk
        if not isinstance(name, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'name', 'str', str(name))
        if help!=None and not isinstance(help, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'help', 'str', str(help))
        if lhelp!=None and not isinstance(lhelp, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'lhelp', 'str', str(lhelp))
        if (wkvalue, wkcontents)==(None, None) or (wkvalue!=None and wkcontents!=None):raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'IOption:' + name + ', Only one of either Attribute: "wk" or text is required for an IOption ! Recceived for wkvalue:' + str(wkvalue) + ', received for text content:' + str(wkcontents) + ' !')
        if wkvalue!=None and not wk.isWKDefinition(wkvalue, class_exit=self.__class__, method_exit=selfMethod):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'wkvalue', 'wkDefinition', str(wkvalue))
        if wkcontents!=None and not wk.isWKDefinition(wkcontents, class_exit=self.__class__, method_exit=selfMethod):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'wkcontents', 'wkDefinition', str(wkcontents))
        if contents!=None and not isinstance(contents, list):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'contents', 'list', str(contents))
        if not isinstance(lock_input, bool):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'lock_input', 'bool', str(lock_input))

        if command!=None and not isinstance(command, str):raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'command', 'str', str(command))

        if fct_command!=None and not isinstance(fct_command, (types.FunctionType, types.MethodType)):raise kastmenuxception.apimenuParameterException(self.__class__.__name__, selfMethod, 'Uncorrect type received for: fct_command. The type expected is: ether a function or a method ! Received:' + str(fct_command) + ' !')

        if list_separator_car==None or not isinstance(list_separator_car, str) or len(list_separator_car)!=1:raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'list_separator_car', 'str/len 1', str(list_separator_car))

        BaseOption.__init__(self, roles_autz=roles_autz, except_roles=except_roles)
        VideoColors.__init__(self, set_color=set_color, police_bold=police_bold, police_color=police_color, police_bgcolor=police_bgcolor)
        
        # - MultiLang support
        MULTILANG.convertWk(wkvalue)
        MULTILANG.convertWk(wkcontents)

        # A045: self.__name=name
        name=name.replace('_', ' ').replace('.', ' ')

        self.__name=self.__label=name
        self.__wkvalues=wkvalue
        self.__wkcontents=wkcontents
        if self.__wkcontents==None:
            self.__isValue=True
            self.__wkvalues['*withCoolTyping']=True
        else:
            self.__isValue=False
            # D040: if not ('*type' in self.__wkcontents and self.__wkcontents['*type'] in ('list', 'tuple')):raise apimenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'IOption:' + name + ', a txt wkDefinition must support the key *type:list or *type:tuple ! Your value:' + str(self.__wkcontents) + ' !')
            self.__wkcontents['*withCoolTyping']=True
        
        descs=self.getIODescs()
        
        # -- help
        if help==None and '*help' in descs:help=descs['*help']
        if lhelp==None and '*lhelp' in descs:lhelp=descs['*lhelp']        
        # - MultiLang support
        self.__help, self.__lhelp=MULTILANG.convert(help, lhelp)
        # Removed:
        ## if self.__help!=None:self.__help = self.__help.replace('\\\\', '\n')
        ## if self.__lhelp!=None:self.__lhelp = self.__lhelp.replace('\\\\', '\n')

        # -- label
        if '*label' in descs:self.__label=descs['*label']

        self.__lock_input=lock_input
        self.__fct_command=fct_command
        self.__command=command
        self.__list_separator_car=list_separator_car
        self.__index=None
        
        # init
        if self.__isValue:
            if '*value' in self.__wkvalues:self.__value=self.__value_dft=self.__wkvalues['*value']
            else:self.__value=self.__value_dft=None
            if value!=None:self.__value=value

            # self.__contents=[]
            self.__contents=None
        else:
            # M035:
            # if '*value' in self.__wkcontents:self.__contents=self.__contents_dft=self.__wkcontents['*value'].split('\n')
            if '*value' in self.__wkcontents:self.__contents=self.__contents_dft=self.__wkcontents['*value']
            else:self.__contents=self.__contents_dft=None # else:self.__contents=self.__contents_dft=[]
            if contents!=None:self.__contents=contents
            self.__value=None
    
    def getName(self):
        return self.__name    
    
    def getLabel(self):
        if self.__label!=None:return self.__label
        return self.__name
    
    def getHelp(self):
        return self.__help    
    
    def getLHelp(self):
        return self.__lhelp
    
    def getValue(self):
        return self.__value

    def getContents(self):
        return self.__contents

    # A035:
    def getContentsAsList(self):
        if isinstance(self.__contents, (tuple, list)):return list(self.__contents)
        elif self.__contents!=None: return  str(self.__contents).split('\n')
        return []
    
    def getList_separator_car(self):
        return self.__list_separator_car
    
    def isValue(self):
        return self.__isValue
    
    def getIODescs(self):
        if self.isValue():return self.__wkvalues
        return self.__wkcontents
    
    def getIOValue(self):
        if self.isValue():
            return self.__value
        else:return self.__contents    
        
    def getIODftValue(self):
        if self.isValue():
            return self.__value_dft
        else:return self.__contents_dft

    def setIOValue(self, value, error_prefix=None, verbose=0, fct_output=None):
        
        if self.isValue():
            isok, value=self.checkIOValue(value, error_prefix=error_prefix, verbose=verbose, fct_output=fct_output)
            if not isok:return False
            self.__value=value
            
        else:
            isok, value=self.checkIOValue(value, error_prefix=error_prefix, verbose=verbose, fct_output=fct_output)
            if not isok:return False
            # M035: if value==None:value=[]
            self.__contents=value   
            
        return True
            
    def checkIOValue(self, value, error_prefix=None, verbose=0, fct_output=None):
        selfMethod='checkIOValue'
        if error_prefix==None:error_prefix=''
        from . import wk
        
        p=wk.WantedKeywords()            
        setattr(p, 'value', self.getIODescs())
        
        try:
            wk.getKeywords(wantedKeywords=p, keywords={'value':value}, class_exit=self.__class__.__name__, method_exit=selfMethod)
        except Exception as e:
            if e.hasSubException():message=e.getSubException().getMessage()
            else:message=str(e)
            
            if fct_output!=None:doGet=True
            else:doGet=False
            warn=kastmenuxception.kastmenuInformation(self.__class__.__name__, selfMethod, error_prefix + ' ' + message).warn(verbose=verbose, doGet=doGet)
            if fct_output!=None:fct_output.write(warn)
            
            return False, None
        
        return True, p.value

    def isLocked(self):
        return self.__lock_input

    def getCommand(self):
        return self.__command

    def getFct_command(self):
        return self.__fct_command
        
    def getLinesCount(self):
        # M035:
        return len(self.getContentsAsList())
    
    def getIndex(self):
        return self.__index    
    
    def _setIndex(self, index):
        self.__index=index

    def accept(self, p_visitor):
        p_visitor.visitBaseOption(self)
        p_visitor.visitIOption(self)



def default_fct_menu(config, menu):

    # - Finish to setup the Menu content
    menu_node=config.config_node.getTopParent().getQuickTunNode(menu.tun)
    
    if isinstance(menu, Menu):feedMenuChild(menu, menu_node)
    else:feedIMenuChild(menu, menu_node)

def feedMenuChild(menu, menu_node): ## Menu
    selfMethod='feedMenuChild'
    if menu.isFed():return False
    
    # - Childs
    child_nodes=menu_node.getNodes()
    
    for child_node in child_nodes:
        child_attrs=child_node.getAttrs()
        
        ## Child is a Menu
        if child_node.getTag()=='menu':
            child=Menu(child_attrs.title, roles_autz=child_attrs.roles_autz, except_roles=child_attrs.except_roles, help=child_attrs.help, lhelp=child_attrs.lhelp, confirm_exit=child_attrs.confirm_exit, set_color=child_attrs.set_color, police_bold=child_attrs.police_bold, police_color=child_attrs.police_color, police_bgcolor=child_attrs.police_bgcolor)

        ## Child is an IMenu
        elif child_node.getTag()=='imenu':
            # A041:
            command = child_attrs.command if child_attrs.command != None else child_node.getText()
            if command == None:
                raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Menu:' + menu.getTitle() + ', IMenu:' + child_node.getTag() + ' a command should be provided either as an attribute named: command or as tag text !')
            # A051: + command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit:
            child=IMenu(child_attrs.title, roles_autz=child_attrs.roles_autz, except_roles=child_attrs.except_roles, help=child_attrs.help, lhelp=child_attrs.lhelp, command=command, command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit, confirm=child_attrs.confirm, confirm_exit=child_attrs.confirm_exit, verbose_exec_command=child_attrs.verbose_exec_command, set_color=child_attrs.set_color, police_bold=child_attrs.police_bold, police_color=child_attrs.police_color, police_bgcolor=child_attrs.police_bgcolor, lock_name=child_attrs.lock_name, lock_timeout=child_attrs.lock_timeout)
            
        ## Child is an Option
        elif child_node.getTag()=='option':
            # A041:
            command = child_attrs.command if child_attrs.command != None else child_node.getText()
            if command == None:
                raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Menu:' + menu.getTitle() + ', Option:' + child_node.getTag() + ' a command should be provided either as an attribute named: command or as tag text !')
            # M035:
            if child_attrs.command!=None and child_node.hasText():contents = child_node.getText()
            else:contents=None
            # A051: + command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit:
            child=Option(child_attrs.name, roles_autz=child_attrs.roles_autz, except_roles=child_attrs.except_roles, help=child_attrs.help, lhelp=child_attrs.lhelp, command=command, command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit, confirm=child_attrs.confirm, contents=contents, verbose_exec_command=child_attrs.verbose_exec_command, set_color=child_attrs.set_color, police_bold=child_attrs.police_bold, police_color=child_attrs.police_color, police_bgcolor=child_attrs.police_bgcolor, lock_name=child_attrs.lock_name, lock_timeout=child_attrs.lock_timeout)
        
        else:raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Menu:' + menu.getTitle() + ', not managed Tag:' + child_node.getTag() + ' !')
            
        # - Keeps track of the epixml Node Tag uniq id
        child.tun=child_node.getTun()
        
        menu.add(child)
        
    return True

def feedIMenuChild(menu, menu_node): ## IMenu
    selfMethod='feedMenuChild'    
    if menu.isFed():return False
    
    # - Childs
    child_nodes=menu_node.getNodes()
    
    for child_node in child_nodes:
        child_attrs=child_node.getAttrs()

        ## Child is an IOption
        if child_node.getTag()=='ioption':
            # M035:
            if child_node.hasText():contents = child_node.getText()
            else:contents=None

            # M035:
            # if contents!=None:
            #    if len(contents)>1:raise apimenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'IMenu:' + menu_node.getFiliation() + '@name=' + menu.getTitle() + '/ioption@name=' + child_node.name + ', Only one line of text (a wkDefinition) is allowed for an ioption tag. Found:' + str(len(contents)) + ' lines !)')
            #    else:contents=contents[0]
            child=IOption(child_attrs.name, roles_autz=child_attrs.roles_autz, except_roles=child_attrs.except_roles, help=child_attrs.help, lhelp=child_attrs.lhelp, value=child_attrs.value, wkvalue=child_attrs.wk, wkcontents=contents, lock_input=child_attrs.lock_input, list_separator_car=child_attrs.list_separator_car, set_color=child_attrs.set_color, police_bold=child_attrs.police_bold, police_color=child_attrs.police_color, police_bgcolor=child_attrs.police_bgcolor)
        
        ## Child is a Menu
        elif child_node.getTag()=='menu':
            child=Menu(child_attrs.title, roles_autz=child_attrs.roles_autz, except_roles=child_attrs.except_roles, help=child_attrs.help, lhelp=child_attrs.lhelp, set_color=child_attrs.set_color, police_bold=child_attrs.police_bold, police_color=child_attrs.police_color, police_bgcolor=child_attrs.police_bgcolor)

        ## Child is an IMenu
        elif child_node.getTag()=='imenu':
            # A041:
            command=child_attrs.command if child_attrs.command!=None else child_node.getText()
            if command == None:
                raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Menu:' + menu.getTitle() + ', IMenu Tag:' + child_node.getTag() + ' a command should be provided either as an attribute named: command or as tag text !')
            # A051: + command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit:
            child=IMenu(child_attrs.title, roles_autz=child_attrs.roles_autz, except_roles=child_attrs.except_roles, help=child_attrs.help, lhelp=child_attrs.lhelp, command=command, command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit, confirm=child_attrs.confirm, verbose_exec_command=child_attrs.verbose_exec_command, set_color=child_attrs.set_color, police_bold=child_attrs.police_bold, police_color=child_attrs.police_color, police_bgcolor=child_attrs.police_bgcolor, lock_name=child_attrs.lock_name, lock_timeout=child_attrs.lock_timeout)
            
        ## Child is an Option
        elif child_node.getTag()=='option':
            # A041:
            command = child_attrs.command if child_attrs.command != None else child_node.getText()
            if command == None:
                raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Menu:' + menu.getTitle() + ', Option:' + child_node.getTag() + ' a command should be provided either as an attribute named: command or as tag text !')
            # M035:
            if child_attrs.command!=None and child_node.hasText():contents = child_node.getText()
            else:contents=None
            # A051: + command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit:
            child=Option(child_attrs.name, roles_autz=child_attrs.roles_autz, except_roles=child_attrs.except_roles, help=child_attrs.help, lhelp=child_attrs.lhelp, command=command, command_enter=child_attrs.command_enter, command_exit=child_attrs.command_exit, confirm=child_attrs.confirm, contents=contents, verbose_exec_command=child_attrs.verbose_exec_command, set_color=child_attrs.set_color, police_bold=child_attrs.police_bold, police_color=child_attrs.police_color, police_bgcolor=child_attrs.police_bgcolor, lock_name=child_attrs.lock_name, lock_timeout=child_attrs.lock_timeout)
        
        else:raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Menu:' + menu.getTitle() + ', not managed Tag:' + child_node.getTag() + ' !')
            
        # - Keeps track of the epixml Node Tag uniq id
        child.tun=child_node.getTun()
        
        menu.add(child)
        
    return True

def __run(menu_file, record=False, go_menu=None, go=None, batch=None, pause=None, noclear=False, kdealer=True, port=None, secid=None, is_listening=False, showResultingSourceOnly=False, temp_dir=None, keep_temp_dir=False, tmpl_kws={}, log=False, log_output=False, log_dir=None, log_rotate=None, call_cde=None, aliases=None, debug=False, show_shortcut=False, verbose=0):
    selfMethod='__run'
    from . import epicxmlp
    from os import path, chdir
    global CONFIG

    # First change current dir to menu file's dir:
    menu_dir = path.split(menu_file)[0]
    if path.isdir(menu_dir):
        chdir(menu_dir)

    config_node=epicxmlp.digest(file_source=menu_file, file_desc=APIMENU_HOME + '/conf/descs/menu.desc.xml', showResultingSourceOnly=showResultingSourceOnly, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir, tmpl_kws=tmpl_kws, aliases=aliases, verbose=verbose)
    if showResultingSourceOnly:
        print(config_node)
        import sys
        sys.exit()
    
    ## Roles Mapping
    """ sample entry:
    roles_mapping={
        'role_namea': {
                'uers': ['myusera1', 'myusera2'],                            
                'groups': ['mygroupa1', 'mygroupa2']
            },
        'role_nameb': {
                'uers': ['myuserb1', 'myuserb2'],                            
                'groups': ['mygroupb1', 'mygroupb2']
            }
        }
    """
    roles_mappings=None
    if config_node.hasNode('roles_mapping'):
        roles_mappings={}
        role_nodes=config_node.getNode('roles_mapping')[0].getNode('role')
        for role_node in role_nodes:
            rname=role_node.getAttr('name')
            roles_mappings[rname]={}
            roles_mappings[rname]['users']=[]
            roles_mappings[rname]['groups']=[]
            mapping_node=role_node.getNode('mapping')[0]
            
            if mapping_node.hasNode('users'):
                users=mapping_node.getNode('users')[0].getText()
                roles_mappings[rname]['users'].extend(users)
            if mapping_node.hasNode('groups'):
                groups=mapping_node.getNode('groups')[0].getText()
                roles_mappings[rname]['groups'].extend(groups)
    
        
    # - Config
    config_attrs=config_node.getAttrs()

    CONFIG=Config(default_fct_menu, title=config_attrs.title, temp_dir=config_attrs.temp_dir, show_host=config_attrs.show_host,
    up_car=config_attrs.up_car, up_message=config_attrs.up_message, down_car=config_attrs.down_car, down_message=config_attrs.down_message, 
    exit_car=config_attrs.exit_car, exit_message=config_attrs.exit_message, choice_message=config_attrs.choice_message, 
    check_all_car=config_attrs.check_all_car, check_all_message=config_attrs.check_all_message, confirm_message=config_attrs.confirm_message, 
    confirm_exit_message=config_attrs.confirm_exit_message, screen_max_lines=config_attrs.screen_max_lines, 
    wait_message=config_attrs.wait_message, option_upper=config_attrs.option_upper, option_check_message1=config_attrs.option_check_message1, 
    option_check_message2=config_attrs.option_check_message2, input_field_message1=config_attrs.input_field_message1, 
    input_field_message2=config_attrs.input_field_message2, input_field_default_message=config_attrs.input_field_default_message, 
    input_field_checkin_message=config_attrs.input_field_checkin_message, command_label=config_attrs.command_label, 
    indent=config_attrs.indent, option_help_indent=config_attrs.option_help_indent, option_value_indent=config_attrs.option_value_indent, 
    skip_line=config_attrs.skip_line, dont_use_unix_color=config_attrs.dont_use_unix_color, lang_dir=config_attrs.lang_dir,
    record=record, go_menu=go_menu, go=go, batch=batch, pause=pause, noclear=noclear, kdealer=kdealer, port=port, secid=secid, is_listening=is_listening, roles_autz_dft=config_attrs.roles_autz_dft, roles_mappings=roles_mappings, log=log, log_output=log_output, log_dir=log_dir, log_rotate=log_rotate, call_cde=call_cde, debug=debug, show_shortcut=show_shortcut, verbose=verbose)
    CONFIG.config_node=config_node

    # - Top Menu
    if not config_node.hasNode('menu') and not config_node.hasNode('imenu'):raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'At least one Node with Tag:menu or imenu is required !')
    
    # - Check menu/imenu
    if config_node.hasNode('menu') and config_node.hasNode('imenu'):raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Only One node of either "menu" or "imenu" is allowed at root level !')

    ## Node is a Menu
    if config_node.hasNode('menu'):
        menu_node=config_node.getNode('menu')[0]
        menu_attrs=menu_node.getAttrs()    
        menu=Menu(menu_attrs.title, roles_autz=menu_attrs.roles_autz, except_roles=menu_attrs.except_roles, help=menu_attrs.help, lhelp=menu_attrs.lhelp, confirm_exit=menu_attrs.confirm_exit, set_color=menu_attrs.set_color, police_bold=menu_attrs.police_bold, police_color=menu_attrs.police_color, police_bgcolor=menu_attrs.police_bgcolor)
         # Interception of xml menus.
        menu.setConfig(CONFIG)
        menu.tun=menu_node.getTun()
        feedMenuChild(menu, menu_node)
        
        
    ## Node is an IMenu
    elif config_node.hasNode('imenu'):
        menu_node=config_node.getNode('imenu')[0]
        menu_attrs=menu_node.getAttrs()
        # A041:
        command = menu_attrs.command if menu_attrs.command != None else menu_node.getText()
        if command == None:
            raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'IMenu:' + menu_node.getTitle() + ', IMenu:' + menu_node.getTag() + ' a command should be provided either as an attribute named: command or as tag text !')

        # A051: + command_enter=menu_attrs.command_enter, command_exit=menu_attrs.command_exit
        menu=IMenu(menu_attrs.title, roles_autz=menu_attrs.roles_autz, except_roles=menu_attrs.except_roles, help=menu_attrs.help, lhelp=menu_attrs.lhelp, command=command, command_enter=menu_attrs.command_enter, command_exit=menu_attrs.command_exit, confirm=menu_attrs.confirm, confirm_exit=menu_attrs.confirm_exit, verbose_exec_command=menu_attrs.verbose_exec_command, set_color=menu_attrs.set_color, police_bold=menu_attrs.police_bold, police_color=menu_attrs.police_color, police_bgcolor=menu_attrs.police_bgcolor, lock_name=menu_attrs.lock_name, lock_timeout=menu_attrs.lock_timeout)
        menu.setConfig(CONFIG)
        menu.tun=menu_node.getTun()
        feedIMenuChild(menu, menu_node)
        # menu.checkCommand()
        
    else:raise kastmenuxception.kastmenuXmlSyntaxException('Main', selfMethod, 'Not managed Tag:' + config_node.getTag() + ' !')
    
    # - run
    return CONFIG.go(menu)

def digest(menu_file, record=False, go_menu=None, go=None, batch=None, pause=None, noclear=False, kdealer=True, port=None, secid=None, is_listening=False, showResultingSourceOnly=False, temp_dir=None, keep_temp_dir=False, tmpl_kws={}, log=False, log_output=False, log_dir=None, log_rotate=10, call_cde=None, aliases=None, debug=False, show_shortcut=False, verbose=0):
    return __run(menu_file, record=record, go_menu=go_menu, go=go, batch=batch, pause=pause, noclear=noclear, kdealer=True, port=port, secid=secid, is_listening=is_listening, showResultingSourceOnly=showResultingSourceOnly, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir, tmpl_kws=tmpl_kws, log=log, log_output=log_output, log_dir=log_dir, log_rotate=log_rotate, call_cde=call_cde, aliases=aliases, debug=debug, show_shortcut=show_shortcut, verbose=verbose)

def launchProcessKdealer(secid_md5=None, secid=None, port=None, queue_max=QUEUE_MAX, verbose=0):
    from time import sleep
    from os import path
    from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
    from kwadlib.security.crypting import setSecidToFile
    setSecidToFile(secid_md5, secid, port, temp_dir=default.getKastTempDir())

    print('launching kdealer Qmq, on port:' + str(port) + ' ...')
    
    bin=path.normpath(path.realpath(APIMENU_HOME + '/bin/kdealer.py'))
    
    parms=[  'python3', bin, '--secid', secid_md5, '--queue_max', str(queue_max), '--verbose', str(verbose)]
    process = Popen(parms, startupinfo=None)

    sleep(2) # sleep while kdealer is launching

    return process

""" Former tests:
Sample test:
/opt/kastmenu/current/bin/apimenu   /opt/kastmenu/current/samples/apimenu/menu2_follow.xml -b 'name=optiona1..title=menub.title=menuc.title=MyIMenu1.name=field2.3333;555.s.y...name=optionc5.' -s 'abcd' -p 1234   -P 2 -r


/opt/kastmenu/current/bin/apimenu  ../samples/apimenu/menu2.xml 


/opt/kastmenu/current/bin/apimenu   /opt/kastmenu/current/samples/apimenu/menu2_follow.xml -b '' -s 'abcd' -p 1234   -P 2 -r

Menu Path:3.2.y..3..7.4.3.sss..3.b...8./Names:name=imbmenu.name=optiona2.y..name=optiona3..title=menud.title=MyIMenu2.name=field3.sss..name=field3.b...name=optiona5.

ok: sur menu2.xml
 /opt/kastmenu/current/bin# ./apimenu  ../samples/apimenu/menu2_follow.xml -b '3.2.y..3..7.4.3.sss..3.b...8.'   -p 1234  -s abcd

?: sur menu2_follow.xml
 /opt/kastmenu/current/bin# ./apimenu  ../samples/apimenu/menu2_follow.xml  -p 1234 -s abcd  -b '3.3.3.3..3.'

               Menu Path:2.y..3.5.4..3.7.4.2.aaaaaaaa;bbbbbbbb..5./Names:name=optiona2.y..name=imbmenu.title=menub.name=optionb5..name=imbmenu.title=menud.title=MyIMenu2.name=field2.aaaaaaaa;bbbbbbbb..name=optiond1.




ok:
2.y..3.7.5...3.7.4.2.aaaa;bbbb...8..9..3.8..7.4.4..4.zzz..4.22...3.8..7.6..4.3.b.......7.4.6.zzz..6.3;2;1.2.a;b;c;d;e;f;.3.dd..3c..3.c../Names:name=optiona2.y..name=imbmenu.title=menud.name=optiond1...name=imbmenu.title=menud.title=MyIMenu2.name=field2.aaaa;bbbb...name=optiona5..name=optiona6..name=imbmenu.name=optiona5..title=menud.title=MyIMenu2.name=field4..name=field4.zzz..name=field4.22...name=imbmenu.name=optiona5..title=menud.name=optiond2..title=MyIMenu2.name=field3.b.......title=menud.title=MyIMenu2.name=field6.zzz..name=field6.3;2;1.name=field2.a;b;c;d;e;f;.name=field3.dd..3c..name=field3.c..
ok indexes:
2.y..3.7.5...3.7.4.2.aaaa;bbbb...8..9..3.8..7.4.4..4.zzz..4.22...3.8..7.6..4.3.b.......7.4.6.zzz..6.3;2;1.2.a;b;c;d;e;f;.3.dd..3c..3.c..
ok names:
name=optiona2.y..name=imbmenu.title=menud.name=optiond1...name=imbmenu.title=menud.title=MyIMenu2.name=field2.aaaa;bbbb...name=optiona5..name=optiona6..name=imbmenu.name=optiona5..title=menud.title=MyIMenu2.name=field4..name=field4.zzz..name=field4.22...name=imbmenu.name=optiona5..title=menud.name=optiond2..title=MyIMenu2.name=field3.b.......title=menud.title=MyIMenu2.name=field6.zzz..name=field6.3;2;1.name=field2.a;b;c;d;e;f;.name=field3.dd..3c..name=field3.c..

IPython avec Indexes ==> 2.y..3.7.5...3.7.4.2.aaaa;bbbb...8..9..3.8..7.4.4..4.zzz..4.22...3.8..7.6..4.3.b.......7.4.6.zzz..6.3;2;1.2.a;b;c;d;e;f;.3.dd..3c..3.c.
name=optiona2.y..name=imbmenu.title=menud.name=optiond1...name=imbmenu.title=menud.title=MyIMenu2.name=field2.aaaa;bbbb...name=optiona5..name=optiona6..name=imbmenu.name=optiona5..title=menud.title=MyIMenu2.name=field4..name=field4.zzz..name=field4.22...name=imbmenu.name=optiona5..title=menud.name=optiond2..title=MyIMenu2.name=field3.b.......title=menud.title=MyIMenu2.name=field6.zzz..name=field6.3;2;1.name=field2.a;b;c;d;e;f;.name=field3.dd..3c..name=optiond3.c.
Le dernier: ..3c..name=optiond3.c.
n'est pas correct:
                3c..name=field3.c..
IPython avec Names   ==> 2.y..3.7.1...3.7.4.2.aaaa;bbbb...8..9..3.8..7.4.4..4.zzz..4.22...3.8..7.2..4.3.b.......7.4.6.zzz..6.3;2;1.2.a;b;c;d;e;f;.3.dd..3c..name=field3.c.



ko:
2.y..3.7.5...3.7.4.2.aaaa;bbbb...8..9..3.8..7.4.4..4.zzz..4.22...3.8..7.6..4.3.b.......7.4.6.zzz..6.3;2;1.2.a;b;c;d;e;f;.3.dd..3c..3.c../Names:

name=optiona2.y..name=imbmenu.title=menud.name=optiond1...name=imbmenu.title=menud.title=MyIMenu2.name=field2.aaaa;bbbb...name=optiona5..name=optiona6..name=imbmenu.name=optiona5..title=menud.title=MyIMenu2.name=field4..name=field4.zzz..name=field4.22...name=imbmenu.name=optiona5..title=menud.name=optiond2..title=MyIMenu2.name=field3.b.......title=menud.title=MyIMenu2.name=field6.zzz..name=field6.3;2;1.name=field2.a;b;c;d;e;f;.name=field3.dd..3c..name=field3.c..
name=optiona2.y..name=optiona3.7.title=menub...3.title=menud.title=MyIMenu2.name=field2.aaaa;bbbb...name=optiona5..name=optiona6..name=optiona3.8..7.name=optiona4.4..4.zzz..4.22..

"""