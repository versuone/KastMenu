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


# 001: Python 2 to 3 conversion no more long.

""" 
Maybe sometimes like me, you wondered how to enter complexes Python types, 
straight from the command line.
   
CoolTyping comes for this purpose
of dealing with basics and comlexes types typed from a command line or a string.

CoolTyping can be compared to a lite serialisation mechanism,
working in two directions :
    _ from a string representation to a Python representation.
    _ from a Python representation to a string representation.
    
CoolTyping is heavily used in AskApy, everywhere datas coming
from the user are expected.
It is an intuitive way for users to type datas and
it is an practical serialazeable form for AskApy.

CoolTyping can be find :
    _ In the kind of parameters expected by the command ask.py.
    _ In the way View input fields are transmitted to the server.
    _ In the way to defined attribute in xmlMaker and attrMaker descriptor
    files.


example
-------

    From a Python representation to a string representation :

        The Python representation of a list is :
            ['this', 'is', 'a', 'list']
            
        The CoolTyped representation of the list is :
            '[this,is,a,list]'
            
        CoolTyping get rid of accessories,
        that is the reason why the method (or function) of this operation is called unDress.
        The complete example is :

        >>> from kwadlib.tools import CoolTyping as ct #this line won't be repeated in the next examples
        >>> l=['this', 'is', 'a', 'list']
        >>> print ct.unDress(l)
        [this,is,a,list]


    From a string representation to a Python representation.    

        >>> print ct.dress('[this,is,a,list]')
        ['this', 'is', 'a', 'list']
    
    
    Spaces are significative CoolTyping supports spaces in the both directions
    
        >>> l=[' this ','  is  ' ,'a','    list    ']
        >>> ct.unDress(l)
        '[ this ,  is  ,a,    list    ]'
        >>> s=ct.unDress(l)
        >>> ct.dress(s)
        [' this ', '  is  ', 'a', '    list    ']
        >>> ct.dress(s)==l
        True
        >>>


CoolTyping supported types are :
    str, int, float, bool, tuple, list, dict, date (*), ts (*)


str CoolTyping
==============
'this is a string'  --> 'this is a string'
                    <--
No change


bool CoolTyping
===============
True    -->     'True'
        <--


tuple CoolTyping
================
('this', 'is', 'a', 'tuple')    -->     (this,is,a,tuple)
                                <--


list CoolTyping
===============
['this', 'is', 'a', 'list']     -->     [this,is,a,list]
                                <--


dict CoolTyping
===============
{'kind':'dog', 'fly':False, 'color':'brown', 'number':2}
<--
-->
{fly:False,color:brown,kind:dog,number:2}



CoolTyping is recursive :

['this', 'is', 'a', 'list with a dict', {'kind':'dog', 'fly':False, 'color':'brown', 'number':2}]
<--
-->
[this,is,a,list with a dict,{fly:False,color:brown,kind:dog,number:2}]


CoolTyping works with wk
    For more information see the docstring of the wk class,
    or from a command line type: doc.py apy.tools.wk.
    or  if you have added <INSTALL_DIRECTORY>/askapy/lib in your PYTHONPATH variable, from a python interpreter type:
        from kwadlib import tools
        help(tools.wk)


* : futures versions.

WARNING:
========
Since Python 2.6 integer expressions starting with 0 are interpreted as octal,
octal greater than 07 mean nothing and eval will fail:
Try this into python interpreter:
eval('08')
So do not pass CoolTyped expression with integer with a leading 0 !
-
"""
# 001 : P.G.P. : Negative int Management.
# 002 : Bug correction

from . import ctexception



#-----------------#
#  Protected eval #
#-----------------#

def _eval(value, locals=None):
    ALLOWED_TYPES=('None', 'False', 'True', 'str', 'int', 'float', 'bool', 'tuple', 'list', 'dict')
    gbs={}

    try:
        for typ in ALLOWED_TYPES:gbs[typ]=__builtins__[typ]

        gbs={"__builtins__": gbs}  
            
        if locals!=None:gbs.update(locals)

        res=eval(value, gbs)

    except:
        raise
        import sys
        raise ctexception.ctSystemException('Echec trying to evaluate:' + str(value) + '. SubException:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]), fromClass='Main', fromMethod="_eval")     
    return res



#--------------#
#  CoolTyping  #
#--------------#
    
ESCAPE_CAR ='~'
import re
RE_QUOTE = re.compile(r'([^:^,^\{^\}^\(^\)^\[^\]]+)')
RE_TRUE = re.compile(r'"(True)"')
RE_FALSE = re.compile(r'"(False)"')
RE_NONE = re.compile(r'"(None)"')
RE_NUMERIC = re.compile(r'"([-]*[0-9]+\.{0,1}[0-9]*)"')

RE_BRACES = re.compile(r'([:,\{\}\(\)\[\]])')
RE_PIPE = re.compile(r'\'|"')
RE_COMMA = re.compile("([:,]+)\s")

def dress(st):
    selfMethod='dress'
    # M002:
    st = ''.join(st.split('\n'))
    st = st.replace(', ', ',').replace('{ ', '{').replace(',}', '}').replace(' }', '}').replace('[ ', '[').replace(',]', ']').replace(' ]', ']')
    if not isinstance(st, str) :raise ctexception.ctParameterTypeException('st', 'str', str(st), fromClass='CoolTyping', fromMethod=selfMethod)
                    
    """
    {attr1:value1,attr2:value2,attr3:value3,attr4:(value1,value2,value3,value4,value5),attr5:value5,attr6:value6}
    """      
    
    st=st.strip()


    ## 1    treat escape caracter forward
    dl=backSlach(st, ((',', '&eacute_virg'), (':', '&eacute_dble'), ('(', '&eacute_left1'), (')', '&eacute_right1'), ('[', '&eacute_left2'), (']', '&eacute_right2'), ('{', '&eacute_left3'), ('}', '&eacute_right3')))
    
    ## 2    stick "" everywhere 
    dl=RE_QUOTE.sub(r'"\1"', dl)
    
    ## 3    treat escape caracter backward
    dl=unBackSlach(dl, ((',', '&eacute_virg'), (':', '&eacute_dble'), ('(', '&eacute_left1'), (')', '&eacute_right1'), ('[', '&eacute_left2'), (']', '&eacute_right2'), ('{', '&eacute_left3'), ('}', '&eacute_right3')))
    
    ## 3    get rid of "" for: True/False, None, Numeric
    ## True/False
    dl=RE_TRUE.sub(r"\1", dl)
    dl=RE_FALSE.sub(r"\1", dl)
    ## None
    dl=RE_NONE.sub(r"\1", dl)
    ## Numeric
    # D001:dl=re.sub(r'"([0-9]+\.{0,1}[0-9]*)"', r"\1", dl)
    # A001
    dl=RE_NUMERIC.sub(r"\1", dl)
    dl=_eval(dl)
    
    return dl

def unDress(dl):
    selfMethod='unDress'
    ALLOWED_TYPES=(tuple, list, dict)

    if not isinstance(dl, tuple) and not isinstance(dl, list) and not isinstance(dl, dict):return str(dl)

    ## protect caller
    if isinstance(dl, dict):dl=dict(dl)
    if isinstance(dl, tuple):dl=tuple(dl)
    if isinstance(dl, list):dl=list(dl)
    
    ##  treat escape caracter
    ### dl is tuple or list
    if isinstance(dl, tuple) or isinstance(dl, list):
        if isinstance(dl, tuple):_dl=list(dl)
        else:_dl=dl
        for i in range(len(_dl)):
            if isinstance(_dl[i], str):
                import re                    
                r="r'" + ESCAPE_CAR  + "\\1'"
                #test ok:#_dl[i]=re.sub(r'([:,\{\}\(\)\[\]])', r'~\1', _dl[i])
                _dl[i]=RE_BRACES.sub(_eval(r), _dl[i])
            else:_dl[i]=unDress(_dl[i])
        if isinstance(dl, tuple):dl=tuple(_dl)
        
    ### dl is dict
    ##test:d={thread:$Thread,format:(%(asctime)s,%(levelname)s,%(process)d,%(message)s)}
    else:
        for key in list(dl.keys()):
            if isinstance(dl[key], str):
                if dl[key]=='' or dl[key]==len(dl[key])*' ':
                    dl[key]=None
                    continue

                import re
                r="r'" + ESCAPE_CAR  + "\\1'"
                #test ok:dl[key]=re.sub(r'([:,\{\}\(\)\[\]])', r'~\1', dl[key])
                dl[key]=RE_BRACES.sub(_eval(r), dl[key])
                                    
            else:dl[key]=unDress(dl[key])
    st=str(dl)        

    import re 
    st=RE_PIPE.sub(r"", st)

    ## treat spaces arround escape caracter
    ## test ok:dl={"a b  c    d  fg":'x yz', 'b':23}
    st=RE_COMMA.sub(r"\1", st)
    return st
        
def backSlach(st, lst):
    for tp in lst:
        source, target = tp
        source=ESCAPE_CAR + source              
        st=st.replace(source, target)
    return st                
        
def unBackSlach(st, lst):
    for tp in lst:
        source, target = tp            
        st=st.replace(target, source)
    return st