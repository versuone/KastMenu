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
            if code!=None and not str(code).isdigit() and code>0 and code<1000:raise Exception ('Parameter Error: code. received:' + str(code) + ' of type:' + type(code) + '. Expected: a numeric value between 0 and 1000 !')
            if code!=None:self.__code=code
            else:self.__code=''
            if prefix!=None:self.__prefix=prefix
            else:self.__prefix=''
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

class BaseInformation:
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
            if code!=None and not str(code).isdigit() and code>0 and code<1000:raise Exception ('Parameter Error: code. received:' + str(code) + ' of type:' + type(code) + '. Expected: a numeric value between 0 and 1000 !')
            if code!=None:self.__code=code
            else:self.__code=''
            if prefix!=None:self.__prefix=prefix
            else:self.__prefix=''
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
    
    def warn(self, verbose=0, doPrint=True):
        import sys

        if verbose<5:message=self.short1()
        elif verbose<10:message=self.short2()
        else:message=self.__prefix + self.__class__.__name__ + ': ' + 'From class:' + str(self.__fromClass) + ', from method:' + str(self.__fromMethod) + ' ' + self.__message
        
        if doPrint:sys.stderr.write('\n' + message + '\n')
        else:return message


#-------------------------------------#
#  Specfic BaseExceptions/Information |
#-------------------------------------#


## Project: picxml
class picxmlBaseException(BaseException):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
        if prefix==None:prefix='Epicxml'
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)

class picxmlBaseInformation(BaseInformation):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
        if prefix==None:prefix='Ipicxml'
        BaseInformation.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)


## Project: kwad
class kwadBaseException(BaseException):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
        if prefix==None:prefix='EKAST'
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)

class kwadBaseInformation(BaseInformation):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None):
        if prefix==None:prefix='IKAST'
        BaseInformation.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)



#------------------------#
# Exceptions/Information |
#------------------------#


## Project: picxml
class picxmlParameterTypeException(picxmlBaseException):
    def __init__(self, fromClass, fromMethod, parm, expected, received, code=None, prefix=None):
        picxmlBaseException.__init__(self, fromClass, fromMethod, 'Incorrect type for ' + str(parm) + ', expected type:' + str(expected) + ', received:' + str(received) + '.', code=code, prefix=prefix)
class picxmlParameterException(picxmlBaseException):pass
class picxmlSystemException(picxmlBaseException):pass 
class picxmlXmlSyntaxException(picxmlBaseException):pass
class picxmlPxQueryException(picxmlBaseException):pass
class picxmlPxQueryNoNodeFoundException(picxmlBaseException):pass

class picxmlInformation(picxmlBaseInformation):pass


## Project: kwad
class kwadParameterTypeException(kwadBaseException):
    def __init__(self, fromClass, fromMethod, parm, expected, received, code=None, prefix=None):
        kwadBaseException.__init__(self, fromClass, fromMethod, 'Incorrect type for ' + str(parm) + ', expected type:' + str(expected) + ', received:' + str(received) + '.', code=code, prefix=prefix)
class kwadParameterException(kwadBaseException):pass
class kwadSystemException(kwadBaseException):pass
class kwadInformation(kwadBaseInformation):pass
class kwadSVNClientInitException(kwadBaseException):pass
class kwadUnsupportedOperationException(kwadBaseException):pass
class kwadSoftClassSyntaxException(kwadBaseException):pass
class kwadSoftClassDescriptorSyntaxException(kwadBaseException):pass
class kwadSoftClassRestrictorSyntaxException(kwadBaseException):pass
class kwadSoftClassCheckException(kwadBaseException):pass
class kwadSoftClassRestrictorCheckException(kwadBaseException):pass
class kwadSoftClassDescriptorCheckException(kwadBaseException):pass
class kwadSoftClassExecutionException(kwadBaseException):pass
class kwadXmlSyntaxException(picxmlBaseException):pass
class kwadXmlUnSupportedTagAttributeError(picxmlBaseException):pass
class kwadPxQueryException(kwadBaseException):pass
class kwadXNodeHasNoParentException(kwadBaseException):pass
class kwadOSNoOperationsFound(kwadBaseException):pass
class kwadOSNoOperationFound(kwadBaseException):pass
class kwadOSMoreThenOneOperationFound(kwadBaseException):pass
class kwadHostUserException(kwadBaseException):pass

class kwadInformation(kwadBaseInformation):pass


## Project: kwad/SoftClass
class kwadBaseSoftClassException(kwadBaseException):
    def __init__(self, softclass, fromMethod, message, code=None, prefix=None):
        from kwadlib.softclass import SoftClass
        if not isinstance(softclass, SoftClass):raise Exception ('Parameter Error: softclass. received:' + str(softclass) + ' of type:' + str(type(softclass)) + '. Expected: an instance of class SoftClass !')

        prefix='EKAST' + softclass.getTop().getBalSoftware().upper() + softclass.getName().upper()
        fromClass=softclass.__class__.__name__
        kwadBaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)
        
class kwadBaseSoftClassInformation(kwadBaseInformation):
    def __init__(self, softclass, fromMethod, message, code=None, prefix=None):
        from kwadlib.softclass import SoftClass
        if not isinstance(softclass, SoftClass):raise Exception ('Parameter Error: softclass. received:' + str(softclass) + ' of type:' + str(type(softclass)) + '. Expected: an instance of class SoftClass !')

        prefix='IKAST' + softclass.getTop().getBalSoftware().upper() + softclass.getName().upper()
        fromClass=self.__class__.__name__
        kwadBaseInformation.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)
        
class kwadSoftClassException(kwadBaseSoftClassException):pass
class kwadSoftClassParameterException(kwadBaseSoftClassException):pass
class kwadSoftClassSystemException(kwadBaseSoftClassException):pass
class kwadSoftClassInformation(kwadBaseSoftClassInformation):pass


## Project: kwad/Exit
class kwadBaseExitException(kwadBaseException):
    def __init__(self, config, fromMethod, message, code=None, prefix=None):
        prefix='EKAST' + config.getBelName().upper() + config.getBelSoftware().upper()
        kwadBaseException.__init__(self, 'Main', fromMethod, message, code=code, prefix=prefix)

class kwadBaseExitInformation(kwadBaseInformation):
    def __init__(self, config, fromMethod, message, code=None, prefix=None):
        prefix='IKAST' + config.getBelName().upper() + config.getBelSoftware().upper()
        kwadBaseInformation.__init__(self, 'Main', fromMethod, message, code=code, prefix=prefix)

class kwadExitException(kwadBaseExitException):pass
class kwadExitParameterException(kwadBaseExitException):pass
class kwadExitSystemException(kwadBaseExitException):pass
class kwadExitInformation(kwadBaseExitInformation):pass


## Project: kwad/Session
class SessionIsNotAttr(kwadBaseException):pass
class SessionObjectSignatureHasChanged(kwadBaseException):pass

# kldap:
class kwadLdapException(kwadBaseException):pass
class kwadLdapParameterException(kwadBaseException):pass
class kwadLdapSystemException(kwadBaseException):pass
class kwadLdapInformation(kwadBaseInformation):pass
class kwadLdapExecutionException(BaseException):
    def __init__(self, fromClass, fromMethod, message, ldap_exception, code=None, prefix=None, checks=None, checkstr=None):
        if ldap_exception!=None:self.ldap_exception = ldap_exception
        else:self.ldap_exception = None
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)
class kwadLdapAlreadyExistException(kwadBaseException):
    def __init__(self, fromClass, fromMethod, message, ldap_response=None, code=None, prefix=None, checks=None, checkstr=None):
        if ldap_response!=None:self.ldap_response = ldap_response
        else:self.ldap_response = None
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)
class kwadLdapInUseByInstanceException(kwadBaseException):
    def __init__(self, fromClass, fromMethod, message, ldap_instances=None, code=None, prefix=None, checks=None, checkstr=None):
        if ldap_instances!=None:self.ldap_instances = ldap_instances
        else:self.ldap_instances = None
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)
class kwadLdapMoreThanOneExistException(kwadBaseException):pass
class kwadLdapNotExistException(kwadBaseException):pass

# svn:
class kwadSVNxception(kwadBaseException):pass
class kwadSVNParameterException(kwadBaseException):pass
class kwadSVNSystemException(kwadBaseException):
    def __init__(self, fromClass, fromMethod, message, stdout_stderr=None, code=None, prefix=None, checks=None, checkstr=None):
        if stdout_stderr!=None:self.stdout_stderr = stdout_stderr
        else:self.stdout_stderr = None
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)
class kwadSVNNoSuchRevErrorE160006(kwadBaseException):
    def __init__(self, fromClass, fromMethod, message, stdout_stderr=None, code=None, prefix=None, checks=None, checkstr=None):
        if stdout_stderr!=None:self.stdout_stderr = stdout_stderr
        else:self.stdout_stderr = None
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)
class kwadSVNInformation(kwadBaseInformation):pass



# svn:
class kwadSSLException(kwadBaseException):pass
class kwadSSLParameterException(kwadBaseException):pass
class kwadSSLSystemException(kwadBaseException):pass
class kwadSSLInformation(kwadBaseInformation):pass



class kwadAccessDenied(BaseException):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None, lindex=None, lname=None, checks=None, checkstr=None):
        if lindex!=None:self.lindex = lindex
        else:self.lindex = None
        if lname!=None:self.lname = lname
        else:self.lname = None
        if checks!=None:self.checks = checks
        else:self.checks = None
        if checkstr!=None:self.checks = checkstr
        else:self.checkstr = None
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)


class kwadAccessNotAllowed(BaseException):
    def __init__(self, fromClass, fromMethod, message, code=None, prefix=None, lindex=None, lname=None, checks=None, checkstr=None):
        if lindex!=None:self.lindex = lindex
        else:self.lindex = None
        if lname!=None:self.lname = lname
        else:self.lname = None
        if checks!=None:self.checks = checks
        else:self.checks = None
        if checkstr!=None:self.checks = checkstr
        else:self.checkstr = None
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)


class kwadHTTPException(kwadBaseException):
    def __init__(self, fromClass, fromMethod, message, reason=None, code=None, prefix=None, checks=None, checkstr=None):
        self.reason = reason
        BaseException.__init__(self, fromClass, fromMethod, message, code=code, prefix=prefix)