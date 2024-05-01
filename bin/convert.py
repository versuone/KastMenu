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


SELF_MODULE='convert'
CONVERT_HOME = None
DESC_SUFFIXES = ('xml', 'swagger', 'json', 'yaml', 'hcl')
DESC_TYPES=('softclass', 'k8')

##########
## Main ##
##########

"""
e.g. test:
cd /opt/kastmenu/current/bin
- menu may be replaced by menu1 or menu2.

# from xaml:
# ----------
# --toyaml:
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.xml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toyaml -v300
# --tohcl
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.xml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --tohcl -v300

# from yaml:
# ----------
# --toxml: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.yaml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toxml -v300
# --tohcl: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.yaml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --tohcl -v300

# from hcl:
# ---------
# --toxml: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.hcl --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toxml -v300
# --toyaml: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.hcl --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toyaml -v300 
"""


def usage():
    return """
convert <file_source.xml|.yaml|.hcl|.json|.jinja|.mako>
convert <file_source[.xml|.yaml|.hcl|.json> --to[yaml|hcl|json]

This command accept only one sole argument: <file_source>
Note: <file_source> must be properly suffixed !

By default the command will convert any input file to xml.
With Options: --toyaml, --tok8yaml, --tohcl or --tojson
Will convert any input file yaml, hcl or json. 


--------------
| e.g. tests |
--------------
cd /opt/kastmenu/current/bin
- menu may be replaced by menu1 or menu2.

# from xaml:
# ----------
# --toyaml:
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.xml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toyaml -v300
# --tohcl
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.xml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --tohcl -v300

# from yaml:
# ----------
# --toxml: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.yaml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toxml -v300
# --tohcl: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.yaml --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --tohcl -v300

# from hcl:
# ---------
# --toxml: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.hcl --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toxml -v300
# --toyaml: 
./convert  -f /opt/kastmenu/current/samples/kastmenu/menu.hcl --file_desc  /opt/kastmenu/current/conf/descs/menu.desc.xml --toyaml -v300
"""

def call(file_source, file_desc = None, show_dft = False, toyaml = False, tok8yaml=False, tohcl = False, toterra=False, tojson = False, checkonly = False, emhclcheck = False,
        tmpl_kws = None, temp_dir=None, keep_temp_dir = False, aliases = None, notcase = False, desconly = False, doStdout=True, verbose = 0):
    from kwadlib import epicxmlp
    if file_desc == None: force = True
    else:force = False
    if temp_dir == None:raise Exception('temp_dir is required !')
    nn = epicxmlp.digest(file_desc=file_desc, file_rest=None, file_source=file_source, capSensitive=not notcase, force=force, showResultingSourceOnly=False, temp_dir=temp_dir, tmpl_kws=tmpl_kws, aliases=aliases, keep_temp_dir=keep_temp_dir, get_desc_only=desconly, verbose=verbose)
    if checkonly:return

    if desconly:
        from io import StringIO
        import json as jsonmod
        sb = StringIO()

        if tojson:
            json = nn.printJSON(doChild=True, doCT = False, to_yaml_or_hcl = True)
            sb.write(jsonmod.dumps(json, sort_keys=False, indent=4, ensure_ascii=False))
        elif toterra:
            sb_names = StringIO()
            json, json_names = nn.printJSON(doChild=True, doCT = False, to_yaml_or_hcl = True, doTerraNames=True)
            sb.write(jsonmod.dumps(json, sort_keys=False, indent=4, ensure_ascii=False))
            sb_names.write(jsonmod.dumps(json_names, sort_keys=False, indent=4, ensure_ascii=False))
        elif toyaml:
            sb = nn.printYAML(doChild=True, step=6)
        elif tohcl:
            sb = nn.printHCL(doChild=True, indent='', step=6)
        else: # xml
            sb = nn.printXml(doChild=True, indent='', step=4)

        if doStdout:print('\n\n\n' + sb.getvalue())

        if toterra:return sb, sb_names
        else:return sb

    if not tojson and toyaml:sb = nn.printYAML(tok8yaml=tok8yaml, doChild=True, noDft=not show_dft, noDftRaise=False, noNone=not show_dft, fct_omit=None)
    elif toterra:
        sb = nn.printHCL(doTerraNames=True, doChild=True, indent='', step=4, noDft=not show_dft, noDftRaise=False, noNone=not show_dft, fct_omit=None)
    elif tohcl:
        sb = nn.printHCL(doChild=True, indent='', step=4, noDft=not show_dft, noDftRaise=False, noNone=not show_dft, fct_omit=None)
    elif tojson:
        from io import StringIO
        import json as jsonmod
        sb = StringIO()
        json = nn.printJSON(to_yaml = True, tok8yaml=tok8yaml, doChild=True, noDft=not show_dft, noDftRaise=False, noNone=not show_dft, fct_omit=None)
        sb.write(jsonmod.dumps(json, sort_keys=False, indent=4, ensure_ascii=False))
    else:sb = nn.printXml(doChild=True, indent='', step=4, doSpaceWrapEq=False, doLBBeforTag=True, doLBBeforAttr=True, noDft=not show_dft, noDftRaise=False, noNone=not show_dft, noComment=False, _nbstep=0, _sb=None, fct_omit=None)

    if emhclcheck:
        import pygohcl
        import json

        d = pygohcl.loads(sb.getvalue())

        if doStdout:print(json.dumps(d, indent=2, ensure_ascii=False))

    else:
        if doStdout:print('\n\n\n' + sb.getvalue())

    return sb

def main(args, aliases=None, doStdout = True):
    self_funct='main'
    from kwadlib import tools, xception
    from os import path, makedirs
    import optparse
    import sys
    bsl = None
    KAST_CONFS = tools.getKastConfs()
    if aliases == None: aliases = {}

    parser = optparse.OptionParser(usage())
    parser.add_option("-f", "--file_source", dest="file_source", help="(Optional) file_source: a file containing one or many softclasses separated by --- or ...\n Exclusive with using the <bals> argument and file_dir (--cacdir, -c) or STDIN pushing directly softclass source into the pipe.\this file can be either: xml, hcl or yaml and jinja or mako e.g.: my.yaml.jinja or my.xml.mako.")
    parser.add_option('-D', "--file_desc", dest="file_desc", help="A file descriptor that is used to check the input file. Allowed suffixes are: %s\n"
        "Notice: json, yaml, hcl are accepted if they were generated by convert. swagger are standard yaml OpenApi swagger files." %  ', '.join(DESC_SUFFIXES))
    parser.add_option("-v", "--verbose", dest="verbose", type=int, default=0, help="The verbose level.")
    parser.add_option("--toxml", dest="dummy", action="store_true", default=False, help="(optional) parse to xml, No need this is the default.")
    parser.add_option("--toyaml", dest="toyaml", action="store_true", default=False, help="(optional) Instead of parsing to xml, this will parse to yaml.")
    parser.add_option("--tok8yaml", dest="tok8yaml", action="store_true", default=False, help="(optional) Instead of parsing to xml, this will parse to yaml. tok8yaml will withdraw the top tag.")
    parser.add_option("--tohcl", dest="tohcl", action="store_true", default=False, help="(optional) Instead of parsing to xml, this will parse to hcl.")
    parser.add_option("--tojson", dest="tojson", action="store_true", default=False, help="(optional) Instead of parsing to xml, this will parse to json.")
    parser.add_option("--toterra", dest="toterra", action="store_true", default=False, help="(optional) Instead of parsing to xml, this will parse to an hcl file (With --desconly also provided to a json file) but with names expected by Terraform (All tag names in lower cases...).")
    parser.add_option("--desconly", dest="desconly", action="store_true", default=False, help="(optional) This will output the associated descriptor file as xml (default), yaml, hcl, json or terra file (depending if --toyaml, --toyhcl, --tojson, --toterra is provided).")
    parser.add_option('-t', '--show_dft', dest="show_dft", action="store_true", default=False, help="(optional) By default Attributes with value matching the default value into the descriptor are not shown ! if --show_dft (-t) is provided they would be shown.")
    parser.add_option("--temp_dir", dest="temp_dir", help="Temporary directory (optional usefull for mako or jinja debug).")
    parser.add_option("--keep_temp_dir", dest="keep_temp_dir", action="store_true", default=False, help="This will keep the temporary dir ! Allowing to see all the intermediate state will parsing the file. e.g: from mako, jinja, yaml, hcl to xml.\n Beware Parsing is usually done in memory, keeping the resulting files into temp_dir could be a security breach.")
    parser.add_option("--notcase", dest="notcase", default=False, action="store_true", help="Case sensitivity, Do we ignore tag case.")
    parser.add_option('-c', '--checkonly', dest="checkonly", default=False, action="store_true", help="Check only.")
    parser.add_option("--emhclcheck", dest="emhclcheck", default=False, action="store_true", help="Internal GR check.")
    parser.add_option("--tmpl_kws", dest="tmpl_kws", help="(optional) A set of parameters (a CoolTyped dict) to feed mako or jinja with, when the softclass file found into the file_dir rather than beeing an .xml, .yaml or .hcl file is ending by .jinja or .mako (e.g. myfile.xml.jinja or myfile.yaml.jinja).")

    #-- From STDIN:
    og=optparse.OptionGroup(parser, 'STDIN Options', description='When using kact from stdin. E.g.: cat my_file_source[.xml|.yaml|.hcl|.xml.jinja|.yaml.jinja|.hcl.jinja|.xml.mako|.yaml.mako...] | kact -v3, kact cannot gess the file type from the suffixe. So it must be provided.')
    parser.add_option_group(og)
    og.add_option("--xml", dest="file_type_xml", action="store_true", default=False, help="(STDIN only) The type of the input combined_file is xml")
    og.add_option("--hcl", dest="file_type_hcl", action="store_true", default=False, help="(STDIN only) The type of the input combined_file is hcl")
    og.add_option("--yaml", dest="file_type_yaml", action="store_true", default=False, help="(STDIN only) The type of the input combined_file is yaml")
    og.add_option("--mako", dest="file_type_mako", action="store_true", default=False, help="(STDIN only) The type of the input combined_file is mako works together with --xml, --yaml or --hcl.")
    og.add_option("--jinja", dest="file_type_jinja", action="store_true", default=False, help="(STDIN only) The type of the input combined_file is jinja with --xml, --yaml or --hcl.")

    (options, args) = parser.parse_args(args=args)
    verbose=options.verbose

    file_desc = None
    if options.file_desc != None:
        if not path.isfile(options.file_desc):raise xception.kwadSystemException('Main', self_funct, 'Incorect Option --file_desc: %s, should Exist !' % options.file_desc)
        file_desc = options.file_desc
    else:
        raise xception.kwadSystemException('Main', self_funct, 'Option --file_desc (-D) is required !')


    ## aliases:
    aliases.update(KAST_CONFS)

    ## Retreives temp_dir:
    if options.temp_dir != None: temp_dir = options.temp_dir
    else:
        temp_dir = tools.getTempDir() + '/convert/' + tools.genUid()
        if not path.isdir(temp_dir):makedirs(temp_dir)

    tools.verbose(SELF_MODULE + ': Temporary dir is: ' + temp_dir + '.', level=verbose, ifLevel=50, indent='', logFile=verbose)


    # tmpl_kws
    if options.tmpl_kws!=None:
        try:
            from kwadlib import ct
            tmpl_kws=ct.dress(options.tmpl_kws)
        except:
            print('Option --tmpl_kws incorrect: Must be a CoolTyped expression of a dict ! Your value:' + str(options.tmpl_kws) + '.')
            raise
    else:tmpl_kws={}
    
    try:
        if len(args)!=0:raise xception.kwadSystemException('Main', self_funct, 'No argument is supported !')

        file_source = None

        # SoftClass file From STDIN:
        # -----------------------
        wrk_source = None
        wrk_suffixe = None
        wrk_do_jinja = False
        wrk_do_mako = False
        l = [options.file_type_xml, options.file_type_yaml, options.file_type_hcl]
        l.sort()
        if not sys.stdin.isatty():  # Has stdin input:
            if options.file_source != None:
                raise xception.kwadSystemException('Main', self_funct, "Option: --file_source (-f) is not allowed when injecting softclass to STDIN !")
            # Input file type:
            if l == [False, False, False]:
                raise xception.kwadSystemException('Main', self_funct, "When Retreiving custon file from STDIN the file type must be provided ! E.g.: --xml, --hcl or --yaml.")
            elif l != [False, False, True]:
                raise xception.kwadSystemException('Main', self_funct, "Only one file type must be provided ! E.g.: --xml, --hcl or --yaml. Found many !")
            if options.file_type_jinja and options.file_type_mako:
                raise xception.kwadSystemException('Main', self_funct, "Options --jinja and --mako are not allowed together !")
            if options.file_type_xml:
                wrk_suffixe = 'xml'
            elif options.file_type_yaml:
                wrk_suffixe = 'yaml'
            elif options.file_type_hcl:
                wrk_suffixe = 'hcl'
            wrk_do_jinja = options.file_type_jinja
            wrk_do_mako = options.file_type_mako

            tools.verbose(SELF_MODULE + ': Retreiving softclass file from STDIN.', level=verbose, ifLevel=10, indent='', logFile=verbose)
            wrk_source = sys.stdin.read()

        else:
            if not options.desconly:
                if options.file_source == None:
                    raise xception.kwadSystemException('Main', self_funct, "Option: --file_source (-f) is required when not provided by STDIN (the Pipe) !")
                if (options.file_type_xml, options.file_type_yaml, options.file_type_hcl) != (False, False, False):
                    raise xception.kwadSystemException('Main', self_funct, "Options --xml, --hcl or --yaml are not allowed ! They are only suppported when retreiving softclass file from STDIN (the pipe).")
                if options.file_type_jinja and options.file_type_mako:
                    raise xception.kwadSystemException('Main', self_funct, "Options --jinja or --mako are not allowed. They are only suppported when retreiving softclass file from STDIN (the pipe).")

        if options.file_source:
            if not path.isfile(options.file_source):
                raise xception.kwadSystemException('Main', self_funct, "Uncorrect options --file_source (-f): %s. This file do not exists !" % options.file_source)
            fd = open(options.file_source)
            wrk_source = fd.read()
            fd.close()
            f = options.file_source
            if f.endswith('.jinja'):
                f = f[:-6]
                wrk_do_jinja = True
            elif f.endswith('.mako'):
                f = f[:-5]
                wrk_do_mako = True
            s = f.split('.')[-1]
            if s not in ('xml', 'yaml', 'hcl'):
                raise xception.kwadSystemException('Main', self_funct, "Uncorrect options --file_source (-f): %s. The suffixe should be either xml, yaml or hcl ! Even if ends with jinja or mako should be for instance: my.xml.jinja or my.yaml.mako, ..." % options.file_source)
            wrk_suffixe = s

        if wrk_source != None:
            if options.file_source != None:
                more = options.file_source
            else:
                more = 'STDIN (the Pipe)'
            from kwadlib.tools import Convert
            if wrk_do_jinja:
                wrk_source = Convert.jinja(wrk_source, temp_dir=temp_dir, tmpl_kws=tmpl_kws)
            elif wrk_do_mako:
                wrk_source = Convert.mako(wrk_source, temp_dir=temp_dir, tmpl_kws=tmpl_kws)

            """ From STDIN (the pipe) pr from a file -f : the content should be like:
            Example 1:
            ----------
cat << EOF | kact -v100 --xml
<ssl type ='softclass' bsl='middleware§jss.ssl' dir='/tmp/kwad'> 
    <p12/>
</ssl>
EOF

            Example 2:
            ----------
cat << EOF | kact -v100 --xml
<ssl type ='softclass' bsl='middleware§jss.ssl' dir='/tmp/kwad'> 
    <p12/>
</ssl>
---    
<ssl type='softclass' bsl='middleware§jss.ssl' sub_type='configuration' name='my_srv_keystore' dir='/tmp/kwad' expire='3650' password='mypass' sclabel='my1scl' scfile='my_srv.cert' scsize='512' scpassword='mypass' scexpire='3650' scalg='DSA' scdn='CN=my_srv,O=my_srv_company,OU=my_srv_unit,OU=my_srv_other_unit,C=US'>
    <p12 label='my1l' name='my_clt1_keystore' kpassword='mypass' password='mypass' expire='3650' alg='DSA' dn='CN=my_clt1,O=my_clt_company,OU=my_clt_unit,OU=my_clt_other_unit,C=US'/>
</ssl>
...
<ssl type='softclass' bsl='middleware§jss.ssl' sub_type='configuration' name='my_srv_keystore2' dir='/tmp/kwad' expire='3650' password='mypass' sclabel='my2scl' scfile='my_srv.cert' scsize='512' scpassword='mypass' scexpire='3650' scalg='DSA' scdn='CN=my_srv,O=my_srv_company,OU=my_srv_unit,OU=my_srv_other_unit,C=US'>
    <p12 label='my2l' name='my_clt2_keystore2' kpassword='mypass' password='mypass' expire='3650' alg='DSA' dn='CN=my_clt2,O=my_clt_company,OU=my_clt_unit,OU=my_clt_other_unit,C=US'/>
</ssl>
EOF
            """

            # Split multiple sources separated by yaml separator: --- or ...:
            from io import StringIO
            import re
            wrk_source = re.sub('\n\.\.\.\s*', '\n---', wrk_source)
            m = re.match('\n---\s*', wrk_source)
            if m!=None:raise xception.kwadSystemException('Main', self_funct, "kiktpl: Do not support multiple file. This source:  %s\nfrom %s contains more than one file." % (wrk_source, more))

            if not (options.file_source and not wrk_do_jinja and not wrk_do_mako): # keep file_source if has not changed
                file_source = temp_dir + '/file_source' + '.' + wrk_suffixe
                fd = open(file_source, 'w')
                fd.write(wrk_source)
                fd.close()
            else:file_source=options.file_source

        l = [options.toyaml, options.tok8yaml, options.tohcl, options.toterra]
        l.sort()
        if l !=  [False, False, False, False ] and l != [False, False, False, True ]:raise xception.kwadSystemException('Main', self_funct, 'options --toyaml, --tok8yaml, --tohcl and --toterra are not mutual exclusives !')
        if options.toyaml and options.tok8yaml:raise xception.kwadSystemException('Main', self_funct, 'options --toyaml and --tok8yaml are not allowed together !')
        if (options.tohcl or options.toterra) and options.tojson:raise xception.kwadSystemException('Main', self_funct, 'options --tohcl (or --toterra) and --tojson are not allowed together !')
        if (options.toyaml or options.tok8yaml) and options.tojson:raise xception.kwadSystemException('Main', self_funct, 'options --toyaml and --tojson are not allowed together !')
        if options.emhclcheck and not (options.tohcl or options.toterra):raise xception.kwadSystemException('Main', self_funct, 'When option: emhclcheck (--emhclcheck) is provided, option --tohcl (or --toterra) is required together !')

        if options.tok8yaml:options.toyaml = True


        return call(file_source, file_desc = file_desc, show_dft = options.show_dft, toyaml = options.toyaml, tok8yaml = options.tok8yaml, tohcl = options.tohcl, toterra = options.toterra, tojson = options.tojson, desconly = options.desconly, checkonly = options.checkonly, emhclcheck=options.emhclcheck,
             tmpl_kws = options.tmpl_kws, temp_dir=temp_dir, keep_temp_dir = options.keep_temp_dir, aliases=aliases, notcase = options.notcase, doStdout=doStdout, verbose=verbose)


    except Exception as e:

        if verbose==None:
            try:verbose=int(options.verbose)
            except:verbose=0
        if verbose>=10:raise

        import sys
        if not hasattr(e, 'short1') or not hasattr(e, 'short2'):
            message=e.__class__.__name__ + ': ' + str(e)
        elif verbose<5:
            message=e.short1()
        elif verbose>=5:
            message=e.short2()
        sys.stderr.write(message + '\n')
        sys.exit(2)
        
        
if __name__ == '__main__':
    from os import path
    import utils
    import sys
    CONVERT_HOME=utils.getInstallDir()

    for _path in (CONVERT_HOME + '/core',):
        if not _path in sys.path:sys.path.append(_path)

    main(sys.argv[1:])
