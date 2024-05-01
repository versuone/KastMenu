config = {
    title = "OAT Environment Management"
    temp_dir = "/tmp"
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
    }
}
