#!/usr/bin/python
#encoding:utf-8
#mysql connect information, used by db_construct.py and 
import os,sys,stat
import commands
import stat
from sys import path
path.append(sys.path[0]+"/model/")
import db_construct
def read_config(file_path):
    config_dict={}
    fopen=open(file_path,'r')
    for field in fopen:
        field=field.strip()
        if field.startswith("#"):
            continue
        else:
            valid_part=field.split('#')
            valid_value=valid_part[0]
            first_equal_site=valid_value.index("=")
            e=first_equal_site
            config_dict[valid_value[:e].strip()]=valid_value[e+1:].strip()
    return config_dict
def chmod_check(execute_file):
    if os.path.isfile(execute_file):
        permission_number=stat.S_IMODE(os.stat(execute_file ).st_mode)&stat.S_IXGRP
    else:
        print "%s is not found."%(execute_file)
        sys.exit(1)
    return permission_number
script_loc=os.path.split(os.path.realpath(sys.argv[0]))[0]
config_file_root=script_loc+"/config.txt"
config_file_sub=script_loc.strip("model")+"/config.txt"
if os.path.isfile(config_file_root):
    config_file=config_file_root
    pass
elif os.path.isfile(config_file_sub):
    config_file=config_file_sub
conf_dict=read_config(config_file)
host=conf_dict["host"]
username=conf_dict["username"]
password=conf_dict["password"]
db=conf_dict["database"]
port=conf_dict["port"]
if __name__=="__main__":
    script_loc=os.path.split(os.path.realpath(sys.argv[0]))[0]
    if not os.path.isfile(script_loc+"/config.txt"):
        print "ERROR, config.txt is not found."
        sys.exit(1)
    try:
        db_construct.create_conn(host,username,password)
        print "configuration check...OK"
    except:
        print "ERROR, can not connect to mysql database. Please, check for 'config.txt'."
        sys.exit(1)
    try:
        db_commands="python %s/model/db_construct.py" % (script_loc)
        os.system(db_commands)
        print "Database creation...OK"
    except:
        print "Error, can not operate mysql."
        sys.exit(1)
#permission
    check_file=script_loc+"/dbHT-Trans-Operator"
    result=chmod_check(check_file)
    if result:
        print "dbHT-Trans-Operator...OK"
    else:
        print "Error, it's failure to give execute permissions to 'dbHT-Trans-Operator'."
        sys.exit(1)
#
    check_file=script_loc+"/dbHT-Trans-Extractor"
    result=chmod_check(check_file)
    if result:
        print "dbHT-Trans-Extractor...OK"
    else:
        print "Error, it's failure to give execute permissions to 'dbHT-Trans-Extractor'."
        sys.exit(1)
#
    check_file=script_loc+"/model/usearch7.0.1090_i86linux32"
    result=chmod_check(check_file)
    if result:
        print "usearch7.0.1090_i86linux32...OK"
    else:
        print "Error, it's failure to give execute permissions to 'model/usearch7.0.1090_i86linux32'."
        sys.exit(1)
