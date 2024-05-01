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


SELF_MODULE = 'addmachine'
KINIT_TEMP_DIR = None


##########
## Main ##
##########

def usage():
    return """
Interactively:
addmachine -i
or 
addmachine -m myhost -p 40

Use this command to add/update a Machine to KastMenu.
    """


def main(args):
    self_funct = 'main'
    from kwadlib.security.crypting import sanitize_kastmenu, sanitize_hostorip, sanitize
    from kwadlib import tools, xception
    from kwadlib import default
    from kwadlib import db
    db.initdb()
    import optparse
    global KINIT_TEMP_DIR
    KINIT_TEMP_DIR = default.getUserKastTempDir()
    global VERBOSE
    VERBOSE = None

    parser = optparse.OptionParser(usage())
    parser.add_option('-v', "--verbose", dest="verbose", type=int, default=0, help="Verbose level, int value.")
    parser.add_option('-m', "--machine", dest="machine", help="Machine Host. Dont provide IP but FQDN as possible.")
    parser.add_option('-t', "--title", dest="title", help="Title.")
    parser.add_option("--ssh_port", dest="ssh_port", type=int, default=22, help="ssh_port (Default 22)")
    parser.add_option('-l', "--list", dest="doList", action="store_true", default=False, help="Will take no action but list all KastMenu Machines !")
    parser.add_option('-A', "--xaccept_mail", dest="xaccept_mail", action="store_true", default=False, help="""Beware options starting with 'x' are Experimental are obviously include a security risk.
    If you use them this is at your own risk.
    Only if a sudo_user is attached to this machine (see addkuser).
    With xaccept_mail (-A): Users connecting via the WebMenu would be allowed to automatically create their own account simply providing their mail accounts.
""")
    parser.add_option("--ispublic", dest="ispublic", action="store_true", default='False', help="If true will allow the display of this machine (in the search list) for all users, even if they dont have any account on this machine.")
    parser.add_option("--isdefault", dest="isdefault", action="store_true", default=False, help="In conjunction with --ispublic. If true will display this machine by default when entering the WebMenu.")
    parser.add_option('-M', "--default_menu", dest="default_menu", help="In conjunction with --xaccept_mail (-A). Will add this menu name for the newly created user.")
    parser.add_option('-P', "--default_menu_fpath", dest="default_menu_fpath", help="In conjunction with --xaccept_mail (-A). Will add this menu file path for the newly created user.")
    parser.add_option("--rmv_ispublic", dest="rmv_ispublic", action="store_true", default=False, help="Remove ispublic (and isdefault).")
    parser.add_option("--rmv_isdefault", dest="rmv_isdefault", action="store_true", default=False, help="Remove isdefault alone.")
    parser.add_option('-a', "--rmv_accept_mail", dest="rmv_accept_mail", action="store_true", default=False, help="Remove xaccept_mail (and default_menu and default_menu_fpath).")
    parser.add_option('-s', "--rmv_sudo_user", dest="rmv_sudo_user", action="store_true", default=False, help="Remove sudo_user (and xaccept_mail, default_menu, default_menu_fpath).")
    parser.add_option('-i', "--doInteractive", dest="doInteractive", action="store_true", default=False, help="Use this if you want to provide options interactivly !")
    parser.add_option('-F', "--force", dest="force", action="store_true", default=False, help="Use this to force when machine preexist !")

    (options, args) = parser.parse_args(args=args)
    VERBOSE = options.verbose

    try:
        if len(args) > 0:
            print(usage())
            # raise xception.kwadSystemException('Main', self_funct, 'Arguments: %s are not supported but options yes !' % str(args))

        tools.verbose(SELF_MODULE + ': Temporary dir is: ' + KINIT_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='',
                      logFile=VERBOSE)
        if options.doList:
            from io import StringIO
            sb = StringIO()
            l = db.Machine().list()
            if l == False:
                xception.kwadInformation('Main', self_funct, 'No User found !').warn()
                return

            for rows in l:
                sb.write('Machine: ')
                firstTime = True
                for f in db.Machine.FIELDS:
                    if not firstTime:sb.write(', ')
                    firstTime=False
                    sb.write(('%s=%s') % (f, str(rows[f])))
                sb.write('\n')

            print (sb.getvalue())
            return

        if options.doInteractive:
            fields = [
                ('machine', "Machine Host, rather FQDN"),
                ('ssh_port', "Ssh port"),
            ]

            i = 0
            while i < len(fields):
                field, help = fields[i]
                message = "Enter %s  %s: " % (field, help)
                v = input(message).strip()

                if v == '': v = None
                if v == None:
                    if getattr(options, field)!=None:
                        v=getattr(options, field)
                    elif field=='ssh_port':v=22
                    else:
                        print ('%s cannot be None !' % field)
                        continue
                if field == 'ssh_port':
                    if not v.isdigit():
                        print ('ssh_port: %s must be a digit !' % v)
                        continue
                    v=int(v)
                try:
                    if field == 'machine':sanitize_hostorip(v)
                except:
                    print('Unsupported value: %s for field: %s !' % (v, field))
                    continue

                i += 1
                if v != None:
                    print('%s = %s' % (field, v))
                    setattr(options, field, v)

        if options.machine == None: raise xception.kwadSystemException('Main', self_funct, 'Option --machine (-m) is required !')
        sanitize_hostorip(class_exit='Main', method_exit=self_funct, **{'machine': options.machine})
        # Space not allowed to title:
        if options.title!=None:sanitize_kastmenu(class_exit='Main', method_exit=self_funct, **{'title': options.title})

        # Check Machine E:
        machine = db.Machine(host=options.machine)
        preexist =  machine.load()
        if preexist and not options.force:
            xception.kwadInformation('Main', self_funct, 'Option --machine (-m): %s Exist ! Use --force (-F) to force.' % options.machine).warn()
            return

        if options.xaccept_mail and (not preexist or machine.sudo_user == None):
            raise xception.kwadSystemException('Main', self_funct, 'Before using option: xaccept_mail (-A), a sudo user must be attached to this machine using command: addkuser --is_machine_sudo_user (-S) !')

        if options.xaccept_mail and (options.rmv_accept_mail or options.rmv_sudo_user):
            raise xception.kwadSystemException('Main', self_funct, 'Option: --xaccept_mail (-A) cannot be used together with either: --rmv_xaccept_mail (-a) nor --rmv_sudo_user (-s) !')
        if options.xaccept_mail:
            if not preexist or machine.sudo_user == None:
                raise xception.kwadSystemException('Main', self_funct, 'Before using option: --xaccept_mail (-A) on machine:%s, a sudo user must be attached to this machine using command: addkuser  --is_machine_sudo_user (-S) first !' % options.machine)
            if options.default_menu==None or options.default_menu_fpath==None:
                raise xception.kwadSystemException('Main', self_funct, 'Options: --default_menu (-M) and --default_menu_fpath (-P) are required for xaccept_mail !' % options.machine)
        else:
            if options.default_menu!=None or options.default_menu_fpath!=None:
                raise xception.kwadSystemException('Main', self_funct, 'Options: --default_menu (-M) and --default_menu_fpath (-P) are only allowed with --xaccept_mail (-A) !' % options.machine)
        if options.isdefault and not options.ispublic:
            raise xception.kwadSystemException('Main', self_funct, 'Options: --isdefault is only allowed with option --ispublic !')

        if options.title!=None:machine.title=options.title
        if options.ssh_port not in (None, 0):machine.ssh_port=options.ssh_port
        machine.ipv4=True
        machine.ipv6=False


        if options.rmv_sudo_user:
            machine.sudo_user = None
            if machine.xaccept_mail:print('Machine: accept_mail (default_menu and default_menu_fpath) has been removed along rmv_sudo_user !')
            machine.xaccept_mail = False
            machine.default_menu = None
            machine.default_menu_fpath = None
        elif options.rmv_accept_mail:
            machine.xaccept_mail=False
            machine.default_menu = None
            machine.default_menu_fpath = None
        elif options.xaccept_mail:
            machine.xaccept_mail=True
            machine.default_menu = options.default_menu
            machine.default_menu_fpath = options.default_menu_fpath
        if options.rmv_isdefault:machine.isdefault=False
        elif options.isdefault:machine.isdefault=True
        if options.rmv_ispublic:
            machine.ispublic=False
            machine.isdefault = False
        elif options.ispublic:machine.ispublic=True


        machine.save()
        print ('Machine: %s Created ! Use addmachine -l to list.' % options.machine)

    except Exception as e:

        if VERBOSE == None:
            try:
                VERBOSE = int(options.verbose)
            except:
                VERBOSE = 0
        if VERBOSE >= 10: raise

        import sys
        if not hasattr(e, 'short1') or not hasattr(e, 'short2'):
            message = e.__class__.__name__ + ': ' + str(e)
        elif VERBOSE < 5:
            message = e.short1()
        elif VERBOSE >= 5:
            message = e.short2()
        sys.stderr.write(message + '\n')
        sys.exit(2)


if __name__ == '__main__':
    from os import path
    import utils
    import sys

    addmachine_home = utils.getInstallDir()

    ## Set paths
    for _path in ('core',):
        _path = path.normpath(addmachine_home + '/' + _path)
        if not _path in sys.path: sys.path.append(_path)

    main(sys.argv[1:])
