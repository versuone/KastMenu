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

"""
# -A, -F    
sudo -u kastserver /opt/kastmenu/current/bin/addmachine -m k8node2 -t sdqdqss -v3 -F
sudo -u kastserver /opt/kastmenu/current/bin/addskuser -m k8node2 -u adetruire  -t sdqdqss -v3 -F
sudo -u kastserver /opt/kastmenu/current/bin/addmenu  -m k8node2 -u adetruire -t sdqsddssf  -v300 -p /sdfsdf/Dfg/fdgh/fgh -l
"""

##########
## Main ##
##########

def usage():
    return """
Interactively:
addkuser -i
or 
addkuser -m myhost -u myuser
or
addkuser -m myhost -u myuser -f mypassfile 

Use this command to add/update an User to KastMenu.
An User is always associated to a Machine so the Machine must
have been added first.
KastMenu will create an SSH key no password to this new user.
Kastmenu will use this no password ssh key for further connection to this new machine/user.

The user password will be requested trying to construct the key.

Future connections to this machine/user through the webMenu interface:
    https://<host:port>/kastmenu/machine/<machine>/user/<user>/menu/<menu_name>.
will always require the user password.
The user password is never stored locally by KastMenu but rather convoyed and checked on the 
target machine.

Machine Kastagent User: (Required to run a node)
-----------------------
If provided: this user will be associated to the machine as the Machine's kastagent_user.
A Machine's kastagent_user:
- is used to install the kastagent binary on a node.
- is used to run kastweb on a node.
kastweb is the generic part of the kastagent run on a node, while the other part kastmenup 
is run under the specific user requesting the menu.
A kastagent_user is required to run a node.
This user will also be: disabled: This means it  will be no more accessable from the WebMenu.

Machine Super User: (Optional)
-------------------
If you use addskuser instead of addkuser.
Or if you use adduser with option: --is_machine_sudo_user:
This user is special as it is associated to the machine as this machine's super user.
This user must support sudo root no password.

Once a machine has a super user it is no more need to add users to this machine.
(No more need to use addkuser)
Because furthers user's connection through KastMenu webMenu will be checked and connected 
through this super user on this target machine.
KastMenu will use this super user to check the user password on the target machine,
and sudo to switch to this user. 
    """

def main(args):
    self_funct='main'
    from kwadlib.security.crypting import sanitize_kastmenu, sanitize_hostorip, sanitize
    from kwadlib import tools, xception
    from kwadlib import default
    from getpass import getpass
    from kwadlib import db
    db.initdb()
    import optparse
    global KINIT_TEMP_DIR
    KINIT_TEMP_DIR = default.getUserKastTempDir()
    GUEST_USER = default.getKastConfs()['guestuser']
    global VERBOSE
    VERBOSE=None

    parser = optparse.OptionParser(usage())
    parser.add_option('-v', "--verbose", dest="verbose", type=int, default=0, help="Verbose level, int value.")
    parser.add_option('-m', "--machine", dest="machine", help="Machine Host. Dont provide IP but FQDN as possible.")
    parser.add_option('-u', "--user", dest="user", help="""User name.
When a kuser is created.
Only if the target machine has no sudo_user set to it,
- A no pass ssh_key is specifically created for the user kastmenu to access this user on the target machine.
Beware as "no pass ssh_keys" are created for the user kastmenu on the kastmenu, 
this user and by extension the kastmenu or the machine holding the kastmenu must be super protected.
The WebMenu will use this ssh_key to connect this user on the remote machine.

As WebMenu is using ssh_key to connect to this user to remote machine:
- it will still work even if the user change their password on the remote machine.
- Use delkuser to remove the specific "no pass ssh_keys".
- Authentication of user to machine: is run by WebMenu checking the user password directly on the remote machine.
KastMenu do not store user password.
""")
    parser.add_option('-t', "--title", dest="title", help="Title.")
    parser.add_option('-f', "--password_file", dest="password_file", help="Optional Password File. If not provided password will be prompted !")
    parser.add_option('-F', "--force", dest="force", action="store_true", default=False, help="Use this to force ssh keys regeneration even when user preexist !")
    parser.add_option('-l', "--list", dest="doList", action="store_true", default=False, help="Will take no action but list all KastMenu recorded Users !")
    parser.add_option('-i', "--doInteractive", dest="doInteractive", action="store_true", default=False, help="Use this if you want to provide options interactivly !")
    parser.add_option('-D', "--disabled", dest="disabled", action="store_true", default=False, help="If provided this user will be no more accessable from the WebMenu !")
    parser.add_option("--ispublic", dest="ispublic", action="store_true", default='False', help="If true will allow the display of this user (in the search list) for all users, even if they dont have any account on this machine.")
    parser.add_option("--rmv_ispublic", dest="rmv_ispublic", action="store_true", default=False, help="Remove ispublic (and isdefault).")
    parser.add_option('-E', "--enabled", dest="enabled", action="store_true", default=False, help="If provided this user will accessable again from the WebMenu !")
    parser.add_option('-K', "--is_machine_kastagent_user", dest="is_machine_kastagent_user", action="store_true", default=False, help="""
If provided: this user will be associated to the machine as the Machine's kastagent_user.
A Machine's kastagent_user:
- is used to install the kastagent binary on a node.
- is used to run kastweb on a node.
kastweb is the generic part of the kastagent run on a node, while the other part kastmenup 
is run under the specific user requesting the menu.
A kastagent_user is required to run a node.
This user will also be: disabled: This means it  will be no more accessable from the WebMenu.
.""")
    parser.add_option('-S', "--is_machine_sudo_user", dest="is_machine_sudo_user", action="store_true", default=False, help="""
If provided: this user will be associated to the machine as the Machine's sudo_user.
This user must have sudo power on the target machine (in order to allow sudo -u <other_kuser>).
This user will also be: disabled: This means it  will be no more accessable from the WebMenu.
If can enable it afterwards but but this is not recommended.

Once a super user is set to a machine:
- A no pass ssh_key is created for the user kastmenu to access this user on the target machine.
Beware as "no pass ssh_keys" are created for the user kastmenu on the kastmenu, 
this user and by extension the kastmenu or the machine holding the kastmenu must be super protected.
- Once a machine as a sudo_user further user adds (using addkuser) will no more create specific "no pass ssh_keys"
for kastmenu user.
- The WebMenu will run remote connection to this target machine exclusively using this sudo_user. 

You can use delkuser on previous kusers of this machine in order to remove the specific "no pass ssh_keys".
And recreate them.
""")
    parser.add_option('-N', "--xnopassword", dest="xnopassword", action="store_true", default=False, help="""Beware options starting with 'x' are Experimental are obviously include a security risk.
    If you use them this is at your own risk.
    Only if a sudo_user is attached to this machine (see addkuser).
    
    With xnopassword (-N): This user is allowed to connect with no Password check via the WebMenu.
    Typically this is a 'guest' user with low rigth menus attached to it.
    It can only be no more than one 'guest' user per machine.
    
    The 'guest' user is named after the attribute: guestuser into the kastmenu configuration file at:
     %s, for this site this value is: %s.
""" % (default.KAST_CONF, GUEST_USER))
    parser.add_option('--rmv_xnopassword', dest="rmv_xnopassword", action="store_true", default=False, help="Remove xnopassword.")
    (options, args) = parser.parse_args(args=args)
    VERBOSE=options.verbose

    try:
        if len(args) > 0:
            print (usage())
            raise xception.kwadSystemException('Main', self_funct, 'Arguments: %s are not supported but options yes !' % str(args))
        kwad_attrs = tools.getKastConfs()
        tools.verbose(SELF_MODULE + ': Temporary dir is: ' + KINIT_TEMP_DIR + '.', level=VERBOSE, ifLevel=50, indent='',
                      logFile=VERBOSE)
        if options.doList:
            from io import StringIO
            sb = StringIO()
            l = db.User().list()
            if l==False:
                xception.kwadInformation('Main', self_funct, 'No User found !').warn()
                return

            for rows in l:
                sb.write('User: ')
                firstTime = True
                for f in db.User.FIELDS:
                    if not firstTime:sb.write(', ')
                    firstTime=False
                    sb.write(('%s=%s') % (f, str(rows[f])))
                sb.write('\n')

            print (sb.getvalue())
            return

        if options.doInteractive:
            fields=[
    ('machine', "Machine Host, rather FQDN"),
    ('user', "User name"),
    ]
            if options.password_file==None:fields.append(('password', "User Password"))

            i = 0
            doSkipPassword = False
            while i < len(fields):
                field, help = fields[i]
                if doSkipPassword and field == 'password':
                    i += 1
                    continue

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
                    if field == 'machine':
                        sanitize_hostorip(v)
                        machine = db.Machine(host=options.machine)
                        if machine.load() and machine.sudo_user!=None:doSkipPassword = True
                        else:doSkipPassword = False

                    elif field == 'user':sanitize(v)
                except:
                    print('Unsupported value: %s for field: %s !' % (v, field))
                    continue

                i += 1
                if v != None:
                    if field != 'password':print ('%s = %s' % (field, v))
                    setattr(options, field, v)


        if options.disabled and options.enabled: raise xception.kwadSystemException('Main', self_funct, 'Options disabled (-D) and enabled (-E) cannot be provided together !')
        if options.machine == None: raise xception.kwadSystemException('Main', self_funct, 'Option --machine (-m) is required !')
        # Check Machine E:
        machine = db.Machine(host=options.machine)
        if not machine.load():
            raise xception.kwadSystemException('Main', self_funct, 'Option --machine (-m): %s do not Exist ! Create it first using "addMachine".' % options.machine)

        # Check User:
        if options.user == None: raise xception.kwadSystemException('Main', self_funct, 'Option --user (-u) is required !')
        # Check User E:
        user = db.User(host=options.machine, user=options.user)
        if user.load() and not options.force:
            xception.kwadInformation('Main', self_funct, "Option --user (-u): %s for Machine: %s Exist ! Use --force (-F) to force the regeneration the kastmenu's ssh keys." % (options.user, options.machine)).warn()
            return

        sanitize_hostorip(class_exit='Main', method_exit=self_funct, **{'machine': options.machine})
        sanitize(class_exit='Main', method_exit=self_funct, **{'user': options.user})
        # Space not allowed to title:
        if options.title!=None:sanitize_kastmenu(class_exit='Main', method_exit=self_funct, **{'title': options.title})

        more=''
        if options.is_machine_sudo_user and machine.sudo_user!=None:machine.sudo_user = None
        if machine.sudo_user == None:
            if options.password_file!=None:
                if not path.isfile(options.password_file): raise xception.kwadSystemException('Main', self_funct, 'Option --password_file (-f): %s should Exist !' % options.password_file)
                with open(options.password_file) as f:options.password = f.read().strip()
            if not hasattr(options, 'password'): options.password = None

            # If Password not provided prompt for it:
            if options.password == None:
                print ('Please provide password for User: %s on remote Machine: %s' % (options.user, options.machine))
                v=None
                while True:
                    v = getpass('Password: ').strip()
                    if v == '':
                        print('Password cannot be None !')
                        continue
                    break
                options.password = v

            sanitize_kastmenu(do_hide=True, class_exit='Main', method_exit=self_funct, **{'password': options.password})

            from kwadlib.security.crypting import sshNoPassword
            from kwadlib.default import getKastConfs

            # Allow bypass ssh on localhost:
            kast_host = getKastConfs()['kast_host']
            if options.machine == kast_host:
                # just check the password locally:
                sshNoPassword('localhost', options.user, options.password, type='rsa', ssh_port=machine.ssh_port, verbose=options.verbose)
                more = """Because this machine: {machine} matches the local host: {kast_host} (value kast_host into {kast_conf}), 
The user: {user} has been check using ssh but on localhost instead of the host: {kast_host}.
And future check for this user on this local machine will do the same.
Note: by local host we mean the server where the kastserver is running.""".format(machine=options.machine, kast_host=kast_host, user=options.user, kast_conf=default.KAST_CONF)
            else:
                sshNoPassword(options.machine, options.user, options.password, type='rsa',ssh_port=machine.ssh_port, verbose=options.verbose)
                more = """No password Ssh key was added to user kastmenu, if you are admin test it with: 
    sudo -u kastserver ssh {user}@{machine} hostname.
    """

        if options.xnopassword:
            if machine.sudo_user == None:
                raise xception.kwadSystemException('Main', self_funct, 'Before using option: xnopassword (-N) for user:%s on machine:%s, a sudo user must be attached to this machine using command: addkuser first !' % (options.user, options.machine))
            if options.user != GUEST_USER:
                raise xception.kwadSystemException('Main', self_funct, "A 'guest' user can only be named: %s as defined into the kastmenu configuration file at: %s !" % (GUEST_USER, default.KAST_CONF))

        user.title = options.title
        if options.rmv_xnopassword:user.xnopassword = False
        else:user.xnopassword = options.xnopassword

        # machine_sudo_user or options.is_machine_kastagent_user:
        if options.is_machine_sudo_user or options.is_machine_kastagent_user:
            user.enabled = False
        else:
            if options.enabled:user.enabled = True
            if options.disabled:user.enabled = False

        if options.rmv_ispublic:
            user.ispublic=False
        elif options.ispublic:user.ispublic=True
        if options.is_machine_kastagent_user:user.ispublic=False

        user.save()
        # machine_sudo_user:
        if options.is_machine_sudo_user:
            machine.sudo_user = options.user
        else:
            if user == machine.sudo_user:machine.sudo_user = None
        # machine_kastagent_user:
        if options.is_machine_kastagent_user:
            machine.kastagent_user = options.user
        else:
            if user == machine.kastagent_user:machine.kastagent_user = None

        machine.save()

        print("""User: {user} Created ! Use addkuser -l to list.
{more}K users are allowed to connect to KastMenu webMenu on Menu Links:
    https://<host:port>
    /kastmenu/machine/{machine}/user/{user}/menu/<menu_name>.
        """.format(more=more, user=options.user, machine=options.machine))


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
