<!-- Dont copy/paste this file into a Terminal. Prefere scp !!! -->

<%doc>  *==========================*  Infos  *==========================*
<!-- Copyright (c) 2008, Patrick Germain Placidoux                          -->
<!-- All rights reserved.                                                   -->
<!--                                                                        -->
<!-- This file is part of DKwad Public Software.                           -->
<!--                                                                        -->
<!-- DKwad Public Software is released under the modified BSD License,     -->
<!-- which should accompany it or any part of it in the file "COPYING".     -->
<!-- If you do not have this file you can access the license                -->
<!-- through the WWW at http://www.dkwad.org/license/bsd/license.txt.      -->
<!--                                                                        -->
<!-- Home page: http://www.dkwad.org                                       -->
<!-- Contact: dkwad@dkwad.org                                                -->
<!-- ====================================================================== -->
<!--                                                                        -->
<!--                                                                        -->
<!--                                                                        -->
<!-- ====================================================================== -->
<!-- UPDATE     |     DATE     |   CODE   |  REASON                         -->
<!-- ====================================================================== -->
<!--            |              |          |                                 -->
<!--                                                                        -->
<!--                                                                        -->
<!-- ====================================================================== -->

Run with: </where/is/kwad-5.5>/bin>/apimenu  ../samples/apimenu/menu.mako  -v3

Sample Menu:
------------


          [serenity]     MIDDLEWARE MANAGEMENT

                    ________________
                    |              |
                    | *** MENU *** |
                    |______________|


            1/ Applications 

            2/ J2EE Instances 

            3/ WebServers Instances 



               ( Exit:0)
                       Choice ?1


          [serenity]     MIDDLEWARE MANAGEMENT

                    ________________
                    |              |
                    | APPLICATIONS |
                    |______________|


            1/ oinc_incomes 

            2/ pinc_incomes 



               ( Exit:0)
                       Choice ?1


          [serenity]     MIDDLEWARE MANAGEMENT

                    ________________
                    |              |
                    | OINC_INCOMES |
                    |______________|


            1/ J2EE Instances 

            2/ WebServers Instances 

            3/ Config jee on machine1 



               ( Exit:0)
                       Choice ?1


          [serenity]     MIDDLEWARE MANAGEMENT

                   __________________
                   |                |
                   | J2EE INSTANCES |
                   |________________|


            1/ oinc_incomes_jvm_01 

            2/ oinc_incomes_jvm_02 

            3/ oinc_incomes_jvm_04 



               ( Exit:0)
                       Choice ?


          [serenity]     MIDDLEWARE MANAGEMENT

                    ________________
                    |              |
                    | OINC_INCOMES |
                    |______________|


            1/ J2EE Instances 

            2/ WebServers Instances 

            3/ Config jee



               ( Exit:0)
                       Choice ?


          [serenity]     MIDDLEWARE MANAGEMENT

                    ________________
                    |              |
                    | APPLICATIONS |
                    |______________|


            1/ oinc_incomes 

            2/ pinc_incomes 



               ( Exit:0)
                       Choice ?



          [serenity]     MIDDLEWARE MANAGEMENT

                    ________________
                    |              |
                    | *** MENU *** |
                    |______________|


            1/ Applications 

            2/ J2EE Instances 

            3/ WebServers Instances 



               ( Exit:0)
                       Choice ?
          ________________________________________


</%doc>


<%doc>  *==========================*  Globals  *==========================*  </%doc>

<%doc>Init Template level</%doc>
<%!
	from kwadlib import tools
	from os import path
	import sys
	
	BASE_MIDDLEWARE_DIR='/middleware'
	KAST_HOME=tools.getInstallDir()
	
	# Where is kwad_attrs:
	KAST_ATTRS=path.normpath(path.realpath(KAST_HOME + '/conf/kwad.attrs'))
	# Loading kwad_attrs as a dictionary:
	print 'Using kwad.attrs at :' + KAST_ATTRS + '.'
	KAST_ATTRS=tools.getKwadAttrs(KAST_ATTRS)
	# Checking required Categories
	if KAST_ATTRS['middleware_apa_bin']==None:raise Exception('The entry:' + middleware_apa_bin + ' must exist into kionf.attrs !')
%>

<%doc>Init Render level</%doc>
<%
	# ==> USER INPUTS HERE (Begin)
	# Describes Applications JVM and WebServer instances.
	APPLICATIONS={
	    'oinc_incomes': {
		'jvms': ('oinc_incomes_jvm_01', 'oinc_incomes_jvm_02', 'oinc_incomes_jvm_03'),
		'wbs': ('oinc_incomes_wbs_01', 'oinc_incomes_wbs_02')
	    },

	    'pcon_contracts': {
		'jvms': ('pcon_contracts_jvm_01', 'pcon_contracts_jvm_02', 'pcon_contracts_jvm_03'),
		'wbs': ('pcon_contracts_wbs_01', 'pcon_contracts_wbs_02')
	    }
	}
	WEB_APP_DIR='/webapps'
	# <== USER INPUTS HERE (End)
%>



<%doc>  *==========================*  J2EE Applications  *==========================*  </%doc>
<%def name="fj2ee_applications()">
% for application in APPLICATIONS:
		      <menu title='${application}'>
		
		<!-- J2EE Instances -->
			    <menu title='J2EE Instances'>
      % for jvm_name in APPLICATIONS[application]['jvms']:
		      <%
			  status='ps -elf | grep ' + jvm_name
			  start='su - ' + jvm_name[0:4] + ' -c "' + WEB_APP_DIR + '/' + application + '/tom/' + jvm_name + '/bin/start.sh' + '"'
			  stop='su - ' + jvm_name[0:4]  + ' -c "' + WEB_APP_DIR + '/' + application + '/tom/' + jvm_name + '/bin/stop.sh' + '"'
		      %>
				  <menu title='${jvm_name}'>
				      <option name='status' command='${status}'/>
				      <option name='start' command='${start}'/>
				      <option name='stop' command='${stop}'/>
				  </menu>
      % endfor
      
				  <option name='Config exemple: samples/custombis.xml/pinc_contract_jvm_02' command='${KAST_HOME}/bin/kupd --kcac  ${KAST_HOME}/samples/kcac/custombis.xml business_application/jeeserver@name=pinc_contract_jvm_02 --console --overwrite -C ${KAST_ATTRS} -v5'/>
			    
			    </menu>

		
		<!-- WebServers Instances -->
			    <menu title='WebServers Instances'>
      % for wbs_name in APPLICATIONS[application]['wbs']:
	    <%
	    start=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  start'
	    restart=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  restart'
	    graceful=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  graceful'
	    graceful_stop=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  graceful-stop'
	    stop=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  stop'
	    %>
				
				  <menu title='${wbs_name}'>
					  <option name='status' command='${status}'/>
					  <option name='start' command='${start}'/>
					  <option name='restart' command='${restart}'/>
					  <option name='graceful' command='${graceful}'/>
					  <option name='graceful_stop' command='${graceful_stop}'/>
					  <option name='stop' command='${stop}'/>
				  </menu>
      % endfor
			    </menu>
		      </menu>
% endfor

</%def>



<%doc>  *==========================*  J2EE Instances  *==========================*  </%doc>
<%def name="fj2ees()">


      <!-- J2EE Instances -->	
      <menu title='J2EE Instances'>

% for application in APPLICATIONS:
      <%
      jvm_instances=APPLICATIONS[application]['jvms']
      %>
      % for jvm_name in jvm_instances:
	    <%
		status='ps -elf | grep ' + jvm_name
		start='su - ' + jvm_name[0:4] + ' -c "' + WEB_APP_DIR + '/' + application + '/tom/' + jvm_name + '/bin/start.sh' + '"'
		stop='su - ' + jvm_name[0:4]  + ' -c "' + WEB_APP_DIR + '/' + application + '/tom/' + jvm_name + '/bin/stop.sh' + '"'
	    %>
		    <menu title='${jvm_name}'>
			<option name='status' command='${status}'/>
			<option name='start' command='${start}'/>
			<option name='stop' command='${stop}'/>
		    </menu>
      % endfor
% endfor
	</menu>
</%def>


<%doc>  *==========================*  WebServers Instances  *==========================*  </%doc>
<%def name="fwebservers()">

      <!-- WebServers Instances -->
      <menu title='WebServers Instances'>
      
% for application in APPLICATIONS:
      <%
      wbs_instances=APPLICATIONS[application]['wbs']
      %>

      % for wbs_name in wbs_instances:
	    <%
	    status='ps -elf | grep ' + wbs_name
	    start=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  start'
	    restart=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  restart'
	    graceful=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  graceful'
	    graceful_stop=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  graceful-stop'
	    stop=KAST_ATTRS['middleware_apa_bin'] + '/apachectl -f ' + WEB_APP_DIR + '/' + application + '/apa/' + wbs_name + '/conf/' +  wbs_name + '_httpd.conf -k  stop'
	    %>
		<menu title='${wbs_name}'>
			<option name='status' command='${status}'/>
			<option name='start' command='${start}'/>
			<option name='restart' command='${restart}'/>
			<option name='graceful' command='${graceful}'/>
			<option name='graceful_stop' command='${graceful_stop}'/>
			<option name='stop' command='${stop}'/>
		</menu>
      % endfor
% endfor

      </menu>
</%def>






<config title='MiddleWare Management'  temp_dir='/tmp' option_upper='False' screen_max_lines='25' skip_line='True' dont_use_unix_color='False'>

	<menu title='*** MENU ***' confirm_exit='True'>	

		<!-- Applications -->	
		<menu title='Applications'>
		${fj2ee_applications()}
		</menu>

		${fj2ees()}
			
		${fwebservers()}

	</menu>

</config>
