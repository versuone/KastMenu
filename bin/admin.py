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


SELF_MODULE='addkuser'
KINIT_TEMP_DIR = None


##########
## Main ##
##########

def usage():
    return """
Interactively:
addmin -i
or 
addmin --add -u <user> -f /where/is/password/file
or
addmin --del -u <user>
or
addmin -l

Use this command to create a local KastMenu admin user.
Many local KastMenu admin users can be created.
These users are KastMenu super users.
These KastMenu admin users are allowed to use the KastMenu admin webMenu at: https://<host:port>/kastmenu/admin.
To run command: add(/del)kuser and add(/del)skuser.
"""

def main(args):
    self_funct='main'
    from kwadlib.security.crypting import sanitize_kastmenu
    from kwadlib import tools, xception
    from kwadlib import default
    from getpass import getpass
    from kwadlib import db
    db.initdb()
    import optparse
    global KINIT_TEMP_DIR
    KINIT_TEMP_DIR = default.getUserKastTempDir()
    ALLOWED_ARGS = ('user', )
    global VERBOSE
    VERBOSE=None

    parser = optparse.OptionParser(usage())
    parser.add_option('-v', "--verbose", dest="verbose", type=int, default=0, help="Verbose level, int value.")
    parser.add_option('-u', "--user", dest="user", help="User name")
    parser.add_option('-a', "--add", dest="add", action="store_true", default=False, help="Action add User")
    parser.add_option('-d', "--del", dest="delete", action="store_true", default=False, help="Action del User")
    parser.add_option('-f', "--password_file", dest="password_file", help="Optional Password File. If not provided password will be prompted !")
    parser.add_option('-F', "--force", dest="force", action="store_true", default=False, help="Use this to force ssh keys regeneration even when user preexist !")
    parser.add_option('-l', "--list", dest="doList", action="store_true", default=False, help="Will take no action but list all KastMenur recorded admin Users !")
    parser.add_option('-D', "--disabled", dest="disabled", action="store_true", default=False, help="If provided this user will be no more accessable from the WebMenu !")
    parser.add_option('-E', "--enabled", dest="enabled", action="store_true", default=False, help="If provided this user will accessable again from the WebMenu !")
    parser.add_option('-i', "--doInteractive", dest="doInteractive", action="store_true", default=False, help="Use this if you want to provide options interactivly !")

    (options, args) = parser.parse_args(args=args)
    VERBOSE=options.verbose

    try:
        if len(args) > 0:
            print (usage())
            raise xception.kwadSystemException('Main', self_funct, 'Arguments: %s are not supported but options yes !' % str(args))

        kwad_attrs = tools.getKastConfs()
        tools.verbose(SELF_MODULE + ': Temporary dir is: ' + KINIT_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='',
                      logFile=VERBOSE)


        l = [options.add, options.delete, options.doList]
        l.sort()
        if l != [False, False, True]:
            raise xception.kwadSystemException('Main', self_funct, 'Only One of these Options: add, del or list is required !')

        if options.doList:
            from io import StringIO
            sb = StringIO()
            l = db.AdminUser().list()
            if l==False:
                xception.kwadInformation('Main', self_funct, 'No Admin User found !').warn()
                return

            for rows in l:
                sb.write('AdminUser: ')
                firstTime = True
                for f in db.AdminUser.FIELDS:
                    if not firstTime:sb.write(', ')
                    firstTime=False
                    sb.write(('%s=%s') % (f, str(rows[f])))
                sb.write('\n')

            print (sb.getvalue())
            return

        if options.delete:
            # Check User E:
            adminuser = db.AdminUser(user=options.user)
            if not adminuser.load():
                xception.kwadInformation('Main', self_funct, "Option --user (-u): %s Do not not Exist ! Nothing to do." % options.user).warn()
                return
            adminuser.delete()
            print('AdminUser: %s Deleted !' % options.user)
            return


        if options.doInteractive:
            fields=[
    ('user', "User name"),
    ]
            if options.password_file!=None:fields.append(('password', "User Password"))

            i = 0
            while i < len(fields):
                field, help = fields[i]
                message = "Enter %s  %s: " % (field, help)
                if field != 'password':
                    v = input(message).strip()
                else:
                    v = getpass(message).strip()
                if v == '': v = None
                if v == None:
                    if getattr(options, field)!=None:
                        v=getattr(options, field)
                    else:
                        print ('%s cannot be None !' % field)
                        continue

                try:
                    sanitize_kastmenu(v)
                except:
                    print('Unsupported value: %s for field: %s !' % (v, field))
                    continue

                i += 1
                if v != None:
                    print ('%s = %s' % (field, v))
                    setattr(options, field, v)


        if options.disabled and options.enabled: raise xception.kwadSystemException('Main', self_funct, 'Options disabled (-D) and enabled (-E) cannot be provided together !')
        if options.user == None: raise xception.kwadSystemException('Main', self_funct, 'Option --user (-u) is required !')
        # Check User E:
        adminuser = db.AdminUser(user=options.user)
        if adminuser.load():
            if  not options.force:
                xception.kwadInformation('Main', self_funct, "Option --user (-u): %s Exist ! Use --force (-f) to force." % options.user).warn()
                return
            if adminuser.enabled == None:adminuser.enabled = True
        else: adminuser.enabled = True

        sanitize_kastmenu(class_exit='Main', method_exit=self_funct, **{'user': options.user})

        if options.password_file!=None:
            if not path.isfile(options.password_file): raise xception.kwadSystemException('Main', self_funct, 'Option --password_file (-f): %s should Exist !' % options.password_file)
            with open(options.password_file) as f:options.password = f.read().strip()
        if not hasattr(options, 'password'): options.password = None

        # If Password not provided prompt for it:
        if options.password == None:
            print ('Please provide password for Admin User: %s' % options.user)
            v=None
            while True:
                v = getpass('Password: ').strip()
                if v == '':
                    print('Password cannot be None !')
                    continue
                break
            options.password = v

        sanitize_kastmenu(do_hide=True, class_exit='Main', method_exit=self_funct, **{'password': options.password})

        from kwadlib.security.crypting import sha256
        adminuser.user=options.user
        adminuser.password=sha256(options.password)
        if options.enabled:adminuser.enabled = True
        if options.disabled:adminuser.enabled = False
        adminuser.save()
        print("""AdminUser: {user} Created ! Use addmin user -l to list.
As admin user it will be allowed to connect to KastMenu webMenu:
    at: https://<host:port>/kastmenu/admin/<user>     
        """.format(user=options.user))


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

    addkuser_home=utils.getInstallDir()
    
    ## Set paths
    for _path in ('core',):
        _path=path.normpath(addkuser_home + '/' + _path)
        if not _path in sys.path:sys.path.append(_path)

    main(sys.argv[1:])
