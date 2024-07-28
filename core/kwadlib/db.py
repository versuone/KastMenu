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



# Debian Install (Debug Only): sudo apt-get install sqlite3
# kastagent_user: is kastagent install user and kastweb run user.s
SCHEMAS=(
"""
CREATE TABLE machine (
id INTEGER PRIMARY KEY AUTOINCREMENT,
host TEXT UNIQUE NOT NULL,
title TEXT,
ssh_port INTEGER DEFAULT 22,
ipv4 BOOLEAN NOT NULL DEFAULT 0 CHECK (ipv4 IN (0, 1)),
ipv6 BOOLEAN NOT NULL DEFAULT 0 CHECK (ipv6 IN (0, 1)),
sudo_user TEXT,
xaccept_mail BOOLEAN NOT NULL DEFAULT 0 CHECK (xaccept_mail == 0 or (xaccept_mail == 1 and sudo_user IS NOT NULL)),
ispublic BOOLEAN NOT NULL DEFAULT 0 CHECK (ispublic IN (0, 1)),
isdefault BOOLEAN NOT NULL DEFAULT 0 CHECK (isdefault IN (0, 1)),
default_nologin BOOLEAN DEFAULT 1 CHECK (default_nologin IN (0, 1)),
default_menu TEXT,
default_menu_fpath TEXT,
kastagent_user TEXT,
kastagent_dir TEXT,
kastweb_port INTEGER,
kastweb_pid INTEGER,
kastweb_ssh_pid INTEGER,
tscreated INTEGER(4) NOT NULL DEFAULT (cast(strftime('%s','now') as int)),
tsupdated INTEGER(4) NOT NULL
);
""",
"""
CREATE TABLE adminuser (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT NOT NULL,
password TEXT,
enabled BOOLEAN DEFAULT 1 CHECK (enabled IN (0, 1)),
tscreated INTEGER(4) DEFAULT (cast(strftime('%s','now') as int)),
tsupdated INTEGER(4) NOT NULL,
UNIQUE(user)
);
""",
"""
CREATE TABLE user (
id INTEGER PRIMARY KEY AUTOINCREMENT,
host TEXT NOT NULL,
user TEXT NOT NULL,
title TEXT,
mail TEXT,
ispublic BOOLEAN NOT NULL DEFAULT 0 CHECK (ispublic IN (0, 1)),
enabled BOOLEAN DEFAULT 1 CHECK (enabled IN (0, 1)),
xnopassword BOOLEAN DEFAULT 1 CHECK (xnopassword IN (0, 1)),
tscreated INTEGER(4) DEFAULT (cast(strftime('%s','now') as int)),
tsupdated INTEGER(4) NOT NULL,
UNIQUE(host, user),
FOREIGN KEY (host) REFERENCES machine(host)
ON DELETE CASCADE
);
""",
"""
CREATE TABLE menufile (
id INTEGER PRIMARY KEY AUTOINCREMENT,
host TEXT NOT NULL,
user TEXT NOT NULL,
name TEXT NOT NULL,
path TEXT NOT NULL,
tscreated INTEGER(4) DEFAULT (cast(strftime('%s','now') as int)),
tsupdated INTEGER(4) NOT NULL,
UNIQUE(host, user, name),
UNIQUE(host, user, path),
FOREIGN KEY (host, user) REFERENCES user(host, user)
ON DELETE CASCADE
);
""",
"""
PRAGMA foreign_keys = ON;
"""
)


WEB_SCHEMAS=(
"""
CREATE TABLE ses_session (
sessionid TEXT NOT NULL PRIMARY KEY,
go_pages TEXT,
vcode TEXT,
lastused INTEGER
);
""",
"""
CREATE TABLE ses_adminuser (
sessionid TEXT,
user TEXT NOT NULL,
authenticated BOOLEAN NOT NULL CHECK (authenticated IN (0, 1)),
lastused INTEGER,
FOREIGN KEY (sessionid) REFERENCES ses_session(sessionid)
ON DELETE CASCADE,
UNIQUE(sessionid, user)
);
""",
"""
CREATE TABLE ses_user (
sessionid TEXT,
host TEXT NOT NULL,
user TEXT NOT NULL,
authenticated BOOLEAN NOT NULL DEFAULT 0 CHECK (authenticated IN (0, 1)),
lastused INTEGER,
FOREIGN KEY (sessionid) REFERENCES ses_session(sessionid)
ON DELETE CASCADE,
UNIQUE(sessionid, host, user)
);
""",
"""
CREATE TABLE ses_menufile (
sessionid TEXT,
host TEXT NOT NULL,
user TEXT NOT NULL,
name TEXT NOT NULL,

kastagent_port INTEGER,
kastagent_shasecid TEXT,
kastagent_pid INTEGER,
kastagent_ssh_pid INTEGER,

lastused INTEGER,
FOREIGN KEY (sessionid, host, user) REFERENCES ses_user(sessionid, host, user)
ON DELETE CASCADE,
UNIQUE(sessionid),
UNIQUE(kastagent_shasecid)
);
""",
"""
PRAGMA foreign_keys = ON;
"""
)

DATABASE=None
DATABASE_CONNECTION=None
DATABASE_CURSOR=None
from kwadlib.default import KAST_DBPATH
import time

WEB_DATABASE=None
WEB_DATABASE_CONNECTION=None
WEB_DATABASE_CURSOR=None
VERBOSE=0

def printlog(fromf, message, level=0):
    from kwadlib.tools import printlog as plog
    plog(fromf, message, level=level, verbose=VERBOSE)

def sanitize_input(value, allow_cars=None):
    from kwadlib.security.crypting import sanitize_kastmenu
    if allow_cars!=None and value in allow_cars:return value
    try:
        sanitize_kastmenu(value)
        return value
    except:
        return ''


class Entity:
    def load(self):
        self_funct = 'load'
        from kwadlib.security.crypting import sanitize_kastmenu
        kvalues = []

        for f in self.KEYS:
            kvalue=getattr(self, f)
            if f not in self.UNCHECKED_FIELDS:
                sanitize_kastmenu(do_hide=False, class_exit=self.__class__.__name__, method_exit=self_funct, **{f: kvalue})
            # If one key is null do nothing.
            if kvalue==None:return False
            kvalues.append(kvalue)

        sql = 'SELECT %s FROM %s WHERE %s' % (','.join(self.FIELDS), self.__class__.__name__.lower(), ' and '.join([ f + '=?' for f in self.KEYS]))
        printlog('Entity/load', 'Running: %s' % sql, level=150)
        printlog('Entity/load',  '      With values: %s' % str(kvalues), level=150)
        self.DATABASE_CURSOR.execute(sql, kvalues)
        results = self.DATABASE_CURSOR.fetchall()
        if results==None or len(results)==0:
            return False
        if len(results)>1:raise Exception('Table: %s, Many rows found at row: %s with kvalues: %s,  while supposed to be unique !' % (self.__class__.__name__, ', '.join(self.KEYS), ','.join(kvalues)))

        rows = results[0]
        for i in range(len(self.FIELDS)-1): # -1: without id
            try:
                if rows[i]!=None:
                    value=rows[i]
                    if self.FIELDS[i] not in self.UNCHECKED_FIELDS:
                        sanitize_kastmenu(do_hide=False, class_exit=self.__class__.__name__, method_exit=self_funct, **{self.FIELDS[i]: value})
                else:value=None
            except:
                raise Exception('Table: %s, Unsupported value: %s, for field: %s ! Found into row: %s with values: %s,  while supposed to be unique !' % (self.__class__.__name__, results[i], self.FIELDS[i], ', '.join(self.KEYS), ','.join(kvalues)))
            setattr(self, self.FIELDS[i], value)
        return True

    def save(self):
        self_funct = 'save'
        self.checkFields()

        if hasattr(self, 'tsupdated'):
            import time
            if self.tsupdated in (None, 0):self.tsupdated=int(time.time())

        from kwadlib.security.crypting import sanitize_kastmenu
        kvalues = []

        found = True
        for f in self.KEYS:
            kvalue = getattr(self, f)
            if f not in self.UNCHECKED_FIELDS:
                sanitize_kastmenu(do_hide=False, class_exit=self.__class__.__name__, method_exit=self_funct, **{f: kvalue})

            # If one key is null do nothing.
            if kvalue==None:
                found=False
                break
            kvalues.append(kvalue)

        if found:
            self.DATABASE_CURSOR.execute('SELECT {what} FROM {table} WHERE {where}'.format(what=','.join(self.FIELDS), table=self.__class__.__name__.lower(), where=' and '.join([ f + '=?' for f in self.KEYS])), kvalues)
            results = self.DATABASE_CURSOR.fetchall()
            if results==None or len(results)==0:found=False
            if len(results)>1:raise Exception('Many rows found at key: %s with kvalues: %s,  while supposed to be unique !' % (', '.join(self.KEYS), ','.join(kvalues)))

        values=[]
        for f in self.FIELDS:
            if f == 'id':continue
            values.append(getattr(self, f))
        if found:
            all_values = values + kvalues
            sql = "update {table} set {what} WHERE {where}".format(table=self.__class__.__name__.lower(), what=', '.join([f + '=?' for f in self.FIELDS if f != 'id']), where=' and '.join([f + '=?' for f in self.KEYS]))
            printlog('Entity/save', 'Running: %s' % sql, level=150)
            printlog('Entity/save', '      With values: %s' % str(all_values), level=150)

            self.DATABASE_CURSOR.execute(sql, all_values)
        else:
            sql = "insert into {table} ({what1}) values ({what2})".format(table=self.__class__.__name__.lower(), what1=', '.join([ f for f in self.FIELDS if f!='id']), what2=', '.join([ '?' for f in self.FIELDS if f!='id']))
            printlog('Entity/save', 'Running: %s' % sql, level=150)
            printlog('Entity/save', '      With values: %s' % str(values), level=150)
            self.DATABASE_CURSOR.execute(sql, values)
        self.DATABASE_CONNECTION.commit()

    def delete(self):
        self_funct = 'delete'
        from kwadlib.security.crypting import sanitize_kastmenu
        kvalues = []

        for f in self.KEYS:
            kvalue=getattr(self, f)
            if f not in self.UNCHECKED_FIELDS:
                sanitize_kastmenu(do_hide=False, class_exit=self.__class__.__name__, method_exit=self_funct, **{f: kvalue})
            # If one key is null do nothing.
            if kvalue==None:return False
            kvalues.append(kvalue)

        sql ='DELETE FROM %s WHERE %s' % (self.__class__.__name__.lower(), ' and '.join([ f + '=?' for f in self.KEYS]))
        printlog('Entity/delete', 'Running: %s' % sql, level=150)
        printlog('Entity/delete', '      With values: %s' % str(kvalues), level=150)
        self.DATABASE_CURSOR.execute(sql, kvalues)
        self.DATABASE_CONNECTION.commit()
        return True


    def list(self):
        sql = 'SELECT * from {table}'.format(what=','.join(self.FIELDS), table=self.__class__.__name__.lower())
        printlog('Entity/list', 'Running: %s' % sql, level=150)
        self.DATABASE_CURSOR.execute(sql)
        results = self.DATABASE_CURSOR.fetchall()
        if results==None or len(results)==0:return False
        founds=[]

        for rows in results:
            new_rows= {}
            for i in range(len(self.FIELDS)):new_rows[self.FIELDS[i]] = rows[i]
            founds.append(new_rows)

        return founds

    def checkFields(self):
        self_funct = 'checkFields'
        from kwadlib.security.crypting import sanitize_kastmenu
        for f in self.FIELDS:
            if f in self.UNCHECKED_FIELDS:continue
            v = getattr(self, f)
            if v == None:continue
            sanitize_kastmenu(do_hide=False, class_exit=self.__class__.__name__, method_exit=self_funct, **{f: getattr(self, f)})


# =========================================================================================================== #
# SCHEMA:
# =========================================================================================================== #

def initdb():
    global DATABASE
    global DATABASE_CONNECTION
    global DATABASE_CURSOR
    from os import path
    from kwadlib.default import containerdInit
    # In case is running in container may hav esome trailing init:
    containerdInit()

    dbdir = path.split(KAST_DBPATH)[0]
    if not path.isdir(dbdir):raise Exception('dbdir: %s must Exist !' % dbdir)
    if not path.isfile(KAST_DBPATH):
        with open(KAST_DBPATH, 'w') as f:f.write('')

    DATABASE=KAST_DBPATH
    import sqlite3

    DATABASE_CONNECTION = sqlite3.connect(DATABASE)
    DATABASE_CURSOR = DATABASE_CONNECTION.cursor()

    # Check if Table E:
    results = DATABASE_CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='machine';")
    if results!=None:results=results.fetchall()
    if len(results)==1 and results[0][0]=='machine':
        results = DATABASE_CURSOR.execute("PRAGMA foreign_keys = ON;")
        return False

    # Create tables:
    # --------------
    for e in SCHEMAS:
        DATABASE_CURSOR.execute(e)

    return True


class Machine(Entity):
    KEYS=('host',)
    FIELDS=('id', 'host', 'title', 'ssh_port', 'ipv4', 'ipv6', 'sudo_user', 'xaccept_mail', 'ispublic', 'isdefault', 'default_nologin', 'default_menu', 'default_menu_fpath', 'kastagent_user', 'kastagent_dir', 'kastweb_port', 'kastweb_pid', 'kastweb_ssh_pid', 'tscreated', 'tsupdated')
    UNCHECKED_FIELDS = []

    def __init__(self, host=None, title=None, ssh_port=22, ipv4=True, ipv6=False, sudo_user=None, xaccept_mail=False, ispublic=False, isdefault=False, default_nologin=True, default_menu=None, default_menu_fpath=None, kastagent_user=None, kastagent_dir=None, kastweb_port=None, kastweb_pid=None, kastweb_ssh_pid=None, tsupdated=None):
        self.DATABASE = DATABASE
        self.DATABASE_CONNECTION = DATABASE_CONNECTION
        self.DATABASE_CURSOR = DATABASE_CURSOR

        self.host=host
        self.title=title
        self.ssh_port=ssh_port
        self.ipv4=ipv4
        self.ipv6=ipv6
        self.xaccept_mail = xaccept_mail # Only if machine.sudo_user != None
        self.sudo_user=sudo_user

        self.ispublic = ispublic
        self.isdefault = isdefault
        self.default_nologin = default_nologin
        self.default_menu = default_menu
        self.default_menu_fpath = default_menu_fpath

        self.kastagent_user = kastagent_user
        self.kastagent_dir = kastagent_dir
        self.kastweb_port = kastweb_port
        self.kastweb_pid = kastweb_pid
        self.kastweb_ssh_pid = kastweb_ssh_pid

        self.tscreated=int(time.time())
        self.tsupdated=tsupdated
        self.id=None


class AdminUser(Entity):
    KEYS=('user',)
    FIELDS=('id', 'user', 'password', 'enabled', 'tscreated', 'tsupdated')
    UNCHECKED_FIELDS = []

    def __init__(self, user=None, password=None, enabled=True, tsupdated=None):
        self.DATABASE = DATABASE
        self.DATABASE_CONNECTION = DATABASE_CONNECTION
        self.DATABASE_CURSOR = DATABASE_CURSOR

        self.user=user
        self.password = password
        self.enabled = enabled

        self.tscreated=int(time.time())
        self.tsupdated=tsupdated
        self.id = None

class User(Entity):
    KEYS=('host', 'user')
    FIELDS=('id', 'host', 'user', 'title', 'mail', 'ispublic', 'enabled', 'xnopassword', 'tscreated', 'tsupdated')
    UNCHECKED_FIELDS = []

    def __init__(self, host=None, user=None, title=None, mail=None, ispublic=False, enabled=True, tsupdated=None):
        self.DATABASE = DATABASE
        self.DATABASE_CONNECTION = DATABASE_CONNECTION
        self.DATABASE_CURSOR = DATABASE_CURSOR

        self.host = host
        self.user=user
        self.title = title
        self.mail = mail # Only if machine.sudo_user != None
        self.ispublic = ispublic
        self.enabled = enabled
        self.xnopassword = False
        self.tscreated=int(time.time())
        self.tsupdated=tsupdated
        self.id = None

class MenuFile(Entity):
    KEYS=('host', 'user', 'name')
    FIELDS=('id', 'host', 'user', 'name', 'path', 'tscreated', 'tsupdated')
    UNCHECKED_FIELDS = []

    def __init__(self, host=None, user=None, name=None, path=None, tsupdated=None):
        self.DATABASE = DATABASE
        self.DATABASE_CONNECTION = DATABASE_CONNECTION
        self.DATABASE_CURSOR = DATABASE_CURSOR

        self.host = host
        self.user=user
        self.name=name
        self.path=path
        self.tscreated=int(time.time())
        self.tsupdated=tsupdated
        self.id = None



# =========================================================================================================== #
# WEB SCHEMA:
# =========================================================================================================== #

def initwebdb():
    global WEB_DATABASE
    global WEB_DATABASE_CONNECTION
    global WEB_DATABASE_CURSOR

    import sqlite3

    WEB_DATABASE_CONNECTION = sqlite3.connect(':memory:')
    # e.g./: Multiple in memory + shared cache to allow many connection on same in-memory db:
    # WEB_DATABASE_CONNECTION = sqlite3.connect('file:dbweb?mode=memory&cache=shared')
    WEB_DATABASE_CURSOR = WEB_DATABASE_CONNECTION.cursor()

    # Check if Table E:
    results = WEB_DATABASE_CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ses_session';")
    if results!=None:results=results.fetchall()
    if len(results)==1 and results[0][0]=='ses_session':
        results = WEB_DATABASE_CURSOR.execute("PRAGMA foreign_keys = ON;")
        return False

    # Create tables:
    # --------------
    for e in WEB_SCHEMAS:
        WEB_DATABASE_CURSOR.execute(e)

    return True

class ses_Session(Entity):
    KEYS=('sessionid',)
    FIELDS=('sessionid', 'go_pages', 'vcode', 'lastused')
    UNCHECKED_FIELDS = ['go_pages']

    def __init__(self, sessionid=None, go_pages=None, vcode=None, lastused=None):
        self.DATABASE = WEB_DATABASE
        self.DATABASE_CONNECTION = WEB_DATABASE_CONNECTION
        self.DATABASE_CURSOR = WEB_DATABASE_CURSOR

        self.sessionid = sessionid
        self.go_pages = go_pages
        self.vcode = vcode
        self.lastused = lastused

class ses_AdminUser(Entity):
    KEYS=('sessionid', 'user',)
    FIELDS=('sessionid', 'user', 'authenticated', 'lastused')
    UNCHECKED_FIELDS = []

    def __init__(self, sessionid=None, user=None, lastused=None, authenticated=False):
        self.DATABASE = WEB_DATABASE
        self.DATABASE_CONNECTION = WEB_DATABASE_CONNECTION
        self.DATABASE_CURSOR = WEB_DATABASE_CURSOR

        self.sessionid = sessionid
        self.user = user
        self.authenticated = authenticated
        self.lastused = lastused

class ses_User(Entity):
    KEYS=('sessionid', 'host', 'user')
    FIELDS=('sessionid', 'host', 'user', 'authenticated', 'lastused')
    UNCHECKED_FIELDS = []

    def __init__(self, sessionid=None, host=None, user=None, lastused=None, authenticated=False):
        self.DATABASE = WEB_DATABASE
        self.DATABASE_CONNECTION = WEB_DATABASE_CONNECTION
        self.DATABASE_CURSOR = WEB_DATABASE_CURSOR

        self.sessionid = sessionid
        self.host = host
        self.user = user
        self.authenticated = authenticated
        self.lastused = lastused

class ses_MenuFile(Entity):
    KEYS=('sessionid',)
    FIELDS=('sessionid', 'host', 'user', 'name', 'kastagent_port', 'kastagent_shasecid', 'kastagent_pid', 'kastagent_ssh_pid', 'lastused')
    UNCHECKED_FIELDS = []

    def __init__(self, sessionid=None, host=None, user=None, name=None, kastagent_port=None, kastagent_shasecid=None, kastagent_pid=None, kastagent_ssh_pid=None, lastused=None):
        self.DATABASE = WEB_DATABASE
        self.DATABASE_CONNECTION = WEB_DATABASE_CONNECTION
        self.DATABASE_CURSOR = WEB_DATABASE_CURSOR

        self.sessionid = sessionid
        self.host = host
        self.user = user
        self.name = name
        self.kastagent_port = kastagent_port
        self.kastagent_shasecid = kastagent_shasecid
        self.kastagent_pid = kastagent_pid
        self.kastagent_ssh_pid = kastagent_ssh_pid
        self.lastused = lastused