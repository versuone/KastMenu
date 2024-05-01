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




#-----------------------------------#
#  Global BaseException/Information |
#-----------------------------------#


class ctBaseException(Exception):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
            Exception.__init__(self, '') # python: cpickle needs proper super class init.
        
            if code!=None and not str(code).isdigit() and code>0 and code<1000:raise Exception ('Parameter Error: Unsupported Error code:' + str(code) + '! code should be a numeric value between 0 and 1000 !')
            if code!=None:self.__code=code
            else:self.__code=''
            if prefix!=None:self.__prefix=prefix
            else:self.__prefix='CT'
            self.__short1=None
            self.__short2=None
            self.__sube=None
            
            self.__code=code
            self.__fromClass=fromClass
            self.__fromMethod=fromMethod
            self.__message=message
            if self.__code!=None:self.__prefix=self.__prefix +'%03i' % self.__code + ': '
            else:self.__prefix=self.__prefix + ': '
            self.__value = self.__prefix + 'From class:' + str(self.__fromClass) + ', from method:' + str(self.__fromMethod) + ' ' + self.__message

    def __str__(self):
        return self.__value

    def setShort1(self, value):
        self.__short1=value    

    def setShort2(self, value):
        self.__short2=value

    def hasSubException(self):
        if self.__sube!=None:return True
        return False
    
    def getSubException(self):
        return self.__sube

    def setSubException(self, e):
        if not isinstance(e, Exception):raise Exception ('Parameter Error: e. received:' + str(e) + ' of type:' + type(e) + '. Expected: an instance of class Exception !')
        self.__sube=e  

    def short1(self, noPrefix=False):
        """
        Priority to arbitrary short message otherwise to top Message.
        """
        if noPrefix:prefix=''
        else:prefix=self.__prefix
        if self.__short1!=None:message=self.__short1
        else:message=self.getTopMessage()
        
        return prefix + message
    
    def short2(self, noPrefix=False, noClassName=False):
        if noPrefix:prefix=''
        else:prefix=self.__prefix
        if noClassName:className=''
        else:className=self.__class__.__name__ + ': '

        if self.__short2!=None:message=self.__short2
        else:message=self.getTopMessage()
        
        return prefix + className + self.getTopMessage()    
        
    def getMessage(self):
        return self.__message

    def setMessage(self, message):
        self.__message=message
        
    def getTopMessage(self):
        if self.hasSubException():
            sube=self.getSubException()
            if not hasattr(sube, 'getTopMessage'):return str(sube)
            return self.getSubException().getTopMessage()
        else:return self.getMessage()



class ctBaseInfomation:
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
            if code!=None and not str(code).isdigit() and code>0 and code<1000:raise Exception ('Parameter Error: Unsupported Error code:' + str(code) + '! code should be a numeric value between 0 and 1000 !')
            if code!=None:self.__code=code
            else:self.__code=''
            if prefix!=None:self.__prefix=prefix
            else:self.__prefix='CT'
            self.__short1=None
            self.__short2=None
            self.__sube=None

            self.__code=code
            self.__fromClass=fromClass
            self.__fromMethod=fromMethod
            self.__message=message
            if self.__code!=None:self.__prefix=self.__prefix +'%03i' % self.__code + ': '
            else:self.__prefix=self.__prefix + ': '
            self.__value = self.__prefix + 'From class:' + str(self.__fromClass) + ', from method:' + str(self.__fromMethod) + ' ' + self.__message

    def __str__(self):
        return self.__value

    def setShort1(self, value):
        self.__short1=value    

    def setShort2(self, value):
        self.__short2=value

    def hasSubException(self):
        if self.__sube!=None:return True
        return False
    
    def getSubException(self):
        return self.__sube

    def setSubException(self, e):
        if not isinstance(e, Exception):raise Exception ('Parameter Error: e. received:' + str(e) + ' of type:' + type(e) + '. Expected: an instance of class Exception !')
        self.__sube=e  

    def short1(self, noPrefix=False):
        """
        Priority to arbitrary short message otherwise to top Message.
        """
        if noPrefix:prefix=''
        else:prefix=self.__prefix
        if self.__short1!=None:message=self.__short1
        else:message=self.getTopMessage()
        
        return prefix + message
    
    def short2(self, noPrefix=False, noClassName=False):
        if noPrefix:prefix=''
        else:prefix=self.__prefix
        if noClassName:className=''
        else:className=self.__class__.__name__ + ': '

        if self.__short2!=None:message=self.__short2
        else:message=self.getTopMessage()
        
        return prefix + className + self.getTopMessage()    
        
    def getMessage(self):
        return self.__message

    def setMessage(self, message):
        self.__message=message
        
    def getTopMessage(self):
        if self.hasSubException():
            return self.getSubException().getTopMessage()
        else:return self.getMessage()
    
    def warn(self, verbose=0):
        import sys
        if verbose<5:message=self.short1()
        elif verbose<10:message=self.short2()
        else:message=self.__prefix + self.__class__.__name__ + ': ' + 'From class:' + str(self.__fromClass) + ', from method:' + str(self.__fromMethod) + ' ' + self.__message
            
        sys.stderr.write('\n' + message + '\n')


#------------------------#
# Exceptions/Information |
#------------------------#


## Project: ct

class ctParameterTypeException(ctBaseException):
    def __init__(self, name, typeExpected, typeReceived, fromClass=None, fromMethod=None, code=None, prefix=None):
        self.name=name 
        self.typeExpected=typeExpected 
        self.typeReceived=typeReceived
        ctBaseException.__init__(self, fromClass, fromMethod, "Received Bad pamameter type for:" + name  + \
          ". Type Expected:" + str(typeExpected) + \
          ". Type Received:" + str(typeReceived), code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( ctParameterTypeException, (self.name, self.typeExpected, self.typeReceived, self.fromClass, self.fromMethod, self.code, self.prefix) )

class ctParameterException(ctBaseException):

    def __init__(self, name, why, fromClass=None, fromMethod=None, code=None, prefix=None):
        self.name=name
        self.why=why
        ctBaseException.__init__(self, fromClass, fromMethod, "Received Bad pamameter for:" + name  + ". Reason:" + str(why), code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( ctParameterException, (self.name, self.why, self.fromClass, self.fromMethod, self.code, self.prefix) )

class ctSystemException(ctBaseException):

    def __init__(self, why, fromClass=None, fromMethod=None, code=None, prefix=None):
        self.why=why
        ctBaseException.__init__(self, fromClass, fromMethod, why, code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( ctSystemException, (self.why, self.fromClass, self.fromMethod, self.code, self.prefix) )