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


from . import tmplxception
import optparse

MARK_BEGIN='[['
MARK_END=']]'
MARK_SINGLE='$'
ALLOWED_OPERATORS=('<', '>', '=')
usage=       \
"\nusage:"   + \
"\n====="  + \
"\n"  + \
"\nlinears operations:"
"\n------------------"
"\n_ Simple replace syntaxe: " + MARK_BEGIN + 'some text' + MARK_END                          + \
"\n_ Replacement syntaxe: some text " +  MARK_SINGLE + 'var1 more text'            + \
"\n    var will be replaced by the value of a known variable named var1."    + \
"\n_ Condition syntaxe: " + MARK_BEGIN + '?' + 'var1<var2:some text that may contains variables'  + MARK_END        + \
"\n    Condition type can be: ? (test true), or ! (test false)"                    + \
"\n  Operators can be " + str(ALLOWED_OPERATORS) + '.'
"\n"  + \
"\nBlocs operations:" +\
"\n----------------"  +\
"\n"  + \
"\n_ Condition syntaxe: " +\
"\n    [[bk_?$var1=yes]]" +\
"\n    some text," +\
"\n    that may contains linears operations." +\
"\n    more text" +\
"\n    [[ebk]]" +\
"\n  Operators can be " + str(ALLOWED_OPERATORS) + '.' +\
"\n"  + \
"\n_ Iteration syntaxe: " +\
"\n    [[bk_l $var_list]]" +\
"\n    some text," +\
"\n    that may contains linears operations." +\
"\n    more " + MARK_BEGIN + MARK_SINGLE + '_ITEM' + MARK_END + "text" +\
"\n    [[ebk]]" +\
"\n"  + \
"\n    The variable "  + MARK_BEGIN + MARK_SINGLE + '_ITEM' + MARK_END + ": will be replaced by the next item of the list." +\
"\n    [[bk_*]] and [[ebk]] marks must start from the begining of the line."

# D001:
# False=0
# True=1

## Internal softclass:
SKIP_BLOCK=1
KEEP_BLOCK=2
## ITER_BLOCK=list



class  TmplMaker:
        
    def __init__(self, listIn=None, fileIn=None, vars=None, fileOut=None):
        self.init(listIn=listIn, fileIn=fileIn, vars=vars, fileOut=fileOut)
        
    def init(self, listIn=None, fileIn=None, vars=None, fileOut=None):
        selfMethod='__init__'
        self.fileOut=None
        self.linesOut=[]
        
        if (listIn!=None and fileIn!=None) or (listIn==None and fileIn==None):raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Just one of listIn or fileIn must given.')                                    
        if fileIn!=None:
            import os    
            fileIn=os.path.normpath(str(fileIn))            
            if not os.path.isfile(fileIn):raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'fileIn: ' + fileIn + ' Must Exist.')                                    
            f=open(fileIn, 'r')
            self.lines=list(f.readlines())
            f.close()
        else:
            if not isinstance(listIn, list):raise tmplxception.tmplmkParameterTypeException(str(self.__class__), selfMethod, 'listIn', 'list', str(listIn))
            self.lines=list(listIn)
            
        if vars!=None and not isinstance(vars, dict):raise tmplxception.tmplmkParameterTypeException(str(self.__class__), selfMethod, 'vars', 'dict', str(vars))
        if vars!=None:self.vars=dict(vars)
        else:self.vars=dict()
                    
        if fileOut!=None:
            self.fileOut=fileOut
            import os    
            self.fileOut=os.path.normpath(str(self.fileOut))
            fd=open(self.fileOut, 'wb')
            fd.close()
            
    # A003
    def setRepozInfos(self, repoz, alias):
        import weakref
        self.__repoz=weakref.ref(repoz)   
        self.__alias=alias       

    def getRepozInfos(self):
        if self.__repoz==None or self.__repoz()==None:return None
        return {'repoz': self.__repoz(), 'alias': self.__alias}

    def clearRepozInfos(self):
        self.__repoz=None
        self.__alias=None
        
    def _SessionBeforStore_(self):
        self.clearRepozInfos()
        
    def operate(self):
  
        do_skip_to_eblk=False
        do_iter=False        
        do_end_iter=False        
        treat_blocks=True
        
        for index in range(0, len(self.lines)):
            line=self.lines[index]           
            
            if do_skip_to_eblk and not line.startswith(MARK_BEGIN + 'ebk' + MARK_END):continue
            if line.startswith(MARK_BEGIN + 'ebk' + MARK_END):
                treat_blocks=True
                do_skip_to_eblk=False
                if do_iter:
                    do_iter=False
                    do_end_iter=True                
                continue
                        
            if do_end_iter:
                self.__endIter(index, iters, iter_list, self.linesOut)
                do_end_iter=False
            
            if do_iter:
                iters.append(line)            
                continue
            line=self.__treatMark(line, treat_blocks=treat_blocks)             

            if isinstance(line, str):self.linesOut.append(line)
            else:
                softclass=line
                ## Conditioned Block
                if softclass==SKIP_BLOCK:
                    treat_blocks=False
                    do_skip_to_eblk=True
                    continue
                elif softclass==KEEP_BLOCK:
                    treat_blocks=False
                    continue
                else:
                ## Iteration
                    treat_blocks=False
                    iters=[]
                    iter_list=softclass
                    do_iter=True
                    
        if do_end_iter:self.__endIter(index, iters, iter_list, self.linesOut)
                    
        if self.fileOut!=None:
            fd=open(self.fileOut, 'wb')
            for line in self.linesOut:
                fd.write(bytes(line, 'utf-8'))
            fd.close()

        return self.linesOut

    def show(self, sb=None, **prt_keywords):
        """ Facade for Repository """
        from io import StringIO
        if sb==None:sb=StringIO()

        sb.write(''.join(self.operate()))

        return sb
        
    def __endIter(self, index, iters, iter_list, linesOut):
        for i in range(0, len(iter_list)):
            for j in range(0, len(iters)):
                vars=dict(self.vars)
                vars.update({'_ITEM':iter_list[i]})
                l=self.__treatMark(iters[j] , treat_blocks=False, vars=vars) 
                linesOut.append(l) 
                

    def __treatMark(self, line, treat_blocks=True, vars=None):
        start=line.find(MARK_BEGIN)
        if start<0:
            return line
        end=line.find(MARK_END)
        if end<0:
            return line
        if end<start:
            return line
        pattern=line[start + len(MARK_BEGIN):end]            
        
        if treat_blocks and (pattern.startswith('bk') and start==0):
            ## Block operations
            return self._evaluate_block(pattern)
        else:
            ## Linears operations
            content=self._evaluate_line(pattern, vars=vars)

            line=line[0:start] + str(content) + line[end + len(MARK_END):]
            return self.__treatMark(line, treat_blocks=False, vars=vars)
                
    def _evaluate_block(self, pattern):
        selfMethod='_evaluate_block'
        test=True
        ## pattern starts with : [[bk_*
        pattern=pattern[3:]
        
        ## linear condition
        if pattern[0] in ('?', '!'):
            end=pattern.find(':')
            if len(pattern) <= 3:raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Condition: ' + pattern + ' is to short.' + usage)
            condition=pattern[1:]
            
            test=self.__treatCond(condition)
                
            if pattern[0]=='!':
                if test:test=False
                else:test=True
                
            ## softclass:
            if test:return KEEP_BLOCK
            return SKIP_BLOCK
        elif pattern[0]=='l':
            iter_var=pattern[1:]
            iter_list=None
            try:
                iter_list=self.vars[iter_var[len(MARK_SINGLE)+1:].strip()]
            except:
                raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Block Iteration shouild contains a known variable. ' + 'SubException:' + str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]) + usage)
            if not isinstance(iter_list, list):raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Block Iteration variable should be a list. Variable Name:' + str(iter_var) + ', Variable value' + str(iter_list) + '.')
            return iter_list
        else:return SKIP_BLOCK
        
        ## ITER_BLOCK=5

    def _evaluate_line(self, pattern, vars=None):
        selfMethod='_evaluate_line'
        content=pattern
        
        ## linear condition
        if pattern[0] in ('?', '!'):
            end=pattern.find(':')
            if end <= 3:raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Condition: ' + pattern + ', Unable to find ":" separator in your condition.' + usage)                                    
            condition=pattern[1:end]            
            if end + 1 >= len(pattern)-1:content=''
            else:content=pattern[end + 1:]
            
            test=self.__treatCond(condition)
                
            if pattern[0]=='!':
                if test:test=False
                else:test=True
            if not test:content=''

        content=self.__treatVar(content, vars=vars)

        return content

    def __treatCond(self, condition):
        selfMethod='__treatCond'
        test=False
        while True:
            op=condition.find('<')
            if op > 0 and op < len(condition) - 1: 
                left=self.__treatVar(condition[0:op]).strip()
                right=self.__treatVar(condition[op+1:]).strip()
                if len(left)==0 or len(right)==0:raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Condition: ' + condition + ', should contains 2 non null arguments.' + usage)
                test=left < right
                break
            op=condition.find('>')
            if op > 0 and op < len(condition) - 1:
                left=self.__treatVar(condition[0:op]).strip()
                right=self.__treatVar(condition[op+1:]).strip()
                if len(left)==0 or len(right)==0:raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Condition: ' + condition + ', should contains 2 non null arguments.' + usage)                
                test=left > right
                break                       
            op=condition.find('=')
            if op > 0 and op < len(condition) - 1:                  
                left=self.__treatVar(condition[0:op]).strip()
                right=self.__treatVar(condition[op+1:]).strip()
                if len(left)==0 or len(right)==0:raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Condition: ' + condition + ', should contains 2 non null arguments.' + usage)
                test=left == right                   
                break                             
            raise tmplxception.tmplmkSystemException(str(self.__class__), selfMethod, 'Your Condition: ' + condition + ', Unable to find an allowed operator in your condition. Allowed operators are:' + str(ALLOWED_OPERATORS) + '. ' + usage)                                                        
            break       
        
        return test 
            
    def __treatVar(self, value, vars=None):
        if vars==None:vars=self.vars
        if value.find(MARK_SINGLE) >= 0:return replaceVar(lineIn=value, vars=vars)
        else:return value
                
def replaceVar(lineIn=None, listIn=None, vars=None):
        selfMethod='replaceVar'    
        if (listIn!=None and lineIn!=None) or (listIn==None and lineIn==None):raise tmplxception.tmplmkSystemException('Main', selfMethod, 'Just one of listIn or lineIn must given.')
        if listIn!=None and not isinstance(listIn, list):raise tmplxception.tmplmkParameterTypeException('Main', selfMethod, 'listIn', 'list', str(listIn))
        if lineIn!=None and not isinstance(lineIn, str):raise tmplxception.tmplmkParameterTypeException('Main', selfMethod, 'lineIn', 'str', str(lineIn))
        if not isinstance(vars, dict):raise tmplxception.tmplmkParameterTypeException('Main', selfMethod, 'vars', 'dict', str(vars))
        
        if lineIn!=None:strIn=lineIn
        else:strIn='&&&&&'.join(listIn)
        for var in vars:
            strIn=strIn.replace(MARK_SINGLE + var, str(vars[var]))
        
        if lineIn!=None:return strIn
        else:return strIn.split('&&&&&')




#--------------------#
# Processor Commands #
#--------------------#


#=== xpath ===#

def xpath_options(parser):

    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option("-H", "--HELP", dest="HELP", action="store_true", default=False, help="Shows the processor extended options.")
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False, help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")

    #-- Print extended options:
    og=optparse.OptionGroup(parser, 'Print extended options', description='The following options are allowed in conjunction with command show and save commands.')
    parser.add_option_group(og)
    
    parser.add_option("-a", "--alias", dest="alias", help="The repoz entry alias.")
    
def save_and_show_options(parser):

    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option('-a', "--all", dest="all", action="store_true", default=False, help="(default False) If used, save all processors.")
    parser.add_option("-x", "--xforce", dest="xforce", action="store_true", default=False, help="(default False) force writing with no check and regardingless to descriptor file. BE CAUTIOUS !")

def xpath_usage():
    return """
    Supported xpath commands are: save, show

    For help on command type: 
        h (or help) <command>
    """
    
def save_and_show_usage():
    return """
    Save the current mounted  processor,
    or the whole processor with the --all (-a) option.
    The best practice is to use --all.

    Syntax:
    -------
    save [--all]
    """

def xpath_command(tm, command, pcInfo, fct_save=None, verbose=0, sb=None):
    self_funct='xpath_command'
    ALLOWED_COMMANDS=('show', 'save')
    import shlex
    
    args=shlex.split(command)
    command=args[0]
    del args[0]
    
    if command not in ALLOWED_COMMANDS:raise tmplxception.tmplmkSystemException('Main', self_funct, 'UnSupported command:' + command.split()[0] + '. Supported commands are:' + str(ALLOWED_COMMANDS)[1:-1].replace("'", '') + ' !')
    
    parser = optparse.OptionParser(xpath_usage())
    if command in ('save', 'show'):save_and_show_options(parser)    
    else:xpath_options(parser)
    
    try:(options, xpaths) = parser.parse_args(args)    
    except:raise tmplxception.tmplmkOptionException('Main', self_funct) 
    
    if verbose==0:verbose=options.verbose
        
    if command in ('show', 'save'):
        
        if command=='show':

            if len(xpaths)!=0:raise tmplxception.epicxmlSystemException('Main', self_funct, 'No arguments is allowed with the show command !')
            tm.show(sb=sb, **{})
            return

        print_keywords={'all':options.all}
        fct_save(alias=pcInfo.getAlias(), sb=sb, force=options.xforce, **print_keywords)
        return




#------#
# Main #
#------#


def main(args):
    temp=TmplMaker(fileIn='test.tmpl', fileOut='test.out', vars={'var1':'yes', 'var2':[1, 2, 3], 'A1':'1234', 'A2':456, 'A3':'1234'})
    #print temp.operate()

if __name__ == '__main__':  
    import sys
    main(sys.argv)