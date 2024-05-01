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


# 001: python 2 to 3 conversion

try:
    # D001: import org.python.core.PyLong
    import org.python.core.PyInteger
    import builtins
    
    # Detect Jython 1.1
    try:
        JYTHON_VERSION=2
        True
        builtins.globals()['tint']=int
        # D001: builtins.globals()['tlong']=int
        builtins.globals()['tfloat']=float
        builtins.globals()['tstr']=str
        builtins.globals()['ttuple']=tuple
        builtins.globals()['tlist']=list
        builtins.globals()['tdict']=dict
        builtins.globals()['tunicode']=str
        builtins.globals()['tbool']=bool  
        
    except Exception as e:
        JYTHON_VERSION=1

        # D001: # long: No more long
        """
        flong=builtins.long
        builtins.flong=flong
        builtins.tlong=org.python.core.PyLong
        class long(org.python.core.PyLong):
            def __init__(self, val=None):
                if val==None:org.python.core.PyLong.__init__(self)
                elif not isinstance(val, org.python.core.PyLong):org.python.core.PyLong.__init__(self, flong(val))
                else:org.python.core.PyLong.__init__(self, val)    
        """

        ## float
        ffloat=builtins.float
        builtins.ffloat=ffloat
        builtins.tfloat=org.python.core.PyFloat
        import org.python.core.PyFloat
        class float(org.python.core.PyFloat):
            def __init__(self, val=None):
                if val==None:org.python.core.PyFloat.__init__(self)
                elif not isinstance(val, org.python.core.PyFloat):org.python.core.PyFloat.__init__(self, ffloat(val))
                else:org.python.core.PyFloat.__init__(self, val)  
      
        ## str
        fstr=builtins.str
        builtins.fstr=fstr
        builtins.tstr=builtins.tunicode=org.python.core.PyString
        import org.python.core.PyString
        class str(org.python.core.PyString):
            def __init__(self, val=None):
                if val==None:org.python.core.PyString.__init__(self)
                elif not isinstance(val, org.python.core.PyString):org.python.core.PyString.__init__(self, fstr(val))
                else:org.python.core.PyString.__init__(self, val)

        ## int
        fint=builtins.int
        builtins.fint=fint
        builtins.tint=org.python.core.PyInteger
        import org.python.core.PyInteger
        class int(org.python.core.PyInteger):
            def __init__(self, val=None):
                if val==None:org.python.core.PyInteger.__init__(self)
                elif isinstance(val, org.python.core.PyString) and val.isdigit():org.python.core.PyInteger.__init__(self, fint(val))
                else:org.python.core.PyInteger.__init__(self, val)
        import org.python.core.PyList
        
        ## list
        flist=builtins.list
        builtins.flist=flist
        builtins.tlist=org.python.core.PyList
        class list(org.python.core.PyList):
            def __init__(self, val=None):
                self.copy_back(val=val, twist=0)
                
            def copy_back(self, val=None, twist=1):
                if twist:val=self
                
                if val==None:
                    if twist:return org.python.core.PyList()
                    else:org.python.core.PyList.__init__(self)
                elif isinstance(val, org.python.core.PyTuple) or isinstance(val, org.python.core.PyList) or isinstance(val, org.python.core.PyArray):
                    if twist:return org.python.core.PyList(*val)
                    else:org.python.core.PyList.__init__(self, *val)
                else:
                    if twist:return org.python.core.PyList(val)
                    else:org.python.core.PyList.__init__(self, val)
        builtins.list = list
        
        ## tuple
        import org.python.core.PyTuple
        builtins.ttuple=org.python.core.PyTuple
        class tuple(org.python.core.PyTuple):
            def __init__(self, val=None):
                self.copy_back(val=val, twist=0)
                
            def copy_back(self, val=None, twist=1):
                if twist:val=self
                
                if val==None:
                    if twist:return org.python.core.PyTuple()
                    else:org.python.core.PyTuple.__init__(self) 
                elif isinstance(val, org.python.core.PyTuple) or isinstance(val, org.python.core.PyList) or isinstance(val, org.python.core.PyArray):
                    if twist:return org.python.core.PyTuple(*val)
                    else:org.python.core.PyTuple.__init__(self, *val)
                else:
                    if twist:return org.python.core.PyTuple(val)
                    else:org.python.core.PyTuple.__init__(self, val)  
        builtins.tuple = tuple
        
        ## dict
        import org.python.core.PyDictionary
        builtins.tdict=org.python.core.PyDictionary
        """ The Nasty syntax to initialize a PyDictionary is : org.python.core.PyDictionary(*['b', 2, 'a', 1, 'c', 3]) """
        class dict(org.python.core.PyDictionary):
            def __init__(self, val=None):
                self.copy_back(val=val, twist=0)
                
            def copy_back(self, val=None, twist=1):
                if twist:val=self
                
                if isinstance(val, org.python.core.PyDictionary):
                    l=[]
                    for key in list(val.keys()):
                        l.append(key)
                        l.append(val[key])
                    
                    if twist:return org.python.core.PyDictionary(*l)
                    else:
                        org.python.core.PyDictionary.__init__(self, *l)
                    
                elif val==None:
                    if twist:return org.python.core.PyDictionary()
                    else:org.python.core.PyDictionary.__init__(self)
                    
                else:raise Exception('Unsupported type for dict !')
        builtins.dict = dict

        ## bool
        class bool(type(1)):
            def __init__(self, val = 0):
                if val:
                    type(1).__init__(self, 1)
                else:
                    type(1).__init__(self, 0)
            def __repr__(self):
                if self:return "True"
                else:return "False"
                
            def copy_back(self):
                if self:return org.python.core.PyInteger(1)
                else:return org.python.core.PyInteger(0)

            __str__ = __repr__
        builtins.bool = builtins.tbool = bool

        # M001:
        # builtins.False = bool(0)
        # builtins.True = bool(1)
        setattr(builtins, 'False', bool(0))
        setattr(builtins, 'True', bool(1))



    RUN_IN_JYTHON=True
    
except Exception as e:
    RUN_IN_JYTHON=False
    __builtins__['tint']=int
    # D001: __builtins__['tlong']=int
    __builtins__['tfloat']=float
    __builtins__['tstr']=str
    __builtins__['ttuple']=tuple
    __builtins__['tlist']=list
    __builtins__['tdict']=dict
    __builtins__['tunicode']=str
    __builtins__['tbool']=bool