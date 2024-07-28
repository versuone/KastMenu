config = {
    title = "OAT Environment Management"
    temp_dir = "/tmp"
    menu = {
        title = "menua"
        confirm_exit = True
        option = {
            name = "optiona1"
            command = "ls -ltr"
        }
        option = {
            name = "optiona2"
            help = "MyHelp optiona2"
            command = "dir"
            confirm = True
        }
        option = {
            name = "optiona3"
            command = "dir"
        }
        option = {
            name = "optiona4"
            help = "MyHelp optiona4"
            command = "ls -ltr"
        }
        option = {
            name = "option5"
            help = "MyHelp optiona5"
            command = "ls -ltr"
        }
        option = {
            name = "optiona5"
            command = "ls -ltr"
        }
        option = {
            name = "optiona6"
            command = "dir"
        }
        menu = {
            title = "menub"
            option = {
                name = "optionb1"
                command = "dir"
            }
            option = {
                name = "optionb3"
                command = "ls -ltr"
            }
            option = {
                name = "optionb4"
                command = "dir"
            }
            option = {
                name = "optionb5"
                command = "ls -ltr"
            }
            option = {
                name = "option6"
                command = "ls -ltr"
            }
            menu = {
                title = "menuc"
                option = {
                    name = "optionc1"
                    command = "ls -ltr"
                }
                option = {
                    name = "optionc5"
                    command = "dir"
                }
                imenu = {
                    title = "MyIMenu1"
                    help = "MyIMenu1 help."
                    command = "dir $field1 $field2 $field3"
                    confirm = True
                    ioption = {
                        name = "field1"
                        help = "myfield1 help"
                        wk = {"*type": "str", "*value": "test1.dat"}
                    }
                    ioption = {
                        __text__ = {"*type": "list", "*ltype": {"*type": "int"}, "*value": [1, 2, 3]}
                        name = "field2"
                        help = "myfield2 help"
                    }
                    ioption = {
                        name = "field3"
                        help = "myfield3 help"
                        wk = {"*type": "str", "*value": "test3.dat"}
                    }
                    option = {
                        name = "option1"
                        command = "dir"
                    }
                    option = {
                        name = "option2"
                        help = "MyHelp optiona4"
                        command = "ls -ltr"
                    }
                    menu = {
                        title = "menub"
                        option = {
                            name = "optionb1"
                            command = "dir"
                        }
                        option = {
                            name = "optionb3"
                            command = "ls -ltr"
                        }
                        option = {
                            name = "optionb4"
                            command = "dir"
                        }
                        option = {
                            name = "optionb5"
                            command = "ls -ltr"
                        }
                    }
                    imenu = {
                        title = "MyIMenu2"
                        help = "MyIMenu2 help."
                        command = "dir $field1 $field2 $field3"
                        confirm = True
                        ioption = {
                            name = "field1"
                            help = "myfield1 help"
                            wk = {"*value": "test1.dat", "*label": "My Field1"}
                        }
                        ioption = {
                            __text__ = {"*type": "list", "*value": ["test1.dat", "test2.dat", "test3.dat", "a", "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "mk", "l", "m"], "*label": "My Field2"}
                            name = "field2"
                            help = "myfield2 help"
                        }
                        ioption = {
                            name = "field3"
                            help = "myfield3 help"
                            wk = {"*value": "a", "*checkIn": ("a", "b", "c")}
                        }
                        ioption = {
                            name = "field4"
                            help = "myfield4 help"
                            wk = {"*type": "int", "*value": 3, "*label": "My Field4"}
                        }
                        ioption = {
                            __text__ = {"*type": "list"}
                            name = "field5"
                            help = "myfield5 help"
                        }
                        ioption = {
                            __text__ = {"*type": "list", "*ltype": {"*type": "int"}, "*value": [1, 2, 3]}
                            name = "field6"
                        }
                    }
                }
            }
        }
        menu = {
            title = "menud"
            option = {
                name = "optiond1"
                command = "ls -ltr"
            }
            option = {
                name = "optiond2"
                command = "ls -ltr"
            }
            option = {
                name = "optiond3"
                command = "dir"
            }
            option = {
                name = "optiond1"
                command = "ls -ltr"
            }
            option = {
                name = "optiond2"
                command = "ls -ltr"
            }
            option = {
                name = "optiond3"
                command = "ls -ltr"
            }
            imenu = {
                title = "MyIMenu2"
                help = "MyIMenu2 help."
                command = "dir $field1 $field2 $field3"
                confirm = True
                set_color = True
                police_bold = True
                police_color = "RED"
                police_bgcolor = "YELLOW"
                ioption = {
                    name = "field1"
                    help = "myfield1 help"
                    wk = {"*value": "test1.dat", "*label": "My Field1"}
                }
                ioption = {
                    __text__ = {"*type": "list", "*value": ["test1.dat", "test2.dat", "test3.dat", "a", "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "mk", "l", "m"], "*label": "My Field2"}
                    name = "field2"
                    help = "myfield2 help"
                }
                ioption = {
                    name = "field3"
                    help = "myfield3 help"
                    wk = {"*value": "a", "*checkIn": ("a", "b", "c")}
                }
                ioption = {
                    name = "field4"
                    help = "myfield4 help"
                    wk = {"*type": "int", "*value": 3, "*label": "My Field4"}
                    set_color = True
                    police_bold = True
                    police_color = "CYAN"
                    police_bgcolor = "GREEN"
                }
                ioption = {
                    __text__ = {"*type": "list"}
                    name = "field5"
                    help = "myfield5 help"
                }
                ioption = {
                    __text__ = {"*type": "list", "*ltype": {"*type": "int"}, "*value": [1, 2, 3]}
                    name = "field6"
                }
            }
        }
    }
}
