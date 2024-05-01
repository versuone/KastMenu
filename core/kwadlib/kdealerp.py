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




from multiprocessing.managers import BaseManager
from queue import Queue
from threading import Thread
import random
random.seed()
import time

QUEUE_MAX=20000
IS_ALIVE=True
MENU_INSTANCES={}
TS_MAXIMUM_INACTIVITY=3600
TS_LAUNCHED=time.time()
TS_LAST_USED=time.time()
SECID=None
# SLICE_IS_ALIVE=180
SLICE_IS_ALIVE=10
KDEALER_TEMP_DIR=None
KDEALER_CALLER = None


class MManager(BaseManager):pass

class Maintainer(Thread):
    
    def run(self):
        cde_check_apimenu = 'ps -elf | grep {PPID} | grep -v grep'
        from sys import platform
        from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE

        while IS_ALIVE:
            time.sleep(SLICE_IS_ALIVE)
            if time.time() - TS_LAST_USED > TS_MAXIMUM_INACTIVITY: break
            cde_check_apimenu = cde_check_apimenu.replace('{PPID}', str(KDEALER_CALLER))

            # is_linux: If no more caller process user Terminate.
            if KDEALER_CALLER!=None and platform!='win32':
                #1:
                p = Popen(cde_check_apimenu, shell=True, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT)
                output, errmsg = p.communicate()
                ret = p.wait()
                if p.returncode != 0 and len(output) == 0:break

        print('... Kwad/KDealer: unlaunching after:' + str(time.time() - TS_LAST_USED) + ' seconds of inactivity.')

        import os
        terminate(os.getpid())
        
def terminate(pid):
    import os
    try:import ctypes
    except:ctypes=None 
        
    import sys
    if sys.platform!='win32':
        from signal import SIGTERM
        os.kill(int(pid), SIGTERM)
    else:
        handle = ctypes.windll.kernel32.OpenProcess(1, False, int(pid))
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)

class QMQueue(Queue):

    def __init__(self, *args, **keywords):
        global TS_LAST_USED    
        TS_LAST_USED=time.time()
    
        Queue.__init__(self, *args, **keywords)
    
    def put(self, *args, **keywords):
        global TS_LAST_USED    
        TS_LAST_USED=time.time()

        Queue.put(self, *args, **keywords)
            
    def get(self, *args, **keywords):
        global TS_LAST_USED    
        TS_LAST_USED=time.time()

        return Queue.get(self, *args, **keywords)

def newApiMenuInstance():
    global TS_LAST_USED
    TS_LAST_USED=time.time()
    
    api_menu_instance=genUid()
    MENU_INSTANCES[api_menu_instance]={}
    MENU_INSTANCES[api_menu_instance]['aconfigs']={}
    MENU_INSTANCES[api_menu_instance]['queue_input']=QMQueue(QUEUE_MAX)
    MENU_INSTANCES[api_menu_instance]['queue_output']=QMQueue(QUEUE_MAX)
    MENU_INSTANCES[api_menu_instance]['queue_command_output']=QMQueue(QUEUE_MAX)

    return api_menu_instance

def getConfig(api_menu_instance=None):
    if api_menu_instance not in MENU_INSTANCES:raise Exception('Kdealer: Menu Instance entry:' + str(api_menu_instance )+ ' not found in internal Table !')
    global TS_LAST_USED
    TS_LAST_USED=time.time()
    
    return dict(MENU_INSTANCES[api_menu_instance]['aconfigs'])

def setConfig(api_menu_instance=None, roles=None, user=None, groups=None, is_listening=False, records=None, record_names=None, is_going=None, is_menu_going=None, is_batch=None, pause=0, noclear=False, do_record=False, do_record_for_log_only=False, log=False, log_output=False, log_file=None, debug=False, show_shortcut=False, kwad_instance=None, verbose=0):
    if api_menu_instance not in MENU_INSTANCES:raise Exception('Kdealer: Menu Instance entry:' + str(api_menu_instance )+ ' not found in internal Table !')
    global TS_LAST_USED    
    TS_LAST_USED=time.time()
    
    MENU_INSTANCES[api_menu_instance]['aconfigs']['roles']=roles
    MENU_INSTANCES[api_menu_instance]['aconfigs']['user']=user
    MENU_INSTANCES[api_menu_instance]['aconfigs']['groups']=groups
    MENU_INSTANCES[api_menu_instance]['aconfigs']['is_listening']=is_listening
    MENU_INSTANCES[api_menu_instance]['aconfigs']['records']=records
    MENU_INSTANCES[api_menu_instance]['aconfigs']['record_names']=record_names
    MENU_INSTANCES[api_menu_instance]['aconfigs']['is_going']=is_going
    MENU_INSTANCES[api_menu_instance]['aconfigs']['is_menu_going']=is_menu_going
    MENU_INSTANCES[api_menu_instance]['aconfigs']['is_batch']=is_batch
    MENU_INSTANCES[api_menu_instance]['aconfigs']['pause']=pause
    MENU_INSTANCES[api_menu_instance]['aconfigs']['noclear']=noclear
    MENU_INSTANCES[api_menu_instance]['aconfigs']['do_record']=do_record
    MENU_INSTANCES[api_menu_instance]['aconfigs']['do_record_for_log_only']=do_record_for_log_only
    MENU_INSTANCES[api_menu_instance]['aconfigs']['log']=log
    MENU_INSTANCES[api_menu_instance]['aconfigs']['log_file']=log_file
    MENU_INSTANCES[api_menu_instance]['aconfigs']['log_output']=log_output
    MENU_INSTANCES[api_menu_instance]['aconfigs']['debug'] = debug
    MENU_INSTANCES[api_menu_instance]['aconfigs']['show_shortcut'] = show_shortcut
    MENU_INSTANCES[api_menu_instance]['aconfigs']['kwad_instance'] = kwad_instance
    MENU_INSTANCES[api_menu_instance]['aconfigs']['verbose'] = verbose

def getQueueInput(api_menu_instance=None):
    global TS_LAST_USED    
    TS_LAST_USED=time.time()
    
    if api_menu_instance not in MENU_INSTANCES:raise Exception('Kdealer: Menu Instance entry:' + str(api_menu_instance )+ ' not found in internal Table !')
    return MENU_INSTANCES[api_menu_instance]['queue_input']

def getQueueOutput(api_menu_instance=None):
    global TS_LAST_USED    
    TS_LAST_USED=time.time()
    
    if api_menu_instance not in MENU_INSTANCES:raise Exception('Kdealer: Menu Instance entry:' + str(api_menu_instance )+ ' not found in internal Table !')
    return MENU_INSTANCES[api_menu_instance]['queue_output']

def getQueueCommandOutput(api_menu_instance=None):
    global TS_LAST_USED
    TS_LAST_USED=time.time()

    if api_menu_instance not in MENU_INSTANCES:raise Exception('Kdealer: Menu Instance entry:' + str(api_menu_instance )+ ' not found in internal Table !')
    return MENU_INSTANCES[api_menu_instance]['queue_command_output']

def genUid():
    """
    Generats a Unique Id.
    """
    import time

    id=str(int(time.time()*1000))
    rand=random.randint(1, 100000)
    return id + "%05i" % rand

def getKdealerCaller():
    return KDEALER_CALLER

def setKdealerCaller(ppid):
    global KDEALER_CALLER
    from kwadlib.security.crypting import sanitize_int
    sanitize_int(ppid)
    KDEALER_CALLER = ppid

def stop():
    global IS_ALIVE
    IS_ALIVE=False


                                                

def main(secid, port, queue_max, temp_dir, verbose):
    global QUEUE_MAX
    if queue_max!=None:QUEUE_MAX=queue_max
    global MMANAGER
    global SECID
    global KDEALER_TEMP_DIR
    KDEALER_TEMP_DIR=temp_dir
    global VERBOSE
    VERBOSE=verbose
    SECID=secid
    
    ## Start Kdealer
    MManager.register('get_config', callable=getConfig)
    MManager.register('new_api_menu_instance', callable=newApiMenuInstance)
    MManager.register('set_config', callable=setConfig)
    MManager.register('get_queue_input', callable=getQueueInput)
    MManager.register('get_queue_output', callable=getQueueOutput)
    MManager.register('get_queue_command_output', callable=getQueueCommandOutput)
    MManager.register('getKdealerCaller', callable=getKdealerCaller)
    MManager.register('setKdealerCaller', callable=setKdealerCaller)
    MManager.register('stop', callable=stop)

    m = MManager(address=('localhost', port), authkey=bytes(secid, 'utf-8'))
    
    s = m.get_server()
    
    
    Maintainer().start()

    print('... Kwad: kdealer is listening on host/port: localhost/' + str(port))
    
    s.serve_forever()
    # MMANAGER=m
    # m.start() do not support Global Variables (because threaded) !!!
