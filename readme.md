---
KastMenu
Unixes Operating System's Menu broadKast
---


**[Official web site here !](https://www.kastmenu.org)**
**[KastMenu Demo here !](https://www.kastmenu.com:9000)**


**<u>Summary:</u>**


* 1/ What is KastMenu ?
* 2/ How it runs ?
* 3/ What Public is it destinated for ?
* 4/ KastMenu Log System
* 5/ KastMenu Replay
* 6/ KastMenu Help Sytem
* 7/ KastMenu runs under the User and this is Powerfull !
  
**1/ [What is KastMenu ?](#top)**  
  
**K**astMenu is a Terminal Menu and runs into a Terminal Console.
* Localy
* From SSH
Under the User of the session.  
And everywhere you can have a unix Terminal.  
  
**K**astMenu is Powefull because it can run any command that runs on Unix.  
  
**K**astMenu Learning Curve is 0 because you set the command as expected in normal terminal into a menu file.  
This menu file supports 3 formats:  

* XML or
* YAML or
* HCL
You choose the one which suits you.  
  
**K**astMenu is WYSIWYG:  
The supported tags are Logical and StraightForward:  
Config
* **Menu**
* **IMenu**
Menu tags also support Other Menu or IMenu tags.  
IMenu tags also support Other IMenu or Menu tags.  
Option has an Attribute "command" to call a shell command.  
IMenu has an Attribute "command" to call a shell command on validation of the IMenu.  
  
**The command output is not perverted nor tansformed** it is directly dump the User sees what he gets.  
  
**K**astMenu is interactive:  
IMenu are **interactive** Menus, they supports **input fields** as IOptions:  
IOptions are **input fields** with their type leverage by **[wk](./wk.html)** a simple an intuitive declarative type libray.  
  
  
**2/ [How it runs ?](#top)**  
  
**K**astMenu runs simply as:  
$ **km** myfile.xml  
*(or **km** myfile.yaml, km myfile.hcl or longer **kastmenu** myfile.xml)*  
  
An Attribute "command" can explicitly call another km process with the option: --follow-menu:  
e.g.:  
<Option command="**km** --follow-menu myfile.xml" ...>  
  
**M**enus are **indefinitly** imbricable (It is a tree) because:  

* **Menu**, **IMenu** are reciprocally imbricables.
* **km** process can call another km process indefinitly through the tag's **command** Attribute.
  
The syntax of the kastmenu (km) command is [here](./cde-km.html).  
The syntax of the convert command is [here](./cde-convert.html)  
  
  
**/3 [What Public is it destinated for ?](#top)**  
  
**KastMenu is a fair Interactive View of your System**  
  
Because it is structured it allows you to publish only what you want the User to see/access on your system.  
  
It is also **didactic**, whith the nowaday **Developers/Devops pressure** who want to have more and more access to the system's commands.  
This is **not an open ssh** and the Devs can be **happy to see their commands** and openly watch their **not perverted** output.  
  
For these reasons KastMenu is suit to:  

* **New incomming Chalenger Cloud providers:**  
  who directly want to compete big ones providing the treasure of nowadays mass of cloud management commands.  

  * In a per User basis and didactic and structural way.
  * It fast and easy to implement in large scales.
* **Developers/Devops:**  
  Because they want more and more direct accesses to the commands provided by the hyper prolific world  
  of the cloud frameworks of any kinds, public or private.  
  They know them and are actually capable of providing a subset xml of commands to the Admins in order to manages their Applications.
* **Cloud Engineers:**  
  Who want to provide access to complex but monitored commands of the backends to their peers or users.
* **Admins:**  
  Who want to provide powerfull but limited access to the backends.  
  Or to provide: install, start, stop, recovering ... commands, to other departments, e.g. to the supervisors.
* **DBAs:**  
  Who want to access to the strength of their Databases system commands.  
  Or want to publish accesses to their batch commands, to non DBAs expert like night Admins.
* **Supervisors:**  
  Who have to run heartbeat commands on Applications,  
  or to run dedicated recovering command on them.
* **To welcome a Newbee in any of this department:**  
  A restrictive but self demonstrating access to a part of your infrastructure.  
  This way the newbee also learn the commands.
* **To Students:**  
  Students directly see the real commands not perverted by any transformation, running into their real environment.  
  And they can tune them.
* **To Training plaform:** Demo, train and test your students on real platforms.
  
**/4 [KastMenu Log System](#top)**  
  
Abusivly called BigBrother.  
  
Shows in **Realtime**, in colors and **Visually identical**, the very Menu, the User is running into his private terminal:  
Each options, each commands, each output the User runs in real time, is seen.  
This is accessable by a **simple tail -f or cat on the log file** to anyone who has the right to access to it.  
  
This is simply powerfull, use it with care.  
The usefulness of this is obvious.  
  
Called with option -L will enable the log system:  
$ **km** -L -l <logdir> myfile.xml  
  
  
**/5 [KastMenu Replay](#top)**  
  
**All Menu actions are replayable.**  
  
When the option -L is choosen: km will log and will write a **menupath** for each action taken by the User, into the log file:  
e.g. menupath: 1..1.3.2.0.0.4  
When called with a menupath: e.g.:  
km -g 1..1.3.2.0.0.4 -p 5s  
  
KastMenu will **replay** the Menu exactly how it was previously run and **pause** 5 seconds **on every screen**.  
  
Note: Beware if the original file (myfile.xml) changes, the menupath may change.  
  
  
**/6 [KastMenu Help Sytem](#top)**  
  
Each KastMenu tag supports an Attribute: "help".  
This allows to provide an help at the top level menu and to Each (I)Menu and (I)Option.  
  
This help system is multi-language and based on dbm lang dictionaries tuned by the User.  
Help attributes can either be text literal or link to a key of this dictionary.  
  
  
**/7 [KastMenu runs under the User and this is Powerfull !](#top)**  
  
In the unix world, Software set the User's credentials and specifics as hidden files under the home directory:  
For example if I list mine:  
  
patrick@server1$ pwd  
*/home/patick*  
patrick@server1$ ls -a | grep "^\\."  
*.docker  
.kube  
.profile  
.ssh  
.subversion  
...*  
So running under the unix User is running under all his credentials and authorizations to access these softwares.  
  

---
Trademarks :

* "Docker" is a trademark or registered trademark of Docker, Inc.
* "K8S", "kubernetes" is a trademark or registered trademark of The Linux Foundation .
* "Apache Subversion, Subversion" and are trademarks of the Apache Software Foundation.
* Other names may be trademarks of their respective owners.

