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


class BaseException(Exception):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
            Exception.__init__(self, '') # python: cpickle needs proper super class init.
        
            if code!=None and not str(code).isdigit() and code>0 and code<1000:raise Exception ('Parameter Error: code. received:' + str(code) + ' of type:' + type(code) + '. Expected: a numeric value between 0 and 1000 !')
            if code!=None:self.code=code
            else:self.code=''
            if prefix!=None:self.prefix=prefix
            else:self.prefix=''
            self.__short1=None
            self.__short2=None
            self.__sube=None

            self.code=code
            self.fromClass=fromClass
            self.fromMethod=fromMethod
            self.__message=message

            if self.code!=None:self.prefix=self.prefix +'%03i' % self.code + ': '
            else:self.prefix=self.prefix + ': '
            self.__value = self.prefix + 'From class:' + str(self.fromClass) + ', from method:' + str(self.fromMethod) + ' ' + self.__message

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
        else:prefix=self.prefix
        if self.__short1!=None:message=self.__short1
        else:message=self.getTopMessage()
        
        return prefix + message
    
    def short2(self, noPrefix=False, noClassName=False):
        if noPrefix:prefix=''
        else:prefix=self.prefix
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

class BaseInformation:
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
            if code!=None and not str(code).isdigit() and code>0 and code<1000:raise Exception ('Parameter Error: code. received:' + str(code) + ' of type:' + type(code) + '. Expected: a numeric value between 0 and 1000 !')
            if code!=None:self.code=code
            else:self.code=''
            if prefix!=None:self.prefix=prefix
            else:self.prefix=''
            self.__short1=None
            self.__short2=None
            self.__sube=None
            
            self.code=code
            self.fromClass=fromClass
            self.fromMethod=fromMethod
            self.__message=message
            if self.code!=None:self.prefix=self.prefix +'%03i' % self.code + ': '
            else:self.prefix=self.prefix + ': '
            self.__value = self.prefix + 'From class:' + str(self.fromClass) + ', from method:' + str(self.fromMethod) + ' ' + self.__message

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
        else:prefix=self.prefix
        if self.__short1!=None:message=self.__short1
        else:message=self.getTopMessage()
        
        return prefix + message
    
    def short2(self, noPrefix=False, noClassName=False):
        if noPrefix:prefix=''
        else:prefix=self.prefix
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
        
    def warn(self, verbose=0):
        import sys

        if verbose<5:message=self.short1()
        elif verbose<10:message=self.short2()
        else:message=self.prefix + self.__class__.__name__ + ': ' + 'From class:' + str(self.fromClass) + ', from method:' + str(self.fromMethod) + ' ' + self.__message
            
        sys.stderr.write('\n' + message + '\n')


#-------------------------------------#
#  Specfic BaseExceptions/Information |
#-------------------------------------#


## Project: repoz
class repozBaseException(BaseException):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
        if prefix==None:prefix='ERepoz'
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)

class repozBaseInformation(BaseInformation):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
        if prefix==None:prefix='IRepoz'
        BaseInformation.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)


#------------------------#
# Exceptions/Information |
#------------------------#


## Project: repoz
class repozParameterTypeException(repozBaseException):
    def __init__(self, fromClass, fromMethod, parm, expected, received, code=None, prefix=None):
        self.parm=parm
        self.expected=expected
        self.received=received
        repozBaseException.__init__(self, fromClass, fromMethod, 'Incorrect type for ' + str(parm) + ', expected type:' + str(expected) + ', received:' + str(received) + '.', code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( repozParameterTypeException, (self.fromClass, self.fromMethod, self.parm, self.expected, self.received, self.code, self.prefix) )
    
class repozParameterException(repozBaseException):pass
class repozSystemException(repozBaseException):pass 

class repoPreExistingAliasException(repozBaseException):
    def __init__(self, fromClass, fromMethod, alias, code=None, prefix=None):
        self.alias=alias
        repozBaseException.__init__(self, fromClass, fromMethod, 'The alias:' + alias + ' already exists in the temporary repository !', code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( repoPreExistingAliasException, (self.fromClass, self.fromMethod, self.alias, self.code, self.prefix) )

class repoNotExistingAliasException(repozBaseException):
    def __init__(self, fromClass, fromMethod, alias, more, code=None, prefix=None):
        self.alias=alias
        self.more=more
        repozBaseException.__init__(self, fromClass, fromMethod, 'The Processor with alias:' + alias + ' do not exist into the temporary Repository ' + more + '. Use xpc, apc, mpc, jpc, tpc or lpc to add a Processor !', code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( repoNotExistingAliasException, (self.fromClass, self.fromMethod, self.alias, self.more, self.code, self.prefix) )

class repoNotExistingSourceException(repozBaseException):
    def __init__(self, fromClass, fromMethod, file, code=None, prefix=None):
        repozBaseException.__init__(self, fromClass, fromMethod, 'This File:' + file + ' do not Exist !', code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( repoNotExistingSourceException, (self.fromClass, self.fromMethod, self.code, self.prefix) )

class repoPreExistingTargetException(repozBaseException):
    def __init__(self, fromClass, fromMethod, file, aliases, old_pcs, code=None, prefix=None):
        self.file=file
        self.aliases=aliases
        self.old_pcs=old_pcs
        repozBaseException.__init__(self, fromClass, fromMethod, 'At least one processor: ' + str(aliases).replace("'", '')[1:-1] + ', already exits and is marked to be saved for the same target file:' + file + ' ! Advice: Use --new_pc (-n) to force the processor creation. You may also want to use the method: getOldPcs on this exception to list all the pre-existing Pcs.', code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( repoPreExistingTargetException, (self.fromClass, self.fromMethod, self.file, self.aliases, self.old_pcs, self.code, self.prefix) )
        
    def getOldPcs(self):
        return self.old_pcs

class repozOptionException(repozBaseException):
    def __init__(self, fromClass, fromMethod, message=None, code=None, prefix=None):
        if message!=None:more=' SubException is:' + message
        else:more=''
        repozBaseException.__init__(self, fromClass, fromMethod, 'Not supported option !' + more, code=code, prefix=prefix)
        
    # python bug (>2.4<=2.6.5), only concern Exception classes: (c)pickle is unable to call subclass with a different amount of args from moether Exception class !
    def __reduce__(self):
        return ( repozOptionException, (self.fromClass, self.fromMethod, self.code, self.prefix) )

class repozInformation(repozBaseInformation):pass