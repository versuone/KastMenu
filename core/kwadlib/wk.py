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



# 001 # P.G.P. # 20150513 # Support of  wkExtension
# 002: Python 2 to 3 conversion: no more long
# 003: Allow SoftClass attribute output reference




"""
---------------------------------------------------
| I) WantedKeyword (wk) Python Type Checking tool |
---------------------------------------------------


1> INTRODUCTION

What is it ?
------------
wk allows to check a collection of fields, against their characteristics, defined into a wk expressions.

A wk expression (or wk definition) is a dictionary, where each key defines a specific control to operate on the field.

e.g.1:
age = {'*type':int}

wk Will check the field named: age using the control: *type defined into the wk definition: {'*type':int}.

{'*type':int}: means that age must be an integer otherwise an exception is raised.

e.g.2:
vegan = {'*type': bool}
Means that the field vegan must be a bool.


Running checks:
---------------
Checks can be performed in two ways.

a) Using the check method of the wk module:

name = 'john'
age=45
import wk
p=wk.WKS()
p.name={'*type':'str'}
p.age={'*type':'int', '*value':30}
wk.check (wks=p, kws={'name':name, 'age':age})
>>> p.name
'john'
>>> p.age
45

This can be comfortably embedded into a function or method:
def hello(name, age):
    import wk
    p=wk.WKS()
    p.name={'*type':'str'}
    p.age={'*type':'int', '*value':30}
    wk.check (wks=p, kws={'name':name, 'age':age})

    print('Function hello! name: %s, age: %s' % (p.name, p.age))

>>> hello('john', None)
Function hello! name: john, age: 30


b) Using the cp annotation of the wk module:

from wk import cp
@cp({'*type': 'str'}, {'*type':'int', '*value':30})
def hello(name, age):
    print('Function hello! name: %s, age: %s' % (name, age))

>>> hello('john')
Function hello! name: john, age: 30



2> USING THE CHECK FUNCTION


2.1> A simple function hello

import wk
def hello(*args, **keywords):
    p=wk.WKS()
    p.name={'*type':'str'}
    p.age={'*type':'int', '*value':30}
    wk.check (wks=p, kws=keywords )

    print ('function: hello !')
    print ('-----------------')
    print('name: %s' % p.name)
    print('age: %s' % p.age)
    print('parameters as dict: %s' % wk.getAsDict(p))

>>> hello(name='john', age=25)
function: hello !
-----------------
name: john
age: 25
parameters as dict: {'age': 25, 'name': 'john'}
>>>

- With default value: *value:

>>> hello(name='john')
function: hello !
-----------------
name: john
age: 30 # <-- Default value for age
parameters as dict: {'age': 30, 'name': 'john'}

Detail:
-------
Ligne 3: p=wk.WKS(): An WKS instance (wk.WKS is alias for wk.WantedKeyword) is created with no Parameter.
Ligne 4-5: p.name={'*type':'str'}: p.<attribute-name = <wk expression> : One declares wk expressions on the fly on the wk instance.
Ligne 6:wk.check (wks=p, kws=kws ): The wk module's function: check, runs on each Attribute of the wk.WKS instances: "name" and "age".
Regarding the wk expression defined for each one.
The values are retreives from the kws parameter.
The final values are stored on the attributes of the WKS instance (p).

a) wk.check retreives the user value for the attribute name, from kws['name'].
b) wk.check verifies this value on the wk expresion: {'*type':'str'}, defined for attribute name.
c) wk.check applies the final value to p.name


- More on extra Parameters:

If you run the following call, you'll see that no error is generated althought parameter pc is not defined.
>>> hello(name='john', age=25, pc='12345')
To reject extra parameter you must use the keyword: strict.


2.2> Same function but using strict

def hello(*args, **kws):
    p=wk.WKS()
    p.name={'*type':'str'}
    p.age={'*type':'int', '*value':30}
    wk.check (wks=p, kws=kws, strict=True )

    print('Function hello! parameters as dict: %s' % wk.getAsDict(p))

- Using the extra parameter: pc causes an error, because of strict=True:
>>> hello(name='john', age=25, pc='12345')
Traceback (most recent call last):
...
wkexception.wkSystemException: EWK: From class:wk, from method:getKeywords SubClass:None SubMethod:None On strick check:
Unsupported Attribute: pc !. Supported Attributes are: age, name. <==

As you can see into this excerpts from the previous exception: "SubClass:None SubMethod:None",
The calling class and method is not traced.
To trace them one should use class_exit and method_exit as follows.


2.3> Same function but using class_exit and method_exit

def hello(*args, **kws):
    p=wk.WKS()
    p.name={'*type':'str'}
    p.age={'*type':'int', '*value':30}
    wk.check (wks=p, kws=kws, strict=True, class_exit='Main', method_exit='hello')

    print('Function hello! parameters as dict: %s' % wk.getAsDict(p))

>>> hello(name='john', age=25, pc='12345')
Traceback (most recent call last):
...
wkexception.wkSystemException: EWK: From class:wk, from method:getKeywords SubClass:Main SubMethod:hello On strick check: <==
Unsupported Attribute: pc !. Supported Attributes are: age, name.
>>>


2.4> Same function with arguments instead of parameters:

def hello(name, age):
    p=wk.WKS()
    p.name={'*type':'str'}
    p.age={'*type':'int', '*value':30}
    wk.check (wks=p, kws={'name':name, 'age':age}, strict=True )

    print('Function hello! parameters as dict: %s' % wk.getAsDict(p))

>>> hello(name='john', age=25)
Function hello! parameters as dict: {'age': 25, 'name': 'john'}


3> USING THE CP ANNOTATION

cp (wk.cp is ans alias for wk.check_parameters) is an annotation that simplifies declaring wk expressions on Arguments and Parameters.

3.1> As Arguments:
------------------
from wk import cp
@cp({'*type': 'str'}, {'*type':'int', '*value':30}, strict=True)
def hello(name, age):
    print('Function hello! name: %s, age: %s' % (name, age))

>>> hello('john', 25)
Function hello! name: john, age: 25

- Calling with None:
>>> hello('john', None)
Function hello! name: john, age: 30

- hello with *args signature:
from wk import cp
@cp({'*type': 'str'}, {'*type':'int', '*value':30}, strict=True)
def hello(*args):
    print('Function hello! Arguments: %s' % str(args))

- This trigger an error because on strict=True:
>>> hello('john', 25, 'blabla')
wkexception.wkSystemException: EWK: From class:wk, from method:getKeywords SubClass:wkDecorator/args/str SubMethod:hello
On strict check: Unsupported Attribute: arg2 !. Supported Attributes are: arg0, arg1.


3.2> As parameters:
-------------------
from wk import cp
@cp(
    kws={
        'name': {'*type':'str'},
        'age': {'*type':'int', '*value':30},
    }, strict=True)
def hello(name=None, age=None):
    print('Function hello! name: %s, age: %s' % (name, age))

>>> hello(name='john')
Function hello! name: john, age: 30


- Mixed:
from wk import cp
@cp({'*type': 'str', '*value': 'john'}, {'*type': 'int', '*value': 30},
    kws={
        'pc': {'*reg': '^\d{5}([\-]?\d{4})?$'},
        'vegan': {'*type': 'bool', '*value': True}
    }, strict=True)
def hello(*args, pc=None, age=None, vegan=False):
    print('Function hello! arguments: %s, pc: %s, vegan: %s' % (str(args), pc, vegan))

>>> hello()
Function hello! arguments: ('john', 30), pc: None, vegan: True
>>> hello('mia', pc='12345-9876')
Function hello! arguments: ('mia', 30), pc: 12345-9876, vegan: True



-------------------------------
| II) wk Expressions in Depht |
-------------------------------


1> NO CHECK AT ALL:

a) No check with None:
import wk
p=wk.WKS()
p.any=None
wk.check (wks=p, kws={'any': 'hello'}, strict=True )
>>> p.any
'hello'

b) No check with default attribute:
import wk
p=wk.WKS()
p.any='hello'
wk.check (wks=p, kws={}, strict=True )
>>> p.any
'hello'



2> WORKING WITH WK BASE TYPES:


2.1> *type:

*type: checks the value (and default value) for the provided <type>.

Supported types are listed in: wk.SUPPORTED_TYPES:
    ('str', 'int', 'float', 'tuple', 'list', 'dict', 'bool', 'xml', 'color', 'wkDef', 'url')
Or
Any Python type: (a Python type is an obj for which this is True: isinstance(obj, type))
Or  A list of Python types.

Syntax: '*type': <type>
------

Note:
-----
- a) When <type> is a Python type (or a list of ...),  wk always perform isintance ans issubclass on it.
And will return an error only if both are false.
- b) <type> : can be provided as string: like in {'*type': 'int'},
or not: like in {'*type': int}
This is true only for Python standard base types: str, int, float, tuple, list, dict, bool.


Examples:
---------

a) with Base types:
import wk
p=wk.WKS()
p.age={'*type': int}
wk.check (wks=p, kws={'age': 5})
>>> p.age
5

p=wk.WKS()
p.vegan={'*type': bool}
wk.check (wks=p, kws={'vegan': False})
>>> p.vegan
False

b) with any Pyhon types:
import wk
class A:pass

class B(A, list):pass

p=wk.WKS()
p.obj={'*type': A}
wk.check ( wks=p, kws={'obj': A()} )
>>> p.obj
<__main__.A object at 0x00000000032BAD68>

p=wk.WKS()
p.obj={'*type': (A, list)}
wk.check ( wks=p, kws={'obj': B()} )
>>> p.obj
[]


2.2> *value:

*value: Provide a default value to a field.

Syntax: '*value': <any>
-------

import wk
p=wk.WKS()
p.name={'*value': 'john'}
wk.check ( wks=p, kws={'name': None} )
>>> p.name
'john'}


2.3> *required:

*required raises an exception if no value is provided for the field.

Syntax: '*required': True
------

import wk
p=wk.WKS()
p.name={'*required': True}
wk.check ( wks=p, kws={'name': None} )

wkexception.wkSystemException: EWK: From class:wk, from method:getKeywords SubClass:None SubMethod:None On *Required:Received no value
 for required key:name. Your wkDefinition: {'*required': True}



3> COMPARATORS:

3.1> *lt, *gt, *eq, *le, *ge, *ne:

All are unary comparators.
And compare anything that is comparable by the standard Python operators (<, >, ==, <=, >=, !=).

Syntaxe: '*lt': <value>
--------

Examples:
---------
import wk
p=wk.WKS()
p.item={'*lt': 'bbb'}
wk.check ( wks=p, kws={'item': 'aaa'} )
>>> p.item
'aaa'

import wk
p=wk.WKS()
p.index={'*lt': 4}
wk.check ( wks=p, kws={'index': 2} )
>>> p.index
2


3.2> *between:

*between is a binary comparator.

Syntaxe: '*between': <list/tuple>
--------

Examples:
---------
import wk
p=wk.WKS()
p.item={'*between': ('aaa', 'ccc')}
wk.check ( wks=p, kws={'item': 'bbb'} )
>>> p.item
'bbb'

import wk
p=wk.WKS()
p.item={'*between': ('aaa', 'ccc')}
wk.check ( wks=p, kws={'item': 'zbbb'} )

wkexception.wkSystemException: EWK: From class:wk, from method:__checkType SubClass:None SubMethod:None On *between:Received Bad
value for key:item  Value Expected: between ('aaa', 'ccc').  Value Received:zbbb. Your wkDefinition: {'*between': ('aaa', 'ccc')}

import wk
p=wk.WKS()
p.item={'*between': (1, 3)}
wk.check ( wks=p, kws={'item': 2} )
>>> p.item
2


4> DEEP INTO COMPLEXE TYPES DICT, LIST and TUPLE:

4.1> *ltype:

*ltype is an advanced form of {'*type': list} or {'*type': tuple}.
*ltype is only supported for {'*type': list} or {'*type': tuple}.
*ltype will describe the type of the list items by a new wk definition.

Syntax: '*type': list, '*ltype': <wk expression>
-------

Examples:
---------
import wk
p=wk.WKS()
p.cars={'*type': list, '*ltype': {'*type': int}}
wk.check( wks=p, kws={'cars': [1,2,3,4,5]} )
>>> p.cars
[1, 2, 3, 4, 5]

LIST with Colltyping e.g.:
--------------------------
p=wk.WKS()
p.cars={'*type': list, '*ltype': {'*type': int}, '*withCoolTyping': True}
wk.check( wks=p, kws={'cars': '[1,2,3,4,5]'} )
>>> p.cars
[1, 2, 3, 4, 5]


4.2> *dtype:

*dtype is an advanced form of {'*type': dict}.
*dtype is only supported for {'*type': dict}.
*dtype will describe each key of the expected dictionary with a new wk definition.

Syntax: '*type': dict, '*dtype': {'key1': <wk expression>, ['keyn': <wk expression>]}
-------

Examples:
---------
import wk
p=wk.WKS()
p.person={'*type': dict, '*dtype': {'name': {'*type': str}, 'age': {'*type':int}, 'vegan': {'*type': bool}}, '*required': True}
wk.check( wks=p, kws={'person': {'name': 'john', 'age': 30, 'vegan' : False} })
>>> p.person
{'age': 30, 'vegan': False, 'name': 'john'}


DICT with Colltyping e.g.:
--------------------------
p=wk.WKS()
p.person={'*type': dict, '*dtype': {'name': {'*type': str}, 'age': {'*type':int}, 'vegan': {'*type': bool}}, '*withCoolTyping': True}
wk.check( wks=p, kws={'person': '{name:john,age:30,vegan:False}' })
>>> p.person
{'age': 30, 'vegan': False, 'name': 'john'}


LIST OF DICT:
-------------
p=wk.WKS()
p.lperson={'*type': list, '*ltype':{
    '*dtype': {'name': {'*type': str}, 'age': {'*type':int}, 'vegan': {'*type': bool}}
}}
wk.check( wks=p, kws={'lperson': [
    {'name': 'john', 'age': 30, 'vegan' : False},
    {'name': 'jim', 'age': 40, 'vegan' : True},
    {'name': 'lee', 'age': 50, 'vegan' : False}
]})
>>> p.lperson
[{'age': 30, 'name': 'john', 'vegan': False}, {'age': 40, 'name': 'jim', 'vegan': True}, {'age': 50, 'name': 'lee', 'vegan': False}]
>>>


4.3/ *checkIn:

checkIn checks a value in a list (or tuple).

Syntax: '*checkIn': <tuple or list>
-------

p=wk.WKS()
p.color={'*type': str, '*checkIn': ('green', 'violet', 'red')}
wk.check( wks=p, kws={'color': 'violet'} )
>>> p.color
'violet'

p=wk.WKS()
p.any={'*type': int, '*checkIn': (False, 5, ('hello',))}
wk.check( wks=p, kws={'any': 5} )
>>> p.any
5


4.4> *checkXIn:

*checkXIn checks the presence of all elements of a list (or tuple) into another list (or tuple).
value must be a list ('*type': list or '*type': tuple).

Syntax: '*checkXIn': <tuple or list>
-------

Examples:
---------
p=wk.WKS()
p.colors={'*type': tuple, '*checkXIn': ('green', 'violet', 'red')}
wk.check( wks=p, kws={'colors': ('violet', 'green')} )
>>> p.colors
('violet', 'green')


5> CONVERTIONS:

Sometimes the input value for the field is not formatted like you want it.
And you migth want to apply a specific convertion to this value before to perform any control on it.
The following wk keys stands for this purpose.
Convertions are always performed first and Controls afterward.
Convertions are applyied on any value or default value (*value) for a field.


5.1> *force_str:

*force_str: force the convertion of an obj to a string.

Syntax: 'force_str': True
-------
Note: if value is a bytes, wk will try: value.decode('utf-8') on it.

Examples:
---------

a) An int to a string:
import wk
p=wk.WKS()
p.name={'*force_str': True, '*type': str} # While simple this fails: {'*type': str}
wk.check ( wks=p, kws={'name': 123 } )
>>> p.name
'123'

b) A byte to a string:
import wk
p=wk.WKS()
p.name={'*force_str': True, '*type': str}
wk.check ( wks=p, kws={'name': 'abc'.encode('utf-8') } )
>>> p.name
'abc'


5.2> *withEval:

Restricted evals:
*withEval is supported by a python eval handled par the _eval function of the ct.py mofdule.
The _eval function use a restricted eval is the sens that it uses no locals, globals no extra function or modules.
But a restricted "__builtins__" list of base types:
    ('None', 'False', 'True', 'str', 'int', 'float', 'bool', 'tuple', 'list', 'dict').
So any of these base type can be evaluated.

The field's value in input, must always be a String.

Syntax: '*withEval': True
-------

Examples:
---------
import wk
p=wk.WKS()
p.age={'*type': int, '*withEval': True}
wk.check (wks=p, kws={'age': '5'})
>>> p.age
5

p=wk.WKS()
p.age={'*type': float, '*withEval': True}
wk.check (wks=p, kws={'age': '5.0'})
>>> p.age
5.0

p=wk.WKS()
p.cars={'*type': tuple, '*withEval': True}
wk.check (wks=p, kws={'cars': '(1, 2, 3)'})
>>> p.cars
(1, 2, 3)

p=wk.WKS()
p.person={'*type': dict, '*withEval': True}
wk.check (wks=p, kws={
    'person': "{'name': 'john', 'age': 30, 'adress': '21 jump street', 'vegan': True}"
})
>>> p.person
{'name': 'john', 'age': 30, 'adress': '21 jump street', 'vegan': True}

And so on !

5.3> *withJson: The same as withEval but evaluate using json parser.

5.4> *withCoolTyping:

*withCoolTyping is a more advanced version of *withEval.
*withCoolTyping stands for convertion of string values with no: ' and no: " to any of the previous base types:
    ('None', 'False', 'True', 'str', 'int', 'float', 'bool', 'tuple', 'list', 'dict').
*withCoolTyping stands to be used in environment that mess with: ' and " like terminal, console, xml for example.

The field's value in input, must always be a String.

Syntax: '*withCoolTyping': True
-------

Examples:
---------
import wk
p=wk.WKS()
p.person={'*type': dict, '*withCoolTyping': True}
wk.check (wks=p, kws={
    'person': "{name:john,age:30,adress:21 jump street,vegan:True}" # Note that all not significative spaces must be wiped off !
})
>>> p.person
'name': 'john', 'age': 30, 'adress': '21 jump street', 'vegan': True}

p=wk.WKS()
p.story={'*type': tuple, '*withCoolTyping': True}
wk.check (wks=p, kws={
    'story': "(once,upon a time,in the east)"
})
>>> p.story
('once', 'upon a time', 'in the east')

And so on !


5.4> *withConvert:

*withConvert is to be used when none of the previous convertion method works.
*withConvert takes a user function in its description, and calls this function on any value or default value (*value) for the field.
The field's value in input, may be of any type.

Syntax: '*withConvert': <Python function(value)>
-------

Examples:
---------
p=wk.WKS()
p.age={'*type': int, '*withConvert': lambda e: int(e)}
wk.check (wks=p, kws={
    'age': "123"
})
>>> p.age
123

p=wk.WKS()
p.person={'*type': int, '*withConvert': lambda e: e == 'john'}
wk.check (wks=p, kws={
    'person': "john"
})
>>> p.person
True



6> REGULAR EXPRESSION:

*reg:
*reg will check any value (or the default value) on this regular expression.

Syntax: '*reg': '<regular_expression>'
-------

Examples:
---------
p=wk.WKS()
p.pc={'*reg': '^\d{5}([\-]?\d{4})?$'}
wk.check (wks=p, kws={'pc': "12345-9876"})
>>> p.pc
"12345-9876"

p=wk.WKS()
p.pc={'*reg': '^wel.+'}
wk.check (wks=p, kws={'pc': "wel"})

wkexception.wkSystemException: EWK: From class:wk, from method:__checkType SubClass:None SubMethod:None On *reg:Received Bad  value fo
r key:pc  Value Expected: reg:dct['*reg'].  Value Received:wel, type:<class 'str'>. Your wkDefinition: {'*reg': '^wel.+'}

p=wk.WKS()
p.pc={'*reg': '^wel.+'}
wk.check (wks=p, kws={'pc': "welcome"})
>>> p.pc
'welcome'



7> DATE AND TIMESTAMP:

7.1> *date:

*date expects a Standard Python strptime/strftime string format  (actually based on the C standard (1989 version)).
See for instance the grid from chapter: "8.1.8. strftime() and strptime() Behavior" at
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

Syntax:
-------
Either you use '*date': <strptime string> and your date entry should match the exact pattern.
or {'*date': None} and your date entry may be:
    - a String supported date literal
    - or an instance of datetime.date.


Examples :
----------
a) With a strptime string:

import wk
p=wk.WKS()
p.birthday = {'*date': '%d/%m/%Y'}
wk.check( wks=p, kws={'birthday': '01/11/2016'})
>>> p.birthday
datetime.datetime(2016, 11, 1)

- In fact wk do this in background:
>>> datetime.date(*time.strptime("01/11/2016", "%d/%m/%Y")[0:3])
datetime.date(2016, 11, 1)

Or:

p = wk.WKS()
p.birthday = {'*date': '%d %b %Y'}
wk.check(p, {'birthday': '29 Aug 2017'})
>>> p.birthday
datetime.date(2017, 8, 29)


b) With None

Value is a datetime:
import datetime
p = wk.WKS()
p.birthday = {'*date': None}
wk.check(p, {'birthday': datetime.date(2016, 11, 1)})
>>> p.birthday
datetime.date(2016, 11, 1)

Value a Supported date literal:
p = wk.WKS()
p.birthday  = {'*date': None}
wk.check(p, {'birthday': 'Tue Jun 16 20:18:03 1981'})
>>> p.birthday
datetime.date(1981, 6, 16)


DATE With Colltyping e.g.:
--------------------------
import wk
p=wk.WKS()
p.person={'*type': dict, '*dtype': {'name': {'*type': str}, 'age': {'*type':int}, 'birthdate': {'*date': '%d/%m/%Y'}}, '*withCoolTyping': True}
wk.check( wks=p, kws={'person': '{name:john,age:30,birthdate:01/11/2016}' }, strict=True )
>>> p.person
{'age': 30, 'birthdate': datetime.datetime(2016, 11, 1), 'name': 'john'}


7.2> *ts:

*ts expects a Standard Python strptime/strftime string format  (actually based on the C standard (1989 version)).
See for instance the grid from chapter: "8.1.8. strftime() and strptime() Behavior" at
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

Syntax:
-------
Either you use '*ts': <strptime string> and your date entry should match the exact pattern.
or {'*ts': None} and your date entry may be:
    - a String supported date literal
    - or an instance of datetime.date.

Examples :
----------
a) With a strptime string:
import wk
p=wk.WKS()
p.birthdate = {'*ts': '%d/%m/%Y %Hh%Mmn%Ss'}
wk.check( wks=p, kws={'birthdate': '01/11/2016 16h40mn3s'})
>>> p.birthdate
datetime.datetime(2016, 11, 1, 16, 40, 3)

- In fact wk do this in background:
>>> datetime.datetime(*time.strptime("01/11/2016 16h40mn3s", "%d/%m/%Y %Hh%Mmn%Ss")[0:6])
datetime.datetime(2016, 11, 1, 16, 40, 3))

Or:
p = wk.WKS()
p.birthdate = {'*ts': '%d %b %Y:%H:%M:%S'}
wk.check(p, {'birthdate': '29 Aug 2017:02:00:46'})
>>> p.birthdate
datetime.datetime(2017, 8, 29, 2, 0, 46)


b) With None

Value is a datetime:
import datetime
p = wk.WKS()
p.birthdate = {'*ts': None}
wk.check(p, {'birthdate': datetime.datetime(2016, 11, 1, 16, 40, 3)})
>>> p.birthdate
datetime.datetime(2016, 11, 1, 16, 40, 3)


Value a Supported datetime literal:
p = wk.WKS()
p.birthdate  = {'*ts': None}
wk.check(p, {'birthdate': 'Tue Jun 16 20:18:03 1981'})
>>> p.birthdate
datetime.datetime(1981, 6, 16, 20, 18, 3)


TS With Colltyping e.g.:
-------------------------
import wk
p=wk.WKS()
p.person={'*type': dict, '*dtype': {'name': {'*type': str}, 'age': {'*type':int}, 'birthday': {'*ts': '%d/%m/%Y %Hh%Mmn%Ss'}}, '*withCoolTyping': True}
wk.check( wks=p, kws={'person': '{name:john,age:30,birthday:01/11/2016 16h40mn3s}' }, strict=True )
>>> p.person
{'age': 30, 'birthday': datetime.datetime(2016, 11, 1, 16, 40, 3), 'name': 'john'}



8> MISCELLANEOUS:

8.1> *len:

Syntax: '*len': <int>
-------

Examples :
----------
import wk
p=wk.WKS()
p.size={'*len': 3}
wk.check( wks=p, kws={'size': 'abc'} ) # Will check len('abc') == 3
>>> p.size
'abc'

8.2> *minLen, *maxLen:

Syntax: '*minLen': <int>
-------

Examples :
----------
import wk
p=wk.WKS()
p.size={'*minLen': 3}
wk.check( wks=p, kws={'size': 'abcefg'} ) # Will check len('abc') >= 3
>>> p.size
'abcefg'


8.3> *startsWith, *endsWith:

Syntax: '*startsWith': <value>
-------

Examples :
----------
import wk
p=wk.WKS()
p.story={'*startsWith': 'once upon'}
wk.check( wks=p, kws={'story': 'once upon a time'} )
>>> p.story
'once upon a time'



9> WKDEF ITSELF:

wkDef: check that value is a wk expression.

Syntax: '*type': '*wkDef'
-------

Examples :
----------

a) Example with the previous one for *startsWith.

import wk
p=wk.WKS()
p.wkexp={'*type': 'wkDef'}
wk.check( wks=p, kws={'wkexp':
    {'*startsWith': 'once upon'}
}, strict=True )
>>> p.wkexp
{'*startsWith': 'once upon'}


b) Exemple with this wk expression from the *dict example:
p.person={'*type': dict, '*dtype': {'name': {'*type': str}, 'age': {'*type':int}, 'vegan': {'*type': bool}}}

import wk
p=wk.WKS()
p.wkexp={'*type': 'wkDef', '*withCoolTyping': True}
wk.check( wks=p, kws={'wkexp':
    {'*type': dict, '*dtype': {'name': {'*type': str}, 'age': {'*type':int}, 'vegan': {'*type': bool}}} # The CoolTyped expression.
}, strict=True )
p.wkexp
{'*type': <class 'dict'>, '*dtype': {'name': {'*type': <class 'str'>}, 'age': {'*type': <class 'int'>}, 'vegan': {'*type': <class 'boo
l'>}}}



10> NOTATION KEYS:

Here are 3 notation key with no associated function at all,
may be used outside wk for any programme purpose.
*label, *help, *lhelp, *ksearch, *shortcut, *roles, *rolesAutzDft, *rolesAutz, *password, *password_file_option
"""


from . import wkexception
import time, datetime
from . import ct
import warnings

DATE_HELP = """
Date example:
-------------
Either you use 	{'*date': <strptime string>} and your date entry should match your pattern.
or {'*date': None} and your date entry may be any supported Date literal.

Ex1:
mydate = '01/11/2016'
p = wk.WantedKeywords()
p.mydate = {'*date': '%d/%m/%Y'}
wk.getKeywords(wantedKeywords=p, keywords={'mydate': mydate})

- Do this in background:
>>> p.mydate = datetime.date(*time.strptime("01/11/2016", "%d/%m/%Y")[0:3])
datetime.date(2016, 11, 1)

Ex2:
mydate = 'Tue Jun 16 20:18:03 1981'
p = wk.WantedKeywords()
p.mydate = {'*date': None}
wk.getKeywords(wantedKeywords=p, keywords={'mydate': mydate})

- Do this in background:
>>> datetime.date(*time.strptime('Tue Jun 16 20:18:03 1981')[0:3])
datetime.date(1981, 6, 16)
"""

TS_HELP = """
TS example:
-----------
Either you use 	{'*ts': <strptime string>} and your ts entry should match your pattern.
or				{'*ts': None} and you ts entry may be any supported Time Stamp literal.
Ex1:
myts = '01/11/2016 16h40mn3s'
p = wk.WantedKeywords() # <=> wk.WKS()
p.myts = {'*ts': '%d/%m/%Y %Hh%Mmn%Ss'}
wk.getKeywords(wantedKeywords=p, keywords={'myts': myts}) # <=> wk.check(p, {'myts': myts})

- Does this in background:
>>> p.myts = datetime.datetime(*time.strptime('01/11/2016 16h40mn3s', '%d/%m/%Y %Hh%Mmn%Ss')[0:6])
datetime.datetime(2016, 11, 1, 16, 40, 3)

Ex2:
myts = 'Tue Jun 16 20:18:03 1981'
p = wk.WantedKeywords()
p.myts = {'*date': None}
wk.getKeywords(wantedKeywords=p, keywords={'myts': myts})

- Do this in background:
>>> datetime.datetime(*time.strptime('Tue Jun 16 20:18:03 1981')[0:6])
datetime.datetime(1981, 6, 16, 20, 18, 3)
"""

KSEARCH_FORMAT = """
- Type Command:
Syntax:
*ksearch': {\
    'type': <type>,\
    'parms': <parms>,\ 
    'command': <command>,\ 
    'resultKey': <resultKey>\
}
Example:
*ksearch': {\
    'type': 'command',\
    'parms': {'parm1': 'value1', 'parm2': 'value2'},\ 
    'command': 'mycommand $attr1$ $attr2$ $parm1$ $parm2$',\ 
    'resultKey': 'tag0/tag1/tag2'\
}
- Type OptStruct:
Syntax:
*ksearch': {\
    'type': <type>,\
    'section': <section>,\
    'operation': <operation>,\
    'bsl':  <bsl>,\
    'appinst': <appinst>,\
    'resultKey': <resultKey>\
    'okey': <okey>,\
    'okeys': <okeys>,\
    'oattrs': <oattrs>\
}
Example:
*ksearch': {\
    'type': 'optstruct',\
    'section': 'Machine',\
    'operation': 'read',\
    'bsl':  'middleware§kwad.Machine',\
    'appinst': 'kcontrol',\
    'resultKey': 'Machine/operations/read/Machine'\
    'okey': 'machine',\
    'okeys': ('machine', 'name', 'title'),\
    'oattrs': ('machine', 'name', 'title', 'description'),\
}

*ksearch is a notation to search for a field into a structured file (xml, yaml or hcl).
*ksearch is a notation key (wk has no function on it), may be used by programs outside wk.
Two type of *ksearch are supported: command and optstruct.

- attrs: is a list or tuple of bottom up (bu) paths.
A bu path into a structured file (xml, yaml, hcl) works like this.
Let say that the field we want search for is the attribute name at path: app/jvms/jvm@name
For example the 
<app name = 'myapp'>
    <jvms>
        <jvm name = '[jvms/app@name]-jvm1'  xmx='50m'>
    <jvms>
</app>
A bu path is a reversed path from this field's node that may refer to any ascendant 
attributes's value above it.
This [jvms/app@name]-jvm1 would give: myapp-jvm1.
@xmx would guive 50m this is the attribute at the same level.
The bu path must end with @attr.

- Type Command: {'type': 'command', 'parms': {'parm1': 'value1', 'parm2': 'value2'}, 'command': 'mycommand $attr1$ $attr2$ $parm1$ $parm2$', 'resultKey': 'tag0/tag1/tag2'}
The search for that field is using the command: mycommand.
resultKey is an optional td path (tag0/tag1/tagn) of tags where to search the result json for a value or list of values for the field. 

- Type OptStruct: {'type': 'otstruct', 'attrs': [<tag2/tag1/tag02@attr1>, <tag2@attr2>, ...], 'parms': [{'parm1': 'value1', 'parmn': 'valuen'}], 'operation': 'read', 'section': <section>, 'bsl': [<otherSoftClassBal>], 'appinst': <appinst>, 'machine': [<machine>], 'resultKey': 'tag0/tag1/tag2'}
The search for that field is using the current softclass or another one specified at: bsl using operation (here read).
resultKey is an optional td path (tag0/tag1/tagn) of tags where to search the result json for a value or list of values for the field.

section: if section is not set and bsl is not set and the calling SoftClass is an OptStruct it will be retreived from it.
machine: if appinst is kcontrol machine can be omitted. If there is only one machine on the appinst, it can be omitted.

JSON output:
------------ 
This json is the result returned by either the command or the SoftClass.
This json is a list of dict of keys/values.
okey okeys and oattrs: are information about how to manage the resulting json.
oattrs: is a list of attribute's name, that says what are the entries to pick up from the dict.
okey: says what attribute in oattrs is the key.
okeys: says what attributes in oattrs could be used as sorting key.
"""





#------------------#
#  WantedKeywords  #
#------------------#


    
SUPPORTED_TYPES=('str', 'unicode', 'int', 'float', 'tuple', 'list', 'dict', 'bool', 'date', 'ts', 'xml', 'color', 'wkDef', 'url' )

CHECKED_KEYS=(
    '*value', '*checkIn', '*checkXIn', '*type', '*date', '*ts', '*ltype', '*dtype',
    '*required', '*isDir', '*isFile', '*regex', '*force_str', '*raw', '*between', '*lt', '*gt',
    '*eq', '*le', '*ge', '*ne', '*len', '*minLen', '*maxLen', '*startsWith', '*endsWith', '*withEval', '*withJson', '*withCoolTyping',
    '*label', '*help', '*lhelp', '*ksearch', '*shortcut', '*roles', '*rolesAutzDft', '*rolesAutz', '*password', '*password_file_option'
    )
# - Note : help, lhelp, label, shortcut, roles, rolesAutzDft and rolesAutz are armless keys.
ARMLESS_KEYS=('help', 'lhelp', 'label', 'shortcut', 'roles', 'rolesAutzDft', 'rolesAutz', 'password')

DOC_CHECKED_KEYS="A WKDefinition is a dictionary of one or more of these keys:{'*value':any type, '*checkIn':tuple/list', '*checkXIn':tuple/list, '*type':str in ('str', 'int', 'tuple', 'list', 'dict', 'bool'), *ltype:Wk Definiton, *dtype:dict of Wk Definitons, '*required':True False/default, '*isDir':bool, '*isFile':bool, '*regex':str, '*force_str':True False/default, '*raw':True False/default, '*between':list of 2 elts, '*lt':any type, '*gt':any type, '*eq':any type, '*le':any type, '*ge':any type, '*ne':any type, '*maxLen':int, '*startsWith':str, '*endsWith':str, '*withEval':True False/default, '*withJson':True False/default, '*withCoolTyping':True False/default, '*ksearch': {source: [<td1, td,2 ...], bsl: <bsl>, operation: read}}"
import re
RE_CHECK_COLOR=re.compile('#[A-Z0-9]{6}')
ROLES_ALLOWED_AUTZ=('all', 'allow', 'display', 'displayNew', 'displaySoftClassNew', 'update', 'execute', '*optimistic')
ROLES_SPECIALS=('*anyone',)
from kwadlib.default import ACTION_OUTPUT_MARK


class WantedKeywords:
    def __init__(self):
        pass

WK=WantedKeywords

def yourWkDefinition(wks):
    if not isinstance(wks, dict):return str(wks)
    return str({key: wks[key] for key in wks if key[1:] not in ARMLESS_KEYS})

# A001 + wkExtension
def getKeywords(wantedKeywords, keywords, attrs_orders=[], remove=False, acceptedComb=(), wkExtension=None, except_defs=None, class_exit=None, method_exit=None):
    selfMethod='getKeywords'
    """For functions that just receives *args, **keywords (since they dont controle *args),
    and still need keywords parameters
    wantedKeywords is an instance of WantedKeywords, each attr is a value you expect
    UseFullWhen:default keywords needs

    When forEach is true and typ is a list:
    a loop is made througth the type list to check  wantedKeywords.attr and/or keywords[attr].
    at it's end the list restart to 0.        
    """

    if not isinstance(keywords, dict):raise wkexception.wkParameterTypeException(str(keywords), 'dict', str(keywords), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
    if not isinstance(attrs_orders, (tuple, list)):raise wkexception.wkParameterTypeException(str(attrs_orders), 'tuple/list', str(attrs_orders), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
    if except_defs != None and not isinstance(except_defs,(list, tuple)): raise wkexception.wkParameterTypeException('wk', selfMethod, 'except_defs', 'list/tuple', str(except_defs))

    apb_checkIsDones=()
    if hasattr(wantedKeywords, 'apb_noCheckIfDone'):
        apb_noCheckIfDone=wantedKeywords.apb_noCheckIfDone
        if 'apb_checkIsDones' in keywords:apb_checkIsDones=keywords['apb_checkIsDones']
    else:
        apb_noCheckIfDone=False
    
    original_keywords=keywords
    keywords=dict(keywords)
    if acceptedComb!=():
        chooseComb=[' ' for s in acceptedComb[0]]
        
    attrs_keys=dir(wantedKeywords)
    attrs_keys=[attr for attr in attrs_keys if attr[0]!='_']
    
    if len(attrs_orders)!=0:
        attrs_keys.sort()
        l=list(attrs_orders)
        l.sort()
        if l!=attrs_keys:raise wkexception.wkParameterException('attrs_orders:' + str(attrs_orders).replace("'", '')[1:-1], ' ! attrs_orders and the wantedKeywords instance should share the same keys. wantedKeywords instance attributes are:' + str(attrs_keys).replace("'", '')[1:-1] + '.', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        attrs_keys=attrs_orders
    
    for attr in attrs_keys:
        if apb_noCheckIfDone and attr in apb_checkIsDones:continue

        ischeckedDict=False
        dct=None

        if isWKDefinition(getattr(wantedKeywords, attr), class_exit=class_exit, method_exit=method_exit):
            dct=getattr(wantedKeywords, attr)
            ## Default type dict if dtype is given.
            if '*type' not in dct:
                if '*ltype' in dct:dct['*type']='list'                
                elif '*dtype' in dct:dct['*type']='dict'
            
            setattr(wantedKeywords, attr, None)


            # withEval, withJson or withCoolTyping
            l =   ['*withEval' in dct, '*withCoolTyping' in dct, '*withJson' in dct]
            l.sort()

            if l in ([False, True, True], [True, True, True]) :
                raise wkexception.wkSystemException("On *withEval/*withJson/*withCoolTyping: They are exclusive to each others only one can be specified ! Your wkDefinition: " + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

            # withCoolTyping
            if ('*withCoolTyping' in dct and dct['*withCoolTyping']) and not (('*type' in dct and dct['*type']=='str') or ('*force_str' in dct and dct['*force_str'])):
                if attr in keywords and isinstance(keywords[attr], str):
                    try: 
                        if (keywords[attr].find('"')>=0 or keywords[attr].find("'")>=0) and '*type' in dct:keywords[attr]=_eval(typ=dct['*type'], value=keywords[attr])
                        else:keywords[attr]=ct.dress(keywords[attr])
                    except:
                        import sys
                        raise wkexception.wkSystemException("On *withCoolTyping:Received Bad value for key:" + attr + ' your value: ' + str(keywords[attr])  + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                                                        

                if '*value' in dct and isinstance(dct['*value'], str):
                    try:        
                        if (dct['*value'].find('"')>=0 or dct['*value'].find("'")>=0) and '*type' in dct:dct['*value']=_eval(typ=dct['*type'], value=dct['*value'])
                        else:dct['*value']=ct.dress(dct['*value'])                            
                    except:
                        import sys
                        raise wkexception.wkSystemException("On *withCoolTyping:Received Bad value for key:" + attr + ' your value: ' + str(dct['*value']) + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                                                        
            
            # withEval
            if ('*withEval' in dct and dct['*withEval']) and not (('*type' in dct and dct['*type']=='str') or ('*force_str' in dct and dct['*force_str'])):
                if attr in keywords and isinstance(keywords[attr], str):
                    try: 
                        ##keywords[attr]=eval(keywords[attr])
                        keywords[attr]=_eval(typ=dct['*type'], value=keywords[attr])
                    except:
                        import sys
                        raise wkexception.wkSystemException("On *withEval:Received Bad value for key:" + attr + ' your value: ' + str(keywords[attr])  + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                                                        

                if '*value' in dct and isinstance(dct['*value'], str):
                    try:        
                        ##dct['*value']=eval(dct['*value'])
                        dct['*value']=_eval(typ=dct['*type'], value=dct['*value'])                            
                    except:
                        import sys
                        raise wkexception.wkSystemException("On *withEval:Received Bad value for key:" + attr + ' your value: ' + str(dct['*value']) + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

            # withJson
            if ('*withJson' in dct and dct['*withJson']) and not (('*type' in dct and dct['*type']=='str') or ('*force_str' in dct and dct['*force_str'])):
                import json
                if attr in keywords and isinstance(keywords[attr], str):
                    try:
                        keywords[attr]=json.loads(keywords[attr])
                    except:
                        import sys
                        raise wkexception.wkSystemException("On *withJson:Received Bad value for key:" + attr + ' your value: ' + str(keywords[attr])  + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

                if '*value' in dct and isinstance(dct['*value'], str):
                    try:
                        dct['*value']=json.loads(value=dct['*value'])
                    except:
                        import sys
                        raise wkexception.wkSystemException("On *withJson:Received Bad value for key:" + attr + ' your value: ' + str(dct['*value']) + ' SubException is:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

            # A001:
            if wkExtension!=None:
                if attr in keywords:value=keywords[attr]
                else:value=None
                dct, keywords[attr]=wkExtension.getKeywords(attr, dct, value, keywords=dict(keywords), class_exit=class_exit, method_exit=method_exit)

            # Default Value
            if '*value' in dct:
                setattr(wantedKeywords, attr, dct['*value'])
                if attr not in keywords or keywords[attr]==None:
                    keywords[attr]=dct['*value']
            
            # Required parameters
            if '*required' in dct and dct['*required']==True and (attr not in keywords or keywords[attr]==None):                    
                raise wkexception.wkSystemException("On *Required:Received no value for required key:" + attr + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

            if attr in keywords and keywords[attr]!=None:keywords[attr]=__checkType(keywords[attr], attr=attr, dct=dct, save_key=True, mess_default='', class_exit=class_exit, method_exit=method_exit)
            if getattr(wantedKeywords, attr)!=None:__checkType(getattr(wantedKeywords, attr), attr=attr, dct=dct, save_key=False, mess_default='default', class_exit=class_exit, method_exit=method_exit)

        
        # Combined parameters
        if acceptedComb!=():
            if attr in keywords and keywords[attr]!=None:
                if attr in acceptedComb[0]:chooseComb[acceptedComb[0].index(attr)]='X'
        
    if acceptedComb!=() and chooseComb not in acceptedComb: 
        firtTime=True
        i=0
        for l in acceptedComb:  
            if firtTime==True:
                #message = str(str([s[3:].center(10) for s in acceptedComb[0]])) 
                message = str(str([s[-10:].center(10) for s in acceptedComb[0]])) 
                firtTime=False
                continue

            if i==10:
                message=message + '\n' + str(str([s[3:].center(10) for s in acceptedComb[0]])) 
                i=0            
            message = message  + '\n' + str([s.center(10) for s in l])
            i=i+1            
            
        message = message  + "\nYour Choice is :\n"
        message = message  +  str(str([s.center(10) for s in chooseComb])) 
        raise wkexception.wkSystemException("Autorized combinaison are : \n" + message, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # Received values
    for k in list(keywords.keys()):
        if hasattr(wantedKeywords, k):
            setattr(wantedKeywords, k, keywords[k])
            # Remove
            if remove:
                if k in original_keywords:del original_keywords[k]        

def __checkType(value, attr=None, dct=None, save_key=False, except_defs=None, mess_default='', class_exit=None, method_exit=None):
    selfMethod='__checkType'

    if isinstance(value, str) and value.startswith(ACTION_OUTPUT_MARK):
        # A003:
        """ Allow SoftClass attribute output reference:
        @koutref-myHostedClientOrganization/Applications/aaaaa/bbbbbb/HostedClientOrganization@id
        """
        import re
        l = re.findall(r'%s(?:[a-zA-Z]*/)*[a-zA-Z]*@[a-zA-Z]*$' % ACTION_OUTPUT_MARK, value)
        if len(l) == 0 and l[0] == value:return value

    # checkIn
    if '*checkIn' in dct and not (except_defs!=None and '*checkIn' in except_defs):
        if value not in dct['*checkIn']:
            raise wkexception.wkSystemException("On *checkIn:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected:one of " +  str(dct['*checkIn']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # checkXIn
    if '*checkXIn' in dct and not (except_defs!=None and '*checkXIn' in except_defs):
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise wkexception.wkSystemException("On *checkXIn:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected:list/tuple " + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            
        
        error=False
        if len(value)>len(dct['*checkXIn']):error=True
        vals=[]
        for val in value:
            if val in vals or val not in dct['*checkXIn']:error=True
            vals.append(val)
            
        del vals
        if error:raise wkexception.wkSystemException("On *checkXIn:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected:one or more of " +  str(dct['*checkXIn']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # type
    if '*type' in dct and not (except_defs!=None and '*type' in except_defs):
        # force value to float if received int.
        if (dct['*type']=='float' and isinstance(value, int)):value=float(value)
        # force value to str if received unicode.
        elif(dct['*type']=='str' and value!=None or ('*force_str' in dct and dct['*force_str'])):value=str(value)
        if not checkType(value, dct['*type'], class_exit, method_exit):raise wkexception.wkSystemException("On *Type:Received Bad type for key:" + attr + "  Type Expected:" + str(dct['*type']) + "  Type Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

    # *date
    if '*date' in dct and not (except_defs!=None and '*date' in except_defs):
        if not isinstance(value, str) and not isinstance(value, (datetime.date)):
            raise wkexception.wkSystemException("On *date:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: a <strptime str> or None.  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct) + DATE_HELP, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

        if not isinstance(value, str):
            if not isinstance (value, datetime.date):
                raise wkexception.wkSystemException("On *date:Received Bad " +  mess_default + " value for key:" + attr + '  Value Expected a Python datetime.date object. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        else:
            try:
                if dct['*date']==None:value = datetime.date(*time.strptime(value)[0:3])
                else:value = datetime.date(*time.strptime(value, dct['*date'])[0:3])
            except ValueError as e:
                raise wkexception.wkSystemException("On *date:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: a <strptime str> or None.  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct) + '\nSubException is:' + str(e) + '\n' + DATE_HELP, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

    # *ts
    if '*ts' in dct and not (except_defs!=None and '*ts' in except_defs):
        if not isinstance(value, str) and not isinstance(value, (datetime.datetime)):
            raise wkexception.wkSystemException("On *ts:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: a <strptime str> or None.  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct) + TS_HELP, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

        if not isinstance(value, str):
            if not isinstance (value, datetime.datetime):
                raise wkexception.wkSystemException("On *ts:Received Bad " +  mess_default + " value for key:" + attr + '  Value Expected a Python datetime.datetime object. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        else:
            try:
                if dct['*ts']==None:value = datetime.datetime(*time.strptime(value)[0:6])
                else:value = datetime.datetime(*time.strptime(value, dct['*ts'])[0:6])
            except ValueError as e:
                raise wkexception.wkSystemException("On *ts:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: a <strptime str> or None.  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct) + '\nSubException is:' + str(e) + '\n' + TS_HELP, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

    # between
    if '*between' in dct and not (except_defs!=None and '*between' in except_defs):
        if not (dct['*between'][0] <= value and  value <= dct['*between'][1]):
            raise wkexception.wkSystemException("On *between:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: between " +  str(dct['*between']) + "  Value Received:" + str(value) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # *len
    if '*len' in dct and not (except_defs!=None and '*len' in except_defs):
        if not isinstance(value, str) and not isinstance(value, list) and not isinstance(value, tuple):
            raise wkexception.wkSystemException("On *len:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: one of  " +  str((str, list, tuple)) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

        if len(value) != dct['*len']:
            raise wkexception.wkSystemException("On **len:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: len(value) == " +  str(dct['*len']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            
        
    # *minLen
    if '*minLen' in dct and not (except_defs!=None and '*minLen' in except_defs):
        if not isinstance(value, str) and not isinstance(value, list) and not isinstance(value, tuple):
            raise wkexception.wkSystemException("On *minLen:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: one of  " +  str((str, list, tuple)) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

        if len(value) < dct['*minLen']:
            raise wkexception.wkSystemException("On *minLen:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: len(value) >= " +  str(dct['*minLen']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            
        
    # *maxLen
    if '*maxLen' in dct and not (except_defs!=None and '*maxLen' in except_defs):
        if not isinstance(value, str) and not isinstance(value, list) and not isinstance(value, tuple):
            raise wkexception.wkSystemException("On *maxLen:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: one of  " +  str((str, list, tuple)) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

        if len(value) > dct['*maxLen']:
            raise wkexception.wkSystemException("On *maxLen:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: len(value) <= " +  str(dct['*maxLen']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            
        
    # *startsWith
    if '*startsWith' in dct and not (except_defs!=None and '*startsWith' in except_defs):
        if not isinstance(value, str):
            raise wkexception.wkSystemException("On *startsWith:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: str, Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

        if not value.startswith(dct['*startsWith']):
            raise wkexception.wkSystemException("On *maxLen:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: startsWith:" +  str(dct['*startsWith']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                    
        
    # *endsWith
    if '*endsWith' in dct and not (except_defs!=None and '*endsWith' in except_defs):
        if not isinstance(value, str):
            raise wkexception.wkSystemException("On *endsWith:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: str, Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

        if not value.endswith(dct['*endsWith']):
            raise wkexception.wkSystemException("On *maxLen:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: endsWith:" +  str(dct['*endsWith']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # lt
    if '*lt' in dct and not (except_defs!=None and '*lt' in except_defs):
        if not value < dct['*lt']:
            raise wkexception.wkSystemException("On *lt:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: Leater than:" +  str(dct['*lt']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # gt
    if '*gt' in dct and not (except_defs!=None and '*gt' in except_defs):
        if not value > dct['*gt']:raise wkexception.wkSystemException("On *gt:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: Greater than:" +  str(dct['*gt']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # eq
    if '*eq' in dct and not (except_defs!=None and '*eq' in except_defs):
        if not value == dct['*eq']:
            raise wkexception.wkSystemException("On *eq:Received Bad value for key:" + attr + "  Value Expected: Equal to:" +  str(dct['*eq']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # le
    if '*le' in dct and not (except_defs!=None and '*le' in except_defs):
        if not value <= dct['*le']:raise wkexception.wkSystemException("On *gt:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: Leater or equal to:" +  str(dct['*le']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # ge
    if '*ge' in dct and not (except_defs!=None and '*ge' in except_defs):
        if not value >= dct['*ge']:raise wkexception.wkSystemException("On *gt:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: Greater or equal to:" +  str(dct['*ge']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # ne
    if '*ne' in dct and not (except_defs!=None and '*ne' in except_defs):
        if not value != dct['*ne']:raise wkexception.wkSystemException("On *gt:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: Different than: " +  str(dct['*ne']) + "  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            

    # isDir
    if '*isDir' in dct and dct['*isDir'] and not (except_defs!=None and '*isDir' in except_defs):
        from os import path
        if not path.isdir(value):raise wkexception.wkSystemException("On *gt:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: An Existing Directory, Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
    # isFile
    if '*isFile' in dct and dct['*isFile'] and not (except_defs!=None and '*isFile' in except_defs):
        from os import path
        if not path.isfile(value):raise wkexception.wkSystemException("On *gt:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: An Existing File, Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

    # *regex
    if '*regex' in dct and not (except_defs!=None and '*regex' in except_defs):
        if not isinstance(value, str):
            raise wkexception.wkSystemException("On *regex:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: type str,  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            
        import re
        r=re.compile(dct['*regex']).search(value)
        if r==None:
            raise wkexception.wkSystemException("On *regex:Received Bad " +  mess_default + " value for key:" + attr + "  Value Expected: regex:dct['*regex'],  Value Received:" + str(value) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))            
        value=r.group()

    # *ltype and *dtype
    loop=[]
    if ( '*ltype' in dct or '*dtype' in dct ) and isinstance(value, list):loop=value
    elif '*dtype' in dct:loop=[value]

    for i in range(len(loop)):
        val=loop[i]
        
        # *ltype
        if '*ltype' in dct:

            d=dct['*ltype']
            if '*withCoolTyping' in d or '*withEval' in d or '*withJson' in d:raise wkexception.wkSystemException('On *ltype:Internal list Wk Definition do not support *withCoolTyping, *withEval nor *withJson. Your internal dict Wk Definition:' + str(d) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
            p=WantedKeywords()                            
            setattr(p, 'elt', d)

            try:
                getKeywords(wantedKeywords=p, keywords={'elt':val}, class_exit=class_exit, method_exit=method_exit)
            except Exception as e:
                import sys
                _e=wkexception.wkSystemException("On *ltype:Received bad " +  mess_default + " value for:" + attr + "  Expected *ltypes: " +  str(dct['*ltype']) + "  Value Received:" + str(val) + ', type:' + str(type(value)) + '. Your wkDefinition: ' + yourWkDefinition(dct) + '. SubException:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                _e.setSubException(e)
                raise _e
            
            if save_key:loop[i]=p.elt                

        # *dtype
        if '*dtype' in dct:
            
            for key in val:
                if key not in dct['*dtype']:raise wkexception.wkSystemException("On *dtype:Received and undefined key:" + key + "  Value Expected:one of " +  str(list(dct['*dtype'].keys())) + "  Value Received:" + str(val) + ', type:' + str(type(val)) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

            p=WantedKeywords()                            
            for key in dct['*dtype']:
                d=dct['*dtype'][key]
                if '*withCoolTyping' in d or '*withEval' in d or '*withJson' in d:raise wkexception.wkSystemException('On *dtype:Internal dict Wk Definition do not support *withCoolTyping, *withEval nor *withJson. Your internal dict Wk Definition:' + str(d) + '. Your wkDefinition: ' + yourWkDefinition(dct), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                setattr(p, key, d)                    
            try:
                getKeywords(wantedKeywords=p, keywords=val, class_exit=class_exit, method_exit=method_exit)
            except Exception as e:
                import sys
                _e=wkexception.wkSystemException("On *dtype:Received bad " +  mess_default + " value for:" + attr + "  Expected *dtypes: " +  str(dct['*dtype']) + "  Value Received:" + str(val) + ', type:' + str(type(val)) + '. Your wkDefinition: ' + yourWkDefinition(dct) + '. SubException:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                _e.setSubException(e)
                raise _e
            
            if save_key:
                d=dict()
                l=dir(p)
                for e in l:
                    if not e.startswith('_'):d[e]=getattr(p, e)
                loop[i]=d

        if save_key:
            if isinstance(value, list):value=loop
            else:value=loop[0]
            
    return value

getK=getKeywords

def isWKDefinition(defn, class_exit="", method_exit=""):
    selfMethod='isWKDefinition'
    if not isinstance(defn, dict):return False
    
    hasOne=False
    isWKDef=True    
    error_keys=[]
    for key in defn:
        # A001:
        if key.startswith('*@'):continue
        if key in CHECKED_KEYS:
            hasOne=True
        else:
            isWKDef=False
            error_keys.append(key)

    if hasOne and not isWKDef:raise wkexception.wkWKDefinitionException('This Wk Definition ' + str(defn) + ' contains key(s):' + str(error_keys) + ' that are not Wk Definitions, key Expected for Wk Definitions are' + str(CHECKED_KEYS), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                                    
    if isWKDef:
        #+type tuple pour check differents types sur tuple  
        if '*type' in defn and not (isinstance(defn['*type'], str) and defn['*type'].startswith('*')) and defn['*type'] not in SUPPORTED_TYPES:raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *type expected:' + str(SUPPORTED_TYPES) + '. Received:' + str(defn['*type']) + ', type:' + str(type(defn['*type'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                  
        if '*type' in defn and '*ltype' in defn and defn['*type']!='list':raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *ltype: if *type is given it must be list. Received:' + str(defn['*type']) + ', type:' +  str(type(defn['*type'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*type' in defn and '*dtype' in defn and defn['*type'] not in ('list', 'dict'):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *dtype: if *type is given it must be dict or list. Received:' + str(defn['*type']) + ', type:' +  str(type(defn['*type'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*ltype' in defn and '*dtype' in defn:raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *type: Just one of of *ltype or *dtype must be given at a time. Received:' + str(defn['*type']), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*ltype' in defn and not isWKDefinition(defn['*ltype']):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *ltype. *ltype should be given as a Wk Definition. Your value:' + str(defn['*ltype']) + '.', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*dtype' in defn and not isinstance(defn['*dtype'], dict):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *dtype expected:dict. Received:' + str(defn['*dtype']) + ', type:' +  str(type(defn['*dtype'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*dtype' in defn:
            for key in defn['*dtype']:
                if not isWKDefinition(defn['*dtype'][key]):raise wkexception.wkSystemException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key  *dtype. *dtype should be given as a dict of Wk Definition. Your key:' + key + ', Your value:' + str(defn['*dtype'][key]) + ', type:' + str(type(defn['*dtype'][key])) + '.', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

        if '*date' in defn and not (isinstance(defn['*date'], str) or defn['*date']==None):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *date expected:str or None. Received:' + str(defn['*date']) + ', type:' + str(type(defn['*date'])) + DATE_HELP, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*ts' in defn and not (isinstance(defn['*ts'], str) or defn['*ts']==None):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *ts expected:str, or None. Received:' + str(defn['*ts']) + ', type:' + str(type(defn['*ts'])) + DATE_HELP, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

        if '*checkIn' in defn and (not isinstance(defn['*checkIn'], tuple) and not isinstance(defn['*checkIn'], list)):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *checkIn expected:tuple/list received:' + str(defn['*checkIn']) + ', type:' + str(type(defn['*checkIn'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                  
        if '*checkXIn' in defn and (not isinstance(defn['*checkXIn'], tuple) and not isinstance(defn['*checkXIn'], list)):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *checkXIn expected:tuple/list received:' + str(defn['*checkXIn']) + ', type:' + str(type(defn['*checkXIn'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*required' in defn and not isinstance(defn['*required'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *required expected:bool received:' + str(defn['*required']) + ', type:' +  str(type(defn['*required'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if (not ('*withEval' in defn or '*withJson' in defn or '*withCoolTyping' in defn)) and '*value' in defn and defn['*value']!=None and '*type' in defn :
            if isinstance(defn['*type'], str) and not checkType(defn['*value'], defn['*type'], class_exit='tools.Main', method_exit=selfMethod):
                raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *value expected:' + str(defn['*type']) + ' received:' + str(defn['*value']) + ', type:' + str(type(defn['*value'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                      
        if '*between' in defn and (not isinstance(defn['*between'], tuple) and not isinstance(defn['*between'], list)) and not len(defn['*between'])==2:raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *between expected:tuple of 2 elements, received:' + str(defn['*between']), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                      
        if '*maxLen' in defn and not isinstance(defn['*maxLen'], int):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *maxLen expected:int received:' + str(defn['*maxLen']) + ', type:' +  str(type(defn['*maxLen'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                      
        if '*startsWith' in defn and not isinstance(defn['*startsWith'], str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *startsWith expected:str received:' + str(defn['*startsWith']) + ', type:' +  str(type(defn['*startsWith'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*endsWith' in defn and not isinstance(defn['*endsWith'], str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key **endsWith expected:str received:' + str(defn['**endsWith']) + ', type:' +  str(type(defn['**endsWith'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*withJson' in defn and not isinstance(defn['*withJson'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *withJson expected:bool received:' + str(defn['*withJson']) + ', type:' + str(type(defn['*withJson'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*withEval' in defn and not isinstance(defn['*withEval'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *withEval expected:bool received:' + str(defn['*withEval']) + ', type:' + str(type(defn['*withEval'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*withEval' in defn and '*type' not in defn:raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *withEval , key *type is required', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*isDir' in defn and not isinstance(defn['*isDir'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *isDir expected:bool received:' + str(defn['*isDir']) + ', type:' + str(type(defn['*isDir'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*isFile' in defn and not isinstance(defn['*isFile'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *isFile expected:bool received:' + str(defn['*isFile']) + ', type:' + str(type(defn['*isFile'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*regex' in defn and not isinstance(defn['*regex'], str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *regex expected:str received:' + str(defn['*regex']) + ', type:' + str(type(defn['*regex'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*force_str' in defn and not isinstance(defn['*force_str'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *force_str expected:str received:' + str(defn['*force_str']) + ', type:' +  str(type(defn['*force_str'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*raw' in defn and not isinstance(defn['*raw'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *raw expected:bool received:' + str(defn['*raw']) + ', type:' +  str(type(defn['*raw'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

        # Armless keys '*label', '*help', '*lhelp', '*shortcut'
        if '*label' in defn and not isinstance(defn['*label'], str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *label expected:str received:' + str(defn['*label']) + ', type:' +  str(type(defn['*label'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*help' in defn and not isinstance(defn['*help'], str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *help expected:str received:' + str(defn['*help']) + ', type:' +  str(type(defn['*help'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*lhelp' in defn and not isinstance(defn['*lhelp'], str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *lhelp expected:str received:' + str(defn['*lhelp']) + ', type:' +  str(type(defn['*lhelp'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        if '*roles' in defn:checkRoles(defn['*roles'], class_exit=class_exit, method_exit=method_exit)
        if '*rolesAutzDft' in defn:checkRolesAutz('*rolesAutzDft', defn['*rolesAutzDft'], class_exit=class_exit, method_exit=method_exit)
        if '*rolesAutz' in defn:checkRolesAutz('*rolesAutz', defn['*rolesAutz'], class_exit=class_exit, method_exit=method_exit)
        if '*shortcut' in defn and not isinstance(defn['*shortcut'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *shortcut expected:bool received:' + str(defn['*shortcut']) + ', type:' +  str(type(defn['*shortcut'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        if '*password' in defn:
            if not isinstance(defn['*password'], bool):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *password expected:bool received:' + str(defn['*password']) + ', type:' +  str(type(defn['*password'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
            if '*password_file_option' in defn and not isinstance(defn['*password_file_option'], str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *password_file_option expected:str received:' + str(defn['*password_file_option']) + ', type:' +  str(type(defn['*password_file_option'])), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
        else:
            if '*password_file_option' in defn:raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key *password_file_option, is only supported with key: *password.', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

        if '*ksearch' in defn:
            """
            - Type Command: {'type': 'command', 'attrs': [<tag2/tag1/tag0@attr0>, <tag2@attr2>, ...], 'parms': {'parm1': 'value1', 'parm2': 'value2'}, 'command': 'mycommand {attr1} {attr2} {parm1} {parm2}'}
            keys: type, parms, command
            The search for that field is using the command: mycommand.
            - Type OptStruct: {'type': 'otstruct', 'attrs': [<tag2/tag1/tag02@attr1>, <tag2@attr2>, ...], 'parms': {'parm1': 'value1', 'parm2': 'value2'}, 'operation': 'read', 'bsl': 'otherSoftClass'}
            keys: type, attrs, operation, bsl
            """
            prefix = 'This Definition:'  + str(defn) + ' is not a WKDefinition. For key *shortcut expected:bool received:' + str(defn['*ksearch']) + ', type:' +  str(type(defn['*ksearch']))
            sufix = '\nThe *ksearch format is:\n' + KSEARCH_FORMAT
            ksearchs = defn['*ksearch']
            if 'type' not in ksearchs or ksearchs['type'] not in ('command', 'optstruct'):raise wkexception.wkWKDefinitionException(prefix  +'\nkey type is required and must be one of: "command", "optstruct" !' + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
            if 'parms' in ksearchs and not isinstance(ksearchs['parms'], dict): raise wkexception.wkWKDefinitionException(prefix + '\nBad key parms, must be a dict ! Received: %s' % str(ksearchs['parms']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
            if 'resultKey' in ksearchs:
                if not isinstance(ksearchs['resultKey'], str): raise wkexception.wkWKDefinitionException(prefix + '\nBad key resultKey, should be str ! Received: %s' % str(ksearchs['resultKey']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if ksearchs['resultKey'].find('@')>0: raise wkexception.wkWKDefinitionException(prefix + '\nBad key resultKey expected a td path (e.g.: tag0/tag1.tagn), should not contains @ ! Received: %s' % str(ksearchs['resultKey']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
            COMMAND_KEYS = ('type', 'parms', 'command', 'resultKey')
            OPTSTRUCT_KEYS = ('type', 'attrs', 'parms', 'operation', 'section', 'bsl', 'appinst', 'machine', 'resultKey', 'okey', 'okeys', 'oattrs')
            if not isinstance(ksearchs, dict): raise wkexception.wkWKDefinitionException(prefix + '\nUnsupported ksearchs: %s ! Must be a dict.' % str(ksearchs))

            if ksearchs['type'] == 'command':
                # keys: type, parms, command, resultKey
                if not 'command' in ksearchs and not isinstance(ksearchs['command'], str): raise wkexception.wkWKDefinitionException(prefix + '\nBad key command, is required and must be str ! Received: %s' % str(ksearchs['command']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

                # no more keys:
                keys = list(ksearchs.keys())
                for key in keys:
                    if key not in (COMMAND_KEYS):raise wkexception.wkWKDefinitionException(prefix  +'\nUnsupported key: %s for type: %s ! Expected keys are: %s' % (key, 'command', str(COMMAND_KEYS)))
            elif ksearchs['type'] == 'optstruct':
                # keys: type, attrs, parms, operation, bsl, resultKey
                if not 'operation' in ksearchs or not isinstance(ksearchs['operation'], str):raise wkexception.wkWKDefinitionException(prefix  +'\nBad key operation, is required and must be str ! Received: %s' % str(ksearchs['operation']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'bsl' in ksearchs and ksearchs['bsl'] != None and not isinstance(ksearchs['bsl'], str): raise wkexception.wkWKDefinitionException(prefix  +'\nBad key bsl, should be str ! Received: %s' % str(ksearchs['bsl']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'section' in ksearchs and ksearchs['section'] != None and not isinstance(ksearchs['section'], str): raise wkexception.wkWKDefinitionException(prefix  +'\nBad key section, should be str ! Received: %s' % str(ksearchs['section']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'machine' in ksearchs and ksearchs['machine'] != None and not isinstance(ksearchs['machine'], str): raise wkexception.wkWKDefinitionException(prefix  +'\nBad key machine, should be str ! Received: %s' % str(ksearchs['machine']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'appinst' not in ksearchs or ksearchs['appinst'] == None or not isinstance(ksearchs['appinst'], str): raise wkexception.wkWKDefinitionException(prefix  +'\nBad key appinst is required and should be str ! Received: %s' % str(None if not 'appinst' in ksearchs else ksearchs['appinst']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'okey' not in ksearchs or ksearchs['okey'] == None or not isinstance(ksearchs['okey'], str): raise wkexception.wkWKDefinitionException(prefix  +'\nBad key okey is required and should be str ! Received: %s' % str(None if not 'okey' in ksearchs else ksearchs['okey']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'okeys' in ksearchs and ksearchs['okeys'] != None and not isinstance(ksearchs['okeys'], (tuple, list)): raise wkexception.wkWKDefinitionException(prefix + '\nBad key okeys should be list/tuple ! Received: %s' % str(None if not 'okeys' in ksearchs else ksearchs['okeys']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'oattrs' in ksearchs and ksearchs['oattrs'] != None and not isinstance(ksearchs['oattrs'], (tuple, list)): raise wkexception.wkWKDefinitionException(prefix + '\nBad key oattrs should be list/tuple ! Received: %s' % str(None if not 'oattrs' in ksearchs else ksearchs['oattrs']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

                # no more keys:
                keys = list(ksearchs.keys())
                for key in keys:
                    if key not in (OPTSTRUCT_KEYS):raise wkexception.wkWKDefinitionException(prefix  +'\nUnsupported key: %s for type: %s ! Expected keys are: %s' % (key, 'optstruct', str(OPTSTRUCT_KEYS)))

            # Check attrs:
            if 'attrs' in ksearchs and not isinstance(ksearchs['attrs'], (list, tuple)): raise wkexception.wkWKDefinitionException(prefix + '\nBad key attrs, should be tuple/list ! Received: %s' % str(ksearchs['attrs']) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
            if 'attrs' in ksearchs:
                bus = ksearchs['attrs'] # bu: bottom up tags
                for bu in bus:
                    if not len(bu.split('@')) == 2:raise wkexception.wkWKDefinitionException(prefix  +'\nBad attrs key: %s should ends with @<attribute_name> !' % bu + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                    last = bu.split('/')[-1]
                    if not last.find('@')>=0:raise wkexception.wkWKDefinitionException(prefix  +'\nBad attrs key: %s should ends with @<attribute_name> !' % bu + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
            if 'oattrs' in ksearchs and ksearchs['oattrs'] != None:
                oattrs = ksearchs['oattrs']
                # Check on oattrs:
                okey = ksearchs['okey']
                if okey not in oattrs:
                    raise wkexception.wkWKDefinitionException(prefix + '\nBad key okey: %s should be in oattrs: %s !' % (okey, ', '.join(ksearchs['oattrs'])) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
                if 'okeys' in ksearchs and ksearchs['okeys'] != None:
                    okeys = ksearchs['okeys']
                    for _okey in okeys:
                        if _okey not in oattrs:
                            raise wkexception.wkWKDefinitionException(prefix + '\nBad entry: %s in key okeys: %s. This entry should be in oattrs: %s !' % (_okey, ', '.join(okeys), ', '.join(ksearchs['oattrs'])) + sufix, fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))


        #f814290522f79d1e9e5ae4ae83e967b4

    if isWKDef == False:raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition ! Unknown keys:' + str(error_keys)[1:-1].replace("'", '') + '.', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
    return isWKDef

def checkRoles(defn, class_exit=None, method_exit=None):
    selfMethod='checkRoles'
    if not isinstance(defn, list):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition, expected:list received:' + str(defn) + ', type:' +   str(type(defn)), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))
    for e in defn:
        if not isinstance(e, str):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For item:' + str(e) + ', expected:list of str, received:' + str(defn) + ', type:' +  str(type(defn)), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))

def checkRolesAutz(key, defn, class_exit=None, method_exit=None):
    selfMethod='checkRolesAutz'
    if not isinstance(defn, dict):raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key:' + key + ', expected:dict received:' + str(defn['*help']) + ', type:' +  str(defn), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      

    for key in defn:
        values=defn[key].split(';')    
        if key.startswith('*') and key not in ROLES_SPECIALS:
            raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key:' + key + ', The Special Role:' + key + ' do not exist ! Supported Special Roles are:' + str(ROLES_SPECIALS)[1:-1] + '.', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        
        for value in values:
            if len(value)<2 or value[1:] not in ROLES_ALLOWED_AUTZ:
                raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key:' + key + ', Autorization Type:' + value + ' do not exist ! Supported Autorizations are:' + str(ROLES_ALLOWED_AUTZ)[1:-1] + '.', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
            if len(value)<1 or not value.startswith('-') and not value.startswith('+'):
                raise wkexception.wkWKDefinitionException('This Definition:'  + str(defn) + ' is not a WKDefinition. For key:' + key + ', Autorization Type:' + value + ' should start by "-" or "+" !', fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
        
    
def getwkType(wk_, doCheckType=True, class_exit=None, method_exit=None):    
    if doCheckType:isWKDefinition(wk_, class_exit=class_exit, method_exit=method_exit)
    if '*type' in wk_:return wk_['*type']
    if '*ltype' in wk_:return 'list'
    if '*dtype' in wk_:return 'dict'
    return 'str'

def checkType(obj, typ, class_exit=None, method_exit=None):
    selfMethod='checkType'  
    
    if not isinstance(typ, str):
        raise wkexception.wkParameterTypeException(str('typ'), 'str', str(typ), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))      
    if class_exit==None:class_exit='None'
    if method_exit==None:method_exit='None'   
    
    if obj==None:return False
   
    if typ.startswith('*'): 
        if not len(typ) > 1:raise wkexception.wkSystemException("Type:" + typ + " not supported by " + selfMethod  + ", supported types are:" + str(SUPPORTED_TYPES)  + " or *CustomType.", fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                        
        if not hasattr(obj, 'isinstance') or not obj.isinstance(typ[1:]):return False
        else:return True

    if typ=='date':return checkDate(obj, class_exit=class_exit, method_exit=method_exit)
    if typ=='ts':return checkTs(obj, class_exit=class_exit, method_exit=method_exit)
    if typ=='xml':return checkXml(obj, class_exit=class_exit, method_exit=method_exit)
    if typ=='wkDef':return checkWkDef(obj, class_exit=class_exit, method_exit=method_exit)
    if typ=='url':return checkUrl(obj, class_exit=class_exit, method_exit=method_exit)
    if typ=='color':return checkColor(obj, class_exit=class_exit, method_exit=method_exit)
    
    if typ in SUPPORTED_TYPES:return isinstance(obj, ct._eval(typ))
    else:
        raise wkexception.wkSystemException("Type:" + typ + " not supported by " + selfMethod  + ", supported types are:" + str(SUPPORTED_TYPES)  + " or *CustomType.", fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))                

def checkDate(value, class_exit=None, method_exit=None):
    selfMethod='checkDate'
    # date
    if not isinstance(value, str):    
        warnings.warn(str(wkexception.wkSystemException("On *type:date:Received Bad value Expected: type str Date (YY)YY/MM/DD,  Value Received:" + str(value), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))            
        return False
    isOk=True
    if len(value) > 10:isOk=False
    spl = value.split('/');
    if len(spl) != 3:isOk=False
    if not isOk:
        warnings.warn(str(wkexception.wkSystemException("On *type:date:Received Bad value Expected: type str Date (YY)YY/MM/DD,  Value Received:" + str(value), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))            
        return False                                 
    try:
        year  = int(spl[0])
        month = int(spl[1])
        day   = int(spl[2])
        import  datetime
        datetime.datetime(year=year, month=month, day=day)                                        
    except:
        import sys
        warnings.warn(str(wkexception.wkSystemException("On *type:date:Received Bad value Expected: type str Date (YY)YY/MM/DD,  Value Received:" + str(value) + ' SubException:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]), fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))            
        return False
    return True
        
def checkTs(value, class_exit=None, method_exit=None):
    selfMethod='checkTs'
    # ts
    if not isinstance(value, str):
        warnings.warn(str(wkexception.wkSystemException("On *type:ts:Received Bad value Expected: type str Ts (YY)YY/MM/DD-HH:MM:SS:mmmmmm,  Value Received:" + str(value), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))            
        return False
    isOk=False            
    while(True):
        if len(value) > 26:break
        spl = value.split('-');
        spl1 = spl[0].split('/');
        if len(spl1) != 3:break
        
        hh  = 0
        mm  = 0
        ss  = 0
        mmm = 0

        if len(spl) > 1:
            spl2 = spl[1].split(':')
            if (len(spl2) >= 1):
                hh  = spl2[0]
                if (len(hh) != 2):break                                    
            if (len(spl2) > 1):
                mm  = spl2[1]
                if (len(mm) != 2):break
            if (len(spl2) > 2):
                ss  = spl2[2]
                if (len(ss) != 2):break
            if (len(spl2) > 3):
                mmm = spl2[3]
                if (len(mmm) != 5):break
        isOk=True
        break                        
    if not isOk:
        warnings.warn(str(wkexception.wkSystemException("On *type:ts:Received Bad value Expected: type str Ts (YY)YY/MM/DD-HH:MM:SS:mmmmmm,  Value Received:" + str(value), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))           
        return False            
    
    try: 
        year  = int(spl1[0])
        month = int(spl1[1])
        day   = int(spl1[2])
        import  datetime
        datetime.datetime(year=year, month=month, day=day, hour=int(hh), minute=int(mm), second=int(ss), microsecond=int(mmm))            
    except:
        import sys
        warnings.warn(str(wkexception.wkSystemException("On *type:ts:Received Bad value Expected: type str Ts (YY)YY/MM/DD-HH:MM:SS:mmmmmm,  Value Received:" + str(value) + ' SubException:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]), fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))            
        return False
    return True
    
def checkXml(value, class_exit=None, method_exit=None):
    selfMethod='checkXml'
    # date
    if not (value.find('<')>=0 and value.find('>')>=0):    
        warnings.warn(str(wkexception.wkSystemException("On *type:xml:Received Bad value Expected: type xml,  Value Received:" + str(value), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))            
        return False

    return True    
    
def checkWkDef(value, class_exit=None, method_exit=None, doWarn=False):
    selfMethod='checkWkDef'
    
    try:
        if not isWKDefinition(value, class_exit=class_exit, method_exit=method_exit):raise
    except Exception as e:
        if doWarn:
            import warnings
            warnings.warn(str(wkexception.wkSystemException("On *type:wkDef:Received Bad  value Expected: a wkDefinition,  Value Received:" + str(value) + ', type:' + str(type(value)) + ' SubException is:' + str(e), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))
        return False
    
    return True
    
def checkUrl(value, class_exit=None, method_exit=None):
    selfMethod='checkUrl'
    # url
    if not value.find('/')>=0:    
        warnings.warn(str(wkexception.wkSystemException("On *type:url:Received Bad value Expected: type url,  Value Received:" + str(value) + ', type:' + str(type(value)), fromClass='wk', fromMethod=selfMethod + " SubClass:" + str(class_exit) + " SubMethod:" + str(method_exit))))
        return False

    return True
    
def checkColor(value, class_exit=None, method_exit=None):
    selfMethod='checkColor'
    Colors=('yellow', 'black', 'blue', 'cyan', 'orange', 'red', 'pink', 'white', 'green', 'gray', 'lightGray', 'brown')

    if value in Colors:return True
    if not isinstance(value, str) or len(value)!=7:return False

    res=RE_CHECK_COLOR.search(value)
    if res!=None and res.span() == (0,7):return True
    
    return False

# todo:to check: delete and replace everywhere by dict.update.
def setKeywords(wantedKeywords, keywords, preserve=False):   
    """For functions that proxy **keywords for others.
    and still want to pass them new keywords parameters
    wantedKeywords is a dict with keywords:value you want to pass
    """
    if not preserve:keywords.update(wantedKeywords)
    else:
        keywords_keys=list(keywords.keys())
        for k in list(wantedKeywords.keys()):
            if not k in keywords_keys:keywords[k]=wantedKeywords[k]
            
    return keywords
            
def setp1top(p1, p):
    for attr in dir(p1):
        if attr[0]=='_':continue            
        setattr(p, attr, getattr(p1, attr))             
            
def getAsDict(p):
    founds={}
    for attr in dir(p):
        if attr[0]=='_':continue            
        founds[attr]=getattr(p, attr)
    return founds
            
def _eval(typ=None, value=None):
    selfMethod='_eval'
    if typ==None or typ not in SUPPORTED_TYPES:
        raise wkexception.wkParameterTypeException('typ', str(SUPPORTED_TYPES), str(typ), fromClass='wk', fromMethod=selfMethod)
    
    if typ in ('str', 'date', 'ts', 'xml', 'color', 'url' ):return str(value)
    if typ=='wkDef':typ='dict'
    
    try:
        v = ct._eval(value)
    except:
        import sys
        raise wkexception.wkSystemException(str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]), fromClass='wk', fromMethod=selfMethod)
    
    if typ=='wkDef':typ='dict'
    if v!=None and not isinstance(v, ct._eval(typ)):raise wkexception.wkSystemException("Bad final resulting type:" + str(type(v)) + " on evaluation of value:" + str(value) + '. Type expected:' + str(ct._eval(typ)) + '.', fromClass='wk', fromMethod=selfMethod)
    
    return v