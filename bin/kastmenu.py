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



#           005    | P.G.P. | 2012/09/01    | Support Menu Listener and batch
#           006    | P.G.P. | 2012/09/01    | Output logs

SELF_MODULE='apimenu'
APMENU_TEMP_DIR = None

# A006
##class Logger(object):
##    def __init__(self, filename="/tmp/menu.log"):
##        import sys
##        self.terminal = sys.stdout
##        self.log = open(filename, "a")
##
##    def write(self, message):
##        self.terminal.write(message)
##        self.log.write(message)



##########
## Main ##
##########

from signal import signal, SIGINT, SIGHUP
def signal_handler(signal_received, frame):
    from kwadlib import kastmenup
    if kastmenup.CONFIG != None: kastmenup.CONFIG.stop()

def usage():
    return """
Syntax: km mymenu.xml
e.g.: 
With log level:
    km mymenu.xml -v 30          
With debug:
    km mymenu.xml -v 30 --debug
With noclear: do not clear the previous screen:
    km mymenu.xml -v 30 --noclear
Whith BigBrother logging:
    km mymenu.xml -l -L /tmp -O
-l: enable logging
-L /tmp: where to log
-O: allows command outputs logging.         
See km -h for other options.

KastMenu is a tools to allow access transparently to Terminal 
Tree Menus from:
- The Terminal Console
- The Web, with a very oriented Mobile Phone interface.
          
Whatever the interface is:
- A terminal Menu runs under the user for whom it is called for.

1) Menu Tree:
KastMenu is a Menu Tree of the following components:
Menu, Option and
IMenu, IOption.
          
- All final actions target a shell command.
- The output sticks to what comes out from the command stdout.
This means there is no attempt of transformation of the output 
by KastMenu, and everything supported by the O.S. shell is 
accessable and runnable by KastMenu.

2) KastMenu File:
A KastMenu file is a simple file describing the menu.
See syntax above (mymenu.xml).
This file is described by the [kastmenu_home]/conf/descs/menu.desc.xml decriptor.
And this file could be either:
mymenu.yaml
mymenu.hcl or
mymenu.xml
          
If this file is called:
mymenu.[type].mako or mymenu.[type].jinja
It will be parsed using respectively either the mako or jinja parser.
e.g.: mymenu.xml.jinja, mymenu.yaml.mako, mymenu.hcl.jinja
One can use --tmpl_kws option to provide CooltTyped dict of variables
to jinja or mako.
e.g.: {name:sebastian,address:2 open street}.

3) KastMenu API:
KastMenu API provides an API to dynamically create full featured Menus 
on the flow.

4) Indefinitly Pipable:
KastMenu programs can call each others with the --follow_menu
option that allows the same continuous quality of service 
accross the chain of menu.
          
5) Big brother log:
KastMenu provides a WYSIWYG logging system that keep track of every 
action taken on the Menu by a user and (if required) of every outputs.
This log will also trace the mpath.
e.g.: km mymenu.xml -l -L /tmp -O
See syntax.
          
6) Menu Automation:
A mpath is a sequential path of every input played on a menu.
Calling back KastMenu with a menupath will replay the menu and
pause on each screen  (here 2 second).
e.g.: km mymenu.xml -g [mpath] -p 2

7) KastMenu usage:
KastMenu is ideal for supervision, monitoring and production control,
for restricted users access control,
for administration management and automation purposes,
and for training and education.          
          
8) From anywhere to anywhere:
Combined with DKwad:
- KastMenu allows access from any mobile phone to any menu, under any user
on any remote machine, or  VM.
With access control.

- Allows access to the full featured DKwad SoftClass scheme.
DKwad allows to run Software management actions from anywhere
to anywhere.
A DKwad action is a SoftClasse's module with operation on it
(create, update, delete or anything)
          
9) Colors:
KastMenu supports colors: black, red, green, yellow, blue, purple, cyan, white. 
"""


""" e.g.:
import sys
import apimenu
sys.path.append('/opt/kastmenu/current/core')
from kwadlib import kastmenup
w=kastmenup.digest('/opt/kastmenu/current/samples/apimenu/menu.xml', record=False, batch=None, pause=None, noclear=False, port=1234, secid=None, showResultingSourceOnly=False, temp_dir=None, tmpl_kws={})
"""

def call_kastmenup(menu_file, record=False, go_menu=None, go=None, batch=None, pause=None, noclear=False, kdealer=True, port=None, secid=None, showResultingSourceOnly=False, temp_dir=None, keep_temp_dir=False, tmpl_kws={}, aliases=None, log=False, log_output=None, log_dir=None, log_rotate=None, call_cde=None, debug=False):
    from kwadlib import kastmenup
    kastmenup.digest(menu_file, record=record, go_menu=go_menu, go=go, batch=batch, pause=pause, noclear=noclear, kdealer=kdealer, port=port, secid=secid, showResultingSourceOnly=showResultingSourceOnly, temp_dir=temp_dir, keep_temp_dir=keep_temp_dir, tmpl_kws=tmpl_kws, aliases=aliases, log=log, log_output=log_output, log_dir=log_dir, log_rotate=log_rotate, call_cde=call_cde, debug=debug, verbose=VERBOSE) # Digest do the run

def main(args):
    self_funct='main'
    import optparse
    from os import path, makedirs
    global APMENU_TEMP_DIR
    from kwadlib import tools, kastmenuxception
    global VERBOSE
    VERBOSE=None
    import sys

    parser = optparse.OptionParser(usage())
    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option("--debug", dest="debug", action="store_true", default=False, help="Raises and Fails at first issue.")
    parser.add_option("-r", "--record", dest="record", action="store_true", default=False, help="Will record all entries to a string ready to use for remote execution mode.")
    parser.add_option("--show", dest="show", action="store_true", default=False, help="Apimenu (now supports Mako www.makotemplates.org and palletsprojects.com/p/jinja) will do nothing but show the resulting xml file after mako|jinja2 parsing if your menu file ends with .mako or .jinja (e.g. menu.xml.mako instead of menu.xml).")
    parser.add_option("--tmpl_kws", dest="tmpl_kws", help="(optional) A set of parameters (a CoolTyped dict) to feed mako or jinja with, when the file argument rather than beeing an .xml file is a .xml.mako file or a  .xml.jinja file.")
    parser.add_option("--temp_dir", dest="temp_dir", help="Temporary directory (optional usefull for mako or jinja debug).")
    parser.add_option("--keep_temp_dir", dest="keep_temp_dir", action="store_true", help="This will keep the temporary dir ! Allowing to see all the intermediate state will parsing the file. e.g: from mako, jinja, yaml, hcl to xml.\n Beware Parsing is usually done in memory, keeping the resulting files into temp_dir could be a security breach.")
    parser.add_option("-l", "--log", action="store_true", default=False, dest="log", help="Do log console ?")
    parser.add_option("-L", "--log_dir", dest="log_dir", help="Optional log directory path. Required when log (-l) is provided.")
    parser.add_option("-R", "--log_rotate", dest="log_rotate", type=int, default=20, help="(Default 20) How many log files to keep into the log directory.")
    parser.add_option("-O", "--log_output", action="store_true", default=False, dest="log_output", help="By default system commands output is not retrieved into the log, this option allows it.")
    parser.add_option("--show_shortcut", dest="show_shortcut", action="store_true", default=False, help="Only usefull for kupd showing SoftClasses as Menu.\n"
        "When kupd is called with option: show_shortcut, It will show At the same menu's level sublink for sub menus.")

    #-- advanced Menu options:
    og=optparse.OptionGroup(parser, 'Advanced Menu options', description='')
    parser.add_option_group(og)
    og.add_option("-b", "--batch", dest="batch", help="This option requires a value:<mpath>.\n\
        mpath is the value for the menu, e.g.: path:1.abc.2.3.\n\
        The menu path syntax is <option number|option name>.[option number|option name>].")
    og.add_option("-g", "--go", dest="go", help='Same as --batch (-b) but will left the Menu at interactive mode !')
    og.add_option("-G", "--GO", dest="go_menu", help='Same as --go (-g) but will disallow system commands !')
    og.add_option("-p", "--pause", dest="pause", type=int, help="Works in conjunction with the --batch (-b) option. Pause every screen for the amount of seconds provided.")
    og.add_option("-C", "--noclear", dest="noclear", action="store_true", default=False, help="Works in conjunction with the --batch (-b) option. If set the terminal wont be cleared between each option.")
    og.add_option("-k", "--nokdealer", dest="nokdealer", action="store_true", help="""(False by default) When False, Kdealer works in conjunction with batch (or WebMenu: internal is_listening).
          nokdealer False: runs the kdealer menu input/output dispatcher and allows :
          - the support of follow_menu: to follow another independent menu processes, launched by some menu command like if it was the same unique menu.
               These menu command use: --follow_menu.
          - the support of webMenu.
          - the support of batch commands
          - the support of full history for batch commands
    """)
    # og.add_option("-P", "--port", dest="port", type=int, help="(Internal only). Works in conjunction with the kdealer (--kdealer) option. The kdealer port.")
    og.add_option("--secid", dest="secid", help="(Internal only). Works in conjunction with the kdealer (--kdealer) option. An md5 on the kdealer listener session.")
    og.add_option("--follow_menu", dest="follow_menu", action="store_true", default=False, help='Use this option, if you want to pipe this standalone Menu process with another.\n\
        If, within a Menu Option command you are calling another Manu process, use this option (--follow_menu) to allow them to glue together.\n\
        This would allow the listener and batch options to work as if they were called in the same Menu process.')
    
    (options, args) = parser.parse_args(args=args)
    VERBOSE=options.verbose
    
    if options.batch==None and not options.go and not options.go_menu:
        if options.pause!=None:raise kastmenuxception.kastmenuSystemException('Main', self_funct, 'Otpion --pause (-P) cannot be provided when --batch (-b) is not !')
        # if options.noclear:raise apimenuxception.kastmenuSystemException('Main', self_funct, 'Otpion --noclear (-C) cannot be provided when --batch (-b) is not !')
        
    if ( options.batch!=None and (options.go or options.go_menu) or (options.go and options.go_menu) ):
        raise kastmenuxception.kastmenuSystemException('Main', self_funct, 'Otpions: --batch (-b), --go (-g) and --GO (-G) are exlusive !')
    if options.nokdealer:
        if options.batch!=None or options.go or options.go_menu:
            raise kastmenuxception.kastmenuSystemException('Main', self_funct, 'Otpions: --batch (-b), --go (-g), --GO (-G) cannot be provided when --kdealer (-k) is not !')

    kwad_attrs = tools.getKastConfs()
    ## aliases:
    aliases = dict(kwad_attrs)

    ## Retreives temp_dir:
    from kwadlib import default
    if options.temp_dir != None: APMENU_TEMP_DIR = options.temp_dir
    else:
        # APMENU_TEMP_DIR = kwad_attrs['temp_dir'] + '/apimenu/' + tools.genUid()
        APMENU_TEMP_DIR = default.getUserKastTempDir() + '/' + tools.genUid()
        if not path.isdir(APMENU_TEMP_DIR):makedirs(APMENU_TEMP_DIR)

    tools.verbose(SELF_MODULE + ': Temporary dir is: ' + APMENU_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='', logFile=VERBOSE)

    # Kdealer support. Try to get secrets from input: Reads Kdealer secid and port from Stdin. The expected Syntax is: kealer:<secid>,<port>
    from kwadlib.security.crypting import getOptSecidFromFile
    secid, port = getOptSecidFromFile(options.secid, temp_dir=default.getKastTempDir())


    if port==None:
        if options.secid!=None:raise kastmenuxception.kastmenuSystemException('Main', self_funct, 'Otpion --secid cannot be provided when port is not !')
    else:
        if options.secid == None or not isinstance(options.secid, str): raise kastmenuxception.apimenuParameterException('Main', self_funct, 'Otpion  --secid must be provided when port is provided !')
        if options.follow_menu: raise kastmenuxception.apimenuParameterException('Main', self_funct, 'Option --follow_menu cannot be provided when secid provided !')

    # tmpl_kws
    if options.tmpl_kws!=None:
        try:
            from kwadlib import ct
            tmpl_kws=ct.dress(options.tmpl_kws)
        except:
            print('Option --tmpl_kws incorrect: Must be a CoolTyped expression of a dict ! Your value:' + str(options.tmpl_kws) + '.')
            raise
    else:tmpl_kws={}
    
    try:
        if len(args)<1:raise kastmenuxception.kastmenuSystemException('Main', self_funct, 'Argument menu file is required !')
        elif len(args)>1:raise kastmenuxception.kastmenuSystemException('Main', self_funct, 'Only one Argument: the menu file is supported !')
        
        menu_file=args[0]
        menu_file=path.normpath(path.realpath(menu_file))
        if not path.isfile(menu_file):raise kastmenuxception.kastmenuSystemException('Main', self_funct, 'File:' + menu_file + ' should exists !')

        call_kastmenup(menu_file, record=options.record, go_menu=options.go_menu, go=options.go, batch=options.batch, pause=options.pause, noclear=options.noclear, kdealer=not options.nokdealer, port=port, secid=secid, showResultingSourceOnly=options.show, temp_dir=APMENU_TEMP_DIR, keep_temp_dir=options.keep_temp_dir, tmpl_kws=tmpl_kws, aliases=aliases, log=options.log, log_output=options.log_output, log_dir=options.log_dir, log_rotate=options.log_rotate, call_cde=' '.join(sys.argv), debug=options.debug)
        
    except Exception as e:
        
        if VERBOSE==None:
            try:VERBOSE=int(options.verbose)
            except:VERBOSE=0
        if VERBOSE>=10:raise

        import sys
        if not hasattr(e, 'short1') or not hasattr(e, 'short2'):
            message=e.__class__.__name__ + ': ' + str(e)
        elif VERBOSE<5:
            message=e.short1()
        elif VERBOSE>=5:
            message=e.short2()
        sys.stderr.write(message + '\n')
        sys.exit(2)
        
        
if __name__ == '__main__':
    from os import path
    import utils
    import sys
    secid = None
    port = None

    signal(SIGINT, signal_handler)
    signal(SIGHUP, signal_handler)

    apimenu_home=utils.getInstallDir()
    
    ## Set paths
    for _path in ('core',):
        _path=path.normpath(apimenu_home + '/' + _path)
        if not _path in sys.path:sys.path.append(_path)

    main(sys.argv[1:])
