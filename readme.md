**KastMenu**  
**Unixes Operating System's Menu broadKast**
---


**[Official web site here !](https://www.kastmenu.org)**
**[KastMenu Demo here !](https://www.kastmenu.com:9000)**


**<u>Summary:</u>**

*  1/ [What is KastAgent ?](#What is KastAgent)
*  2/ [What is KastMenu ?](#What is KastMenu)
*  3/ [KastMenu Features](#KastMenu Features)
*  4/ [What Public is it dedicated for ?](#What Public is it dedicated for)
*  5/ [KastMenu Server Commands](#KastMenu Commands)
*  6/ [Install KastMenu](#Install KastMenu)
*  7/ [Run](#Run)
*  8/ [Feeding the KastMenu registry](#Feeding the KastMenu registry)
<br>
<br>

**1/ [What is KastAgent ?](#top)**  

**K**astAgent is the agent for KastMenu.  
KastAgent is automanaged and deployed by KastMenu.  
So this project is not intend to be downloaded/installed standalone outside KastMenu.  
But is there to follow the development of KastAgent.  
Hence KastAgent is periodically integrated into KastMenu under the directory kastagent.  

  
**K**astAgent is the remote counterpart of the KastMenu server and runs on the target machine.  
For more information about KastAgent see the KastAgent project.  
  
**K**astAgent is both a Web and a Terminal Menu.

* It is trigered remotly by KastMenu server or locally by the user, via SSH  and runs on a local machine or VM.
* It is called for a specific User and runs under the User of this session.  
* It runs everywhere you can have a unix Terminal.  
* It provides Web or Terminal Menu access to any unix comands under the unix security paradygm.  

**K**astAgent aims to support any linux distributions,  
while KastMenu server will only plan to support real free linux: debian distributions and derivatives.  
  
**K**astAgent is Powefull because it can run any command that runs on Unix.  
  
The KastAgent features include: infinite Menus imbrication and:

*   [KastMenu Log System](https://www.kastmenu.org/index.html#KastMenu_Log)
*   [KastMenu Replay](https://www.kastmenu.org/index.html#KastMenu_Replay)
*   [KastMenu Help Sytem](https://www.kastmenu.org/index.html#KastMenu_Help)

For informations on KastMenu see: [www.kastmenu.com](https://www.kastmenu.com).  

**K**astAgent aims to support any linux distributions,  
while **K**astMenu will only plan to support real free linux: debian distributions and derivatives.  
<br>

**2/ [What is KastMenu ?](#top)**  

Previously KastMenu was called KastMenu server and where separated from KastAgent.  
Now both KastMenu server and KastAgent are merged under the project KastMenu and KastMenu embed KastAgent under the kastagent directory.  
KastMenu autodeploy KastAgent to the first seen machine/VM.  

The full projet is 100% Free and OpenSource under the GPL 3 license.  

**K**astMenu **enhances** the capabilities of KastAgent by providing a **Mobile** and **Web Browser** view of the Terminal Menu by securely running it in the background.  
In the same conditions as KastAgent does it.  
  
With KastMenu Server the User can access his **Menu files** on any **target Machines** through his **SmartPhone** or favourite **Web Browser**.  
He doesn't need, no more to be directly connected to the Machine nor by SSH to run his menu.  
**So using KastMenu Users can run complex unix commands on any Machines from his Mobile or Browser.**  
<br>

**3/ [KastMenu Features](#top)**   

*   **Suppport of Multiple Machines:**  
    Users can open KastMenu sessions on multiple Machines.
  
*   **Suppport of Multiple Tabs:**  
    Users can open multiple tabs of KastMenu session, in the same Browser.  
    These tabs may target distinct machines or not.  
    Tabs would be entitled **<user>@<machine>**.  
  
*   **Support of User authentication:**  
    KastMenu server is able to authenticate Users by delegating authentication to the target Machine.  
    KastMenu server is transparent and **do not store User password**.  
    Users must have an User account to the target Machine (but may be prevented to logon with .profile or .bashrc <=> exit 0. for example).
  
*   **Support of autorization:**  
    KastMenu server will only allow an User to a specific Machine if it is registred to KastMenu Server.
  
*   **Support of default Machine:**  
    A specific Machine can be set as the default Machine.  
    This would show this Machine as the default Machine on the welcome page of the WebView  
    [See the Demo for it !](https://kastmenu.com:9000)
  
*   **Support of guest Users:**  
    This is an advanced feature it needs to be activated into the config file: kast.conf.  
    A specific guest user can be registred for a specific Machine into KastMenu Server.  
    This would show this guest user as the default on the welcome page of the WebView for this specific Machine.  
      
    Typically a guest user is an account on this Machine with low rights.  
    Because it is set as this, **only this guest user would be allowed to no authentication** and would perform the guest **user default menu**.  
    This feature allows to **welcome Newbees** on one Machine.  
    [See the Demo for it !](https://kastmenu.com:9000)
  
*   **Support of Mail Users:**  
    This is an advanced feature it needs to be activated into the config file: kast.conf.  
    One may be bored to register users one by one on a Machine.  
    KastMenu Server supports **Auto user registration and account creation**,  
    with the featrure called **"Signin with your mail"** only if the registred Machine is set to support it.  
      
    Once the "Signin with your mail" form is fullfilled and validated:  
    A new user unix account is created on the target Machine:  
    
    *   prefixed with the value for the _"generated\_user\_linux\_prefix"_ attribute of the config file: kast.conf (e.g.: z). and
    *   rooted with the base name of the mail user plus an index.
    
    e.g.: zpaul01  
      
    So the user account is created on the target Machine with the provided password.  
    This password is not stored in KastMenu Server but the user is registered.  
    By default the mail is not stored also but a derived hashed (this hash can be disabled into kast.conf).  
    [See the Demo for it !](https://kastmenu.com:9000)
  
*   **Support of KastMenu menufile:**  
    Users can access any menufile path as registred for them into KastMenu Server.
  
*   **Support of Replay:**  
    A user can target a menufile on a target Machine with a replayable KastMenu **menupath**,  
    this would **play back** this whole menu sequence into the WebView with a pause of 3s per screen by default.
  
*   **Support of Log system:**  
    BigBrother Log system is supported for the same as KastMenu does.
<br>
<br>

**4/ [What Public is it dedicated for](#top)**   

**KastMenu is a fair Interactive View of your System**  
  
Because it is structured it allows you to publish only what you want the User to see/access on your system.  
  
It is also **didactic**, whith the nowaday **Developers/Devops pressure** who want to have more and more access to the system's commands.  
This is **not an open ssh** and the Devs can be **happy to see their commands** and openly watch their **not perverted** output.  
  
For these reasons KastMenu is suit to:  

*   **New incomming Chalenger Cloud providers:**  
    who directly want to compete big ones providing the treasure of nowadays mass of cloud management commands.  
    *   In a per User basis and didactic and structural way.  
        
    *   It fast and easy to implement in large scales.  
        
  
*   **Developers/Devops:**  
    Because they want more and more direct accesses to the commands provided by the hyper prolific world  
    of the cloud frameworks of any kinds, public or private.  
    They know them and are actually capable of providing a subset xml of commands to the Admins in order to manages their Applications.  
    
  
*   **Cloud Engineers:**  
    Who want to provide access to complex but monitored commands of the backends to their peers or users.  
    
  
*   **Admins:**  
    Who want to provide powerfull but limited access to the backends.  
    Or to provide: install, start, stop, recovering ... commands, to other departments, e.g. to the supervisors.  
    
  
*   **DBAs:**  
    Who want to access to the strength of their Databases system commands.  
    Or want to publish accesses to their batch commands, to non DBAs expert like night Admins.  
    
  
*   **Supervisors:**  
    Who have to run heartbeat commands on Applications,  
    or to run dedicated recovering command on them.  
    
  
*   **To welcome a Newbee in any of this department:**  
    A restrictive but self demonstrating access to a part of your infrastructure.  
    This way the newbee also learn the commands.  
    
  
*   **To Students:**  
    Students directly see the real commands not perverted by any transformation, running into their real environment.  
    And they can tune them.  
    
  
*   **To Training plaform:** Demo, train and test your students on real platforms.  
<br>

**5/ [KastMenu Commands](#top)**   
  
**K**astMenu Server runs simply as:  
**$** **sudo -u kastserver /opt/kastmenu-server/current/bin/kastserver**  
or: **$** **nohup** sudo -u kastserver /opt/kastmenu-server/current/bin/kastserver -v100 **&**  
  
The KastMenu Server commands are:

*   **[addmachine:](https://kastmenu.com/cde-addmachine.html)** use this command to add new Machines to KastMenu Server.
  
*   **[addkuser:](https://kastmenu.com/cde-addkuser.html)** use this command to add new Users to KastMenu Server..
  
*   **[addmenu:](https://kastmenu.com/cde-addmenu.html)** use this command to add new Menu Files to a User into KastMenu Server..
  
*   **[admin:](https://kastmenu.com/cde-admin.html)** use this command to add Super admin users to KastMenu Server.
  
*   **[convert:](https://kastmenu.com/cde-convert.html)** use this command to add Super admin users to KastMenu Server.
<br>
<br>

**6/ [Install KastMenu](#top)**   

Download kastmenu_<versuion>.deb  

**Check if pre-exist**  
**$** dpkg -l | grep kastmenu  

**Delete if pre-exist:**  
**$** sudo dpkg -P kastmenu  

**Install:**  
**$** dpkg -i **/where/is/kastmenu_1.5.deb**  
or:  
**$** sudo apt -y install **/where/is/kastmenu_1.5.deb**  
<br>

**7/ [Run](#top)**  

**$** sudo -u kastserver **/opt/kastmenu/current/bin/kastserver** -v5  
(-v500 full logging)  
or:  
**$** nohup sudo -u kastserver **/opt/kastmenu/current/bin/kastserver** -v5 &  

**Open your Browser at https://<hostname>:9000**   
<br>

**8/ [Feeding the KastMenu registry](#top)**   

**Adding Machines:**   
<u>Adding Machine localhost:</u> (required)   
**$** sudo -u kastserver **/opt/kastmenu/current/bin/addmachine** -m localhost -t Title_for_my_localhost -v3 -F --ispublic   --isdefault --kastagent_dir /home/kastmenu  --kastweb_port 9100   
<span style='color: blue;'><i>--ispublic: this will allow the publishing of the name of this machine in the web interface.   
--isdefault: this will show this machine by default in the web interface.   
--kastagent_dir /home/kastmenu: This will be the home dir of the kastagent server on this machine.  
This usually is the home dir of the kastagent user (see below) for this machine.   
kastagent user must have full right on this directory.   
Note: kastmenu auto deploy the kastagent to the target machine into this target directory.   
<br>
--kastweb_port 9100: Can be any port.   
This will be the port of what is called the kastweb proxy.   
The kastweb proxy is part of the kastagent agent installation,   
and is systematically started for the first menu called for any user on the target machine.   </i></span>
<br>

<u>Adding Machine my_other_host:</u> (for example)   
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addmachine** -m my_other_host -t Title_for_my_other_host -v3 -F --ispublic   --isdefault --kastagent_dir /home/kastm --kastweb_port 9100   
<span style='color: blue;'><i>--kastagent_dir /home/kastm: here we choose kastm as kastmenu user as it can be anyone.   </i></span>


**Adding a Sudo user: (optional)**   
<span style='color: blue;'><i>e.g. Sudo user (mysuser) for my_other_host:   
A typical sudo user must have the following rigth on the target machine (my_other_host):   
ALL=(ALL:ALL) NOPASSWD:ALL   
Note: a sudo user will not be allowed to create menu.   </i></span>
<br>
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addkuser** -m my_other_host -u mysuser  -t Sudo_user_for_my_other_host  -F -S   

<u>Update machine my_other_host:</u>   
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addmachine** -m my_other_host -t Title_for_my_other_host -v3 -F --ispublic -F   


**Adding the kastagent's User: (required)**   
<u>Adding kastmenu user to machine localhost:</u>   
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addkuser** -m localhost -u kastmenu  -t Kastagent_user_for_localhost  -F -K   
<span style='color: blue;'><i>-K: means is kastmenu user.   </i></span>
<br>
<u>Adding kastmenu user to machine my_other_host:</u>   
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addkuser** -m my_other_host -u kastm  -t Kastagent_user_for_my_other_host  -F -K   


**Adding Users:**   
<u>Adding user to Machine localhost:</u>  
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addkuser** -m localhost -u test  -t cfhgfhg  -F   
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addmenu**  -m localhost -u test -n welcome  -p /home/kastmenu/kastagent/current/conf/welcome/tutorials.xml -F   
<u>Adding user to Machine my_other_host:</u>  
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addkuser** -m my_other_host -u asjkinst  -t cfhgfhg  -F  --ispublic   
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addmenu**  -m my_other_host -u asjkinst -n mywelcome  -p /home/kastm/kastagent/current/conf/welcome   /tutorials.xml -F   


| Advanced considérations  (optional) | 
---------------------------------------

**Creating a guest user on a specific Machine:**   
<span style='color: blue;'><i>A guest user is a specific user with low right on a specific machine.  
The machine must support Sudo user.  
--xnopassword: means anyone will be allowed to run any menu under this user with no password.  </i></span>
<br>
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addkuser** -m my_other_host -u guest  -t cfhgfhg  -F --xnopassword  
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addmenu**  -m my_other_host -u guest -n welcome  -p /home/kastmenu/kastagent/current/conf/welcome/tutorials.xml -F  


**Allowing AcceptMail on a specific Machine:**   
<span style='color: blue;'><i>-A: --xaccept_mail: With xaccept_mail (-A): Users connecting via the WebMenu would be allowed to automatically create their own  
account simply providing their mail accounts.  
-M welcome: --default_menu In conjunction with --xaccept_mail (-A). Will add this menu name for the newly created user.  
-P /opt/kastmenu/current/conf/welcome/tutorials.xml: In conjunction with --xaccept_mail (-A). Will add this menu file path for the newly created user.</i></span>                                            
**$** sudo -u kastserver /opt/kastmenu/current/bin/**addmachine** -m my_other_host -t My_other_host_machine -v3 -F -A -M welcome -P /home/kastmenu/kastagent/current/conf/welcome/tutorials.xml --ispublic  -F  

---------------------------------------
Copyright © 2024 - Patrick Germain Placidoux
