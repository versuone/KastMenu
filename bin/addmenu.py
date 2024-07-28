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


SELF_MODULE = 'addkuser'
KINIT_TEMP_DIR = None


##########
## Main ##
##########

def usage():
    return """
Interactively:
addmenu -i
or 
addmenu -m myhost -u myuser -p /where/is/my/menu.xml

This command add a menu file to KastMenu. 
    """


def main(args):
    self_funct = 'main'
    from kwadlib.security.crypting import sanitize_kastmenu, sanitize_hostorip, sanitize_path, sanitize
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
    parser.add_option('-u', "--user", dest="user", help="User name")
    parser.add_option('-n', "--name", dest="name", help="This is a logical name for the menu file for this user on the machine !")
    parser.add_option('-p', "--path", dest="path", help="This is an absolute path for the menu file on this machine.")
    parser.add_option('-l', "--list", dest="doList", action="store_true", default=False, help="Will take no action but list all KastMenu Machines !")
    parser.add_option('-i', "--doInteractive", dest="doInteractive", action="store_true", default=False, help="Use this if you want to provide options interactivly !")
    parser.add_option('-F', "--force", dest="force", action="store_true", default=False, help="Use this to force when machine preexist !")

    (options, args) = parser.parse_args(args=args)
    VERBOSE = options.verbose

    try:
        if len(args) > 0:
            print(usage())
            raise xception.kwadSystemException('Main', self_funct, 'Arguments: %s are not supported but options yes !' % str(args))

        kwad_attrs = tools.getKastConfs()
        tools.verbose(SELF_MODULE + ': Temporary dir is: ' + KINIT_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='',
                      logFile=VERBOSE)
        if options.doList:
            from io import StringIO
            sb = StringIO()
            l = db.MenuFile().list()
            if l == False:
                xception.kwadInformation('Main', self_funct, 'No Menu found !').warn()
                return

            for rows in l:
                sb.write('Menu: ')
                firstTime = True
                for f in db.MenuFile.FIELDS:
                    if not firstTime: sb.write(', ')
                    firstTime = False
                    sb.write(('%s=%s') % (f, str(rows[f])))
                sb.write('\n')

            print(sb.getvalue())
            return

        if options.doInteractive:
            fields = [
                ('machine', "Machine Host, rather FQDN"),
                ('user', "User name"),
                ('name', "A Name for the KastMenu file"),
                ('path', "Path for the KastMenu file"),
            ]

            i = 0
            while i < len(fields):
                field, help = fields[i]
                message = "Enter %s  %s: " % (field, help)
                v = input(message).strip()

                if v == '': v = None
                if v == None:
                    if getattr(options, field) != None:
                        v = getattr(options, field)
                    else:
                        print('%s cannot be None !' % field)
                        continue

                try:
                    if field=='machine':sanitize_hostorip(v)
                    elif field=='user':sanitize(v)
                    elif field=='name':sanitize(v)
                    elif field=='path':sanitize_path(v)
                except:
                    print('Unsupported value: %s for field: %s !' % (v, field))
                    continue

                i += 1
                if v != None:
                    print('%s = %s' % (field, v))
                    setattr(options, field, v)

        if options.machine == None: raise xception.kwadSystemException('Main', self_funct, 'Option --machine (-m) is required !')
        if options.user == None: raise xception.kwadSystemException('Main', self_funct, 'Option --user (-u) is required !')
        if options.name == None: raise xception.kwadSystemException('Main', self_funct, 'Option --name (-n) is required !')
        if options.path == None: raise xception.kwadSystemException('Main', self_funct, 'Option --path (-p) is required !')
        # Check Machine E:
        machine = db.Machine(host=options.machine)
        if not machine.load():
            raise xception.kwadSystemException('Main', self_funct, 'Option --machine (-m): %s do not Exist ! Create it first using "addMachine".' % options.machine)
        # Check User E:
        user = db.User(host=options.machine, user=options.user)
        if not user.load():
            raise xception.kwadSystemException('Main', self_funct, 'Option --user (-u): %s do not Exist on Machine: %s ! Create it first using "addUser".' % (options.user, options.machine))
        # Check MenuFile E:
        menufile = db.MenuFile(host=options.machine, user=options.user, name=options.name)
        if menufile.load() and not options.force:
            xception.kwadInformation('Main', self_funct, "Option --name (-n): %s Exist for Machine: %s and User: %s ! Use --force (-F) to force." % (options.name, options.machine, options.user)).warn()
            return

        if options.name == None: raise xception.kwadSystemException('Main', self_funct, 'Option --name (-n) is required !')
        if options.path == None: raise xception.kwadSystemException('Main', self_funct, 'Option --path (-p) is required !')
        sanitize_hostorip(class_exit='Main', method_exit=self_funct, **{'machine': options.machine})
        sanitize(class_exit='Main', method_exit=self_funct, **{'user': options.user, 'name': options.name})
        sanitize_path(class_exit='Main', method_exit=self_funct, **{'path': options.path})

        if options.path!=None:menufile.path = options.path
        menufile.save()
        print("""Menu File: name: {name} path: {path} Created ! Use addmenu -l to list.   
K users are allowed to connect to KastMenu webMenu on Menu Links:
    https://<host:port>/kastmenu/machine/{machine}/user/{user}/menu/{name}.     
        """.format(machine=options.machine, user=options.user, name=options.name, path=options.path))


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

    addkuser_home = utils.getInstallDir()

    ## Set paths
    for _path in ('core',):
        _path = path.normpath(addkuser_home + '/' + _path)
        if not _path in sys.path: sys.path.append(_path)

    main(sys.argv[1:])
