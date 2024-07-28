#!/usr/bin/python3
###############################################################################
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
###############################################################################



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
    parser.add_option('-l', "--list", dest="doList", action="store_true", default=False, help="Will take no action but list all KastMenu Machines !")

    # -- Optional AcceptMail options:
    og = optparse.OptionGroup(parser, 'kastagent options')
    parser.add_option_group(og)
    og.add_option("--ssh_port", dest="ssh_port", type=int, default=22, help="ssh port on this machine (Default 22)")
    og.add_option("--kastagent_dir", dest="kastagent_dir", help="Directory for the kastagent binary on this node machine (Default /home/<kastagent_user>)")
    og.add_option("--kastweb_port", dest="kastweb_port", type=int, default=9100, help="Port for the kastweb deamon that will run on the kastagent (Default 9100)")

    parser.add_option('-S', "--rmv_sudo_user", dest="rmv_sudo_user", action="store_true", default=False, help="Only if a sudo_user was attached to this machine (see addkuser). Remove sudo_user (and xaccept_mail, default_menu, default_menu_fpath).")
    parser.add_option('-s', "--rmv_kastagent_user", dest="rmv_kastagent_user", action="store_true", default=False, help="Only if a kastagent_user was attached to this machine (see addkuser). Remove kastagent_user. Notice: A kastagent user is required to run a node.")

    # -- Optional AcceptMail options:
    og = optparse.OptionGroup(parser, 'Optional AcceptMail options', description='Use this if you want to sigin user and auto-create their user profiles on this machine.')
    parser.add_option_group(og)
    og.add_option("--cattrs", dest="kwad_attrs", help="(optional and appinst local only) The path to a custom kwad.attrs file. \n" + \
                                                          "If not provided the file: kwad.attrs and kwad.desc.attrs will be retreived from respectives : <pugin_dir>/softclasses/category/<category>/software/<software> SoftClass directories.")
    og.add_option('-A', "--xaccept_mail", dest="xaccept_mail", action="store_true", default=False, help="""Beware options starting with 'x' are Experimental are obviously include a security risk.
    If you use them this is at your own risk.
    Only if a sudo_user is attached to this machine (see addkuser).
    With xaccept_mail (-A): Users connecting via the WebMenu would be allowed to automatically create their own account simply providing their mail accounts.
""")
    og.add_option('-a', "--rmv_accept_mail", dest="rmv_accept_mail", action="store_true", default=False, help="Remove xaccept_mail (and default_menu and default_menu_fpath).")
    og.add_option("--default_nologin", dest="default_nologin", action="store_true", default=False, help="In conjunction with --xaccept_mail (-A). If True (default) will set nologin to new created users for accepted mail.")
    og.add_option("--rmv_default_nologin", dest="rmv_default_nologin", action="store_true", default=False, help="Remove default_nologin.")
    og.add_option('-M', "--default_menu", dest="default_menu", help="In conjunction with --xaccept_mail (-A). Will add this menu name for the newly created user.")
    og.add_option('-P', "--default_menu_fpath", dest="default_menu_fpath", help="In conjunction with --xaccept_mail (-A). Will add this menu file path for the newly created user.")

    # -- Optional Advanced options:
    og = optparse.OptionGroup(parser, 'Optional Advanced options')
    parser.add_option_group(og)
    og.add_option("--ispublic", dest="ispublic", action="store_true", default='False', help="If true will allow the display of this machine (in the search list) for all users, even if they dont have any account on this machine.")
    og.add_option("--rmv_ispublic", dest="rmv_ispublic", action="store_true", default=False, help="Remove ispublic (and isdefault).")
    og.add_option("--isdefault", dest="isdefault", action="store_true", default=False, help="In conjunction with --ispublic. If true will display this machine by default when entering the WebMenu.")
    og.add_option("--rmv_isdefault", dest="rmv_isdefault", action="store_true", default=False, help="Remove isdefault alone.")

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
                xception.kwadInformation('Main', self_funct, 'No Machine found !').warn()
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
                raise xception.kwadSystemException('Main', self_funct, 'Options: --default_menu (-M) and --default_menu_fpath (-P) are required for xaccept_mail !')
        else:
            if options.default_menu!=None or options.default_menu_fpath!=None:
                raise xception.kwadSystemException('Main', self_funct, 'Options: --default_menu (-M) and --default_menu_fpath (-P) are only allowed with --xaccept_mail (-A) !')
            if options.rmv_default_nologin:
                raise xception.kwadSystemException('Main', self_funct, 'Options: --rmv_default_nologin if allowed only with --xaccept_mail !')

        if options.isdefault and not options.ispublic:
            raise xception.kwadSystemException('Main', self_funct, 'Options: --isdefault is only allowed with option --ispublic !')

        if options.title!=None:machine.title=options.title
        if options.ssh_port not in (None, 0):machine.ssh_port=options.ssh_port
        if options.kastagent_dir!=None:machine.kastagent_dir=options.kastagent_dir
        if options.kastweb_port not in (None, 0):machine.kastweb_port=options.kastweb_port
        machine.ipv4=True
        machine.ipv6=False


        if options.rmv_kastagent_user:machine.kastagent_user = None

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
            if options.default_nologin: machine.default_nologin = True
            elif options.rmv_default_nologin: machine.default_nologin = False
            else:machine.default_nologin = False
        else:
            machine.default_nologin = False

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
