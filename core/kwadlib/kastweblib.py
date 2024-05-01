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


WEB_OUTPUTS = None
from . import kastmenuxception


def serialize(value):
    from . import ct
    return ct.unDress(value)

def printweb(line=None, noln=False, nospace=False, shared_queueWebOutput=None):
    selfMethod='printweb'
    if shared_queueWebOutput == None:raise kastmenuxception.kastmenuSystemException('Main', selfMethod, 'printweb is on not supported in console context !')
    line = serialize(line)

    return shared_queueWebOutput.put(line, False)

class WebMenu(list):

    def __init__(self, history, menuindex):
        list.__init__(self)
        self.__history = history
        self.__menuindex = menuindex

    def getMenu(self): return self.__history.getMenu(self.__menuindex)

    def getMenuId(self): return self.__history.getMenu(self.__menuindex)['contents']['mid']

    def addItem(self, itemindex):
        self.append(itemindex)


class WebHistory(dict):

    def __init__(self):
        dict.__init__(self)
        self.messages = []
        self.__orders = []

    def addMenu(self, menuindex):
        mid = self.messages[menuindex]['contents']['mid']
        self.__orders.append(mid)
        self[mid] = WebMenu(self, menuindex)

    def getLastWebMenu(self):
        return self[self.__orders[-1]]

    def getMenu(self, menuindex):
        return self.messages[menuindex]


class WebFacade:
    """
A typical Menu message :
------------------------
{
'type': menu # menu, input_field, command_result or dialog,
'raise': None
'contents'={
    'mid' MID,
    'big_title': {
        'title': title,
        'host': host,
        'menu_path': menu_path
    },
    'choices': {
        'exit_car': None,
        'up_car': None,
        'down_car': None,
        'check_all_car': None
    },
    'is_locked': False,
    'sub_type': 'Menu',
    'title': title,
    'sub_titles': sub_titles,
    'items': [{
        'oid' OID,
        'type': classtype,
        'index':child_index,
        'label': name,
        'value': value,
        'help': help,
        'frColor': frColor,
        'bgColor': bgColor,
        'olegend': None
    }]
}

A typical Raw message :
----------------------------
{
'type': 'input_field'
'raise': None
'contents':{
    'raws': [],
    'outputs': None,
    'return_code': None
}

{
'type': 'command_result'
'raise': None
'contents':{
    'raws': [],
    'outputs': None,
    'return_code': None
}

A typical Dialog message :
----------------------------
{
'type': 'dialog',
'raise': None
'contents':{
    'is_choice': True,
    'is_to_confirm': False,
    'is_value': False,
    'confirm_ok': 'y',
    'confirm_ko': 'n',
    'id': MID,
    'message': 'mymessage'
}
    """

    MENU_RESPONSE_TIMEOUT = 2

    def __init__(self, port=None, secid=None, queue_input=None, queue_output=None, queue_command_output=None, config=None):
        selfMethod = '__init__'
        self.__secid = secid
        self.__port = port
        self.__queue_input = queue_input
        self.__queue_output = queue_output
        self.__queue_command_output = queue_command_output
        self.__webHistory = WebHistory()
        self.__config = config
        self.__isAlive = True

    def getPort(self):
        return self.__port
    def getTempDir(self):
        return self.__config.getTempDir()

    def getShaSecid(self):
        from kwadlib.security.crypting import sha256
        return sha256(self.__secid)

    def put(self, entry):
        selfMethod = 'put'
        self.__queue_input.put(entry)

    def puts(self, entry):
        """
        puts for put stream.
        """
        selfMethod = 'put'

        packets = entry.split('.')
        for packet in packets:
            self.__queue_input.put(packet, False)

        web_outputs = dict(WEB_OUTPUTS)
        web_outputs['type'] = 'raise'
        web_outputs['contents'] = {'type': 'APIMENU_END_RUNNING_PUTS'}
        self.__queue_output.put(serialize(web_outputs))

    def get(self, nowait=True, smartwait=False, lock=False, last_messageid=None):
        selfMethod = 'get'
        from queue import Empty
        if not isinstance(nowait, bool): raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'nowait', 'bool', str(nowait))
        if not isinstance(lock, bool): raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'lock', 'bool', str(lock))
        if not isinstance(smartwait, bool): raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'smartwait', 'bool', str(smartwait))
        if last_messageid != None and not isinstance(last_messageid, int): raise kastmenuxception.kastmenuParameterTypeException(self.__class__.__name__, selfMethod, 'last_messageid', 'int', str(last_messageid))
        if (nowait and (lock, smartwait) != (False, False)) or \
                (lock and (nowait, smartwait) != (False, False)) or \
                (smartwait and (nowait, lock) != (False, False)): raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Parameter Error: When one of nowait, lock, smartwait is True the others must be false ! Your values:' + str({'nowait': nowait, 'lock': lock, 'smartwait': smartwait})[1:-1] + '.')

        web_outputs = []
        message = None
        if last_messageid != None: web_outputs.extend(self.__webHistory.messages[last_messageid:])

        if nowait or smartwait:
            while True:
                try:
                    message = self._get_(self.__queue_output.get(False))
                    web_outputs.append(message)
                except Empty:
                    break

        if smartwait:
            wait = WebFacade.MENU_RESPONSE_TIMEOUT
            if message != None:
                if 'type' in message[-1] and message[-1]['type'] == 'raise':
                    if message[-1]['contents']['type'] == 'APIMENU_STUKE_ON_READING': wait = None
                    if message[-1]['contents']['type'] == 'APIMENU_NEXT_GET_MAY_BE_LONG': wait = WebFacade.MENU_RESPONSE_TIMEOUT * 3

            if wait != None:
                try:
                    web_outputs.append(self._get_(self.__queue_output.get(True, wait)))
                except Empty:
                    pass
                else:
                    while True:
                        try:
                            web_outputs.append(self._get_(self.__queue_output.get(True, wait)))
                        except Empty:
                            break

        elif lock:
            web_outputs = self._get_(self.__queue_output.get(True))

        return web_outputs

    def _get_(self, message):
        selfMethod = '_get_'
        """
        'menu': True, 
        'dialog': False, 
        'output': False, 
        'raise': None
        """
        from . import ct

        message = ct.dress(message.strip())
        self.__webHistory.messages.append(message)
        index = len(self.__webHistory.messages) - 1

        if message['type'] == 'menu':
            webMenu = self.__webHistory.addMenu(index)
        else:
            webMenu = self.__webHistory.getLastWebMenu()
            if message['type'] == 'dialog' and message['contents']['is_choice'] and 'mid' in message['contents'] and message['contents']['mid'] != webMenu.getMenuId():
                raise kastmenuxception.kastmenuSystemException(self.__class__.__name__, selfMethod, 'Retreived Dialog "Choice" with id:' + message['contents']['id'] + 'do not match current active Menu mid:' + webMenu.getId() + ' !')
            webMenu.addItem(index)

        return [index, message]

    def getCommandOutput(self):
        return self.__queue_command_output.get(True)

    def suicide(self):
        self.__queue_input.put('suicide')

    def isAlive(self):
        if self.__isAlive and not self.__config.isAlive():
            self.__config.stop()
            self.__isAlive = False

        return self.__isAlive

    def stop(self):
        self.__config.stop()
        self.__isAlive = False

    def getSecid(self):
        return self.__config.getSecid()

