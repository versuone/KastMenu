/** @license
* Copyright (c) 2007-2024, Patrick Germain Placidoux
* All rights reserved.
*
* This file is part of KastMenu (Unixes Operating System's Menus Broadkasting).
*
* KastMenu is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* KastMenu is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with KastMenu.  If not, see <http://www.gnu.org/licenses/>.
*
* Home: http://www.kastmenu.org
* Contact: kastmenu@kastmenu.org
*/



/*
 * 20230905: 001: Replacing JQuery bu Bootsrap5
 * Html5 Fetch is far slower then JQuery Ajax, so we can no more loop on get.
 * oo WebSocket is renamed OOWebSocketGet
 * MenuWebSocketGet is Added to replace all get() 
 * 
 * 20230905: 002: Adding: _active_oodialog.
 */

/* ================ *
  |                 | 
  | Singleton MENUS |
  |                 | 
  * =============== */

MENUS = {
    menus 			: [],
    _current_menu 		: 0,
    _show_all 			: false,
    _call_url: "/kmenu/do_menu",
    _call_last_message_id	: null,
    _oo_menu_paths_show_all 	: false,
    _is_locked 			: false,
    STATUS			: null,
    COMMAND_IS_RUNNING: false,
    _oo_menu_paths_show_all	: false,
    
    
    clear : function () {
        this.menus.length = 0; // Clear and garbade collect array content.
        var md=document.getElementById("main");
        md.innerHTML = "";
    },
    
    doShowMenuPaths : function () {
      return this._oo_menu_paths_show_all;
    },
      

    isLocked : function () {
      return this._is_locked;
    },
    
    lock : function () {
      var comp=document.getElementById("running_img");
      this._is_locked=true;                              
      comp.src='/kastmenu/images/' + "tec6tem-spinner-logo.gif"
    },
    
    unLock : function () {
      var comp=document.getElementById("running_img");
      this._is_locked=false;
      comp.src='/kastmenu/images/' + "tec6tem-spinner-logo-slow.gif"
    },
    makeMenu : function (entries) {
	this.setCurrentMenu(this.menus.length);
	menuid=this._current_menu;
	
	var source = document.getElementById("menu-template").innerHTML;
	var template = Handlebars.compile(source);
	var md=document.getElementById("main");
	var menu_select = document.getElementById("menu_select");
	
	//md=$( "#main")
	//md.html( "" );
	//md.html(template(entries));
	
	// Menuid Propagation
	entries["config"]["id"]=menuid;
	for (var i=0; i<entries["config"]["items"].length; i++) entries["config"]["items"][i]["config_id"]=menuid;
	if (this.menus.length==0) entries["config"]["prevmenu_car"]=false;
	
	md.innerHTML+=template(entries);
	//md.trigger( "updatelayout");
	
	menu=new Menu(this.menus.length);
	this.menus[menu.getId()]=menu;
		
	//Option range
	for (var i=0; i<entries["config"]["items"].length; i++) menu._option_ranges[i]=entries["config"]["items"][i]["index"];
	// Menu exits
	menu._is_first_menu_process=entries["config"].is_first_menu_process;
	menu._is_first_menu=entries["config"].is_first_menu;
	menu._has_prevmenu_car=entries["config"]["prevmenu_car"];
	menu._prevmenu_car='';
	menu._call_check_all_car=entries["config"].check_all_car;
	menu._call_exit_car=entries["config"].exit_car;
	menu._call_up_car=entries["config"].up_car;
	menu._call_down_car=entries["config"].down_car;
	this.goCurrentMenu();
	
	option=document.createElement('option');
	option.setAttribute('value', this._current_menu)
	option.appendChild(document.createTextNode(this._current_menu));
	menu_select.appendChild(option);
	
	// this.get();
	
	return menu;
    },
    
    setCurrentMenu : function (id) {
      title=document.getElementById('title');
      this._current_menu=id;
      title.innerHTML='Sequence:' + this._current_menu.toString()
    },
    
    getCurrentMenu : function () {
      return this.menus[this._current_menu];
    },
    
    getMenu : function (id) {
	return this.menus[id];
    },
    
    getLastMenu : function () {
	return this.menus[this.menus.length -1];
    },
    
    goCurrentMenu : function () {
      // hide others if need
      if (!(this._show_all)) {
	  for (var i=0; i<this.menus.length; i++) {
	      if (i!=this._current_menu) this.getMenu(i).hide();
	  }
      }
      this.getMenu(this._current_menu).show();
      this.getMenu(this._current_menu).go();
    },

    goMenuLast : function () {
	this.setCurrentMenu(this.menus.length -1);
	this.goCurrentMenu();
    },
    
    goMenuFirst : function () {
	this.setCurrentMenu(0);
	this.goCurrentMenu();
    },

    goMenuPrev : function () {
	this.setCurrentMenu(this._current_menu - 1);
	if (this._current_menu < 0) this.setCurrentMenu(this.menus.length-1);
	this.goCurrentMenu();
    },
    
    goMenuNext : function () {
	this.setCurrentMenu(this._current_menu + 1);
	if (this._current_menu > this.menus.length-1) this.setCurrentMenu(0);
	this.goCurrentMenu();
    },
    
    showAll : function () {
    	this._show_all=true;
	for (var i=0; i<this.menus.length; i++) this.getMenu(i).show();
	this.goCurrentMenu();
    },
    
    hideAll : function () {
	this._show_all=false;
	// goCurrentMenu : alrredy include an hideAll operation
	this.goCurrentMenu();
    },
    
    // MenuPaths

    showMenuPaths : function () {
    	this._oo_menu_paths_show_all=true;
	for (var i=0; i<this.menus.length; i++) this.getMenu(i).getMenuPath().show();
	menu.getMenuPath().go();
    },
    
    hideMenuPaths : function () {
	this._oo_menu_paths_show_all=false;
	for (var i=0; i<this.menus.length; i++) this.getMenu(i).getMenuPath().hide();
    },
    
    runOnClick : function (indexes, names) {
	if (MENUS.isLocked()) return;
	
	menu=this.getLastMenu();
	if (!( menu.isFirstMenu() && menu.isFirstMenuProcess() )) alert('Not First Menu Process !!!');
	else {
	  this.STATUS='IS_RUNNING_PUTS';
	  this.puts(indexes);
	}
    },   
    
    // Goo
    
    goCurrentMenuOoPrev : function () {
	this.getMenu(this._current_menu).goCurrentOoPrev();
    },
    
    goCurrentMenuOoNext : function () {
	this.getMenu(this._current_menu).goCurrentOoNext();
    },
    
    goCurrentMenuOoLast : function () {
	this.getMenu(this._current_menu).goCurrentOoLast();
    },
    
    goOoPrev : function () {
	var menu=this.getMenu(this._current_menu);
	var current_oo=menu._current_oo - 1;
	
	if (current_oo < 0) {
	    this.goMenuPrev();
	    menu=this.getCurrentMenu();
	    current_oo=menu._oos.length-1;
	}
	
	menu.goOo(current_oo);
    },
    
    goOoNext : function () {
	var menu=this.getMenu(this._current_menu);
	var current_oo=menu._current_oo + 1;
	
	if (current_oo > menu._oos.length-1) {
	    this.goMenuNext();
	    menu=this.getCurrentMenu();
	    current_oo=0;
	}
	
	menu.goOo(current_oo);
    },
    
    goOoFirst : function () {
	var menu=this.getFirstMenu();
	this.setCurrentMenu(0);
	menu.goOo(0);
    },
    
    goOoLast : function () {
// 	this.setCurrentMenu(this.getLastMenu().getId());
	this.getLastMenu().goCurrentOoLast();
    },    

    
    /* ---------- */
    /* Lazy Calls */
    /* ---------- */
    /* D001:
    get : function () {
// 	return this._call_ajax('get')
    }, */
    
    put : function (value) {
	return this._call_ajax('put', value);
    },
    
    puts : function (value) {
	return this._call_ajax('puts', value);
    },
    
    _call_ajax : async function (type, value) {
	MENUS.lock()
	
    
    // bootstrap5: call: Works but seems to have some latency => Replacing fetch get by MenuWebSocket -->
    let response = null;
    try {
        response = await fetch(this._call_url + '?' + new URLSearchParams({"operation": type, "value": value, "last_message_id": MENUS._call_last_message_id}), {
            method: 'GET',
            headers: {
            'Content-Type': 'application/json',
            'Session-Part': getSessionPart(),
            // Default: 300sec, here 7sec:
            signal: AbortSignal.timeout(7000)
            },
            // Post: body: JSON.stringify({"operation": type, "value": value, "last_message_id": MENUS._call_last_message_id})
        });
        //Response from server
        const ajax_datas = await response.text();       
    }catch(error){
        window.location.href = window.location.host;
        return;
        /*
        makeGlobalError(error, null);                    
        // Unlock MENUS
        MENUS.unLock();          
        // console.log(e)
        */
    }
    success = await response.ok
    if (!(success)) {
        DISPATCHER.terminateMenu();
        return;
    }
    },
    
    _call_ajax_parse: function (ajax_datas) {
	for (var i=0; i<ajax_datas.length; i++) {
	    MENUS._call_last_message_id=ajax_datas[i][0];
	    var datas=ajax_datas[i][1];
        
	    if (datas.type=="menu") this._call_ajax_parse_menu(datas);
	    //{"keys": {"menu": "menua", "menu_instance": "M139964406334029"}, "type": "menu", 
	    else if ((datas.type=="dialog") && (datas.contents.is_choice)) {
        // A002 + _oodialog:
		this.getLastMenu()._oos[0] = new ooDialogMenu(this.getLastMenu(), datas.contents.dialog_id);
        
	    }
	    else if (datas.type=="dialog") {               
            MENUS.COMMAND_IS_RUNNING=false;
            MENUS.unLock();
            
            // A049: +is_password:
            this.getLastMenu().makeDialog(datas.contents.messages, datas.contents.dialog_id, datas.contents.is_value, datas.contents.is_password, datas.contents.is_to_confirm, datas.contents.confirm_ok, datas.contents.confirm_ko);
	    }
	    else if (datas.type=="data_input") {
            // Search for the last matching ooDialog or ooDialogMenu:
            // ------------------------------------------------------
            var l = this.getLastMenu()._oos.length -1;
            oodialog = null;
            while (l >= 0) {
                oodialog=this.getLastMenu()._oos[l];                    
                if ((typeof oodialog != 'undefined') && (oodialog._type.startsWith('ooDialog')) && (oodialog.checkOoBackendId(datas.contents.dialog_id))) {
                    break;
                }
                oodialog = null;
                l -= 1;
            }

            /* D002:
                // moins 1 d'un data_input est un dialog ou un menu ==> juste ignore ooCommandOutput
                // -------------------------------------------------
                var l = this.getLastMenu()._oos.length;
                var k = 1;
            var oodialog=this.getLastMenu()._oos[l - k];
                while ((l - i>0) && (oodialog._type=='ooCommandOutput')) {
                    k+=1;
                    oodialog=this.getLastMenu()._oos[l - k];
                }
            */
                
            // D002: Check ooBackendId
            // D002: if ( (oodialog._type=='ooCommandOutput') || (!(oodialog.checkOoBackendId(datas.contents.dialog_id))) ) alert('Dialog-Input failed in sequence, expected:' + oodialog._ooBackendId + ', received:' + datas.contents.dialog_id + ' !');
            if  (oodialog == null) ('Dialog-Input failed in sequence, expected:' + datas.contents.dialog_id + ' !');
                            
            // A002:
            if (oodialog._type == 'ooDialog') MENUS.getLastMenu()._active_oodialog = null;
            oodialog.dispatchValue(datas.contents.data);
	    }
	    else if (datas.type=="print") {
		this.getLastMenu().makeOutput(datas.contents.messages);
	    }
	    else if (datas.type=="input_field") {
		this.getLastMenu().makeOutput(datas.contents.raws);
	    }
	    else if ( (datas.type=="raise") && (datas.contents.type=='APIMENU_END_RUNNING_PUTS') ) {
		MENUS.STATUS=null;
		MENUS.unLock();
	    }
	    else if (datas.type=="raise") {
		if ((datas.contents.type=='APIMENU_STUKE_ON_READING') || (datas.contents.type=='APIMENU_NEXT_GET_MAY_BE_LONG')) continue;
		
		datas.contents.messages.unshift('Error:' + datas.contents.type + '>>>')
		this.getLastMenu().makeError(datas.contents.messages, true);
	    }
	    else if (datas.type=="warn") {
		datas.contents.messages.unshift('Warning:' + datas.contents.type + '>>>')
		this.getLastMenu().makeError(datas.contents.messages, false);
	    }
	    else if (datas.type=="option_list") {
            OPTION_LIST = new OptionList(this.getLastMenu(), datas);
            OPTION_LIST.makeOptionListSearch(null, null);
            /* todo:TEST ONLY: May be to remove hides error:
            try {
                OPTION_LIST.makeOptionListSearch(null, null);
            }catch(error) { 
                switchMenuScreen();
            }*/
        }

	}
	
	// Get until ends puts !!!
	// D001: if (MENUS.STATUS=='APIMENU_END_RUNNING_PUTS') MENUS.get();
	// Get until ends output !!!
	// D001: if ( (datas) && (datas.type=="raise") && (datas.contents.type=='APIMENU_NEXT_GET_MAY_BE_LONG') ) MENUS.get();
	
	MENUS.unLock()
    },
    
    _call_ajax_parse_menu: function (datas) {
	/*
	Menu/contents (datas.contents.big_title) ==>
	Menu/contents (datas.contents.title) ==>
	"contents": {
	  "is_locked": false, "sub_titles": [], "title": "MENUA", "big_title": {"host": "[serenity]     ", "title": "OAT ENVIRONMENT MANAGEMENT"}, 
	Menu/contents (datas.contents.mo_paths) ==>
	  "mo_paths": {"names": null, "indexes": null}, 
	Menu/contents (datas.contents.items) ==>
	Menu/choicess (datas.choices) ==>
	  datas.choices.check_all_car
	  datas.choices.exit_car
	  datas.choices.up_car
	  datas.choices.down_car
	  "choices": {"check_all_car": null, "exit_car": 0, "up_car": null, "down_car": null}, "sub_type": "Menu", "mid": "MENU-menua//MENU_INSTANCE-M139964406334029"}}, 
	*/
    sessionStorageHelpClear();
	var help=null;
    var help_found = false;
    if (datas.contents.help!=null || datas.contents.lhelp!=null) help_found = true;
    
    
	entries={"config": { 
	    "id": null, 
	    "host": datas.contents.big_title.host,
        "user": datas.contents.big_title.user,
	    "big_title": datas.contents.big_title.title,
	    "title": datas.contents.title,
        "htitle": datas.contents.help,
        "help": setSessionStorageHelp(datas.contents.help, null),
        "lhelp": setSessionStorageHelp(datas.contents.lhelp, null),
        "help_found": help_found,
	    "is_first_menu_process": datas.keys.is_first_menu_process,
	    "is_first_menu": datas.keys.is_first_menu,
	    
	    "mo_paths_indexes": datas.contents.mo_paths.indexes,
	    "mo_paths_names": datas.contents.mo_paths.names,
	    "items": []
		/*
		  {"index": 1, "alt": true, "sep": ")", "name": "OPTION1", "help": null, "lock": true},
		  {"index": 2, "alt": false, "sep": ")", "name": "OPTIONA2", "help": "MyHelp optiona2", "lhelp": "MyLHelp optiona2."},
		  {"index": 3, "alt": true, "sep": ")", "name": "IMBMENU", "help": null, "lock": null},
		]
		*/
	    }
	}
	
	for (var i=0; i<datas.contents.items.length; i++) {
	    var items=datas.contents.items[i];
        var help_show = false;
        var help_full=null;
	    if ((items.help!='') && (items.help!=null)) {
            help=help_full=items.help;
            
            if (help.length > 20) {
                help_show = true;
                help = help.substring(0, 20);
                help += ' ...'
            }
        }
	    else help=null;
        
	    if ((items.lhelp!='') && (items.lhelp!=null)) {
            help_show = true;
            lhelp=items.lhelp;
        }
	    else lhelp=null;

        setSessionStorageHelp(help, null);
        
        // is_password: management:
        let ivalue = items.value;
        if (items.value != null && items.is_password!=null && items.is_password) ivalue = '*'.repeat(items.value.length);
        
	    if ((items.type!="Option") && (items.type!="IOption") && (items.type!="Menu") && (items.type!="IMenu"))  alert('Parsing Menu:' + datas.contents.title + ', Unknown item:' + items.type + ' !');
	    entries.config.items[i] = {
		"index": items.option, 
		"alt": (i % 2 == 0),
		"sep": items.sep, 
		"name": items.label,
		"htitle": help,
        "help": help,
        "help_full": setSessionStorageHelp(help_full, null),
		"lhelp": setSessionStorageHelp(lhelp, null),
        "help_show": help_show,
		
		"fr_color": items.frColor,
		"bg_color": items.bgColor,

		"value": ivalue == null ? ivalue : JSON.stringify(ivalue),
		"olegend": items.olegend,
	    }
	}
	
	entries["config"].prevmenu_car=true;
	entries["config"].check_all_car=datas.contents.choices.check_all_car;
	entries["config"].exit_car=datas.contents.choices.exit_car;
	entries["config"].up_car=datas.contents.choices.up_car;
	entries["config"].down_car=datas.contents.choices.down_car;
    
	MENUS.makeMenu(entries);
	
	/*
	"mo_paths": {"names": "title=menud.title=MyIMenu2", "indexes": 7.4}
	*/
	if (datas.contents.mo_paths.names) menu.makeMenuPath(datas.contents.mo_paths.names, datas.contents.mo_paths.indexes.toString());
    },
}



/* =========== *
  |            | 
  | Class MENU |
  |            | 
  * ========== */

Menu = function(id) {
    this._type = 'Menu';
    this._id = id;
    this._isStored = false;
    this._oos = [];
    this._active_oodialog = null; // A002
    this._current_oo = 0;
    this._option_ranges = [];
    
    this._prevmenu_car='';
    this._call_check_all_car=null;
    this._call_exit_car=null;
    this._call_up_car=null;
    this._call_down_car=null;
    this._oo_menu_path=null;
    
    this.getId = function () {
	return this._id;
    };
    
    this.getActiveOodialog = function () {
        return this._active_oodialog
    };

    this.isFirstMenuProcess = function (value) {    
	return this._is_first_menu_process;
    };

    this.isFirstMenu = function (value) {
	return this._is_first_menu;
    };
    
    this.isOption = function (value) {    
	if (this._option_ranges.indexOf(value)>-1) return true;
	else return false;
    };

    this.hide = function () {
	divid=this._getDivMenuAll();
	if (divid) divid.style.display='none';
    };
    
    this.show = function () {
	divid=this._getDivMenuAll();
	if (divid) divid.style.display='block';
    };
    
    this.isStored = function () {
	return this._isStored;
    };
    
    this.store = function () {
        this._isStored=true;
    };
    
    this._getDivMenu = function () {
	var divid='menu_' + this._id.toString();
	return document.getElementById(divid);
    };
    
    this._getDivMenuAll = function () {
	var divid='menu_alldiv_' + this._id.toString();
	return document.getElementById(divid);
    };
    
    this.go = function () {
	// No named anchor because it changes the Url: document.location='#menu_' + this._id.toString();
	var anchor = document.getElementById('anchor_' + this._id.toString() + '_0');
	this.setCurrentOo(0);
	anchor.scrollIntoView();
    };
    
    this.getMenuPath = function () {
	return this._oo_menu_path;
    };
    
    
    /* ----------------------------*
     | Dialog and OutPut and Error |
     |        (make and go)        | 
     * ----------------------------*/
    
    this.makeMenuPath = function (names, indexes) {
	this._oo_menu_path=new ooMenuPath(this, names, indexes);
	
	// Display:
	this._showLine();	
	var source = document.getElementById("menu_path-template").innerHTML;
	var template = Handlebars.compile(source);
	var md=this._getDivOo();
	
	md.innerHTML += template({"id": this._id.toString(), "names": names, "indexes": indexes });
    };
    
    this.makeOutput = function (messages) {
	var ooid = this._oos.length;
        
	this._oos[ooid] = new ooOutput(this, ooid, messages);
	
	// Display:
	this._showLine();	
	var source = document.getElementById("output-template").innerHTML;
	var template = Handlebars.compile(source);
	var md=this._getDivOo();
	
	md.innerHTML += template({"messages": messages, "id": this._id.toString(), "ooid": ooid});
	
	this.goOo(ooid);
    };
    
    this.makeCommandOutput = function (message, coid) {
	var ooid = this._oos.length;
	this._oos[ooid] = new ooCommandOutput(this, ooid, message);
	
	// Display:
	this._showLine();	
	var source = document.getElementById("command-output-template").innerHTML;
	var template = Handlebars.compile(source);
	var md=this._getDivOo();
	
	md.innerHTML += template({"message": message, "coid": coid, "id": this._id.toString(), "ooid": ooid});
	
    MENUS.COMMAND_IS_RUNNING = true;
    MENUS.lock();
	this.goOo(ooid);
    };

    this.makeDialog = function (messages, ooBackendId, is_value, is_password, is_to_confirm, confirm_ok, confirm_ko) {
	var ooid = this._oos.length;
    // A002 + _oodialog:
	this._oos[ooid] = this._active_oodialog = new ooDialog(this, ooid, ooBackendId, is_value, is_to_confirm, confirm_ok, confirm_ko);
	
	// Display:
	this._showLine();	
	var source = document.getElementById("dialog-template").innerHTML;
	var template = Handlebars.compile(source);
	var md=this._getDivOo();
    // A049: +is_password:
	md.innerHTML += template({"messages": messages, "id": this._id.toString(), "ooid": ooid, "is_value": is_value, "is_password": is_password, "is_to_confirm": is_to_confirm, "confirm_ok": confirm_ok, "confirm_ko": confirm_ko});
	
	ifd=this._oos[ooid].getInputField();
	if (ifd!=null) ifd.focus();
	
	this.goOo(ooid);
    };
    
    this.makeError = function (messages, is_raise) {
	var ooid = this._oos.length;
	if (is_raise) type='Error';
	else type='Warn';
	this._oos[ooid] = new ooError(this, ooid, type, messages);
	
	// Display:
	this._showLine();	
	var source = document.getElementById("error-template").innerHTML;
	var template = Handlebars.compile(source);
	var md=this._getDivOo();
	
	md.innerHTML += template({"messages": messages, "id": this._id.toString(), "ooid": ooid, "is_raise": is_raise, "type": type});
	
	this.goOo(ooid);
    };    
    
    this._showLine = function () {
	var line = document.getElementById('menu_line_' + this._id.toString());
	if (!(line.style.display == 'block')) line.style.display = 'block';
    };
    
    this.getOo = function (ooid) {
	return this._oos[ooid];
    };
    
    this._getDivOo = function () {
	var divid='oo_' + this._id.toString();
	return document.getElementById(divid);
    };

    this.setCurrentOo = function (ooid) {
	this._current_oo=ooid;
    };
    
    this.goCurrentOo = function () {
	this.goOo(this._current_oo);
    };
    
    this.goOo = function (ooid) {
      	//ko: if (MENUS.doSleep()) sleep(MENUS._sleep_laps);
      	this.setCurrentOo(ooid);
	var anchor = document.getElementById('anchor_' + this._id.toString() + '_' + ooid.toString());
	anchor.scrollIntoView();
    };
    
    this.goCurrentOoPrev = function () {
	var current_oo =this._current_oo - 1;
	if (current_oo < 0) current_oo=this._oos.length-1;
	this.goOo(current_oo);
    };
    
    this.goCurrentOoNext = function () {
	var current_oo =this._current_oo + 1;
	if (current_oo > this._oos.length-1) current_oo=0;
	this.goOo(current_oo);
    };
    
    this.goCurrentOoLast = function () {
	var current_oo=this._oos.length-1;
	this.goOo(current_oo);
    };

}


/* ================= *
  |                  | 
  | Class ooMenuPath |
  |                  | 
  * ================ */


ooMenuPath = function(menu, names, indexes) {
    this._type 		= 'ooMenuPath';
    this._menu 		= menu;
    this._names		= names;
    this._indexes	= indexes;
    
    this.getMenu = function () {
	return this._menu;
    };
    
    this.getDiv = function () {
	var divid='oo_' + this.getMenu()._id.toString() + '_menupath';
	return document.getElementById(divid);
    };
    
    this.hide = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='none';
    };
    
    this.show = function () {
	if (!( MENUS.doShowMenuPaths() )) return;
	
	divid=this.getDiv(); 
	if (divid) divid.style.display='block';
    };
    
    this.go = function () {
	this.getMenu().goOo(this._ooid);
    };

}


/* =================== *
  |                    | 
  | Class ooError      |
  |                    | 
  * ================= */


ooError = function(menu, ooid, etype, messages) {
    this._type 		= 'ooError';
    this._menu 		= menu;
    this._ooid		= ooid;
    this._etype		= etype
    this._messages	= messages;
    
    this.getMenu = function () {
	return this._menu;
    };
    
    this.getDiv = function () {
	var divid='oo_' + this.getMenu()._id.toString() + '_' + this._ooid.toString();
	return document.getElementById(divid);
    };
    
    this.hide = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='none';
    };
    
    this.show = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='block';
    };    
    
    this.go = function () {
	this.getMenu().goOo(this._ooid);
    };

}

/* =================== *
  |                    | 
  | Class ooOutput     |
  |                    | 
  * ================= */


ooOutput = function(menu, ooid, messages) {
    this._type 		= 'ooOutput';
    this._menu 		= menu;
    this._ooid		= ooid;
    this._messages	= messages;
    
    this.getMenu = function () {
	return this._menu;
    };
    
    this.getDiv = function () {
	var divid='oo_' + this.getMenu()._id.toString() + '_' + this._ooid.toString();
	return document.getElementById(divid);
    };
    
    this.hide = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='none';
    };
    
    this.show = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='block';
    };    
    
    this.go = function () {
	this.getMenu().goOo(this._ooid);
    };

}



/* ====================== *
  |                       | 
  | Class ooCommandOutput |
  |                       | 
  * ==================== */


ooCommandOutput = function(menu, ooid, message) {
    this._type 		= 'ooCommandOutput';
    this._menu 		= menu;
    this._ooid		= ooid;
    this._messages	= message;
    
    this.getMenu = function () {
	return this._menu;
    };
    
    this.getDiv = function () {
	var divid='oo_' + this.getMenu()._id.toString() + '_' + this._ooid.toString();
	return document.getElementById(divid);
    };
    
    this.hide = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='none';
    };
    
    this.show = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='block';
    };    
    
    this.go = function () {
	this.getMenu().goOo(this._ooid);
    };

}


/* =================== *
  |                    | 
  | Class ooDialogMenu |
  |                    | 
  * ================= */


ooDialogMenu = function(menu, ooBackendId) {
    this._type 		= 'ooDialogMenu';
    this._menu 		= menu;
    this._ooid		= 0;
    this._ooBackendId	= ooBackendId;    
    
    this._isGoing 	= false;
    this._value		= null;
    
    this.getMenu = function () {
	return this._menu;
    }
    
    this.getDiv = function () {
      return this.getMenu()._getDivMenu();
    };
    
    this.hide = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='none';
    };
    
    this.show = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='block';
    };    
    
    this.go = function () {
	this.getMenu().goOo(this._ooid);
    };
    
    /* --------------------*
     |        Events       |
     |         and         |
     | (Dialog to backend) |
     |        ==>          | 
     * --------------------*/
     
    this.optionOnMouseOver = function (comp) {
	if ( (MENUS.isLocked()) || (this.getMenu().isStored()) ) return;
	
	comp.style.backgroundColor='#59E817';
	comp.style.color='white';
	comp.style.borderTopColor='black';
	comp.style.borderStyle='blue';
	comp.style.borderStyle='groove';
	comp.style.borderWidth='5px';
	comp.style.cursor='pointer';
    };

    this.optionOnMouseOut = function (comp) {
	if ( (MENUS.isLocked()) || (this.getMenu().isStored()) ) return;
	
	comp.style.backgroundColor='#D1D0CE';
	comp.style.color='black';
	comp.style.borderStyle='blue';
	comp.style.borderStyle='groove';
	comp.style.borderWidtH='5px';
    };

    this.optionOnClick = function (comp, index) {
	if ( (MENUS.isLocked()) || (this.getMenu().isStored()) ) return;
	// menu=MENUS.getMenu(config_id);
	// menu.store();
	this._isGoing=true;
	
 	var div=this.getDiv();
	div.style.pointerEvents='none';
 	comp.style.cursor='wait'; // need to disallow mode pointer when pointerEvents wil turn to normal.
	//div.style.cursor='wait'; useless when pointerEvents is none
	
	MENUS.put(index)
	
	comp.style.backgroundColor='#41A317'; 
	comp.style.color='white';
	comp.style.borderColor='red';
	comp.style.borderTopColor='black';
	comp.style.borderStyle='blue';
	comp.style.borderStyle='ridge';
	comp.style.borderWidth='5px';
    };
     
    this.onMouseOver = function (comp, img) {
	if ( (MENUS.isLocked()) || (this.getMenu().isStored()) ) return;

	comp.style.cursor='pointer';
	comp.src='/kastmenu/images/' + img;
    };

    this.onMouseOut = function (comp, img) {
	if ( (MENUS.isLocked()) || (this.getMenu().isStored()) ) return;

	// comp.style.cursor='pointer';
	comp.src='/kastmenu/images/' + img;
    };
    
    this.getConfirmOk = function () {
        var butOk='confirm_ok_' + this.getMenu().getId().toString() + '_' + this._ooid.toString();
        return document.getElementById(butOk);
    };

    this.onClick = function (comp, img, str) {
	if ( (MENUS.isLocked()) || (this.getMenu().isStored()) ) return;
	if (this._value) str=str.replace( /:/g, '~:' );

	//comp.style.cursor='pointer';
	comp.src='/kastmenu/images/' + img;
	this._isGoing = true;
	
	var div=this.getDiv();
	div.style.pointerEvents='none';
 	comp.style.cursor='wait'; // need to disallow mode pointer when pointerEvents wil turn to normal.
	//div.style.cursor='wait'; useless when pointerEvents is none
	
    MENUS.getLastMenu()._active_oodialog = null;
	MENUS.put(str);
    };
    
    /* ------------------------*
     | Data Input from backend |
     |          <==            | 
     * ------------------------*/
     
    this.checkOoBackendId = function (ooBackendId) {
	return this._ooBackendId==ooBackendId;
    };
    
    this.dispatchValue = function (value) {
	if (this.getMenu().isOption(value)) this.storeOption(value);
	else if ((this.hasExit()) && (value==0)) this.storeExit();
	else if ((this.hasPrevMenu()) && (value==null)) this.storePrevMenu();
	else if ((this.hasCheckAll()) && (value=='s')) this.storeSubmit();
	else if ((this.hasUp()) && (value=='+')) this.storeUp();
	else if ((this.hasDown()) && (value=='-')) this.storeDown();
	else this.storeUnKnown(value);
	
	this._value=value;
	
	var div=this.getDiv();
	div.style.pointerEvents='auto';
	div.style.cursor='wait'; 
    };
    
    this.store = function () {
	this.getMenu().store();
	this._isGoing=false;
    };
    
    this.storeOption = function (index) {
	var comp=document.getElementById('option_' + this.getMenu().getId() + '_' + index.toString());
	this.store();
	
	comp.style.backgroundColor='#41A317'; 
	comp.style.color='white';
	comp.style.borderColor='red';
	comp.style.borderTopColor='black';
	comp.style.borderStyle='blue';
	comp.style.borderStyle='ridge';
	comp.style.borderWidth='5px';
    };
    
    this.storeExit = function () {
	var comp=document.getElementById('exit_' + this.getMenu().getId());
	comp.border=1;
	comp.style.borderWidth='1px'
	comp.style.borderColor='red';
	
	this.store();
    };
    
    this.storePrevMenu = function () {
	var comp=document.getElementById('prevmenu_' + this.getMenu().getId());
	// ::: Sera None si le Menus.runOnclick envoie une valeur Naze !!!
	comp.border=1;
	comp.style.borderWidth='1px'
	comp.style.borderColor='red';
	
	this.store();
    };
    
    this.storeSubmit = function () {
	var comp=document.getElementById('submit_' + this.getMenu().getId());
	comp.border=1;
	comp.style.borderWidth='1px'
	comp.style.borderColor='red';
	
	this.store();
    };
    
    this.storeUp = function () {
	var comp=document.getElementById('up_' + this.getMenu().getId());
	comp.border=1;
	comp.style.borderWidth='1px'
	comp.style.borderColor='red';
	
	this.store();
    };
    
    this.storeDown = function () {
	var comp=document.getElementById('down_' + this.getMenu().getId());
	comp.border=1;
	comp.style.borderWidth='1px'
	comp.style.borderColor='red';
	
	this.store();
    };
    
    this.storeUnKnown = function (value) {
	var comp_span=document.getElementById('unknown_span_' + this.getMenu().getId());
	var comp=document.getElementById('unknown_' + this.getMenu().getId());
	comp.title=value;
	comp.border=1;
	comp.style.borderWidth='1px'
	comp.style.borderColor='red';
	
	comp_span.style.display='block';
	
	this.store();
    };
    
    this.hasPrevMenu = function () {
	return this.getMenu()._has_prevmenu_car!=null;
    };
    this.hasCheckAll = function () {
	return this.getMenu()._call_check_all_car!=null;
    };
    this.hasExit = function () {
	return this.getMenu()._call_exit_car!=null;
    };
    this.hasUp = function () {
	return this.getMenu()._call_up_car!=null;
    };
    this.hasDown = function () {
	return this.getMenu()._call_down_car!=null;
    };
}


/* =============== *
  |                | 
  | Class ooDialog |
  |                | 
  * ============== */


ooDialog = function(menu, ooid, ooBackendId, is_value, is_to_confirm, confirm_ok, confirm_ko) {
    this._type 		= 'ooDialog';
    this._menu 		= menu;
    this._ooid 	= ooid;
    this._ooBackendId 	= ooBackendId;
    
    this._isStored 	= false;
    this._isGoing 	= false;
    this._value 	= null;
    
    this.is_value 	= is_value;
    this.is_to_confirm = is_to_confirm;
    this.confirm_ok 	= confirm_ok;
    this.confirm_ko 	= confirm_ko;
    
    this.isStored = function () {
	return this._isStored;
    }

    this.stopGoing = function () {
        this._isStored 	= false;
	this._isGoing 	= false;
    }
    
    this.getMenu = function () {
	return this._menu;
    }
    
    this.getDiv = function () {
	var divid='oo_' + this.getMenu()._id.toString() + '_' + this._ooid.toString();
	return document.getElementById(divid);
    };
    
    this.hide = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='none';
    };
    
    this.show = function () {
	divid=this.getDiv(); 
	if (divid) divid.style.display='block';
    };    
    
    this.go = function () {
	this.getMenu().goOo(this._ooid);
    };
    
    this.getInputField = function () {
    if (!(this.is_value)) return null;
      var divid='oo_input_' + this.getMenu().getId().toString() + '_' + this._ooid.toString();
      return document.getElementById(divid);
    };
    
    this.getConfirmOk = function () {
      var butOk='confirm_ok_' + this.getMenu().getId().toString() + '_' + this._ooid.toString();
      return document.getElementById(butOk);
    };
    
    
    /* --------------------*
     |        Events       |
     |         and         |
     | (Dialog to backend) |
     |        ==>          | 
     * --------------------*/
     
    this.onMouseOver = function (comp, img) {
	if ( (MENUS.isLocked()) || (this.isStored()) ) return;

	comp.style.cursor='pointer';
	comp.src='/kastmenu/images/' + img;
    };

    this.onMouseOut = function (comp, img) {
	if ( (MENUS.isLocked()) || (this.isStored()) ) return;

	// comp.style.cursor='pointer';
	comp.src='/kastmenu/images/' + img;
    };

    this.onClick = function (comp, img, str) {
	if ( (MENUS.isLocked()) || (this.isStored()) ) return;

	// comp.style.cursor='pointer';
	//comp.src='/kastmenu/images/' + img;
	this._isGoing = true;
	this._isStored = true;
	
	var div=this.getDiv();
	div.style.pointerEvents='none';
 	if (!(this.is_value)) comp.style.cursor='wait'; // need to disallow mode pointer when pointerEvents wil turn to normal.
	//div.style.cursor='wait'; useless when pointerEvents is none
	
    MENUS.getLastMenu()._active_oodialog = null;
	MENUS.put(str);
    };
    
    /* ------------------------*
     | Data Input from backend |
     |          <==            | 
     * ------------------------*/
    this.checkOoBackendId = function (ooBackendId) {
	return this._ooBackendId==ooBackendId;
    };
    
    this.dispatchValue = function (value) {
	this._value=value;
	if (this.is_value) {
	    comp1=document.getElementById('oo_input_' + this.getMenu().getId() + '_' + this._ooid.toString());
	    comp2=document.getElementById('oo_text_' + this.getMenu().getId() + '_' + this._ooid.toString());
	    comp3=document.getElementById('confirm_ok_' + this.getMenu().getId() + '_' + this._ooid.toString());
	    comp1.style.display='none';
	    if (value) comp2.innerHTML=value.toString();
	    else comp2.innerHTML='';
	    comp2.style.display='inline-block';

	    comp3.border=1;
	    comp3.style.borderWidth='2px'
	    comp3.style.borderColor='red';
	    comp3.style.cursor='wait';
	}
	if (this.is_to_confirm) {
	    if (value==this.confirm_ok) {
		var comp=document.getElementById('confirm_ok_' + this.getMenu().getId() + '_' + this._ooid.toString());
		comp.border=1;
		comp.style.borderWidth='2px'
		comp.style.borderColor='red';
	    }
	    else {
		var comp=document.getElementById('confirm_ko_' + this.getMenu().getId() + '_' + this._ooid.toString());
		comp.border=1;
		comp.style.borderWidth='2px'
		comp.style.borderColor='red';
	    }
	}
	
	this.store();
	
	var div=this.getDiv();
	
	div.style.pointerEvents='auto';
	div.style.cursor='wait';
    };
    
    this.store = function () {
	this._isStored=true;
	this._isGoing=false;
    };
}






/* ================ *
 |                  | 
 | Class OptionList |
 |                  | 
 * ================ */


OptionList = function(lastMenu, datas) {
    this._lastMenu = lastMenu;
    this._datas = datas;
    // {'iid': iid, 'rows': option_list_rows, 'oattrs': option_list_oattrs, 'okey': option_list_okey, 'okeys': option_list_okeys, 'option_list_indexes': option_list_indexes}

    
    this._configs = null;
    
    this.makeConfigs = function (skey, svalue) {
        error_prefix = 'fct makeConfigs: MakeOptionList Config: '  
        if (skey == null) skey = this._datas.contents.okey;
        if (svalue == null) svalue = '';        

        // {'iid': iid, 'rows': option_list_rows, 'oattrs': option_list_oattrs, 'okey': option_list_okey, 'okeys': option_list_okeys, 'option_list_indexes': option_list_indexes}
        
        var lindexes = this._datas.contents.option_list_indexes[skey];
        var new_rows = [];
        let rows = this._datas.contents.rows;  // In order to access inside map (map has its own this)
        let started = false;
        lindexes.map(function(value_index){
            let spl = value_index.split('_');
            let value = spl[0];
            let new_index = spl[1];
            if (!started) {
                if (!value.startsWith(svalue)) {}
                else started = true;
            }
            if (started) new_rows.push(rows[new_index]);
        });


        orders = Array.from(this._datas.contents.oattrs);
        orders.splice(orders.indexOf(skey), 1); // remove skey
        orders.splice(0, 0, skey); // to put it at position 0        
        this._configs = {
            'search': skey,
            'orders': orders,
            'fields': new_rows
        };
        /*
        this._configs = {
            'search': 'a',
            'orders': ['a', 'b', 'c'],
            'fields': [
                {'a': 1, 'b': 1, 'c': 1},
                {'a': 11, 'b': 11, 'c': 11},
                {'a': 111, 'b': 111, 'c': 111},
                {'a': 1111, 'b': 1111, 'c': 111},
            ]
        };
        */
    }
        
    this.makeOptionListSearch = function (skey, svalue) {
        error_prefix = 'fct makeOptionList: Parsing datas: '   
        /*
        Expected:
        ---------
        {
            'search': a,
            'orders': ['a', 'b', 'c', 'd'],
            'fields': [
                {'a': 1, 'b': 11, 'c': 111},
            ]
        }
        Digested for HB:
        ----------------
        { 'values': [
                {
                    'key': 'a',
                    'value': 1,
                    'help': 'blabla',
                    'fields': [
                        {'key': 'b', 'value': 11},
                },
            ]
        }
        */
        // Test:
        this.makeConfigs(skey, svalue);
        skey = this._configs.search;
        
        // Surface check:
        if (!this._configs.hasOwnProperty('search')) {
            this._lastMenu.makeError([error_prefix + " Dictionary options should contain key: 'search' !"], true);    
            return;
        }
        if (!this._configs.hasOwnProperty('orders')) {
            this._lastMenu.makeError([error_prefix + " Dictionary options should contain key: 'orders' !"], true);    
            return;
        }
        if (!this._configs.hasOwnProperty('fields')) {
            this._lastMenu.makeError([error_prefix + " Dictionary options should contain key: 'fields' !"], true);    
            return;
        }
        
        // Display:
        let gfh2 = document.getElementById("global_header2");  // to feed
        let gs2 = document.getElementById("global_screen2");  // to clear
        gs2.innerHTML = '';
        
        // To be restored on Error:
        /*
        fh.style.display='block';
        fc.style.display='block';
        fh2.style.display='none';
        fc2.style.display='none';
        */
        
        let source = document.getElementById("global-optionlist-inputs-template").innerHTML;
        let template = Handlebars.compile(source);
        gfh2.innerHTML = template({'name': skey});

        let size = 3;
        document.getElementById("frame_header2").style.height = size + 'em'; 
        document.getElementById("frame_content2").style.marginTop = (size + 0.3) + 'em';    
                    
        this.makeOptionList(svalue);
    }


    this.makeOptionList = function (svalue) {
        error_prefix = 'fct makeOptionList: Parsing datas: '        
        
        /*
        Expected:
        ---------
        {
            'search': 'a',
            'orders': ['a', 'b', 'c'],
            'fields': [
                {'a': 1, 'b': 11, 'c': 111},
            ]
        }
        Digested for HB:
        ----------------
        { 'values': [
                {
                    'key': 'a',
                    'value': 1,
                    'fields': [
                        {'key': 'b', 'value': 11},
                },
            ]
        }
        */

        let fh = document.getElementById("frame_header"); // to close:
        let fc = document.getElementById("frame_content");
        let fh2 = document.getElementById("frame_header2"); // to open:
        let fc2 = document.getElementById("frame_content2");
        let gs2 = document.getElementById("global_screen2");  // to feed        
           
        ghbs = { 'values': []}
        hbs_values = ghbs['values'];
        
        
        // Get key:
        pkey = this._datas.contents.okey;
        let orders = this._configs.orders; // In order to access inside map (map has its own this)
        let lastMenu = this._lastMenu; // In order to access inside map (map has its own this)
        this._configs.fields.map(function(fields, index, array){
            let new_hbs = {}
            hbs_values.push(new_hbs)
            let new_hbs_fields = new_hbs['fields'] = [];
            
            for (var i=0; i<orders.length; i++) {
                let key = orders[i];
    
                if (!fields.hasOwnProperty(key)) {        
                    js = JSON.stringify(fields)
                    // makeGlobalError
                    lastMenu.makeError([error_prefix + " Checking items: $js => Should contain key: '$key' !"], true);
                    return;
                }
                                
                // key value, help:
                let  value = fields[key]
                if ((svalue != null) && (value < svalue)) continue;

                let hbs = null;                                                    
                if (i == 0) hbs = new_hbs; // 0 is skey
                else { 
                    hbs = {};
                    new_hbs_fields.push(hbs);
                }

                hbs['key'] = key;
                hbs['value'] = value;
                hbs['pkey_value'] = fields[pkey];
            }
        });               

        // Display:
        var source = document.getElementById("global-optionlist-template").innerHTML;
        var template = Handlebars.compile(source);       
        gs2.innerHTML = '';
        gs2.innerHTML = template(ghbs);
        
        fh.style.display='none';
        fc.style.display='none';
        fh2.style.display='block';
        fc2.style.display='block';        
    }
}

var OPTION_LIST = null;






/* =================== *
  |                    | 
  | Function Utilities |
  |                    | 
  * ================== */

document.onkeypress = async function (e) {
 var key=e.keyCode || e.which;
  if (key==13){
    switch (DISPATCHER._CURRENT_PAGE) {
    case 'MENU':            
        clickCurrentDialog ();
        break;
    case 'MACHINE':
        await DISPATCHER.settings_machine_submit();
        break;
    case 'ADMIN':
        await DISPATCHER.settings_admin_submit();
        break;
    default:
    }
  }
}

function clickCurrentDialog () {
    var oodialog=MENUS.getLastMenu().getActiveOodialog();
    if (oodialog == null) return false;
    confirmOk = oodialog.getConfirmOk();
    if (confirmOk == null) return false;
    confirmOk.onclick();
    return true;
}


// Global Error:
function makeGlobalError (messages, color) {
    var msd = document.getElementById("global_screen");
    var msd2 = document.getElementById("global_screen2");
    var ghd = document.getElementById("global_help");
    var ged = document.getElementById("global_error");
    
    if (color==null) color='red';
    
    // Display:
    var source = document.getElementById("global-error-template").innerHTML;
    var template = Handlebars.compile(source);
    
    ged.innerHTML = template({"messages": messages, "color": color});
    msd.style.display='none';
    msd2.style.display='none';
    ghd.style.display='none';
    ged.style.display='block';
}; 


// Setting Machine Error:
function showSettingMachineError (message, field, positive) {
    var sme = document.getElementById("settings_machine_error");
    
    sme.innerHTML = message.replace('/\n/g', '<br>') + '<br><br>';    
    sme.style.display='block';
    if (positive!=null && positive) sme.style.color='blue';
    else sme.style.color='red';

    // Add error in field:
    // - has-error, has-warning, has-info, has-success
    if (field != null) {        
        var field = document.getElementById("settings_machine_" + field);
        field.classList.add('is-invalid');        
    }
}
function hideSettingMachineError () {
    var sme = document.getElementById("settings_machine_error");
    sme.style.display='none';
    sme.innerHTML = '';
        
    // Remove error in fields:
    // - has-error, has-warning, has-info, has-success
    fields = ['machine', 'user', 'password', 'menu', 'menupath']
    for (let i = 0; i < fields.length; i++) {
        let field = fields[i];
        field = document.getElementById("settings_machine_" + field);
        field.classList.remove('is-invalid');
        field.classList.remove('is-valid');        
    }    
}
// Setting Admin Error:
function showSettingAdminError (message, field) {
    var sme = document.getElementById("settings_admin_error");
    sme.innerHTML = message.replace('/\n/g', '<br>') + '<br><br>';    
    sme.style.display='block';

    // Add error in field:
    // - has-error, has-warning, has-info, has-success
    if (field != null) {        
        var field = document.getElementById("settings_admin_" + field);
        field.classList.add('is-invalid');        
    }
}
function hideSettingAdminError () {
    var sme = document.getElementById("settings_admin_error");
    sme.style.display='none';
    sme.innerHTML = '';
        
    // Remove error in fields:
    // - has-error, has-warning, has-info, has-success
    fields = ['user', 'password']
    for (let i = 0; i < fields.length; i++) {
        let field = fields[i];
        field = document.getElementById("settings_admin_" + field);
        field.classList.remove('is-invalid');
        field.classList.remove('is-valid');        
    }    
}


function showHelp (title, help_full, lhelp) {   
    var msd = document.getElementById("global_screen");
    var ghd = document.getElementById("global_help");
    var ged = document.getElementById("global_error");
    
    // Display:
    var source = document.getElementById("global-help-template").innerHTML;
    var template = Handlebars.compile(source);
    
    var helps = null;
    help_full = getSessionStorageHelp(help_full);
    if (help_full != null) {
        help_full = help_full.replaceAll(String.fromCharCode(92), 'eacute_backslah');
        help_full = help_full.replaceAll('eacute_backslahn', 'eacute_br');
        help_full = help_full.replaceAll('eacute_backslah', ' ');
        help_full = urlify(help_full);
        var helps = help_full.split('eacute_br');
    }
    else {var helps = null;}
    


    var lhelps = null;
    lhelp = getSessionStorageHelp(lhelp);
    if (lhelp != null) {
        lhelp = lhelp.replaceAll(String.fromCharCode(92), 'eacute_backslah');
        lhelp = lhelp.replaceAll('eacute_backslahn', 'eacute_br');
        lhelp = lhelp.replaceAll('eacute_backslah', ' ');
        lhelp = urlify(lhelp);
        var lhelps = lhelp.split('eacute_br');
    }
    else {var lhelps = null;}
    
    ghd.innerHTML = template({"title": title, "helps": helps, "lhelps": lhelps});
    msd.style.display='none';
    ged.style.display='none';
    ghd.style.display='block';
};


// Session Part:
function setSessionPart (session_part) {       
    if (session_part == null) alert ('session_part cannot be null !');
    spart = sessionStorage.getItem('session_part');
    if ((spart != null) && (spart != '')) return spart;
    sessionStorage.setItem('session_part', session_part);
    
    return session_part;
}
function getSessionPart () {   
    session_part = sessionStorage.getItem('session_part');
    if (session_part == null || session_part == '') return null;
    return session_part;
}

async function genSessionPart () {   
    return await DISPATCHER.postutils('genSessionPart');
}


// Session Help:
function sessionStorageHelpClear () {   
    keys = [];
   for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('help_')) keys.push(key);
    }
    
    for (i = 0; i < keys.length; i++)  {
        sessionStorage.removeItem(keys[key]);
    }
}
function setSessionStorageHelp (value, key) { 
    if (value == null || value == '') return null;
        
    let MIN=1000;
    let MAX=10000;
    
    if (key == null || key == '') {
        key = Math.floor(Date.now() / 1000).toString() + '-' + Math.floor(Math.random() * (MAX - MIN) + MIN);        
    }

    sessionStorage.setItem('help_' + key, value);
    
    return 'help_' + key;
}
function getSessionStorageHelp (key) {   
    return sessionStorage.getItem(key);
}


function setSessionStorageMachineUser(user, machine) { 
    if (user == null || user == '' || machine == null || machine == '') return null;
    machine_users = sessionStorage.getItem('machine_users');
    if (machine_users==null) machine_users = '[]';
    machine_users = JSON.parse(machine_users);
    
    if (machine_users.includes(user + ';' + machine)) return false;    
    machine_users.push(user + ';' + machine);

    sessionStorage.setItem('machine_users', JSON.stringify(machine_users));    
    return true;
}
function getSessionStorageMachineUsers () {
    machine_users = sessionStorage.getItem('machine_users');
    if (machine_users==null) return null;
    
    machine_users = JSON.parse(machine_users);    
    if (machine_users.length==0) return null;
    
    return machine_users;
}



  
     
function onMouseOver (comp, img) {
    if (MENUS.isLocked()) return;
    comp.style.cursor='pointer';
    comp.src='/kastmenu/images/' + img;
};

function autocomplete(inp, arr) {
  var currentFocus;
  
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      inp.scrollIntoView();
            
      closeAllLists();
      // Show everything if blank: if (!val) { return false;}
      currentFocus = -1;
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      this.parentNode.appendChild(a);      

      for (i = 0; i < arr.length; i++) {
        let key = arr[i][0];
        if (key == null) continue;
        let title = null;
        if (arr[i].length > 1) title = arr[i][1];
        else title = null;
          
        if (!val || key.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          b = document.createElement("DIV");
          b.innerHTML = "<strong>" + key.substr(0, val.length) + "</strong>";
          b.innerHTML += key.substr(val.length);
          if (title != null) b.innerHTML += '&nbsp;&nbsp;<i style="font-size:2vmin;">' + title + '</i>';
          b.innerHTML += "<input type='hidden' value='" + key + "'>";
          b.addEventListener("click", function(e) {
              inp.value = this.getElementsByTagName("input")[0].value;
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        currentFocus++;
        addActive(x);
      } else if (e.keyCode == 38) { //up
        currentFocus--;
        addActive(x);
      } else if (e.keyCode == 13) {
        e.preventDefault();
        if (currentFocus > -1) {
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    if (!x) return false;
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}


function onMouseOut (comp, img) {
    if (MENUS.isLocked()) return;

    comp.src='/kastmenu/images/' + img;
};

function onRefreshClick (comp) {
    if (MENUS.isLocked()) return;    
    alert ('FONCTION DEPRECATED !');
    return;
    
    // comp.style.cursor='wait'; 	
    // D001: MENUS.get();
};
  

function setCurrentMenu(id) {
  MENUS.setCurrentMenu(id);
}

function setCurrentOo(id, ooid) {
  MENUS.getMenu(id).setCurrentOo(ooid);
}

function showAll() {
    MENUS.showAll();
    var hint_all_box=document.getElementById('hint_all_box');
    hint_all_box.style.display='block'
}

function hideAll() {
    MENUS.hideAll();
    var hint_all_box=document.getElementById('hint_all_box');
    hint_all_box.style.display='none'
}

function switchWrapNoWrap(divid) {
    div=document.getElementById(divid);
    
    if (div.style.overflowX!='scroll') {
      div.style.overflowX='scroll';
      div.style.wordWrap='normal';
      div.style.wordBreak='normal';
    }
    else {
      div.style.overflowX='hidden';
      div.style.wordWrap='break-word';
      div.style.wordBreak='break-all';
    }
}

function select(id) {
    unSelect();
    if (document.selection) {
	var range = document.body.createTextRange();
	range.moveToElementText(document.getElementById(id));
	range.select();
    }
    else if (window.getSelection) {
	var range = document.createRange();
	range.selectNode(document.getElementById(id));
	window.getSelection().addRange(range);
    }
}

function unSelect() {
	if (document.selection) document.selection.empty(); 
	else if (window.getSelection)
	window.getSelection().removeAllRanges();
}


function hide(divid) {
    var div=document.getElementById(divid);
    div.style.display='none';
}


function dialogOOEnter(but_confirm_ok) {
    if (event.key != "Enter") return;
    const obut_confirm_ok=document.getElementById(but_confirm_ok);        
    obut_confirm_ok.click();
}



function olKeyPress(event) {
    if (event.key == "Enter") {
        let image = document.getElementById("optionlist_search_image");        
        const ofieldkey=document.getElementById("optionlist_key");
        const value = event.target.value;
        curkey = ofieldkey.innerHTML;
        image.style.color='deepskyblue';
        OPTION_LIST.makeOptionListSearch(curkey, value);
    }
    else {
        let image = document.getElementById("optionlist_search_image");
        image.style.color='white';
    }
}
function olSearchClick(obutton) {
    const ofieldkey=document.getElementById("optionlist_key");
    prevKey = ofieldkey.innerHTML;    
    previ = OPTION_LIST._datas.contents.okeys.indexOf(prevKey);
    if (previ + 1 < OPTION_LIST._datas.contents.okeys.length) nexti = previ + 1;
    else nexti=0;
    
    nextkey = OPTION_LIST._datas.contents.okeys[nexti];
    ofieldkey.innerHTML = nextkey;    
    OPTION_LIST.makeOptionListSearch(nextkey, null);
}

function olSelect(value) {
    let id = "{id}_{ooid}".replace('{id}', OPTION_LIST._lastMenu._id.toString()).replace('{ooid}', (OPTION_LIST._lastMenu._oos.length -1) .toString());
    let inputField = document.getElementById('oo_input_' + id);
    let confirmOk = document.getElementById('confirm_ok_' + id);
    inputField.value = value;
    confirmOk.click();
    switchMenuScreen();
}



function switchInputImage(obutton, inputfield, srcfrom, srcto) {
    let oinputfield=document.getElementById(inputfield);
    
    if (obutton.className == srcfrom) {
        oinputfield.dataset.imageSvn = srcto;
        obutton.className = srcto;
        return;
    }
    if (obutton.className == srcto) {
        oinputfield.dataset.imageSvn = srcfrom;
        obutton.className = srcfrom;
    }
}

function launchMenu(go_parms) {
    MENUS.clear();
    OO_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/oo_websocket_get/session-part/" + getSessionPart());
    launchOO_WEBSOCKET_GET();
    MENU_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/menu_websocket_get/session-part/" + getSessionPart());
    launchMENU_WEBSOCKET_GET();

    // New Url:
    let newUrl =  '/kastmenu/machine/[machine]/user/[user]/menu/[menu]'.replace('[machine]', go_parms['machine']).replace('[user]', go_parms['user']).replace('[menu]', go_parms['menu']);
    let menupath = go_parms['menupath']
    if (menupath != null && menupath != '') newUrl = newUrl + '/menupath/[menupath]'.replace('[menupath]', go_parms['menupath']);
    window.history.pushState(go_parms, null, newUrl);
    DISPATCHER._CURRENT_LOCATION = newUrl;
    DISPATCHER._CURRENT_ADMIN_PAGE = 'MACHINE';
    DISPATCHER._CURRENT_ADMIN_GO_PARMS = go_parms;
    document.title = go_parms['user'] + '@' + go_parms['machine'];
    //++
    setSessionStorageMachineUser(go_parms['user'], go_parms['machine']);
    switchMenuScreen();
}


/* ================================================================================================================================= *
  |                | 
  | Class Dispatch |
  |                | 
  * ============== */

// https://192.168.0.13:9000/kastmenu/machine/aaaaa/user/bbbbbb/password/cccccc/menu/dddddd/menupath/eeeeee
DISPATCHER = {
    _call_url: "/kastmenu/dispatch/",
    _call_url_utils: "/kastmenu/utils",
    _is_locked: false,
    _CURRENT_ADMIN_PAGE: null,
    _CURRENT_ADMIN_PAGE_TAB: 'LOGIN',
    _CURRENT_ADMIN_GO_PARMS: null,
    _CURRENT_LOCATION: null,
    _GET_LABEL_ONCE_getPublicMachines: null,
    
    onload : async function (loadvalue) {
        session_part = getSessionPart();
        if ((session_part == null) || (session_part == '')) {
            session_parts = await genSessionPart();
            session_part = session_parts['session-part'];
            setSessionPart (session_part);
        }
        MENUS.clear();
        DISPATCHER._CURRENT_ADMIN_PAGE = null;
        DISPATCHER._CURRENT_ADMIN_PAGE_TAB = 'LOGIN';
        this.__CURRENT_LOCATION = null;
        DISPATCHER._CURRENT_ADMIN_GO_PARMS = null;
        await this.dispatch(loadvalue);
    },
    onunload : async function () {
        if (OO_WEBSOCKET_GET != null) OO_WEBSOCKET_GET.close();
        if (MENU_WEBSOCKET_GET != null) MENU_WEBSOCKET_GET.close();
    },
    lock : function () {
        MENUS.lock();
        var comp=document.getElementById("settings-running_img");
        if (comp == null) return;
        this._is_locked=true;                              
        comp.src='/kastmenu/images/' + "tec6tem-spinner-logo.gif"
    },
    
    unLock : function () {
        MENUS.unLock();
        var comp=document.getElementById("settings-running_img");
        if (comp == null) return;
        this._is_locked=false;
        comp.src='/kastmenu/images/' + "tec6tem-spinner-logo-slow.gif"
    },
        
    isLock : function () {
        return this._is_locked;
    },
    
    dispatch : async function (loadvalue) {
        let rets = null;
        
        if (loadvalue == null) {
            rets = await this.post(null);
        }
        else {
            rets = await this.post(loadvalue);
        }
        
        validations = rets['validations'];
        go_pages = rets['go_pages'];
        go_parms = go_pages['parms']
        DISPATCHER._CURRENT_ADMIN_GO_PARMS = go_parms;

        /*
{"go_pages": {"page": "machine", "parms": null}, "validations": {"succeed": true, "field": null, "message": null, "do_MenuSwitch": false}}
         */
        
        go_page = go_pages['page'];
        
      
        switch (go_page) {
        case 'machine':                  
            DISPATCHER._CURRENT_ADMIN_PAGE = 'MACHINE'            
            switchSettingScreen(false);
            DISPATCHER.settingsMachineValidation (go_parms, validations);
            settings_machine_onUserChange();
            settings_machine_onMachineChange();
            break;
        case 'admin':
            DISPATCHER._CURRENT_ADMIN_PAGE = 'ADMIN';
            switchSettingScreen(false);
            DISPATCHER.settingsAdminValidation (go_parms, validations);
            break;
        case 'menu':      
            switchMenuScreen();
            break;
        default:
            console.log(`Sorry, we are out of ${expr}.`);
        }
    },
    
    settingsMachineValidation : function (go_parms, validations) {
        hideSettingMachineError();
        
        // Machine Active Mail Management:
        // ------------------------------
        let has_mail = (DISPATCHER._CURRENT_ADMIN_PAGE_TAB == 'SIGNIN');
        let has_mail_vcode = false;
        if (validations!=null && validations["type"] == 'mail+vcode') {
            has_mail = false;
            has_mail_vcode = true;
            let divmail_vcode = document.getElementById("settings_machine_div_mail_vcode");
            divmail_vcode.style.display='block';
            /*
            let fieldmachine = document.getElementById("settings_machine_machine");
            let fieldpassword = document.getElementById('settings_machine_password');
            fieldpassword.placeholder=`Enter a new Password for your new user on machine: ${fieldmachine.value} !`;
            */
        }
        else if (validations!=null && validations["type"] == 'mail-vcode') {
            has_mail = false;
            has_mail_vcode = true;
            let vcode = document.getElementById("settings_machine_mail_vcode");
            vcode.disabled=true;
            /*
            let fieldmachine = document.getElementById("settings_machine_machine");
            let fieldpassword = document.getElementById('settings_machine_password');
            fieldpassword.placeholder=`Enter a new Password for your new user on machine: ${fieldmachine.value} !`;
            */
        }
        else if (validations!=null && validations["type"] == 'mail.out') {
            // Enable machine/user + vcode:
            let vcode = document.getElementById("settings_machine_mail_vcode");
            let fielduser = document.getElementById("settings_machine_user");
            vcode.disabled=false;
            fielduser.disabled=false;
            fielduser.value=go_parms['user'];
            vcode.value=go_parms['user'];
        
            setSessionStorageMachineUser(go_parms['user'], go_parms['machine']);
            switchSettingMachineAcceptMail2(false, go_parms);            
        }  
        
            
        // Check Is already authenticated:
        let div = document.getElementById("settings_machine_div_password");
        if (validations!=null && 'authenticated' in validations && validations['authenticated']==true) {                
            div.style.display='none';
        } 
        else {
            if (validations!=null) div.style.display='block';
        }

        // Feed fields:
        if (go_parms != null) {
            let fields = ['machine', 'user', 'menu', 'menupath'];
            if (has_mail) fields.push('mail');
            else if (has_mail_vcode) {
                fields.push('mail');
                fields.push('mail_vcode');
            };
            
            feedFields(fields, go_parms);
        }
        
        // Error Message:
        if (validations!=null && validations["succeed"] == false) {
            if (validations["message"] != null) {
                showSettingMachineError(validations["message"].replaceAll('\n', '<br>'), validations["field"], false);
            } else if (validations["+message"] != null) {
                showSettingMachineError(validations["+message"].replaceAll('\n', '<br>'), null, true);
            }        
        }
        
    },
    settingsAdminValidation : function (go_parms, validations) {
        hideSettingMachineError();
        
        // Error Message:
        if (validations!=null && validations["succeed"] == false) {
            if (validations["message"] != null) {
                showSettingAdminError(validations["message"].replaceAll('\n', '<br>'), validations["field"]);
            }
        }
            
        // Check Is already authenticated:
        div = document.getElementById("settings_admin_div_password");
        if (validations!=null && 'authenticated' in validations && validations['authenticated']==true) {                
            div.style.display='none';
        } 
        else {
            div.style.display='block';
        }
            
        // Feed fields:
        if (go_parms != null) {
            fields = ['user']
            for (let i = 0; i < fields.length; i++) {
                let field = fields[i];
                if (!(field in go_parms)) continue;
                let val = go_parms[field];
                
                field = document.getElementById("settings_admin_" + field);
                field.value = val;
                field.classList.add('is-valid')
            }
        }
    },

    settings_machine_submit: async function () {
        if (this.isLock()) return;
        
        parms = {}
        jsons = {'go_pages': {'page': 'machine', 'parms': parms, 'do_submit': true}}
        if (DISPATCHER._CURRENT_ADMIN_PAGE_TAB == 'LOGIN') jsons['go_pages']['type'] =  'login';
        else if (DISPATCHER._CURRENT_ADMIN_PAGE_TAB == 'SIGNIN') jsons['go_pages']['type'] =  'signin';

        // Feed fields:
        fields = ['machine', 'user', 'menu', 'menupath']
        
        // Machine Active Mail Management:
        let divmail = document.getElementById("settings_machine_div_mail");
        let divmail_vcode = document.getElementById("settings_machine_div_mail_vcode");
        if (divmail.style.display=='block') fields.push('mail');
        if (divmail_vcode.style.display=='block')  {
            fields.push('mail');
            fields.push('mail_vcode');
        }
            
        for (let i = 0; i < fields.length; i++) {
            let field = fields[i];
            let value = document.getElementById('settings_machine_' + field).value;
            if (value == '') continue;
            parms[field] = value;
        }
        let password = document.getElementById('settings_machine_password').value;
        if (password == '') password = null;
        jsons['go_pages']['password'] = password;

        // ==>
        rets = await this.post(jsons);    
        
        validations = rets['validations'];
        go_pages = rets['go_pages'];
        go_parms = go_pages['parms']
        
        if (validations['succeed']) {  
            launchMenu(go_parms);
        }
        else this.settingsMachineValidation (go_parms, validations);
    },
    settings_admin_submit: async function () {
        if (this.isLock()) return;
        
        parms = {}
        jsons = {'go_pages': {'page': 'admin', 'parms': parms, 'do_submit': true}}

        // Feed fields:
        fields = ['user']
        for (let i = 0; i < fields.length; i++) {
            let field = fields[i];
            let value = document.getElementById('settings_admin_' + field).value;
            parms[field] = value;
        }
        let password = document.getElementById('settings_admin_password').value;
        jsons['go_pages']['password'] = password;

        rets = await this.post(jsons);
        
        validations = rets['validations'];
        
        if (validations['succeed']) {           
            OO_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/oo_websocket_get/session-part/" + getSessionPart());
            launchOO_WEBSOCKET_GET();
            MENU_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/menu_websocket_get/session-part/" + getSessionPart());
            launchMENU_WEBSOCKET_GET();
            
            // New Url:
            let newUrl =  '/kastmenu/admin/[user]'.replace('[user]', parms['user']);
            window.history.pushState(parms, null, newUrl);
            DISPATCHER._CURRENT_LOCATION = newUrl;
            DISPATCHER._CURRENT_ADMIN_PAGE = 'ADMIN';
            DISPATCHER._CURRENT_ADMIN_GO_PARMS = parms;

            switchMenuScreen();
        }
        else this.settingsAdminValidation (parms, validations);
    },


    terminateMenu : async function () {
        try {
            values = await this.postutils('terminateMenu');
        }catch(error){
        }
        MENUS.clear();
        switchSettingScreen();
    },

    
    post : async function (values) {     
        output = await this._call_ajax(this._call_url, values, true);        
        return JSON.parse(output);
    },
    postutils : async function (uri, values) {     
        output = await this._call_ajax(this._call_url_utils + '/' + uri, values, false);        
        return JSON.parse(output);
    },
    
    /* ---------- */
    /* Lazy Calls */
    /* ---------- */
    _call_ajax : async function (url, values, do_error) {  
        this.lock()        
        if (values == null) values = {};
        if (do_error == null) do_error = false;
        

    // bootstrap5: call: Works but seems to have some latency => Replacing fetch get by MenuWebSocket -->
    let response = null;
    try {
        response = await fetch(
            url, 
            {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                'Session-Part': getSessionPart(),
                // Default: 300sec, here 7sec:
                signal: AbortSignal.timeout(7000)
                },
                body: JSON.stringify(values)
            });
        
        
        if (! (MENUS.COMMAND_IS_RUNNING)) this.unLock()
        
        //Response from server
        if (response.status == 450 && do_error) // Activation Limit Exception:           
            throw new ActivationLimitError ({
                name: 'ActivationLimitError',
                code: response.status,
                message: await response.text()
            });
        
        
        return response.text();       

    }catch(error){
        if (error instanceof ActivationLimitError) {   
          message = JSON.parse(error.message).error.message;
          makeGlobalError(message, 'violet');
          switchMenuScreen ();
                    
          // Unlock MENUS
          MENUS.unLock();
          throw error;
          
          // console.log(e)
        }
    }
    },
    
    
}
    
class ActivationLimitError extends Error {
    constructor({name, code, message}) {
        super();
        this.name = name;
        this.code = code;
        this.message = message;
    }
}
    
async function restartMenu() {
    MENUS.clear();
    window.location.href = DISPATCHER._CURRENT_LOCATION;
}


/* ----------- *
 * Menu Screen *
 * ----------- */
function switchMenuScreen () {
    DISPATCHER._CURRENT_PAGE = 'MENU'   
    
    let fh = document.getElementById("frame_header"); // to restore
    let fc = document.getElementById("frame_content");
    let fh2 = document.getElementById("frame_header2"); // to close
    let fc2 = document.getElementById("frame_content2");
    
    fh.style.display='block';
    fc.style.display='block';
    fh2.style.display='none';
    fc2.style.display='none';
}


/* --------------- *
 * Settings Screen *
 * --------------- */
function switchSettingScreen (doFeed) {
    if (doFeed == null) doFeed = true;
    let machine_is_active = false;
    let admin_is_active = false;
    
    switch (DISPATCHER._CURRENT_ADMIN_PAGE) {
    case 'MACHINE':            
        DISPATCHER._CURRENT_PAGE = 'MACHINE'            
        machine_is_active = true;
        break;
    case 'ADMIN':
        DISPATCHER._CURRENT_PAGE = 'ADMIN'            
        admin_is_active = true;
        break;
    default:
        machine_is_active = true;
        DISPATCHER._CURRENT_PAGE = 'MACHINE'  
        DISPATCHER._CURRENT_ADMIN_PAGE = 'MACHINE';
    }

    let fh = document.getElementById("frame_header"); // to close:
    let fc = document.getElementById("frame_content");
    let fh2 = document.getElementById("frame_header2"); // to open:
    let fc2 = document.getElementById("frame_content2");
    let gs2 = document.getElementById("global_screen2");  // to feed 
    
    //prevents browser from storing history with each change:
    // window.history.pushState('blabla', 'Title', '/kastmenu/blabla.html');
    
    // Display:
    var source = document.getElementById("global-settings-template").innerHTML;
    var template = Handlebars.compile(source);
    
    gs2.innerHTML = template({'machine_is_active': machine_is_active, 'admin_is_active': admin_is_active});
    
    
    if (doFeed) {
        switch (DISPATCHER._CURRENT_ADMIN_PAGE) {
        case 'MACHINE':            
            DISPATCHER.settingsMachineValidation (DISPATCHER._CURRENT_ADMIN_GO_PARMS, null);
            break;
        case 'ADMIN':
            DISPATCHER.settingsAdminValidation (DISPATCHER._CURRENT_ADMIN_GO_PARMS, null);
            break;
        }
    }
    
    fh.style.display='none';
    fc.style.display='none';
    fh2.style.display='block';
    fc2.style.display='block'; 
    
    settings_machine_onMachineChange();
}

function switchSettingMachineAcceptMail1 (doswitch, machine, title) {
    let divsmx = document.getElementById("settings_machine_xacceptmail");
    if (doswitch) { 
        let msg = `This machine: ${machine} supports Mail Signin !\n To create your personal user on this machine select Signin.`;        
        if (title!=null) msg = msg + '\n' + title.replaceAll('\n', '<br>');
        showSettingMachineError(msg, null, true);
        divsmx.style.display='block';
    }
    else divsmx.style.display='none';
}

function switchSettingMachineAcceptMail2 (toMail, go_parms) {
    fielduser = document.getElementById("settings_machine_user");
    fieldmail = document.getElementById("settings_machine_mail");
    fieldpassword = document.getElementById("settings_machine_password");
    div_password = document.getElementById("settings_machine_div_password");    
    div_password.style.display='none';

        
    // To Mail:
    // --------
    if (toMail==true) {        
        DISPATCHER._CURRENT_ADMIN_PAGE_TAB='SIGNIN';
        
        let divmail = document.getElementById("settings_machine_div_mail");
        let divuser = document.getElementById("settings_machine_div_user");
        let divmenu = document.getElementById("settings_machine_div_menu");
        let divmenupath = document.getElementById("settings_machine_div_menupath");
        let vcode = document.getElementById("settings_machine_mail_vcode");
        vcode.value='';
        // tabbed panes:
        document.getElementById('settings_machine_xacceptmail_login').classList.remove('active');
        document.getElementById('settings_machine_xacceptmail_signin').classList.add('active');
        
        if (divmail.style.display=='none') {
            divmail.style.display='block';
            divuser.style.display='none';
            divmenu.style.display='none';
            divmenupath.style.display='none';
            // Firstime retreive the value from user:                    
            if (go_parms!=null && go_parms['user']!=null && go_parms['user']!='' && go_parms['user'].indexOf('@') > -1) {
                go_parms['mail'] = go_parms['user'];
            }
            else if (go_parms==null && fielduser.value!='' && fielduser.value.indexOf('@') > -1) {
                fieldmail.value = fielduser.value;
            }
            if (go_parms!=null) go_parms['user'] = null;
            // else fielduser.value = null;
            // Disable machine/user:
            fieldmachine = document.getElementById("settings_machine_machine");
            fieldmachine.disabled = true;
            fieldpassword.placeholder=`Enter a new Password for your new user on machine: ${fieldmachine.value} !`;
            fieldpassword.value = '';
            // fielduser = document.getElementById("settings_machine_user");
            // fielduser.value = '';
        }
        divmail.style.display='block';
        return;
    }
    
    // To Login:
    // ---------
    DISPATCHER._CURRENT_ADMIN_PAGE_TAB='LOGIN';
    has_mail = false;
    has_mail_vcode = false;
    let divmail = document.getElementById("settings_machine_div_mail");
    let divmail_vcode = document.getElementById("settings_machine_div_mail_vcode");
    let divuser = document.getElementById("settings_machine_div_user");
    let divmenu = document.getElementById("settings_machine_div_menu");
    let divmenupath = document.getElementById("settings_machine_div_menupath");
    fieldpassword.placeholder="Enter User Password";
    // tabbed panes:
    document.getElementById('settings_machine_xacceptmail_signin').classList.remove('active');
    document.getElementById('settings_machine_xacceptmail_login').classList.add('active');
        
    fieldmachine = document.getElementById("settings_machine_machine");
    fielduser = document.getElementById("settings_machine_user");
    fieldmenu = document.getElementById("settings_machine_menu");
    fieldmenupath = document.getElementById("settings_machine_menupath");
    divmail.style.display='none';
    divmail_vcode.style.display='none';
    divuser.style.display='block';
    divmenu.style.display='block';
    divmenupath.style.display='block';
    if (go_parms!=null) fielduser.value=go_parms['user'];
    // Enable machine/user:    
    fieldmachine.disabled = false; 
    if (go_parms!=null) fieldmenu.value = go_parms['menu'];
    fieldmenupath.value = '';
}

// Machine/Admin Autocomplete:
// ===========================
async function settings_machine_onMachineChange () {    
    getSupportXAcceptMail();
}   
async function settings_machine_onMachineFocus () {   
    // Feed Machine Public only:
    user = document.getElementById("settings_machine_user").value;    
    let rets = null;
    if (DISPATCHER._GET_LABEL_ONCE_getPublicMachines != null) rets = DISPATCHER._GET_LABEL_ONCE_getPublicMachines;
    else rets = await DISPATCHER.postutils('getPublicMachines', null);
    DISPATCHER._GET_LABEL_ONCE_getPublicMachines = rets;
    if (rets == null) return;
    values = rets['values'];
    if (values == null) return;
    
    let inp = document.getElementById("settings_machine_machine");
    autocomplete(inp, values);
    
    // If value is blank force event:input to trigger list:
    if (inp.value=='' || inp.value==null) {
        inp.dispatchEvent(new Event('input'));
    }
}

async function settings_machine_onUserChange () {
    // Feed Machine/UserMachine:
    inp = document.getElementById("settings_machine_user");
    user = inp.value;
    let machine = document.getElementById("settings_machine_machine");    

    let values=null;        
    if (machine.value != '' && machine.value!=null) {
        datas = {'machine': machine.value}
        rets = await DISPATCHER.postutils('getPublicUsers', datas);
        if (rets != null) values = rets['values'];   
    }
    
    session_users = getSessionStorageMachineUsers ();
    if (values == null && session_users == null) return;
    let ars = [];
    if (session_users != null) {
        for (let i=0; i<session_users.length; i++) {
            let vals = session_users[i].split(';');
            if (ars.includes(vals)) continue;
            ars.push(vals)
        }
    }
    session_users = ars;
    if (values == null) values = session_users;
    else {
        if (session_users != null) values.push(...session_users);
    }
    
    autocomplete(inp, values);
    
    // If value is blank force event:input to trigger list:
    if (inp.value=='' || inp.value==null) {
        inp.dispatchEvent(new Event('input'));
    }
}
async function settings_machine_onUserFocus () {    
    machine = document.getElementById("settings_machine_machine").value;
    if (machine == '') return;
    // Feed User Menu:
    user = document.getElementById("settings_machine_user").value;
    let wasUserNull=false;
    if (user == '') {
        user = null;
        wasUserNull=true;
    }
    
    datas = {'user': user, 'machine': machine}
    rets = await DISPATCHER.postutils('getUserMenus', datas);
    if (rets == null) return;
    values = rets['values'];
    if (values == null) return;
    
    // If user was null -> returned dftuser (for machine) feeds user. And dftmenu feeds menu. :
    if (wasUserNull) {
        dftuser = rets['validations']['user']
        if (dftuser!=null) {
            user = document.getElementById("settings_machine_user");
            menu = document.getElementById("settings_machine_menu");
            user.value = dftuser;
            menu.value = values[0][0];
        }
    }
        
    let inp = document.getElementById("settings_machine_menu");
    autocomplete(inp, values);
}
async function settings_machine_onMenuFileFocus () {    
    machine = document.getElementById("settings_machine_machine").value;
    if (machine == '') return;
    // Feed User Menu:
    user = document.getElementById("settings_machine_user").value;
    if (user == '') return;
    
    datas = {'user': user, 'machine': machine}
    rets = await DISPATCHER.postutils('getUserMenus', datas);
    if (rets == null) return;
    values = rets['values'];
    if (values == null) return;
        
    let inp = document.getElementById("settings_machine_menu");
    autocomplete(inp, values);
    // If value is blank force event:input to trigger list:
    if (inp.value=='' || inp.value==null) {
        inp.dispatchEvent(new Event('input'));
    }
}



async function getSupportXAcceptMail () {    
    machine = document.getElementById("settings_machine_machine").value;
    if (machine == '') return;
    
    // Check Machine Supports acceptMail (Sigin)
    datas = {'machine': machine}
    rets = await DISPATCHER.postutils('getSupportXAcceptMail', datas);
    if (rets != null && rets['values']!=null) {
        fmachine = document.getElementById("settings_machine_machine");
        fuser = document.getElementById("settings_machine_user");
        fmenu = document.getElementById("settings_machine_menu");
        
        let more = '';
        if (fmachine.classList.contains('is-valid') && fuser.classList.contains('is-valid') && fmenu.classList.contains('is-valid'))
            more = '\nOr you can Validate your current tab to access the Menu.';
        
        xacceptmail = rets['values']['xacceptmail'];

        if (xacceptmail) {
            title = rets['title'];
            if (title == null) title = ''
            switchSettingMachineAcceptMail1(true, machine, title + more);
        } else switchSettingMachineAcceptMail1(false, null, null);
    } else switchSettingMachineAcceptMail1(false, null, null);
}   





/* ================================================================================================================================= */  

const urlify = (text) => {
  const urlRegex = /(https?:\/\/[^\s\'\"\<\>]+)/g;
  return text.replace(urlRegex, (url) => {
    //noopener noreferrer: to prevent the newly opened tab from being able to modify the original tab maliciously
    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
  })
}





/* =========== *
  |            | 
  | WEBSOCKETS |
  |            | 
  * ========== */


// OO_WEBSOCKET_GET:
// =================


// Now Managed by DISPATCHER:
// var OO_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/oo_websocket_get");
var OO_WEBSOCKET_GET = null;


function launchOO_WEBSOCKET_GET () {
    /*
    ws.onopen = function() {
    ws.send("Hello, world");
    };*/
    OO_WEBSOCKET_GET.onmessage = function (evt) {
        
    /* alert(evt.data);    
        data = window.btoa(msg)  // Encode to base64
        msg = window.atob(data)  // Decode base64
        e.g.:
    16937336803770981[[COID]][[NEW_PROCESS_OUTPUT]]
    16937336803770981[[COID]]Execute command:dir waaaaa t;u b
    16937336803770981[[COID]] 
    16937336803770981[[COID]]dir: cannot access 'waaaaa': No such file or directory
    16937336803770981[[COID]]dir: cannot access 't': No such file or directory
    16937336803770981[[COID]]/bin/sh: 1: u: not found
    16937336803770981[[COID]] 
    16937336803770981[[COID]]Return Code is:127
        */

    // return;
    
        // spl = window.atob(evt.data).split("[[COID]]");
        spl = evt.data.split("[[COID]]");
        
        coid = spl[0];
        message = spl[1];
        
        
        if (message == "[[NEW_PROCESS_OUTPUT]]") {
            MENUS.getLastMenu().makeCommandOutput("", coid);
            return;
        }
        if (! message.endsWith("<BR>")) message += "<BR>";
        
                
        code = document.getElementById(coid);
        message = urlify(message);
        
        code.innerHTML += message;
        /*
        code.dataset.highlighted = false; 
        delete code.dataset.highlighted; 
        hljs.highlightElement(code);
        */    
    };
    
    OO_WEBSOCKET_GET.onclose = function (evt) {    
        try {
            OO_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/oo_websocket_get/session-part/" + getSessionPart());
            launchOO_WEBSOCKET_GET();
        }catch(error){
            MENUS.clear();
            switchSettingScreen();
        }
    };  
}


// MENU_WEBSOCKET_GET:
// ==================

// Now Managed by DISPATCHER:
// var MENU_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/menu_websocket_get");
var MENU_WEBSOCKET_GET = null;

function feedFields (fields, parms) {
    for (let i = 0; i < fields.length; i++) {
        let field = fields[i];
        if (!(field in parms)) continue;
        let val = parms[field];
        
        field = document.getElementById("settings_machine_" + field);
        field.value = val;
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    }
}

function launchMENU_WEBSOCKET_GET () {
    /*
    ws.onopen = function() {
    ws.send("Hello, world");
    };*/
    MENU_WEBSOCKET_GET.onmessage = function (evt) {
        let datas = evt.data
        datas = JSON.parse(datas)

        try {
            MENUS._call_ajax_parse(datas);

        }catch(error){
            //handle error
            makeGlobalError(error, null);

            // Unlock MENUS
            MENUS.unLock();

            // Unlock Dialog
            var oodialog=MENUS.getLastMenu().getActiveOodialog();
            if (oodialog != null) {
                // MENUS.getLastMenu()._active_oodialog = null;
                var div=oodialog.getDiv();
                div.style.pointerEvents='auto';
                div.style.cursor='normal';
                oodialog.stopGoing();

                ifd=oodialog.getInputField();
                if (ifd!=null) ifd.focus();
            }

            // console.log(e)
        }
    };
    
    
    MENU_WEBSOCKET_GET.onclose = function (evt) {
        try {
            MENU_WEBSOCKET_GET = new WebSocket("wss://" + window.location.host + "/kmenu/menu_websocket_get/session-part/" + getSessionPart());
            launchMENU_WEBSOCKET_GET(); 
        }catch(error){
            MENUS.clear();
            switchSettingScreen();
        }
    };    
}
